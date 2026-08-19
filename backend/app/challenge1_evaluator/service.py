import uuid
import time
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


class EvaluatorService:
    """
    Main service for Challenge 1 - Answer Evaluation.
    Orchestrates all evaluation components.
    """

    def _get_subject_evaluator(self, subject: str):
        """Get the appropriate subject evaluator."""
        evaluators = {
            "mathematics": math_evaluator,
            "science": science_evaluator,
            "english": english_evaluator,
            "general": general_evaluator
        }
        return evaluators.get(subject.lower(), general_evaluator)

    async def evaluate(
        self,
        request: EvaluationRequest,
        db: Optional[Session] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main evaluation method.
        Runs multi-layer evaluation and returns complete result.
        """
        start_time = time.time()
        request_id = request_id or str(uuid.uuid4())

        logger.info(
            f"Starting evaluation: "
            f"id={request_id} "
            f"subject={request.subject}"
        )

        try:
            # STEP 1: Semantic similarity (fast, local)
            semantic_sim = scoring_engine.calculate_semantic_score(
                request.student_answer,
                request.reference_answer
            )
            logger.debug(
                f"Semantic similarity: {semantic_sim:.3f}"
            )

            # STEP 2: Concept extraction and comparison
            concept_analysis = (
                await concept_extractor.full_concept_analysis(
                    reference_answer=request.reference_answer,
                    student_answer=request.student_answer,
                    subject=request.subject
                )
            )
            concept_coverage = (
                concept_analysis["coverage_percentage"] / 100.0
            )
            logger.debug(
                f"Concept coverage: "
                f"{concept_analysis['coverage_percentage']}%"
            )

            # STEP 3: Subject-specific LLM evaluation
            subject_evaluator = self._get_subject_evaluator(
                request.subject
            )
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

            # Apply strict mode if enabled
            if request.strict_mode:
                scores_dict = {
                    "correctness": correctness,
                    "completeness": completeness
                }
                scores_dict = scoring_engine.apply_strict_mode(
                    scores=scores_dict,
                    missing_concept_count=len(
                        concept_analysis.get("missing_concepts", [])
                    )
                )
                completeness = scores_dict["completeness"]

            # Aggregate final scores
            final_scores = scoring_engine.aggregate_scores(
                correctness=correctness,
                relevance=relevance,
                completeness=completeness,
                clarity=clarity,
                max_score=request.max_score or 10.0
            )

            # STEP 5: Compute confidence
            ref_len = len(request.reference_answer.split())
            student_len = len(request.student_answer.split())
            length_ratio = (
                student_len / ref_len if ref_len > 0 else 0
            )
            confidence = scoring_engine.compute_confidence(
                semantic_similarity=semantic_sim,
                concept_coverage=concept_coverage,
                answer_length_ratio=length_ratio
            )

            # STEP 6: Generate feedback
            feedback_data = await feedback_generator.generate_feedback(
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                score=final_scores["score_out_of_10"],
                subject=request.subject,
                missing_concepts=concept_analysis.get(
                    "missing_concepts", []
                ),
                wrong_concepts=concept_analysis.get(
                    "wrong_concepts", []
                ),
                grade_level=request.grade_level
            )

            # Subject-specific note
            subject_note = feedback_generator.generate_subject_note(
                subject=request.subject,
                score=final_scores["score_out_of_10"],
                missing_concepts=concept_analysis.get(
                    "missing_concepts", []
                )
            )

            # STEP 7: Bias check on feedback
            bias_result = bias_detector.full_bias_check(
                text=feedback_data["feedback"],
                context="evaluation_feedback"
            )
            if bias_result["has_bias"]:
                logger.warning(
                    f"Bias detected in feedback: "
                    f"{bias_result['overall_severity']}"
                )

            # STEP 8: Human oversight check
            should_review, review_reason = (
                human_oversight.should_trigger_review(
                    challenge="challenge1",
                    confidence_score=confidence
                )
            )
            if should_review:
                human_oversight.add_to_review_queue(
                    challenge="challenge1",
                    request_id=request_id,
                    reason=review_reason,
                    content={
                        "question": request.question[:100],
                        "score": final_scores["score_out_of_10"],
                        "confidence": confidence
                    },
                    priority=(
                        "high" if confidence < 0.4 else "normal"
                    ),
                    user_id=user_id
                )

            # STEP 9: Build result
            elapsed_ms = (time.time() - start_time) * 1000
            prompt_version = prompt_versioning.get_version(
                f"challenge1_{request.subject}"
            )

            result = {
                "request_id": request_id,
                "score_out_of_10": final_scores["score_out_of_10"],
                "total_score": final_scores["total_score"],
                "percentage": final_scores["percentage"],
                "grade": final_scores["grade"],
                "score_breakdown": {
                    "correctness": correctness,
                    "relevance": relevance,
                    "completeness": completeness,
                    "clarity": clarity,
                    "total": final_scores["total_score"]
                },
                "concept_analysis": {
                    "correct_concepts": concept_analysis.get(
                        "correct_concepts", []
                    ),
                    "missing_concepts": concept_analysis.get(
                        "missing_concepts", []
                    ),
                    "wrong_concepts": concept_analysis.get(
                        "wrong_concepts", []
                    ),
                    "total_expected": concept_analysis.get(
                        "total_expected", 0
                    ),
                    "total_found": concept_analysis.get(
                        "total_found", 0
                    ),
                    "coverage_percentage": concept_analysis.get(
                        "coverage_percentage", 0.0
                    )
                },
                "feedback": feedback_data["feedback"],
                "improvement_suggestions": feedback_data.get(
                    "improvement_suggestions", []
                ),
                "subject_specific_notes": subject_note,
                "semantic_similarity": semantic_sim,
                "confidence_score": confidence,
                "governance_status": "passed",
                "human_review_required": should_review,
                "model_used": llm_scores.get(
                    "model_used", settings.GROQ_MODEL
                ),
                "provider": llm_scores.get("provider", "groq"),
                "processing_time_ms": elapsed_ms,
                "prompt_version": prompt_version
            }

            # STEP 10: Save to database
            if db:
                self._save_evaluation(
                    db=db,
                    request=request,
                    result=result,
                    user_id=user_id
                )

            # STEP 11: Audit log
            audit_logger.log_ai_decision(
                db=db,
                request_id=request_id,
                challenge="challenge1",
                user_id=user_id,
                session_id=None,
                input_summary=f"Q:{request.question[:50]}",
                model_used=result["model_used"],
                model_version="3.3-70b",
                prompt_version=prompt_version,
                output_summary=(
                    f"score={result['score_out_of_10']:.1f}/10 "
                    f"grade={result['grade']}"
                ),
                confidence_score=confidence,
                processing_time_ms=elapsed_ms,
                governance_status="passed",
                metadata={
                    "subject": request.subject,
                    "human_review": should_review
                }
            )

            logger.info(
                f"Evaluation complete: "
                f"id={request_id} "
                f"score={result['score_out_of_10']:.1f}/10 "
                f"grade={result['grade']} "
                f"time={elapsed_ms:.0f}ms"
            )

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Evaluation failed: id={request_id} error={e}"
            )
            raise

    def _save_evaluation(
        self,
        db: Session,
        request: EvaluationRequest,
        result: Dict[str, Any],
        user_id: Optional[str]
    ):
        """Save evaluation result to database."""
        try:
            evaluation = Evaluation(
                id=str(uuid.uuid4()),
                request_id=result["request_id"],
                user_id=user_id,
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
                correct_concepts=result["concept_analysis"]["correct_concepts"],
                missing_concepts=result["concept_analysis"]["missing_concepts"],
                wrong_concepts=result["concept_analysis"]["wrong_concepts"],
                feedback=result["feedback"],
                improvement_suggestions=result["improvement_suggestions"],
                semantic_similarity=result["semantic_similarity"],
                model_used=result["model_used"],
                provider=result["provider"],
                confidence_score=result["confidence_score"],
                processing_time_ms=result["processing_time_ms"],
                prompt_version=result["prompt_version"],
                governance_status=result["governance_status"],
                human_review_required=result["human_review_required"]
            )
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
            result["evaluation_id"] = evaluation.id
            logger.info(
                f"Evaluation saved to DB: {evaluation.id}"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save evaluation: {e}")


# Singleton
evaluator_service = EvaluatorService()
