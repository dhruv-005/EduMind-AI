from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, Text, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Evaluation(Base):
    """
    Stores AI evaluation results for Challenge 1.
    Each evaluation = one student answer scored.
    """

    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True)

    # Foreign key
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Input data
    question = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    subject = Column(String(50), nullable=False, default="general")
    grade_level = Column(String(50), nullable=True)

    # Scores (0-100 scale)
    total_score = Column(Float, nullable=False, default=0.0)
    score_out_of_10 = Column(Float, nullable=False, default=0.0)
    correctness_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)

    # Grade
    grade = Column(String(5), nullable=True)

    # Concept analysis
    correct_concepts = Column(JSON, nullable=True)
    missing_concepts = Column(JSON, nullable=True)
    wrong_concepts = Column(JSON, nullable=True)

    # Feedback
    feedback = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)

    # Similarity score from embeddings
    semantic_similarity = Column(Float, nullable=True)

    # AI metadata
    model_used = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    prompt_version = Column(String(20), nullable=True)

    # Governance
    governance_status = Column(
        String(20), nullable=True, default="passed"
    )
    human_review_required = Column(
        Boolean, default=False, nullable=False
    )
    human_review_done = Column(
        Boolean, default=False, nullable=False
    )
    human_reviewer_id = Column(String(36), nullable=True)
    human_score_override = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="evaluations")

    def __repr__(self):
        return (
            f"<Evaluation id={self.id} "
            f"score={self.score_out_of_10} "
            f"subject={self.subject}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "subject": self.subject,
            "total_score": self.total_score,
            "score_out_of_10": self.score_out_of_10,
            "percentage": self.percentage,
            "grade": self.grade,
            "scores": {
                "correctness": self.correctness_score,
                "relevance": self.relevance_score,
                "completeness": self.completeness_score,
                "clarity": self.clarity_score
            },
            "concepts": {
                "correct": self.correct_concepts or [],
                "missing": self.missing_concepts or [],
                "wrong": self.wrong_concepts or []
            },
            "feedback": self.feedback,
            "improvement_suggestions": (
                self.improvement_suggestions or []
            ),
            "semantic_similarity": self.semantic_similarity,
            "confidence_score": self.confidence_score,
            "human_review_required": self.human_review_required,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }
