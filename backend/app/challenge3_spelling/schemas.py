from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SpellCheckRequest(BaseModel):
    """Request for spell check (for text input)."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text to check for spelling errors"
    )
    language: str = Field(
        default="en",
        description="Language code: en, hi, ar"
    )
    skip_technical_terms: bool = Field(
        default=True,
        description="Skip domain-specific technical terms"
    )
    skip_proper_nouns: bool = Field(
        default=True,
        description="Skip proper nouns and names"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The studnt recieved an excelent grade.",
                "language": "en",
                "skip_technical_terms": True,
                "skip_proper_nouns": True
            }
        }


class SpellingError(BaseModel):
    """Single spelling error details."""
    word: str
    correction: str
    page: int = 1
    line: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = "pyspellchecker"
    context: Optional[str] = None
    alternatives: Optional[List[str]] = None


class SpellCheckSummary(BaseModel):
    """Summary statistics for spell check."""
    total_words: int
    total_errors: int
    error_rate: float
    skipped_count: int
    pages_checked: int
    ocr_used: bool
    ocr_confidence: Optional[float] = None


class SpellCheckResult(BaseModel):
    """Complete spell check result."""
    report_id: str
    request_id: str
    original_filename: str
    file_type: str
    summary: SpellCheckSummary
    errors: List[SpellingError]
    skipped_words: List[str]
    annotated_file_available: bool
    annotated_file_path: Optional[str] = None
    processing_time_ms: float
    governance_status: str = "passed"
    human_verification_required: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "abc123",
                "original_filename": "document.pdf",
                "file_type": "pdf",
                "summary": {
                    "total_words": 500,
                    "total_errors": 12,
                    "error_rate": 0.024
                }
            }
        }


class ErrorCorrectionRequest(BaseModel):
    """Request to apply corrections to document."""
    report_id: str
    corrections: List[Dict[str, str]] = Field(
        description="List of {word: correction} pairs"
    )
    apply_all: bool = Field(
        default=False,
        description="Apply all suggested corrections"
    )
