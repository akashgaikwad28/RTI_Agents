"""
rag/vectorstore/semantic_cache.py
----------------------------------
Redis-backed semantic cache for retrieval results.
Avoids redundant FAISS calls for identical/similar queries.
"""

import redis.asyncio as aioredis
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

_cache_instance: "SemanticCache | None" = None


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

    async def set(self, key: str, value: str, ttl: int = None):
        if not self._client:
            return
        try:
            await self._client.set(key, value, ex=ttl or settings.REDIS_SEMANTIC_CACHE_TTL)
        except Exception as e:
            logger.warning(f"[SemanticCache] SET failed: {e}")

    async def delete(self, key: str):
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
    """Returns singleton SemanticCache."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCache()
        await _cache_instance.connect()
    return _cache_instance
