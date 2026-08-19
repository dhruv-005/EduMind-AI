import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
from app.core.config import settings

# Burst protection: max requests per second
BURST_LIMIT = 10
BURST_WINDOW = 1  # second

# Per-endpoint limits (requests per minute)
ENDPOINT_LIMITS: Dict[str, Tuple[int, int]] = {
    "/api/v1/evaluator/evaluate": (20, 60),
    "/api/v1/generator/generate": (10, 60),
    "/api/v1/spelling/check": (15, 60),
    "/api/v1/voice/ws": (5, 60),
    "/api/v1/sales/chat": (30, 60),
    "/api/v1/admin": (50, 60),
}

# Routes exempt from rate limiting
EXEMPT_ROUTES = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiting middleware.
    Provides burst protection and per-endpoint limits.
    """

    def __init__(self, app):
        super().__init__(app)
        # {ip: [timestamps]}
        self._ip_requests: Dict[str, list] = defaultdict(list)
        # {ip+endpoint: [timestamps]}
        self._endpoint_requests: Dict[str, list] = defaultdict(list)
        # Blocked IPs {ip: unblock_time}
        self._blocked_ips: Dict[str, float] = {}

    def _is_exempt(self, path: str) -> bool:
        """Check if route is exempt from rate limiting."""
        for exempt in EXEMPT_ROUTES:
            if path.startswith(exempt):
                return True
        return False

    def _clean_old(self, requests: list, window: int) -> list:
        """Remove timestamps outside window."""
        cutoff = time.time() - window
        return [t for t in requests if t > cutoff]

    def _check_burst(self, ip: str) -> Tuple[bool, str]:
        """Check burst limit (requests per second)."""
        key = f"burst:{ip}"
        now = time.time()
        self._ip_requests[key] = self._clean_old(
            self._ip_requests[key], BURST_WINDOW
        )

        if len(self._ip_requests[key]) >= BURST_LIMIT:
            return False, f"Burst limit exceeded: max {BURST_LIMIT}/second"

        self._ip_requests[key].append(now)
        return True, "OK"

    def _check_endpoint_limit(
        self,
        ip: str,
        path: str
    ) -> Tuple[bool, str, int]:
        """
        Check per-endpoint rate limit.
        Returns: (allowed, reason, retry_after)
        """
        # Find matching endpoint limit
        limit, window = None, 60
        for endpoint, (lim, win) in ENDPOINT_LIMITS.items():
            if path.startswith(endpoint):
                limit, window = lim, win
                break

        if limit is None:
            return True, "No limit configured", 0

        key = f"endpoint:{ip}:{path}"
        now = time.time()
        self._endpoint_requests[key] = self._clean_old(
            self._endpoint_requests[key], window
        )

        count = len(self._endpoint_requests[key])
        if count >= limit:
            return (
                False,
                f"Endpoint limit exceeded: max {limit}/{window}s",
                window
            )

        self._endpoint_requests[key].append(now)
        remaining = limit - count - 1
        return True, f"OK ({remaining} remaining)", 0

    def _is_blocked(self, ip: str) -> Tuple[bool, int]:
        """Check if IP is temporarily blocked."""
        if ip in self._blocked_ips:
            unblock_time = self._blocked_ips[ip]
            if time.time() < unblock_time:
                retry_after = int(unblock_time - time.time())
                return True, retry_after
            else:
                del self._blocked_ips[ip]
        return False, 0

    def _auto_block(self, ip: str, duration: int = 300):
        """Auto-block an IP for repeated violations."""
        self._blocked_ips[ip] = time.time() + duration
        logger.warning(
            f"IP auto-blocked for {duration}s: {ip}"
        )

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to request."""
        path = request.url.path

        if self._is_exempt(path):
            return await call_next(request)

        client_ip = (
            request.client.host if request.client else "0.0.0.0"
        )

        # Check if IP is blocked
        blocked, retry_after = self._is_blocked(client_ip)
        if blocked:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "IP_BLOCKED",
                        "message": (
                            f"Your IP is temporarily blocked. "
                            f"Retry after {retry_after} seconds."
                        )
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Status": "blocked"
                }
            )

        # Check burst limit
        burst_ok, burst_msg = self._check_burst(client_ip)
        if not burst_ok:
            logger.warning(
                f"Burst limit hit: ip={client_ip} path={path}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "BURST_LIMIT_EXCEEDED",
                        "message": burst_msg
                    }
                },
                headers={
                    "Retry-After": "1",
                    "X-RateLimit-Status": "burst_limited"
                }
            )

        # Check endpoint limit
        ep_ok, ep_msg, retry = self._check_endpoint_limit(
            client_ip, path
        )
        if not ep_ok:
            logger.warning(
                f"Endpoint limit hit: "
                f"ip={client_ip} "
                f"path={path} "
                f"msg={ep_msg}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": (
                            "Too many requests. "
                            f"Please retry after {retry} seconds."
                        )
                    }
                },
                headers={
                    "Retry-After": str(retry),
                    "X-RateLimit-Status": "limited"
                }
            )

        # Process request normally
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-IP"] = client_ip
        response.headers["X-RateLimit-Status"] = "ok"

        return response
