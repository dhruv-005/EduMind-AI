from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import logger
import traceback

class EduMindException(Exception):
    """Base exception for EduMind platform."""
    def __init__(self, message: str, code: str = "EDUMIND_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class LLMException(EduMindException):
    """LLM service error."""
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")

class GovernanceException(EduMindException):
    """Governance/safety violation."""
    def __init__(self, message: str):
        super().__init__(message, "GOVERNANCE_VIOLATION")

class FileProcessingException(EduMindException):
    """File processing error."""
    def __init__(self, message: str):
        super().__init__(message, "FILE_ERROR")

class ValidationException(EduMindException):
    """Input validation error."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class RateLimitException(EduMindException):
    """Rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT")

async def edumind_exception_handler(request: Request, exc: EduMindException):
    """Handle EduMind custom exceptions."""
    logger.warning(f"EduMind exception: {exc.code} - {exc.message}")
    status_map = {
        "GOVERNANCE_VIOLATION": 400,
        "VALIDATION_ERROR": 422,
        "RATE_LIMIT": 429,
        "LLM_ERROR": 503,
        "FILE_ERROR": 400,
    }
    status_code = status_map.get(exc.code, 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(e) for e in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": errors
            }
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again."
            }
        }
    )
