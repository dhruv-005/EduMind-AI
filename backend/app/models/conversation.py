from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Conversation(Base):
    """
    Stores individual conversation turns for Challenge 4.
    Each row = one exchange (student speaks + tutor responds).
    """

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, index=True)

    # Foreign keys
    session_id = Column(
        String(36),
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Turn info
    turn_number = Column(Integer, nullable=False, default=1)
    role = Column(String(20), nullable=False)
    # Roles: student, tutor

    # Content
    text_content = Column(Text, nullable=True)
    audio_duration_seconds = Column(Float, nullable=True)

    # STT info (for student turns)
    stt_transcript = Column(Text, nullable=True)
    stt_confidence = Column(Float, nullable=True)
    stt_language = Column(String(10), nullable=True)

    # TTS info (for tutor turns)
    tts_audio_length = Column(Float, nullable=True)
    tts_voice = Column(String(100), nullable=True)

    # AI processing (for tutor turns)
    model_used = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    prompt_version = Column(String(20), nullable=True)

    # Topic and intent
    detected_topic = Column(String(200), nullable=True)
    detected_intent = Column(String(100), nullable=True)
    is_educational = Column(Boolean, nullable=True)
    topic_rejected = Column(Boolean, default=False, nullable=False)

    # Interruption
    was_interrupted = Column(Boolean, default=False, nullable=False)

    # Governance
    governance_status = Column(
        String(20), nullable=True, default="passed"
    )
    content_flagged = Column(Boolean, default=False, nullable=False)

    # Timestamp
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    session = relationship(
        "TutorSession", back_populates="conversations"
    )

    def __repr__(self):
        return (
            f"<Conversation id={self.id} "
            f"role={self.role} "
            f"turn={self.turn_number}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "role": self.role,
            "text_content": self.text_content,
            "detected_topic": self.detected_topic,
            "is_educational": self.is_educational,
            "was_interrupted": self.was_interrupted,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }
