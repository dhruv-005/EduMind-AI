from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TutorSession(Base):
    """
    Stores voice tutor sessions for Challenge 4.
    One session = one complete tutoring conversation.
    """

    __tablename__ = "tutor_sessions"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(
        String(36), unique=True, index=True, nullable=False
    )

    # Foreign key
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Session configuration
    subject = Column(String(100), nullable=True)
    grade_level = Column(String(50), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    tutor_mode = Column(
        String(50), default="standard", nullable=True
    )
    # Modes: standard, socratic, hint_mode

    # Session stats
    total_interactions = Column(Integer, default=0, nullable=False)
    total_duration_seconds = Column(Float, default=0.0, nullable=False)
    student_speaking_time = Column(Float, default=0.0, nullable=False)
    tutor_speaking_time = Column(Float, default=0.0, nullable=False)

    # Topics covered
    topics_covered = Column(JSON, nullable=True)
    questions_asked = Column(Integer, default=0, nullable=False)
    interruptions_count = Column(Integer, default=0, nullable=False)

    # Session status
    status = Column(String(20), default="active", nullable=False)
    # Statuses: active, completed, abandoned, escalated

    # Detected level
    detected_level = Column(String(50), nullable=True)

    # Escalation
    escalated = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(String(255), nullable=True)

    # Session summary (generated at end)
    session_summary = Column(Text, nullable=True)
    learning_progress = Column(JSON, nullable=True)

    # Governance
    governance_flags = Column(JSON, nullable=True)
    content_violations = Column(Integer, default=0, nullable=False)

    # Timestamps
    started_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversations = relationship(
        "Conversation",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<TutorSession id={self.id} "
            f"subject={self.subject} "
            f"status={self.status}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "status": self.status,
            "total_interactions": self.total_interactions,
            "total_duration_seconds": self.total_duration_seconds,
            "topics_covered": self.topics_covered or [],
            "detected_level": self.detected_level,
            "escalated": self.escalated,
            "session_summary": self.session_summary,
            "started_at": self.started_at.isoformat()
            if self.started_at else None,
            "ended_at": self.ended_at.isoformat()
            if self.ended_at else None
        }
