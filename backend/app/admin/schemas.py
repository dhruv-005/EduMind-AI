from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardStats(BaseModel):
    """Overall platform statistics."""
    total_evaluations: int = 0
    total_questions_generated: int = 0
    total_spell_checks: int = 0
    total_voice_sessions: int = 0
    total_sales_conversations: int = 0
    total_users: int = 0
    active_sessions: int = 0
    avg_evaluation_score: float = 0.0
    total_api_calls_today: int = 0
    governance_flags_today: int = 0


class GovernanceStats(BaseModel):
    """Governance and safety statistics."""
    total_requests: int = 0
    passed: int = 0
    flagged: int = 0
    blocked: int = 0
    human_reviews_pending: int = 0
    human_reviews_completed: int = 0
    bias_detections: int = 0
    rate_limit_hits: int = 0
    by_challenge: Dict[str, Any] = {}


class AuditLogFilter(BaseModel):
    """Filter for audit log queries."""
    challenge: Optional[str] = None
    governance_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    human_review_required: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class HumanReviewAction(BaseModel):
    """Action on a human review item."""
    request_id: str
    decision: str = Field(
        description="approved or rejected"
    )
    notes: Optional[str] = None
    reviewer_id: Optional[str] = None


class ModelHealthReport(BaseModel):
    """LLM provider health report."""
    provider: str
    model: str
    status: str
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    is_current: bool = False


class PromptVersionInfo(BaseModel):
    """Prompt version information."""
    prompt_key: str
    version: str
    description: str
    created_at: str


class SystemHealthResponse(BaseModel):
    """System health check response."""
    status: str
    version: str
    timestamp: str
    database: str
    redis: str
    llm_providers: Dict[str, str]
    challenges_status: Dict[str, str]
    uptime_seconds: float


class BiasReportResponse(BaseModel):
    """Bias detection report."""
    total_checks: int
    bias_detected_count: int
    bias_rate: float
    by_severity: Dict[str, int]
    by_challenge: Dict[str, int]
    recent_instances: List[Dict[str, Any]]
