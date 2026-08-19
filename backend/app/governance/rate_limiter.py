import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import RateLimitException


class InMemoryRateLimiter:
    """
    In-memory rate limiter.
    Works without Redis for development.
    """

    def __init__(self):
        # {key: [(timestamp, count)]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._blocked: Dict[str, float] = {}

    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requests outside the time window."""
        now = time.time()
        cutoff = now - window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > cutoff
        ]

    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 3600
    ) -> Tuple[bool, Dict]:
        """
        Check if request is allowed.
        Returns: (allowed, info_dict)
        """
        now = time.time()

        # Check if blocked
        if key in self._blocked:
            block_until = self._blocked[key]
            if now < block_until:
                wait_time = int(block_until - now)
                return False, {
                    "allowed": False,
                    "reason": "temporarily_blocked",
                    "retry_after": wait_time
                }
            else:
                del self._blocked[key]

        # Clean old requests
        self._clean_old_requests(key, window_seconds)

        # Check limit
        current_count = len(self._requests[key])

        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False, {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "current": current_count,
                "limit": limit,
                "reset_after": window_seconds,
                "retry_after": window_seconds
            }

        # Allow and record
        self._requests[key].append(now)

        return True, {
            "allowed": True,
            "current": current_count + 1,
            "limit": limit,
            "remaining": limit - current_count - 1,
            "reset_after": window_seconds
        }

    def block_key(self, key: str, duration_seconds: int = 3600):
        """Temporarily block a key."""
        self._blocked[key] = time.time() + duration_seconds
        logger.warning(f"Key blocked for {duration_seconds}s: {key}")

    def get_usage(self, key: str, window_seconds: int = 3600) -> Dict:
        """Get current usage for a key."""
        self._clean_old_requests(key, window_seconds)
        count = len(self._requests[key])
        return {
            "key": key,
            "current_requests": count,
            "window_seconds": window_seconds
        }

    def reset_key(self, key: str):
        """Reset rate limit for a key (admin use)."""
        if key in self._requests:
            del self._requests[key]
        if key in self._blocked:
            del self._blocked[key]
        logger.info(f"Rate limit reset for key: {key}")


class RateLimitChecker:
    """High-level rate limit checker."""

    def __init__(self):
        self.limiter = InMemoryRateLimiter()

    def check_ip_limit(self, ip: str) -> Tuple[bool, Dict]:
        """Check per-IP rate limit."""
        return self.limiter.is_allowed(
            key=f"ip:{ip}",
            limit=settings.RATE_LIMIT_PER_HOUR,
            window_seconds=3600
        )

    def check_user_limit(self, user_id: str) -> Tuple[bool, Dict]:
        """Check per-user daily rate limit."""
        return self.limiter.is_allowed(
            key=f"user:{user_id}",
            limit=settings.RATE_LIMIT_PER_DAY,
            window_seconds=86400
        )

    def check_endpoint_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int = 20,
        window: int = 60
    ) -> Tuple[bool, Dict]:
        """Check per-endpoint rate limit."""
        return self.limiter.is_allowed(
            key=f"endpoint:{endpoint}:{identifier}",
            limit=limit,
            window_seconds=window
        )

    def enforce(
        self,
        ip: str,
        user_id: Optional[str] = None,
        endpoint: str = ""
    ):
        """
        Enforce all rate limits.
        Raises RateLimitException if exceeded.
        """
        allowed, info = self.check_ip_limit(ip)
        if not allowed:
            raise RateLimitException(
                f"IP rate limit exceeded. Retry after {info.get('retry_after', 60)}s"
            )

        if user_id:
            allowed, info = self.check_user_limit(user_id)
            if not allowed:
                raise RateLimitException(
                    f"Daily limit exceeded. Retry after {info.get('retry_after', 3600)}s"
                )

        if endpoint:
            allowed, info = self.check_endpoint_limit(
                identifier=user_id or ip,
                endpoint=endpoint
            )
            if not allowed:
                raise RateLimitException(
                    f"Endpoint rate limit exceeded. Retry after {info.get('retry_after', 60)}s"
                )


# Singleton
rate_limit_checker = RateLimitChecker()
