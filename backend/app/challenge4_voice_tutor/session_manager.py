import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.models.session import TutorSession
from app.models.conversation import Conversation
from app.challenge4_voice_tutor.conversation_manager import (
    conversation_manager
)


class SessionManager:
    """
    Manage tutor session lifecycle.
    Handles create, update, and close operations.
    Persists session data to database.
    """

    async def create_session(
        self,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        tutor_mode: str = "standard",
        language: str = "en",
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new tutor session.
        Returns session info including WebSocket URL.
        """
        session_id = str(uuid.uuid4())

        # Create in-memory session
        conversation_manager.create_session(
            session_id=session_id,
            subject=subject,
            grade_level=grade_level,
            tutor_mode=tutor_mode,
            language=language
        )

        # Save to database
        if db:
            try:
                db_session = TutorSession(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    subject=subject,
                    grade_level=grade_level,
                    language=language,
                    tutor_mode=tutor_mode,
                    status="active",
                    started_at=datetime.utcnow()
                )
                db.add(db_session)
                db.commit()
                logger.info(
                    f"Session saved to DB: {session_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to save session to DB: {e}"
                )

        ws_url = f"/api/v1/voice/ws/{session_id}"

        logger.info(
            f"Session created: {session_id} "
            f"subject={subject} mode={tutor_mode}"
        )

        return {
            "session_id": session_id,
            "websocket_url": ws_url,
            "subject": subject,
            "grade_level": grade_level,
            "tutor_mode": tutor_mode,
            "message": (
                "Session ready. Connect to WebSocket to start."
            )
        }

    async def save_conversation_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        metadata: Optional[Dict] = None,
        db: Optional[Session] = None
    ):
        """Save a conversation turn to database."""
        if not db:
            return

        try:
            db_session = db.query(TutorSession).filter(
                TutorSession.session_id == session_id
            ).first()

            if not db_session:
                return

            conv = Conversation(
                id=str(uuid.uuid4()),
                session_id=db_session.id,
                turn_number=db_session.total_interactions + 1,
                role=role,
                text_content=text,
                model_used=metadata.get(
                    "model_used", ""
                ) if metadata else "",
                provider=metadata.get(
                    "provider", ""
                ) if metadata else "",
                processing_time_ms=metadata.get(
                    "processing_time_ms", 0
                ) if metadata else 0,
                detected_topic=metadata.get(
                    "detected_topic"
                ) if metadata else None,
                is_educational=metadata.get(
                    "is_educational", True
                ) if metadata else True,
                governance_status="passed"
            )

            db_session.total_interactions += 1
            db.add(conv)
            db.commit()

        except Exception as e:
            logger.error(
                f"Failed to save conversation turn: {e}"
            )
            db.rollback()

    async def close_session(
        self,
        session_id: str,
        summary: str = "",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Close a session and generate summary."""
        # Close in-memory session
        session_data = conversation_manager.close_session(
            session_id
        )
        stats = conversation_manager.get_session_stats(
            session_id
        )

        # Update database
        if db:
            try:
                db_session = db.query(TutorSession).filter(
                    TutorSession.session_id == session_id
                ).first()

                if db_session:
                    db_session.status = "completed"
                    db_session.ended_at = datetime.utcnow()
                    db_session.session_summary = summary
                    db_session.topics_covered = (
                        stats.get("topics_discussed", [])
                    )
                    db.commit()
                    logger.info(
                        f"Session closed in DB: {session_id}"
                    )

            except Exception as e:
                logger.error(
                    f"Failed to close session in DB: {e}"
                )

        return {
            "session_id": session_id,
            "status": "completed",
            "summary": summary,
            "stats": stats
        }

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        active = sum(
            1 for s in conversation_manager._sessions.values()
            if s.get("is_active", False)
        )
        return active


# Singleton
session_manager = SessionManager()
