import uuid
import time
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.core.config import settings
from app.challenge1_evaluator.schemas import (
    EvaluationRequest,
    EvaluationResult,
    ScoreBreakdown,
    ConceptAnalysis
)
from app.challenge1_evaluator.concept_extractor import concept_extractor
from app.challenge1_evaluator.scoring_engine import scoring_engine
from app.challenge1_evaluator.feedback_generator import feedback_generator
from app.challenge1_evaluator.subjects.math_evaluator import math_evaluator
from app.challenge1_evaluator.subjects.science_evaluator import science_evaluator
from app.challenge1_evaluator.subjects.english_evaluator import english_evaluator
from app.challenge1_evaluator.subjects.general_evaluator import general_evaluator
from app.governance.audit_logger import audit_logger
from app.governance.human_oversight import human_oversight
from app.governance.prompt_versioning import prompt_versioning
from app.governance.bias_detector import bias_detector
from app.models.evaluation import Evaluation


# ── GRADE INFO HELPER (replaces missing scoring_engine.get_grade_info) ──
GRADE_THRESHOLDS = [
    {"min": 9.0, "max": 10.0, "grade": "A+", "label": "Outstanding"},
    {"min": 8.0, "max": 9.0,  "grade": "A",  "label": "Excellent"},
    {"min": 7.0, "max": 8.0,  "grade": "B+", "label": "Very Good"},
    {"min": 6.0, "max": 7.0,  "grade": "B",  "label": "Good"},
    {"min": 5.0, "max": 6.0,  "grade": "C",  "label": "Average"},
    {"min": 4.0, "max": 5.0,  "grade": "D",  "label": "Below Average"},
    {"min": 0.0, "max": 4.0,  "grade": "F",  "label": "Fail"},
]

def get_grade_info(score_out_of_10: float) -> Dict[str, str]:
    """Get grade letter and label from score."""
    for t in GRADE_THRESHOLDS:
        if t["min"] <= score_out_of_10 <= t["max"]:
            return {"grade": t["grade"], "label": t["label"]}
    return {"grade": "F", "label": "Fail"}


class EvaluatorService:
    """Main evaluation service."""

    def _get_subject_evaluator(self, subject: str):
        evaluators = {
            "mathematics": math_evaluator,
            "math":        math_evaluator,
            "science":     science_evaluator,
            "english":     english_evaluator,
            "general":     general_evaluator,
        }
        return evaluators.get(subject.lower(), general_evaluator)

    def _is_math_subject(self, subject: str) -> bool:
        return subject.lower() in (
            'mathematics', 'math', 'algebra', 'calculus',
            'geometry', 'arithmetic', 'trigonometry', 'statistics'
        )

    async def evaluate(
        self,
        request: EvaluationRequest,
        db: Optional[Session] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        request_id = request_id or str(uuid.uuid4())

        logger.info(f"Starting evaluation: id={request_id} subject={request.subject}")

        try:
            # STEP 1: Semantic similarity
            semantic_sim = scoring_engine.calculate_semantic_score(
                request.student_answer, request.reference_answer
            )
            logger.debug(f"Semantic similarity: {semantic_sim:.3f}")

            # STEP 2: Concept extraction
            concept_analysis = await concept_extractor.full_concept_analysis(
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                subject=request.subject
            )
            concept_coverage = concept_analysis["coverage_percentage"] / 100.0
            logger.debug(f"Concept coverage: {concept_analysis['coverage_percentage']}%")

            # STEP 3: Subject-specific LLM evaluation
            subject_evaluator = self._get_subject_evaluator(request.subject)
            llm_scores = await subject_evaluator.evaluate(
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                grade_level=request.grade_level
            )
            logger.debug(f"LLM scores: {llm_scores}")

            # STEP 4: Score aggregation
            correctness = scoring_engine.calculate_correctness_score(
                semantic_similarity=semantic_sim,
                llm_correctness=llm_scores.get("correctness", 0.5),
                concept_coverage=concept_coverage
            )
            relevance = scoring_engine.calculate_relevance_score(
                semantic_similarity=semantic_sim,
                llm_relevance=llm_scores.get("relevance", 0.5)
            )
            completeness = scoring_engine.calculate_completeness_score(
                concept_coverage=concept_coverage,
                llm_completeness=llm_scores.get("completeness", 0.5)
            )
            clarity = scoring_engine.calculate_clarity_score(
                llm_clarity=llm_scores.get("clarity", 0.5)
            )

            # ══════════════════════════════════════════════════
            # MATH OVERRIDE: Subject evaluator takes precedence
            # ══════════════════════════════════════════════════
            if self._is_math_subject(request.subject):
                llm_correctness = llm_scores.get("correctness", 0.5)
                llm_completeness = llm_scores.get("completeness", 0.5)
                llm_relevance = llm_scores.get("relevance", 0.5)
                llm_clarity = llm_scores.get("clarity", 0.5)
                final_correct = llm_scores.get("final_answer_correct", None)

                if final_correct is True:
                    correctness = max(correctness, llm_correctness)
                    completeness = max(completeness, llm_completeness)
                    relevance = max(relevance, llm_relevance)
                    clarity = max(clarity, llm_clarity)
                    logger.info(
                        f"Math override: CORRECT answer. "
                        f"correctness={correctness:.2f}"
                    )
                elif final_correct is False:
                    correctness = min(correctness, llm_correctness)
                    completeness = min(completeness, llm_completeness)
                    logger.info(
                        f"Math override: WRONG answer. "
                        f"correctness={correctness:.2f}"
                    )

            # Strict mode
            if request.strict_mode:
                correctness = min(correctness, llm_scores.get("correctness", 0.5) * 0.8)
                completeness = min(completeness, concept_coverage * 0.8)

            # Clamp
            correctness = max(0.0, min(1.0, correctness))
            relevance   = max(0.0, min(1.0, relevance))
            completeness = max(0.0, min(1.0, completeness))
            clarity     = max(0.0, min(1.0, clarity))

            # Weighted scores
            correctness_weighted  = correctness * 40.0
            relevance_weighted    = relevance * 20.0
            completeness_weighted = completeness * 25.0
            clarity_weighted      = clarity * 15.0

            total_score = (
                correctness_weighted + relevance_weighted +
                completeness_weighted + clarity_weighted
            )
            score_out_of_10 = total_score / 10.0

            # ── USE INLINE GRADE FUNCTION ──────────────────────
            grade_info = get_grade_info(score_out_of_10)

            # Feedback — prefer LLM feedback (more specific and real)
            feedback = llm_scores.get("feedback", "")
            if not feedback or len(feedback) < 30:
                feedback = feedback_generator.generate_feedback(
                    score_out_of_10=score_out_of_10,
                    breakdown={
                        "correctness": correctness_weighted,
                        "relevance": relevance_weighted,
                        "completeness": completeness_weighted,
                        "clarity": clarity_weighted
                    },
                    concept_analysis=concept_analysis
                )

            suggestions = llm_scores.get("improvement_suggestions", [])
            if not suggestions:
                suggestions = feedback_generator.generate_suggestions(
                    score_breakdown={
                        "correctness": correctness_weighted,
                        "relevance": relevance_weighted,
                        "completeness": completeness_weighted,
                        "clarity": clarity_weighted
                    },
                    concept_analysis=concept_analysis
                )

            # Confidence
            if self._is_math_subject(request.subject):
                final_correct = llm_scores.get("final_answer_correct", None)
                if final_correct is True:
                    confidence = max(0.75, (semantic_sim * 0.3) + (llm_scores.get("correctness", 0.9) * 0.7))
                elif final_correct is False:
                    confidence = max(0.60, (semantic_sim * 0.3) + (llm_scores.get("correctness", 0.1) * 0.7))
                else:
                    confidence = (semantic_sim * 0.3) + (concept_coverage * 0.3) + (llm_scores.get("correctness", 0.5) * 0.4)
            else:
                confidence = (semantic_sim * 0.3) + (concept_coverage * 0.3) + (llm_scores.get("correctness", 0.5) * 0.4)

            confidence = max(0.0, min(1.0, confidence))
            review_required = confidence < getattr(settings, 'HUMAN_REVIEW_THRESHOLD', 0.6)

            bias_detector.scan_text(request.student_answer + " " + feedback)

            result_payload = {
                "request_id":       request_id,
                "score_out_of_10":  round(score_out_of_10, 2),
                "total_score":      round(total_score, 2),
                "percentage":       round(total_score, 2),
                "grade":            grade_info["grade"],
                "score_breakdown": {
                    "correctness":  round(correctness_weighted, 2),
                    "relevance":    round(relevance_weighted, 2),
                    "completeness": round(completeness_weighted, 2),
                    "clarity":      round(clarity_weighted, 2),
                    "total":        round(total_score, 2)
                },
                "concept_analysis":        concept_analysis,
                "feedback":                feedback,
                "improvement_suggestions": suggestions,
                "subject_specific_notes":   llm_scores.get("reasoning", ""),
                "semantic_similarity":     round(semantic_sim, 4),
                "confidence_score":        round(confidence, 3),
                "governance_status":       "flagged" if review_required else "passed",
                "human_review_required":   review_required,
                "model_used":              llm_scores.get("model_used", "openai/gpt-oss-20b"),
                "provider":                llm_scores.get("provider", "groq"),
                "processing_time_ms":      (time.time() - start_time) * 1000,
                "prompt_version":          "3.0.0"
            }

            if db:
                self._save_evaluation(db, result_payload, request, user_id)

            audit_logger.log_ai_decision(
                challenge="challenge1",
                request_id=request_id,
                model_used=result_payload["model_used"],
                confidence_score=result_payload["confidence_score"],
                status=result_payload["governance_status"],
                time_ms=result_payload["processing_time_ms"],
                summary=f"score={result_payload['score_out_of_10']}/10 grade={result_payload['grade']}",
                metadata={"subject": request.subject, "human_review": review_required}
            )

            return result_payload

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise

    def _save_evaluation(self, db, result, request, user_id):
        try:
            eval_model = Evaluation(
                id=str(uuid.uuid4()),
                request_id=result["request_id"],
                user_id=user_id or "anonymous",
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                subject=request.subject,
                grade_level=request.grade_level,
                total_score=result["total_score"],
                score_out_of_10=result["score_out_of_10"],
                correctness_score=result["score_breakdown"]["correctness"],
                relevance_score=result["score_breakdown"]["relevance"],
                completeness_score=result["score_breakdown"]["completeness"],
                clarity_score=result["score_breakdown"]["clarity"],
                percentage=result["percentage"],
                grade=result["grade"],
                correct_concepts=json.dumps(result["concept_analysis"]["correct_concepts"]),
                missing_concepts=json.dumps(result["concept_analysis"]["missing_concepts"]),
                wrong_concepts=json.dumps(result["concept_analysis"]["wrong_concepts"]),
                feedback=result["feedback"],
                improvement_suggestions=json.dumps(result["improvement_suggestions"]),
                semantic_similarity=result["semantic_similarity"],
                model_used=result["model_used"],
                provider=result["provider"],
                confidence_score=result["confidence_score"],
                processing_time_ms=result["processing_time_ms"],
                prompt_version=result["prompt_version"],
                governance_status=result["governance_status"],
                human_review_required=result["human_review_required"]
            )
            db.add(eval_model)
            db.commit()
            logger.info(f"Evaluation saved: {eval_model.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"DB save failed: {e}")


evaluator_service = EvaluatorService()
