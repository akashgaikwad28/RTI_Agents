"""
rag/vectorstore/semantic_cache.py
----------------------------------
Redis-backed semantic cache for retrieval results.
Avoids redundant FAISS calls for identical/similar queries.
"""

import asyncio
import redis.asyncio as aioredis
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

_cache_instance: "SemanticCache | None" = None
# Fix: async lock to guard singleton creation and prevent connection leak race condition
_cache_lock = asyncio.Lock()


class SemanticCache:
    """Async Redis cache for retrieval results."""

    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def connect(self):
        try:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
            await self._client.ping()
            logger.info(f"[SemanticCache] Redis connected: {settings.REDIS_URL}")
        except Exception as e:
            logger.warning(f"[SemanticCache] Redis unavailable: {e}. Cache disabled.")
            self._client = None

    async def get(self, key: str) -> str | None:
        if not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.warning(f"[SemanticCache] GET failed: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        if not self._client:
            return
        try:
            # Fix: use explicit None check instead of falsy check to allow ttl=0 (no expiry)
            effective_ttl = ttl if ttl is not None else settings.REDIS_SEMANTIC_CACHE_TTL
            if effective_ttl and effective_ttl > 0:
                await self._client.set(key, value, ex=effective_ttl)
            else:
                await self._client.set(key, value)
        except Exception as e:
            logger.warning(f"[SemanticCache] SET failed: {e}")

    async def delete(self, key: str) -> None:
        if not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception:
            pass

    @property
    def is_available(self) -> bool:
        return self._client is not None


async def get_semantic_cache() -> SemanticCache:
    """Returns singleton SemanticCache, protected by an async lock to prevent race conditions."""
    global _cache_instance
    if _cache_instance is not None:
        return _cache_instance
    async with _cache_lock:
        # Double-checked locking: re-check after acquiring lock
        if _cache_instance is None:
            _cache_instance = SemanticCache()
            await _cache_instance.connect()
    return _cache_instance
