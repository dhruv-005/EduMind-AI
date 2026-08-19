from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """
    Stores complete audit trail for all AI decisions.
    Central governance record for all 5 challenges.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(
        String(36), unique=True, index=True, nullable=False
    )

    # Foreign key (optional - anonymous users allowed)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Which challenge
    challenge = Column(String(50), nullable=False, index=True)
    # Values: challenge1, challenge2, challenge3,
    #         challenge4, challenge5

    # Timestamps
    timestamp = Column(
        DateTime, default=datetime.utcnow,
        nullable=False, index=True
    )

    # Session tracking
    session_id = Column(String(36), nullable=True, index=True)

    # Input (privacy-safe hash only)
    input_hash = Column(String(64), nullable=True)

    # Model info
    model_used = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    provider = Column(String(50), nullable=True)
    prompt_version = Column(String(20), nullable=True)

    # Output summary
    output_summary = Column(String(500), nullable=True)

    # Performance
    confidence_score = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)

    # Governance result
    governance_status = Column(
        String(20), nullable=False, default="passed", index=True
    )
    # Values: passed, flagged, blocked
    governance_reason = Column(String(500), nullable=True)

    # Human review
    human_review_triggered = Column(
        Boolean, default=False, nullable=False, index=True
    )
    human_review_completed = Column(
        Boolean, default=False, nullable=False
    )
    human_reviewer_id = Column(String(36), nullable=True)
    human_decision = Column(String(50), nullable=True)
    human_notes = Column(Text, nullable=True)

    # Fallback info
    fallback_used = Column(Boolean, default=False, nullable=False)
    failed_providers = Column(JSON, nullable=True)

    # Extra metadata
    extra_metadata = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return (
            f"<AuditLog id={self.id} "
            f"challenge={self.challenge} "
            f"status={self.governance_status}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "challenge": self.challenge,
            "timestamp": self.timestamp.isoformat()
            if self.timestamp else None,
            "model_used": self.model_used,
            "model_version": self.model_version,
            "provider": self.provider,
            "prompt_version": self.prompt_version,
            "output_summary": self.output_summary,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "governance_status": self.governance_status,
            "governance_reason": self.governance_reason,
            "human_review_triggered": self.human_review_triggered,
            "human_review_completed": self.human_review_completed,
            "human_decision": self.human_decision,
            "fallback_used": self.fallback_used,
            "failed_providers": self.failed_providers or []
        }
