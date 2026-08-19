from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SessionCreateRequest(BaseModel):
    """Request to create a new tutor session."""
    subject: Optional[str] = Field(
        default=None,
        description="Subject: mathematics/science/english/general"
    )
    grade_level: Optional[str] = Field(
        default=None,
        description="Grade level e.g. Grade 8"
    )
    language: str = Field(
        default="en",
        description="Language code: en"
    )
    tutor_mode: str = Field(
        default="standard",
        description="standard/socratic/hint_mode"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "mathematics",
                "grade_level": "Grade 10",
                "language": "en",
                "tutor_mode": "standard"
            }
        }


class SessionCreateResponse(BaseModel):
    """Response after creating a session."""
    session_id: str
    websocket_url: str
    subject: Optional[str]
    grade_level: Optional[str]
    tutor_mode: str
    message: str


class ConversationTurn(BaseModel):
    """Single conversation turn."""
    turn_number: int
    role: str
    text: str
    audio_url: Optional[str] = None
    detected_topic: Optional[str] = None
    is_educational: Optional[bool] = None
    processing_time_ms: Optional[float] = None
    created_at: str


class SessionSummaryResponse(BaseModel):
    """Session summary after completion."""
    session_id: str
    subject: Optional[str]
    duration_seconds: float
    total_interactions: int
    topics_covered: List[str]
    questions_asked: int
    detected_level: Optional[str]
    summary: str
    learning_progress: Optional[Dict[str, Any]]


class VoiceMessageRequest(BaseModel):
    """WebSocket message from client."""
    type: str
    session_id: str
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None


class VoiceMessageResponse(BaseModel):
    """WebSocket message to client."""
    type: str
    session_id: str
    text: Optional[str] = None
    audio_data: Optional[str] = None
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class TopicGuardResult(BaseModel):
    """Result of topic guard check."""
    is_educational: bool
    confidence: float
    detected_topic: Optional[str]
    reason: str
    rejection_message: Optional[str] = None


class LevelDetectionResult(BaseModel):
    """Result of student level detection."""
    detected_level: str
    confidence: float
    vocabulary_complexity: str
    question_type: str
    recommended_response_level: str
