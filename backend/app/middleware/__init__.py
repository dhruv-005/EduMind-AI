from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.governance_middleware import GovernanceMiddleware
from app.middleware.cors_middleware import setup_cors, CORSConfig
from app.middleware.logging_middleware import (
    RequestLoggingMiddleware,
    StructuredLogger
)
from app.middleware.rate_limit_middleware import RateLimitMiddleware


def setup_all_middleware(app):
    """
    Setup all middleware for the FastAPI app.
    Order matters - last added = first executed.
    """
    # 1. CORS (must be first/outermost)
    setup_cors(app)

    # 2. Rate limiting
    app.add_middleware(RateLimitMiddleware)

    # 3. Governance (content filter + request ID)
    app.add_middleware(GovernanceMiddleware)

    # 4. Auth
    app.add_middleware(AuthMiddleware)

    # 5. Logging (innermost)
    app.add_middleware(RequestLoggingMiddleware)


__all__ = [
    "AuthMiddleware",
    "GovernanceMiddleware",
    "setup_cors",
    "CORSConfig",
    "RequestLoggingMiddleware",
    "StructuredLogger",
    "RateLimitMiddleware",
    "setup_all_middleware"
]
