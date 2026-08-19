import time
import json
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from app.core.logger import logger

# Routes to skip detailed logging (too noisy)
SKIP_LOG_ROUTES = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
]

# Routes to skip body logging (privacy)
SKIP_BODY_ROUTES = [
    "/api/v1/auth",
    "/api/v1/voice",
]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured request/response logging middleware.
    Logs method, path, status, timing, and basic metadata.
    """

    def _should_skip(self, path: str) -> bool:
        """Check if route should skip logging."""
        for skip in SKIP_LOG_ROUTES:
            if path.startswith(skip):
                return True
        return False

    def _should_skip_body(self, path: str) -> bool:
        """Check if route should skip body logging."""
        for skip in SKIP_BODY_ROUTES:
            if path.startswith(skip):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        path = request.url.path

        if self._should_skip(path):
            return await call_next(request)

        start_time = time.time()
        request_id = getattr(
            request.state, "request_id", "unknown"
        )

        # Get client info
        client_ip = (
            request.client.host if request.client else "unknown"
        )
        user_agent = request.headers.get("user-agent", "unknown")[:100]

        # Get user info if authenticated
        user_id = "anonymous"
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("user_id", "anonymous")
            if user_id:
                user_id = user_id[:8] + "..."

        # Log request
        logger.info(
            f"→ REQUEST | "
            f"id={request_id} | "
            f"{request.method} {path} | "
            f"ip={client_ip} | "
            f"user={user_id}"
        )

        # Process request
        try:
            response = await call_next(request)
            elapsed_ms = (time.time() - start_time) * 1000

            # Log response
            level = "info"
            if response.status_code >= 500:
                level = "error"
            elif response.status_code >= 400:
                level = "warning"

            log_msg = (
                f"← RESPONSE | "
                f"id={request_id} | "
                f"status={response.status_code} | "
                f"time={elapsed_ms:.0f}ms | "
                f"{request.method} {path}"
            )

            if level == "error":
                logger.error(log_msg)
            elif level == "warning":
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

            return response

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"← ERROR | "
                f"id={request_id} | "
                f"error={str(e)} | "
                f"time={elapsed_ms:.0f}ms | "
                f"{request.method} {path}"
            )
            raise


class StructuredLogger:
    """
    Helper for structured JSON logging.
    Useful for log aggregation services.
    """

    @staticmethod
    def log_api_event(
        event: str,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        elapsed_ms: float,
        user_id: str = "anonymous",
        extra: dict = None
    ):
        """Log a structured API event."""
        log_data = {
            "event": event,
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "elapsed_ms": round(elapsed_ms, 2),
            "user_id": user_id,
        }
        if extra:
            log_data.update(extra)

        logger.info(f"STRUCTURED | {json.dumps(log_data)}")

    @staticmethod
    def log_ai_event(
        challenge: str,
        event: str,
        request_id: str,
        model: str,
        elapsed_ms: float,
        success: bool,
        extra: dict = None
    ):
        """Log a structured AI processing event."""
        log_data = {
            "type": "ai_event",
            "challenge": challenge,
            "event": event,
            "request_id": request_id,
            "model": model,
            "elapsed_ms": round(elapsed_ms, 2),
            "success": success,
        }
        if extra:
            log_data.update(extra)

        logger.info(f"AI_EVENT | {json.dumps(log_data)}")
