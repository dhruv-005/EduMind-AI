from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger


def setup_cors(app):
    """
    Configure CORS middleware for the FastAPI app.
    Call this during app startup.
    """
    origins = settings.ALLOWED_ORIGINS

    logger.info(f"CORS configured for origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Processing-Time-Ms",
            "X-Governance-Version",
            "X-RateLimit-Remaining",
            "Content-Disposition",
        ],
        max_age=3600,
    )


class CORSConfig:
    """CORS configuration helper."""

    @staticmethod
    def get_allowed_origins() -> list:
        """Get list of allowed origins."""
        return settings.ALLOWED_ORIGINS

    @staticmethod
    def is_origin_allowed(origin: str) -> bool:
        """Check if an origin is allowed."""
        allowed = settings.ALLOWED_ORIGINS
        if "*" in allowed:
            return True
        return origin in allowed

    @staticmethod
    def get_cors_headers(origin: str) -> dict:
        """Get CORS headers for a given origin."""
        if CORSConfig.is_origin_allowed(origin):
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": (
                    "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                ),
                "Access-Control-Allow-Headers": (
                    "Content-Type, Authorization, X-Request-ID"
                ),
            }
        return {}
