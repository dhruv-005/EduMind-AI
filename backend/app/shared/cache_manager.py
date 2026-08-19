import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
from app.core.logger import logger
from app.core.redis_client import cache_get, cache_set, cache_delete
from app.core.constants import (
    CACHE_TTL_SHORT,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_LONG
)


class CacheManager:
    """
    High-level cache manager with Redis backend.
    Falls back to no-cache if Redis unavailable.
    """

    def make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"edumind:{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await cache_get(key)
            if value is not None:
                logger.debug(f"Cache HIT: {key}")
                return value
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = CACHE_TTL_MEDIUM
    ) -> bool:
        """Set value in cache with TTL."""
        try:
            result = await cache_set(key, value, ttl)
            if result:
                logger.debug(f"Cache SET: {key} (ttl={ttl}s)")
            return result
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return await cache_delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        ttl: int = CACHE_TTL_MEDIUM
    ) -> Any:
        """
        Get from cache or compute and cache the result.
        fetch_func can be sync or async.
        """
        cached = await self.get(key)
        if cached is not None:
            return cached

        # Compute value
        import asyncio
        if asyncio.iscoroutinefunction(fetch_func):
            value = await fetch_func()
        else:
            value = fetch_func()

        if value is not None:
            await self.set(key, value, ttl)

        return value

    async def invalidate_prefix(self, prefix: str) -> int:
        """
        Invalidate all keys with given prefix.
        Note: This is approximate with hash-based keys.
        Returns number of deleted keys.
        """
        logger.info(f"Cache invalidation requested for prefix: {prefix}")
        return 0

    def cache_evaluation(self, ttl: int = CACHE_TTL_LONG):
        """Decorator to cache evaluation results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                import asyncio
                key_parts = [str(a) for a in args[1:]]
                key_parts += [f"{k}={v}" for k, v in kwargs.items()]
                key = self.make_key("eval", *key_parts)

                cached = await self.get(key)
                if cached:
                    logger.info(f"Returning cached evaluation: {key}")
                    return cached

                result = await func(*args, **kwargs)
                if result:
                    await self.set(key, result, ttl)
                return result
            return wrapper
        return decorator

    async def cache_llm_response(
        self,
        prompt_hash: str,
        response: str,
        ttl: int = CACHE_TTL_LONG
    ) -> bool:
        """Cache an LLM response."""
        key = f"edumind:llm:{prompt_hash}"
        return await self.set(key, response, ttl)

    async def get_cached_llm_response(
        self,
        prompt_hash: str
    ) -> Optional[str]:
        """Get cached LLM response."""
        key = f"edumind:llm:{prompt_hash}"
        return await self.get(key)

    def hash_prompt(self, prompt: str) -> str:
        """Hash a prompt for cache key."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:20]


# Singleton
cache_manager = CacheManager()
