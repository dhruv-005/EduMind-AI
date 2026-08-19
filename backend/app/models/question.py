from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class GeneratedQuestion(Base):
    """
    Stores AI-generated questions for Challenge 2.
    """

    __tablename__ = "generated_questions"

    id = Column(String(36), primary_key=True, index=True)
    batch_id = Column(String(36), index=True, nullable=True)
    request_id = Column(String(36), index=True, nullable=True)

    # Foreign key
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=True)
    difficulty = Column(String(50), nullable=False, default="medium")
    marks = Column(Integer, nullable=True, default=5)
    grade_level = Column(String(50), nullable=True)

    # For MCQ
    options = Column(JSON, nullable=True)
    correct_option = Column(String(10), nullable=True)

    # Answer and marking scheme
    model_answer = Column(Text, nullable=True)
    marking_scheme = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)

    # Source information
    source_paper_id = Column(String(36), nullable=True)
    pattern_source = Column(String(200), nullable=True)

    # Quality metrics
    is_duplicate = Column(Boolean, default=False, nullable=False)
    similarity_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)

    # AI metadata
    model_used = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=True)
    prompt_version = Column(String(20), nullable=True)

    # Governance
    human_approved = Column(Boolean, nullable=True)
    human_reviewer_id = Column(String(36), nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)

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

    def __repr__(self):
        return (
            f"<GeneratedQuestion id={self.id} "
            f"type={self.question_type} "
            f"subject={self.subject}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "subject": self.subject,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "marks": self.marks,
            "grade_level": self.grade_level,
            "options": self.options,
            "correct_option": self.correct_option,
            "model_answer": self.model_answer,
            "marking_scheme": self.marking_scheme,
            "key_points": self.key_points or [],
            "quality_score": self.quality_score,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }


class SourcePaper(Base):
    """
    Stores uploaded source exam papers for Challenge 2.
    """

    __tablename__ = "source_papers"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    subject = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    grade_level = Column(String(50), nullable=True)

    # Parsed content
    raw_text = Column(Text, nullable=True)
    question_count = Column(Integer, default=0, nullable=False)
    topics_detected = Column(JSON, nullable=True)
    difficulty_distribution = Column(JSON, nullable=True)

    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return (
            f"<SourcePaper id={self.id} "
            f"filename={self.filename}>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "subject": self.subject,
            "year": self.year,
            "grade_level": self.grade_level,
            "question_count": self.question_count,
            "topics_detected": self.topics_detected or [],
            "difficulty_distribution": (
                self.difficulty_distribution or {}
            ),
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }
