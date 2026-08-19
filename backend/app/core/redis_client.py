import redis.asyncio as aioredis
import redis as sync_redis
from app.core.config import settings
from app.core.logger import logger
from typing import Optional, Any
import json

# Async Redis client
async_redis_client: Optional[aioredis.Redis] = None

# Sync Redis client
sync_redis_client: Optional[sync_redis.Redis] = None

async def get_async_redis() -> aioredis.Redis:
    """Get async Redis connection."""
    global async_redis_client
    if async_redis_client is None:
        try:
            async_redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            await async_redis_client.ping()
            logger.info("Async Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            async_redis_client = None
    return async_redis_client

def get_sync_redis() -> Optional[sync_redis.Redis]:
    """Get sync Redis connection."""
    global sync_redis_client
    if sync_redis_client is None:
        try:
            sync_redis_client = sync_redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            sync_redis_client.ping()
            logger.info("Sync Redis connected successfully")
        except Exception as e:
            logger.warning(f"Sync Redis connection failed: {e}")
            sync_redis_client = None
    return sync_redis_client

async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set cache value with TTL."""
    try:
        client = await get_async_redis()
        if client:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await client.setex(key, ttl, serialized)
            return True
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")
    return False

async def cache_get(key: str) -> Optional[Any]:
    """Get cache value."""
    try:
        client = await get_async_redis()
        if client:
            value = await client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
    return None

async def cache_delete(key: str) -> bool:
    """Delete cache key."""
    try:
        client = await get_async_redis()
        if client:
            await client.delete(key)
            return True
    except Exception as e:
        logger.warning(f"Cache delete failed: {e}")
    return False

async def close_redis():
    """Close Redis connections."""
    global async_redis_client
    if async_redis_client:
        await async_redis_client.close()
        async_redis_client = None
        logger.info("Redis connection closed")
