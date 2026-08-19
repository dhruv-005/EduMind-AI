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
from app.challenge3_spelling.service import spelling_service
from app.shared.file_handler import file_handler
from app.shared.response_models import success_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/spelling",
    tags=["Challenge 3 - Spelling Detector"]
)


# ── SHARED HANDLER ────────────────────────────────────────────────
async def _run_spell_check(
    file: UploadFile,
    language: str = "en",
    skip_proper_nouns: bool = True,
    skip_technical_terms: bool = True,
    domain: str = "general",
    db: Session = None,
    user_id: Optional[str] = None
) -> dict:
    """Shared logic for both /detect and /check-document endpoints."""

    allowed = [".pdf", ".jpg", ".jpeg", ".png", ".txt", ".docx"]

    try:
        file_path, original_name = await file_handler.save_upload(
            file=file,
            subfolder="spelling",
            allowed_types=allowed
        )
    except Exception as e:
        logger.warning(f"file_handler.save_upload failed: {e} — trying manual save")
        import aiofiles, uuid, pathlib
        ext = os.path.splitext(file.filename or "doc.txt")[1].lower() or ".txt"
        upload_dir = pathlib.Path("uploads/spelling")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = str(upload_dir / f"{uuid.uuid4()}{ext}")
        original_name = file.filename or f"document{ext}"
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

    try:
        report = await spelling_service.check_document(
            file_path=file_path,
            filename=original_name,
            language=language,
            skip_proper_nouns=skip_proper_nouns,
            skip_technical=skip_technical_terms,
            domain=domain,
            db=db,
            user_id=user_id
        )
        return report
    except Exception as e:
        logger.error(f"Spell check service error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Spell check failed: {str(e)}"
        )


# ── DETECT (frontend calls this) ──────────────────────────────────
@router.post(
    "/detect",
    summary="Detect spelling errors in uploaded document"
)
async def detect_spelling(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    skip_proper_nouns: bool = Form(default=True),
    skip_technical_terms: bool = Form(default=True),
    domain: str = Form(default="general"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Detect spelling errors in PDF, image, or text document.
    Alias for /check-document — used by frontend.
    """
    user_id = current_user.get("user_id") if current_user else None

    report = await _run_spell_check(
        file=file,
        language=language,
        skip_proper_nouns=skip_proper_nouns,
        skip_technical_terms=skip_technical_terms,
        domain=domain,
        db=db,
        user_id=user_id
    )

    total_errors = 0
    if isinstance(report, dict):
        summary = report.get("summary", {})
        total_errors = (
            summary.get("total_errors", 0)
            if isinstance(summary, dict)
            else report.get("error_count", 0)
        )

    return success_response(
        data=report,
        message=f"Spell check complete. Found {total_errors} errors."
    )


# ── CHECK-DOCUMENT (original endpoint) ───────────────────────────
@router.post(
    "/check-document",
    summary="Check spelling in uploaded document"
)
async def check_document(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    skip_proper_nouns: bool = Form(default=True),
    skip_technical_terms: bool = Form(default=True),
    domain: str = Form(default="general"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Upload a document and detect spelling errors."""
    user_id = current_user.get("user_id") if current_user else None

    report = await _run_spell_check(
        file=file,
        language=language,
        skip_proper_nouns=skip_proper_nouns,
        skip_technical_terms=skip_technical_terms,
        domain=domain,
        db=db,
        user_id=user_id
    )

    total_errors = 0
    if isinstance(report, dict):
        summary = report.get("summary", {})
        total_errors = (
            summary.get("total_errors", 0)
            if isinstance(summary, dict)
            else report.get("error_count", 0)
        )

    return success_response(
        data=report,
        message=f"Spell check complete. Found {total_errors} errors."
    )


# ── CHECK-TEXT ────────────────────────────────────────────────────
@router.post(
    "/check-text",
    summary="Check spelling in plain text"
)
async def check_text(
    text: str = Form(...),
    language: str = Form(default="en"),
    skip_proper_nouns: bool = Form(default=True),
    skip_technical_terms: bool = Form(default=True),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Check spelling errors in plain text input."""
    try:
        result = await spelling_service.check_text(
            text=text,
            language=language,
            skip_proper_nouns=skip_proper_nouns,
            skip_technical=skip_technical_terms
        )
        total = result.get("total_errors", 0)
        return success_response(
            data=result,
            message=f"Found {total} spelling errors"
        )
    except Exception as e:
        logger.error(f"Text check error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Text check failed: {str(e)}"
        )


# ── ANNOTATED DOWNLOAD ────────────────────────────────────────────
@router.get(
    "/annotated/{report_id}",
    summary="Download annotated document"
)
async def download_annotated(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Download the annotated document for a report."""
    from app.models.spelling_report import SpellingReport

    report = db.query(SpellingReport).filter(
        SpellingReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.annotated_file_path:
        raise HTTPException(
            status_code=404, detail="Annotated file not available"
        )

    if not os.path.exists(report.annotated_file_path):
        raise HTTPException(
            status_code=404, detail="Annotated file has been deleted"
        )

    filename  = os.path.basename(report.annotated_file_path)
    media_type = (
        "application/pdf"
        if filename.endswith(".pdf")
        else "image/jpeg"
    )

    return FileResponse(
        path=report.annotated_file_path,
        filename=filename,
        media_type=media_type
    )


# ── DOWNLOAD (alias) ──────────────────────────────────────────────
@router.get(
    "/download/{report_id}",
    summary="Download annotated document (alias)"
)
async def download_annotated_alias(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Alias for /annotated/{report_id}."""
    return await download_annotated(report_id, db, current_user)


# ── REPORT ────────────────────────────────────────────────────────
@router.get(
    "/report/{report_id}",
    summary="Get spell check report"
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get detailed spell check report."""
    from app.models.spelling_report import SpellingReport

    report = db.query(SpellingReport).filter(
        SpellingReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return success_response(
        data=report.to_dict(),
        message="Report retrieved"
    )


# ── HISTORY ───────────────────────────────────────────────────────
@router.get(
    "/history",
    summary="Get spell check history"
)
async def get_history(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get spelling check history."""
    from app.models.spelling_report import SpellingReport

    user_id = current_user.get("user_id") if current_user else None

    query = db.query(SpellingReport)
    if user_id and user_id != "anonymous":
        query = query.filter(SpellingReport.user_id == user_id)

    total   = query.count()
    reports = (
        query
        .order_by(SpellingReport.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return success_response(
        data={
            "total":   total,
            "page":    page,
            "per_page": per_page,
            "items":   [r.to_dict() for r in reports]
        },
        message="History retrieved"
    )
