"""Gemini embedding provider with async batching, retry, and cache support."""

from __future__ import annotations

import asyncio
import hashlib

from cachetools import TTLCache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)


class GeminiEmbedder:
    """Wrapper around GoogleGenerativeAIEmbeddings using models/embedding-001."""

    def __init__(self, cache_ttl: int | None = None):
        self.model = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )
        ttl = cache_ttl or getattr(settings, "RAG_CACHE_TTL", settings.REDIS_SEMANTIC_CACHE_TTL)
        self._cache: TTLCache[str, list[float]] = TTLCache(maxsize=10000, ttl=ttl)
        logger.info(f"[GeminiEmbedder] Initialized: {settings.GEMINI_EMBEDDING_MODEL}")

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_query(self, text: str) -> list[float]:
        key = self._key(text)
        if key not in self._cache:
            self._cache[key] = self.model.embed_query(text)
        return self._cache[key]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        output: list[list[float] | None] = []
        missing: list[str] = []
        missing_indexes: list[int] = []
        for index, text in enumerate(texts):
            key = self._key(text)
            if key in self._cache:
                output.append(self._cache[key])
            else:
                output.append(None)
                missing.append(text)
                missing_indexes.append(index)

        if missing:
            vectors = self.model.embed_documents(missing)
            for index, text, vector in zip(missing_indexes, missing, vectors):
                self._cache[self._key(text)] = vector
                output[index] = vector

        return [vector for vector in output if vector is not None]

    async def aembed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_query, text)

    async def aembed_documents(self, texts: list[str], batch_size: int | None = None) -> list[list[float]]:
        batch_size = batch_size or getattr(settings, "EMBEDDING_BATCH_SIZE", 32)
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(await asyncio.to_thread(self.embed_documents, batch))
        return vectors

    def get_langchain_embedder(self):
        return self.model
