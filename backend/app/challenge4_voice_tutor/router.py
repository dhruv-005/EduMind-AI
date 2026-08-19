from typing import Optional
from fastapi import (
    APIRouter, WebSocket, Depends,
    HTTPException, WebSocketDisconnect
)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.challenge4_voice_tutor.schemas import (
    SessionCreateRequest,
    SessionCreateResponse
)
from app.challenge4_voice_tutor.session_manager import (
    session_manager
)
from app.challenge4_voice_tutor.websocket_handler import (
    websocket_handler
)
from app.challenge4_voice_tutor.conversation_manager import (
    conversation_manager
)
from app.shared.response_models import success_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/voice",
    tags=["Challenge 4 - Voice AI Tutor"]
)


@router.post(
    "/session",
    summary="Create a new tutor session"
)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Create a new voice tutor session.
    Returns session_id and WebSocket URL to connect to.

    Connect to WebSocket at: /api/v1/voice/ws/{session_id}
    """
    user_id = (
        current_user.get("user_id") if current_user else None
    )

    session_info = await session_manager.create_session(
        subject=request.subject,
        grade_level=request.grade_level,
        tutor_mode=request.tutor_mode,
        language=request.language,
        db=db,
        user_id=user_id
    )

    return success_response(
        data=session_info,
        message="Session created. Connect to WebSocket to start."
    )


@router.websocket("/ws/{session_id}")
async def voice_websocket(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time voice conversation.

    Message types from client:
    - bytes: Audio chunk (PCM/WAV format)
    - JSON {type: "text_message", text: "..."}: Text input
    - JSON {type: "interrupt"}: Stop tutor speaking
    - JSON {type: "end_session"}: End session

    Message types from server:
    - {type: "welcome"}: Initial greeting
    - {type: "status", status: "recording/processing/speaking"}
    - {type: "transcript", text: "..."}: STT result
    - {type: "response", text: "..."}: Tutor text response
    - {type: "audio_chunk", data: "base64..."}: TTS audio
    - {type: "tts_start"}: TTS started
    - {type: "tts_end"}: TTS finished
    - {type: "session_summary"}: Session ended
    """
    await websocket_handler.handle_connection(
        websocket=websocket,
        session_id=session_id
    )


@router.post(
    "/session/{session_id}/end",
    summary="End a tutor session"
)
async def end_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """End a tutor session and get summary."""
    from app.challenge4_voice_tutor.service import (
        voice_tutor_service
    )

    summary = await voice_tutor_service.generate_session_summary(
        session_id=session_id
    )

    result = await session_manager.close_session(
        session_id=session_id,
        summary=summary,
        db=db
    )

    return success_response(
        data=result,
        message="Session ended successfully"
    )


@router.get(
    "/session/{session_id}/status",
    summary="Get session status"
)
async def get_session_status(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get current status and stats for a session."""
    stats = conversation_manager.get_session_stats(session_id)

    if not stats:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return success_response(
        data=stats,
        message="Session status retrieved"
    )


@router.get(
    "/sessions/history",
    summary="Get session history"
)
async def get_session_history(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get tutoring session history for current user."""
    from app.models.session import TutorSession

    user_id = current_user.get("user_id")
    query = db.query(TutorSession).filter(
        TutorSession.user_id == user_id
    )

    total = query.count()
    sessions = (
        query
        .order_by(TutorSession.started_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return success_response(
        data={
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [s.to_dict() for s in sessions]
        },
        message="History retrieved"
    )
