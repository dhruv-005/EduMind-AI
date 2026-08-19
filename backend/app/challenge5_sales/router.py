import uuid
from typing import Optional
from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Form
)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.challenge5_sales.schemas import (
    CustomerMessage,
    StartConversationRequest,
    FollowUpRequest,
    EscalationRequest
)
from app.challenge5_sales.service import sales_service
from app.challenge5_sales.catalogue_manager import (
    catalogue_manager
)
from app.challenge5_sales.followup_generator import (
    followup_generator
)
from app.shared.file_handler import file_handler
from app.shared.response_models import success_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/sales",
    tags=["Challenge 5 - AI Sales Assistant"]
)


@router.post(
    "/catalogue/upload",
    summary="Upload product catalogue"
)
async def upload_catalogue(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Upload product catalogue (CSV, JSON, or Excel).
    Products are indexed in ChromaDB for semantic search.
    """
    file_path, original_name = await file_handler.save_upload(
        file=file,
        subfolder="catalogues",
        allowed_types=[".csv", ".json", ".xlsx", ".xls"]
    )

    try:
        result = await catalogue_manager.process_catalogue_file(
            file_path=file_path,
            filename=original_name
        )

        return success_response(
            data=result,
            message=result["message"]
        )

    except Exception as e:
        file_handler.delete_file(file_path)
        logger.error(f"Catalogue upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Catalogue processing failed: {str(e)}"
        )


@router.post(
    "/conversation/start",
    summary="Start a new sales conversation"
)
async def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Start a new sales conversation with the AI assistant.
    Returns conversation_id and welcome message.
    """
    try:
        result = await sales_service.start_conversation(
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            initial_message=request.initial_message
        )

        return success_response(
            data=result,
            message="Conversation started"
        )

    except Exception as e:
        logger.error(f"Start conversation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/chat",
    summary="Send message to sales AI"
)
async def chat(
    message: CustomerMessage,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Send a message to the AI sales assistant.

    The AI will:
    - Extract your requirements (budget, features, brands)
    - Search and recommend matching products
    - Score your purchase intent (lead scoring)
    - Generate follow-up content if needed
    - Escalate to human rep if needed
    """
    user_id = (
        current_user.get("user_id") if current_user else None
    )

    try:
        result = await sales_service.process_message(
            conversation_id=message.conversation_id,
            message=message.message,
            customer_name=message.customer_name,
            customer_email=message.customer_email,
            db=db,
            user_id=user_id
        )

        return success_response(
            data=result,
            message="Response generated"
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@router.post(
    "/followup",
    summary="Generate follow-up content"
)
async def generate_followup(
    request: FollowUpRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Generate follow-up email or WhatsApp message."""
    conv_data = sales_service._conversations.get(
        request.conversation_id
    )

    if not conv_data:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    recommendations = conv_data.get("recommendations", [])
    requirements = conv_data.get("requirements", {})
    lead_score = conv_data.get("lead_score", {})

    if request.format == "email":
        content = await followup_generator.generate_email(
            customer_name=conv_data.get("customer_name"),
            recommendations=recommendations,
            requirements=requirements,
            lead_score=lead_score or {},
            custom_note=request.custom_note
        )
    else:
        content = await followup_generator.generate_whatsapp(
            customer_name=conv_data.get("customer_name"),
            recommendations=recommendations,
            requirements=requirements
        )

    return success_response(
        data={
            "format": request.format,
            "content": content,
            "conversation_id": request.conversation_id
        },
        message="Follow-up generated"
    )


@router.get(
    "/leads",
    summary="Get all leads"
)
async def get_leads(
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get sales leads with scoring information."""
    from app.models.product import Lead

    query = db.query(Lead)
    if category:
        query = query.filter(Lead.lead_category == category)

    total = query.count()
    leads = (
        query
        .order_by(Lead.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return success_response(
        data={
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [l.to_dict() for l in leads]
        },
        message="Leads retrieved"
    )


@router.get(
    "/conversation/{conversation_id}",
    summary="Get conversation details"
)
async def get_conversation(
    conversation_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get full conversation details including history."""
    conv = sales_service._conversations.get(conversation_id)

    if not conv:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return success_response(
        data={
            "conversation_id": conversation_id,
            "customer_name": conv.get("customer_name"),
            "message_count": conv.get("message_count", 0),
            "lead_score": conv.get("lead_score"),
            "requirements": conv.get("requirements", {}),
            "escalated": conv.get("escalated", False),
            "history": conv.get("history", [])[-20:]
        },
        message="Conversation retrieved"
    )
