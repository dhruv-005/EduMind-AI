import time
import uuid
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
from app.governance.content_filter import content_filter
from app.governance.rate_limiter import rate_limit_checker
from app.core.constants import CONTENT_BLOCKED

# Routes that need content filtering
FILTERED_ROUTES = [
    "/api/v1/evaluator",
    "/api/v1/generator",
    "/api/v1/spelling",
    "/api/v1/voice",
    "/api/v1/sales",
]

# Routes exempt from rate limiting
RATE_LIMIT_EXEMPT = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth",
]


class GovernanceMiddleware(BaseHTTPMiddleware):
    """
    AI Governance middleware.
    Handles:
    - Rate limiting
    - Content filtering on text inputs
    - Request ID generation
    - Processing time tracking
    - Governance header injection
    """

    def _should_filter(self, path: str) -> bool:
        """Check if route needs content filtering."""
        for route in FILTERED_ROUTES:
            if path.startswith(route):
                return True
        return False

    def _should_rate_limit(self, path: str) -> bool:
        """Check if route needs rate limiting."""
        for exempt in RATE_LIMIT_EXEMPT:
            if path.startswith(exempt):
                return False
        return True

    async def _get_request_body_text(
        self, request: Request
    ) -> str:
        """Safely extract text from request body."""
        try:
            content_type = request.headers.get(
                "content-type", ""
            )
            if "application/json" in content_type:
                body = await request.body()
                if body:
                    data = json.loads(body)
                    # Extract text fields for filtering
                    text_fields = []
                    for key in [
                        "question", "answer", "student_answer",
                        "message", "text", "content", "query"
                    ]:
                        if key in data and isinstance(data[key], str):
                            text_fields.append(data[key])
                    return " ".join(text_fields)
        except Exception:
            pass
        return ""

    async def dispatch(self, request: Request, call_next):
        """Process request through governance middleware."""
        start_time = time.time()

        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Rate limiting
        if self._should_rate_limit(path):
            try:
                user_id = None
                if hasattr(request.state, "user") and request.state.user:
                    user_id = request.state.user.get("user_id")

                rate_limit_checker.enforce(
                    ip=client_ip,
                    user_id=user_id,
                    endpoint=path
                )
            except Exception as e:
                logger.warning(
                    f"Rate limit blocked: ip={client_ip} "
                    f"path={path}"
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": str(e)
                        },
                        "request_id": request_id
                    },
                    headers={
                        "X-Request-ID": request_id,
                        "Retry-After": "60"
                    }
                )

        # Content filtering for POST/PUT requests
        if (
            request.method in ["POST", "PUT"] and
            self._should_filter(path)
        ):
            try:
                text = await self._get_request_body_text(request)
                if text:
                    status_result, reason, patterns = (
                        content_filter.check_input(text)
                    )
                    if status_result == CONTENT_BLOCKED:
                        logger.warning(
                            f"Content BLOCKED: "
                            f"ip={client_ip} "
                            f"path={path} "
                            f"reason={reason}"
                        )
                        return JSONResponse(
                            status_code=400,
                            content={
                                "success": False,
                                "error": {
                                    "code": "CONTENT_BLOCKED",
                                    "message": (
                                        "Your input contains content "
                                        "that violates our safety policy."
                                    )
                                },
                                "request_id": request_id
                            },
                            headers={
                                "X-Request-ID": request_id,
                                "X-Governance-Status": "blocked"
                            }
                        )
                    request.state.content_status = status_result
                    request.state.content_reason = reason
            except Exception as e:
                logger.warning(
                    f"Content filter error (non-blocking): {e}"
                )

        # Process request
        response = await call_next(request)

        # Calculate processing time
        elapsed_ms = (time.time() - start_time) * 1000

        # Add governance headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Processing-Time-Ms"] = f"{elapsed_ms:.0f}"
        response.headers["X-Governance-Version"] = "1.0"

        # Log request
        logger.info(
            f"REQUEST | {request.method} {path} | "
            f"status={response.status_code} | "
            f"time={elapsed_ms:.0f}ms | "
            f"ip={client_ip} | "
            f"id={request_id}"
        )

        return response
