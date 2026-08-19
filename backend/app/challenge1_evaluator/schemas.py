from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from app.core.constants import VALID_SUBJECTS, VALID_DIFFICULTIES


class EvaluationRequest(BaseModel):
    """Request schema for answer evaluation."""

    question: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The exam question"
    )
    reference_answer: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="The correct/reference answer"
    )
    student_answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The student's answer to evaluate"
    )
    subject: str = Field(
        default="general",
        description="Subject type: mathematics/science/english/general"
    )
    grade_level: Optional[str] = Field(
        default=None,
        description="Grade level: Grade 5 / Undergraduate etc."
    )
    max_score: Optional[float] = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        description="Maximum possible score"
    )
    strict_mode: Optional[bool] = Field(
        default=False,
        description="If True, penalize more for missing concepts"
    )

    @validator("subject")
    def validate_subject(cls, v):
        v_lower = v.lower()
        if v_lower not in VALID_SUBJECTS:
            return "general"
        return v_lower

    @validator("student_answer")
    def validate_student_answer(cls, v):
        if not v.strip():
            raise ValueError("Student answer cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is photosynthesis?",
                "reference_answer": (
                    "Photosynthesis is the process by which "
                    "plants use sunlight, water, and carbon dioxide "
                    "to produce oxygen and energy in the form of sugar."
                ),
                "student_answer": (
                    "Photosynthesis is when plants make food "
                    "using sunlight and water."
                ),
                "subject": "science",
                "grade_level": "Grade 8",
                "max_score": 10.0
            }
        }


class BatchEvaluationRequest(BaseModel):
    """Request schema for batch evaluation."""

    evaluations: List[EvaluationRequest] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of evaluations to process"
    )
    subject: Optional[str] = Field(
        default=None,
        description="Override subject for all evaluations"
    )


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown."""
    correctness: float = Field(ge=0, le=40)
    relevance: float = Field(ge=0, le=20)
    completeness: float = Field(ge=0, le=25)
    clarity: float = Field(ge=0, le=15)
    total: float = Field(ge=0, le=100)


class ConceptAnalysis(BaseModel):
    """Concept analysis result."""
    correct_concepts: List[str] = []
    missing_concepts: List[str] = []
    wrong_concepts: List[str] = []
    total_expected: int = 0
    total_found: int = 0
    coverage_percentage: float = 0.0


class EvaluationResult(BaseModel):
    """Complete evaluation result."""

    # IDs
    request_id: str
    evaluation_id: Optional[str] = None

    # Scores
    score_out_of_10: float = Field(ge=0, le=10)
    total_score: float = Field(ge=0, le=100)
    percentage: float = Field(ge=0, le=100)
    grade: str

    # Breakdown
    score_breakdown: ScoreBreakdown

    # Concepts
    concept_analysis: ConceptAnalysis

    # Feedback
    feedback: str
    improvement_suggestions: List[str] = []
    subject_specific_notes: Optional[str] = None

    # Metrics
    semantic_similarity: float = Field(ge=0, le=1)
    confidence_score: float = Field(ge=0, le=1)

    # Governance
    governance_status: str = "passed"
    human_review_required: bool = False
    model_used: str
    provider: str
    processing_time_ms: float
    prompt_version: str

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "abc123",
                "score_out_of_10": 7.5,
                "total_score": 75.0,
                "percentage": 75.0,
                "grade": "B",
                "feedback": "Good answer covering main concepts.",
                "governance_status": "passed",
                "human_review_required": False
            }
        }


class BatchEvaluationResult(BaseModel):
    """Batch evaluation result."""
    batch_id: str
    total_evaluations: int
    completed: int
    failed: int
    results: List[EvaluationResult]
    average_score: float
    processing_time_ms: float


class EvaluationHistoryItem(BaseModel):
    """Single item in evaluation history."""
    id: str
    subject: str
    score_out_of_10: float
    grade: str
    created_at: str


class EvaluationHistoryResponse(BaseModel):
    """Evaluation history response."""
    total: int
    items: List[EvaluationHistoryItem]
