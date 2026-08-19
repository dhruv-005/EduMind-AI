from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class SpellingReport(Base):
    """
    Stores spelling check results for Challenge 3.
    One report per uploaded document.
    """

    __tablename__ = "spelling_reports"

    id = Column(String(36), primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True)

    # Foreign key
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Document info
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    annotated_file_path = Column(String(500), nullable=True)
    page_count = Column(Integer, nullable=True, default=1)

    # Processing details
    total_words = Column(Integer, nullable=True, default=0)
    total_errors = Column(Integer, nullable=True, default=0)
    error_rate = Column(Float, nullable=True, default=0.0)

    # Error details (JSON array)
    errors = Column(JSON, nullable=True)
    # Format: [
    #   {
    #     "word": "recieve",
    #     "correction": "receive",
    #     "page": 1,
    #     "x": 100, "y": 200,
    #     "width": 50, "height": 20,
    #     "confidence": 0.95,
    #     "source": "pyspellchecker"
    #   }
    # ]

    # Skipped words (names, abbreviations, technical terms)
    skipped_words = Column(JSON, nullable=True)
    skipped_count = Column(Integer, nullable=True, default=0)

    # OCR info (for scanned docs)
    ocr_used = Column(Boolean, default=False, nullable=False)
    ocr_confidence = Column(Float, nullable=True)
    ocr_language = Column(String(10), nullable=True, default="eng")

    # Processing metadata
    model_used = Column(String(100), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    layers_used = Column(JSON, nullable=True)

    # Governance
    governance_status = Column(
        String(20), nullable=True, default="passed"
    )
    human_verification_required = Column(
        Boolean, default=False, nullable=False
    )

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return (
            f"<SpellingReport id={self.id} "
            f"errors={self.total_errors} "
            f"file={self.original_filename}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "page_count": self.page_count,
            "summary": {
                "total_words": self.total_words,
                "total_errors": self.total_errors,
                "error_rate": round(self.error_rate or 0.0, 3),
                "skipped_count": self.skipped_count
            },
            "errors": self.errors or [],
            "skipped_words": self.skipped_words or [],
            "ocr_used": self.ocr_used,
            "ocr_confidence": self.ocr_confidence,
            "annotated_file_available": bool(
                self.annotated_file_path
            ),
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }
