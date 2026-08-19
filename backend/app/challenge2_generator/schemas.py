from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from app.core.constants import (
    VALID_SUBJECTS,
    VALID_DIFFICULTIES,
    VALID_QUESTION_TYPES
)


class GeneratorConfig(BaseModel):
    """Configuration for question generation."""

    subject: str = Field(
        ...,
        description="Subject: mathematics/science/english/general"
    )
    topic: Optional[str] = Field(
        default=None,
        description="Specific topic e.g. Algebra, Photosynthesis"
    )
    grade_level: Optional[str] = Field(
        default=None,
        description="Grade level e.g. Grade 8, Undergraduate"
    )
    num_questions: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of questions to generate"
    )
    difficulty: str = Field(
        default="mixed",
        description="easy/medium/hard/mixed"
    )
    question_type: str = Field(
        default="mixed",
        description="mcq/short/long/numerical/mixed"
    )
    marks_per_question: Optional[int] = Field(
        default=5,
        ge=1,
        le=25,
        description="Marks per question"
    )
    include_answers: bool = Field(
        default=True,
        description="Include model answers and marking scheme"
    )
    use_source_patterns: bool = Field(
        default=True,
        description="Use patterns from uploaded source papers"
    )

    @validator("subject")
    def validate_subject(cls, v):
        if v.lower() not in VALID_SUBJECTS:
            return "general"
        return v.lower()

    @validator("difficulty")
    def validate_difficulty(cls, v):
        if v.lower() not in VALID_DIFFICULTIES:
            return "mixed"
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "mathematics",
                "topic": "Algebra",
                "grade_level": "Grade 10",
                "num_questions": 10,
                "difficulty": "mixed",
                "question_type": "mixed",
                "marks_per_question": 5,
                "include_answers": True
            }
        }


class SourcePaperUploadResponse(BaseModel):
    """Response after uploading a source paper."""
    paper_id: str
    filename: str
    subject: Optional[str]
    question_count: int
    topics_detected: List[str]
    difficulty_distribution: Dict[str, int]
    is_processed: bool
    message: str


class GeneratedQuestionItem(BaseModel):
    """Single generated question."""
    id: str
    question_text: str
    question_type: str
    subject: str
    topic: Optional[str]
    difficulty: str
    marks: int
    options: Optional[List[str]] = None
    correct_option: Optional[str] = None
    model_answer: Optional[str] = None
    marking_scheme: Optional[str] = None
    key_points: Optional[List[str]] = None
    is_duplicate: bool = False
    quality_score: Optional[float] = None


class GenerationResult(BaseModel):
    """Complete generation result."""
    batch_id: str
    request_id: str
    subject: str
    topic: Optional[str]
    total_generated: int
    duplicates_removed: int
    questions: List[GeneratedQuestionItem]
    topic_coverage: Dict[str, int]
    difficulty_distribution: Dict[str, int]
    question_type_distribution: Dict[str, int]
    processing_time_ms: float
    model_used: str
    provider: str
    governance_status: str


class PatternAnalysisResult(BaseModel):
    """Result of pattern analysis on source papers."""
    paper_id: str
    total_questions: int
    topics: List[Dict[str, Any]]
    difficulty_distribution: Dict[str, float]
    question_type_distribution: Dict[str, float]
    marks_distribution: Dict[str, float]
    recurring_topics: List[str]
    recommended_focus: List[str]


class PDFExportRequest(BaseModel):
    """Request to export questions as PDF."""
    batch_id: str
    title: Optional[str] = "Generated Question Paper"
    institution: Optional[str] = None
    include_answers: bool = False
    watermark: Optional[str] = None
