from typing import Any, Optional, Dict, List, Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()

    class Config:
        arbitrary_types_allowed = True


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    success: bool = True
    data: List[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False

    class Config:
        arbitrary_types_allowed = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = datetime.utcnow().isoformat()
    services: Dict[str, str] = {}
    uptime_seconds: float = 0.0


class GovernanceInfo(BaseModel):
    """Governance metadata for AI responses."""
    governance_status: str = "passed"
    governance_reason: str = ""
    confidence_score: float = 1.0
    human_review_triggered: bool = False
    model_used: str = ""
    provider: str = ""
    prompt_version: str = ""
    processing_time_ms: float = 0.0
    request_id: str = ""


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: Dict[str, Any] = {}
    timestamp: str = datetime.utcnow().isoformat()


def success_response(
    data: Any = None,
    message: str = "Success",
    request_id: str = ""
) -> Dict[str, Any]:
    """Create a success API response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(
    message: str,
    code: str = "ERROR",
    details: Any = None,
    request_id: str = ""
) -> Dict[str, Any]:
    """Create an error API response."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details
        },
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat()
    }


def paginated_response(
    data: List[Any],
    total: int,
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """Create a paginated response."""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "success": True,
        "data": data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "timestamp": datetime.utcnow().isoformat()
    }
