import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_optional_user, get_current_user
from app.challenge1_evaluator.schemas import (
    EvaluationRequest,
    BatchEvaluationRequest,
    EvaluationResult
)
from app.challenge1_evaluator.service import evaluator_service
from app.shared.response_models import success_response, error_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/evaluator",
    tags=["Challenge 1 - Answer Evaluator"]
)


@router.post("/evaluate", summary="Evaluate a student answer")
async def evaluate_answer(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Evaluate a student's answer against a reference answer.

    - **question**: The exam question
    - **reference_answer**: The correct reference answer
    - **student_answer**: The student's answer to evaluate
    - **subject**: mathematics / science / english / general
    - **grade_level**: Optional grade level context

    Returns detailed score, grade, concept analysis, and feedback.
    """
    try:
        request_id = str(uuid.uuid4())
        user_id = (
            current_user.get("user_id") if current_user else None
        )

        result = await evaluator_service.evaluate(
            request=request,
            db=db,
            user_id=user_id,
            request_id=request_id
        )

        return success_response(
            data=result,
            message="Evaluation completed successfully",
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"Evaluation endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post(
    "/evaluate/batch",
    summary="Evaluate multiple answers at once"
)
async def evaluate_batch(
    request: BatchEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Evaluate multiple student answers in one request.
    Maximum 50 evaluations per batch.
    """
    import asyncio
    batch_id = str(uuid.uuid4())
    user_id = current_user.get("user_id")

    results = []
    failed = 0

    for eval_request in request.evaluations:
        try:
            if request.subject:
                eval_request.subject = request.subject

            result = await evaluator_service.evaluate(
                request=eval_request,
                db=db,
                user_id=user_id,
                request_id=str(uuid.uuid4())
            )
            results.append(result)

        except Exception as e:
            logger.error(f"Batch item failed: {e}")
            failed += 1
            results.append({
                "error": str(e),
                "question": eval_request.question[:50]
            })

    avg_score = (
        sum(
            r.get("score_out_of_10", 0)
            for r in results
            if "score_out_of_10" in r
        ) / max(len(results) - failed, 1)
    )

    return success_response(
        data={
            "batch_id": batch_id,
            "total_evaluations": len(request.evaluations),
            "completed": len(results) - failed,
            "failed": failed,
            "average_score": round(avg_score, 2),
            "results": results
        },
        message="Batch evaluation completed",
        request_id=batch_id
    )


@router.get(
    "/history",
    summary="Get evaluation history"
)
async def get_evaluation_history(
    page: int = 1,
    per_page: int = 20,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get evaluation history for the current user."""
    from app.models.evaluation import Evaluation

    user_id = current_user.get("user_id")
    query = db.query(Evaluation).filter(
        Evaluation.user_id == user_id
    )

    if subject:
        query = query.filter(Evaluation.subject == subject)

    total = query.count()
    evaluations = (
        query
        .order_by(Evaluation.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return success_response(
        data={
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [e.to_dict() for e in evaluations]
        },
        message="History retrieved successfully"
    )


@router.get(
    "/history/{evaluation_id}",
    summary="Get single evaluation detail"
)
async def get_evaluation_detail(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed result for a specific evaluation."""
    from app.models.evaluation import Evaluation

    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    return success_response(
        data=evaluation.to_dict(),
        message="Evaluation retrieved successfully"
    )


@router.get(
    "/subjects",
    summary="Get supported subjects"
)
async def get_supported_subjects():
    """Get list of supported subjects and their configurations."""
    return success_response(
        data={
            "subjects": [
                {
                    "id": "mathematics",
                    "name": "Mathematics",
                    "icon": "📐",
                    "description": (
                        "Algebra, Calculus, Geometry, Statistics"
                    )
                },
                {
                    "id": "science",
                    "name": "Science",
                    "icon": "🔬",
                    "description": (
                        "Physics, Chemistry, Biology"
                    )
                },
                {
                    "id": "english",
                    "name": "English",
                    "icon": "📝",
                    "description": (
                        "Grammar, Literature, Writing"
                    )
                },
                {
                    "id": "general",
                    "name": "General",
                    "icon": "📚",
                    "description": (
                        "History, Geography, General Knowledge"
                    )
                }
            ]
        },
        message="Subjects retrieved successfully"
    )
