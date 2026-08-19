from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
from app.core.logger import logger
from app.core.security import decode_token

# Public routes that don't need authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/evaluator/evaluate",
    "/api/v1/generator/generate",
    "/api/v1/spelling/check",
    "/api/v1/voice/ws",
    "/api/v1/sales/chat",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware.
    Validates token on protected routes.
    Attaches user info to request state.
    """

    def __init__(self, app, public_routes: Optional[List[str]] = None):
        super().__init__(app)
        self.public_routes = public_routes or PUBLIC_ROUTES

    def _is_public_route(self, path: str) -> bool:
        """Check if route is public."""
        for public_path in self.public_routes:
            if path == public_path:
                return True
            if path.startswith(public_path):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        """Process request through auth middleware."""
        path = request.url.path

        # Skip auth for public routes
        if self._is_public_route(path):
            request.state.user = None
            request.state.authenticated = False
            response = await call_next(request)
            return response

        # Extract token from header
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            request.state.user = None
            request.state.authenticated = False
            response = await call_next(request)
            return response

        token = auth_header.split(" ", 1)[1]

        try:
            payload = decode_token(token)
            request.state.user = {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "student"),
                "exp": payload.get("exp")
            }
            request.state.authenticated = True
            logger.debug(
                f"Auth OK: user={payload.get('sub')} "
                f"path={path}"
            )
        except HTTPException:
            request.state.user = None
            request.state.authenticated = False
            logger.warning(
                f"Auth failed for path={path}"
            )

        response = await call_next(request)
        return response
