import uuid
import os
from typing import Optional
from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Form
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.challenge2_generator.schemas import (
    GeneratorConfig,
    PDFExportRequest
)
from app.challenge2_generator.service import generator_service
from app.shared.file_handler import file_handler
from app.shared.response_models import success_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/generator",
    tags=["Challenge 2 - Question Generator"]
)


@router.post(
    "/upload-paper",
    summary="Upload a source exam paper"
)
async def upload_source_paper(
    file: UploadFile = File(...),
    subject: str = Form(default="general"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a previous year exam paper for pattern analysis.
    Supports PDF, JPG, PNG files.
    """
    user_id = current_user.get("user_id")

    # Save uploaded file
    file_path, original_name = await file_handler.save_upload(
        file=file,
        subfolder="papers",
        allowed_types=[".pdf", ".jpg", ".jpeg", ".png"]
    )

    try:
        result = await generator_service.process_source_paper(
            file_path=file_path,
            filename=original_name,
            subject=subject,
            db=db,
            user_id=user_id
        )

        return success_response(
            data=result,
            message="Source paper processed successfully"
        )

    except Exception as e:
        # Clean up file on error
        file_handler.delete_file(file_path)
        logger.error(f"Paper upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process paper: {str(e)}"
        )


@router.post(
    "/generate",
    summary="Generate exam questions"
)
async def generate_questions(
    config: GeneratorConfig,
    source_paper_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Generate exam questions based on configuration.

    - **subject**: mathematics/science/english/general
    - **topic**: Specific topic to focus on
    - **num_questions**: How many questions to generate (1-50)
    - **difficulty**: easy/medium/hard/mixed
    - **question_type**: mcq/short/long/numerical/mixed
    """
    user_id = (
        current_user.get("user_id") if current_user else None
    )

    try:
        result = await generator_service.generate_questions(
            config=config,
            db=db,
            user_id=user_id,
            source_paper_id=source_paper_id
        )

        return success_response(
            data=result,
            message=(
                f"Successfully generated "
                f"{result['total_generated']} questions"
            )
        )

    except Exception as e:
        logger.error(f"Generation endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.post(
    "/export-pdf",
    summary="Export questions as PDF"
)
async def export_pdf(
    request: PDFExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export a generated question batch as a PDF file."""
    try:
        file_path = await generator_service.export_pdf(
            batch_id=request.batch_id,
            title=request.title or "Question Paper",
            institution=request.institution,
            include_answers=request.include_answers,
            db=db
        )

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Export file not found"
            )

        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
            if file_path.endswith(".pdf")
            else "text/plain"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get(
    "/history",
    summary="Get generation history"
)
async def get_generation_history(
    page: int = 1,
    per_page: int = 20,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get question generation history."""
    from app.models.question import GeneratedQuestion

    user_id = current_user.get("user_id")
    query = db.query(GeneratedQuestion).filter(
        GeneratedQuestion.user_id == user_id
    )

    if subject:
        query = query.filter(
            GeneratedQuestion.subject == subject
        )

    total = query.count()
    questions = (
        query
        .order_by(GeneratedQuestion.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return success_response(
        data={
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [q.to_dict() for q in questions]
        },
        message="History retrieved"
    )


@router.get(
    "/papers",
    summary="Get uploaded source papers"
)
async def get_source_papers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of uploaded source papers."""
    from app.models.question import SourcePaper

    user_id = current_user.get("user_id")
    papers = db.query(SourcePaper).filter(
        SourcePaper.user_id == user_id
    ).order_by(SourcePaper.created_at.desc()).all()

    return success_response(
        data=[p.to_dict() for p in papers],
        message="Papers retrieved successfully"
    )
