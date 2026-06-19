"""Redis-backed translation cache with in-memory fallback."""

from __future__ import annotations

import hashlib

from cachetools import TTLCache

from rag.vectorstore.semantic_cache import get_semantic_cache


class TranslationCache:
    def __init__(self):
        self._memory = TTLCache(maxsize=10000, ttl=86400)

    def key(self, text: str, source: str, target: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
        return f"translation:{source}:{target}:{digest}"

    async def get(self, text: str, source: str, target: str) -> str | None:
        key = self.key(text, source, target)
        if key in self._memory:
            return self._memory[key]
        try:
            cache = await get_semantic_cache()
            value = await cache.get(key)
            if value:
                self._memory[key] = value
            return value
        except Exception:
            return None

    async def set(self, text: str, source: str, target: str, translated: str) -> None:
        key = self.key(text, source, target)
        self._memory[key] = translated
        try:
            cache = await get_semantic_cache()
            await cache.set(key, translated, ttl=86400)
        except Exception:
            pass
