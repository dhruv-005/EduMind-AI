import uuid
import time
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.core.config import settings
from app.challenge1_evaluator.schemas import EvaluationRequest
from app.challenge1_evaluator.subjects.math_evaluator import math_evaluator
from app.challenge1_evaluator.subjects.science_evaluator import science_evaluator
from app.challenge1_evaluator.subjects.english_evaluator import english_evaluator
from app.challenge1_evaluator.subjects.general_evaluator import general_evaluator
from app.governance.audit_logger import audit_logger
from app.governance.bias_detector import bias_detector
from app.models.evaluation import Evaluation


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
    for t in GRADE_THRESHOLDS:
        if t["min"] <= score_out_of_10 <= t["max"]:
            return {"grade": t["grade"], "label": t["label"]}
    return {"grade": "F", "label": "Fail"}


class EvaluatorService:
    """Master evaluator service across all subjects."""

    def _get_subject_evaluator(self, subject: str):
        evaluators = {
            "mathematics": math_evaluator,
            "math":        math_evaluator,
            "science":     science_evaluator,
            "physics":     science_evaluator,
            "chemistry":   science_evaluator,
            "biology":     science_evaluator,
            "english":     english_evaluator,
            "general":     general_evaluator,
            "history":     general_evaluator,
            "geography":   general_evaluator,
        }
        return evaluators.get(subject.lower(), general_evaluator)

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
            # 1. Subject-specific LLM evaluation with intelligent concept extraction
            subject_evaluator = self._get_subject_evaluator(request.subject)
            llm_scores = await subject_evaluator.evaluate(
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                grade_level=request.grade_level
            )

            # 2. Extract scores (0.0 to 1.0 scale)
            correctness = float(llm_scores.get("correctness", 0.5))
            relevance   = float(llm_scores.get("relevance", 0.5))
            completeness= float(llm_scores.get("completeness", 0.5))
            clarity     = float(llm_scores.get("clarity", 0.5))

            # Apply strict mode multiplier if requested
            if request.strict_mode:
                correctness = correctness * 0.85

            # Clamp scores strictly between 0.0 and 1.0
            correctness  = max(0.0, min(1.0, correctness))
            relevance    = max(0.0, min(1.0, relevance))
            completeness = max(0.0, min(1.0, completeness))
            clarity     = max(0.0, min(1.0, clarity))

            # 3. Calculate weighted scores (40 + 20 + 25 + 15 = 100 max)
            correctness_weighted  = correctness * 40.0
            relevance_weighted    = relevance * 20.0
            completeness_weighted = completeness * 25.0
            clarity_weighted      = clarity * 15.0

            total_score = (
                correctness_weighted +
                relevance_weighted +
                completeness_weighted +
                clarity_weighted
            )
            score_out_of_10 = total_score / 10.0
            grade_info = get_grade_info(score_out_of_10)

            # 4. Use clean, high-precision concepts from the subject evaluator
            correct_concepts = llm_scores.get("correct_concepts") or []
            missing_concepts = llm_scores.get("missing_concepts") or []
            wrong_concepts   = llm_scores.get("wrong_concepts") or []

            # Calculate actual coverage percentage
            total_concepts = len(correct_concepts) + len(missing_concepts)
            coverage_pct = round((len(correct_concepts) / max(1, total_concepts)) * 100.0, 1)

            concept_analysis = {
                "correct_concepts": correct_concepts,
                "missing_concepts": missing_concepts,
                "wrong_concepts": wrong_concepts,
                "total_expected": total_concepts,
                "total_found": len(correct_concepts),
                "coverage_percentage": coverage_pct
            }

            feedback = llm_scores.get("feedback") or "Evaluation complete."
            suggestions = llm_scores.get("improvement_suggestions") or ["Keep practicing to refine your problem-solving process."]

            # 5. Governance and Confidence calculations
            confidence = round(max(0.70, (correctness * 0.5) + (completeness * 0.3) + (clarity * 0.2)), 2)
            review_required = confidence < getattr(settings, 'HUMAN_REVIEW_THRESHOLD', 0.60) or (len(wrong_concepts) > 3)

            # Check for bias safely
            try:
                bias_detector.scan_text(request.student_answer + " " + feedback)
            except Exception:
                pass

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
                "semantic_similarity":     round(correctness, 4),
                "confidence_score":        confidence,
                "governance_status":       "flagged" if review_required else "passed",
                "human_review_required":   review_required,
                "model_used":              llm_scores.get("model_used", "openai/gpt-oss-20b"),
                "provider":                llm_scores.get("provider", "groq"),
                "processing_time_ms":      (time.time() - start_time) * 1000,
                "prompt_version":          "4.0.0"
            }

            # Persist to database if provided
            if db:
                self._save_evaluation(db, result_payload, request, user_id)

            # Log audit trail
            try:
                audit_logger.log_ai_decision(
                    db=db,
                    request_id=request_id,
                    challenge="challenge1",
                    user_id=user_id,
                    model_used=result_payload["model_used"],
                    confidence_score=result_payload["confidence_score"],
                    governance_status=result_payload["governance_status"],
                    processing_time_ms=result_payload["processing_time_ms"],
                    output_summary=f"score={result_payload['score_out_of_10']}/10 grade={result_payload['grade']}",
                    metadata={"subject": request.subject, "human_review": review_required}
                )
            except Exception as e:
                logger.error(f"Audit logger failed (non-critical): {e}")

            return result_payload

        except Exception as e:
            logger.error(f"Evaluation process failed: {e}")
            raise

    def _save_evaluation(self, db: Session, result: dict, request: EvaluationRequest, user_id: Optional[str]):
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
            logger.info(f"Evaluation record stored in DB: {eval_model.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to commit evaluation to DB: {e}")

evaluator_service = EvaluatorService()
