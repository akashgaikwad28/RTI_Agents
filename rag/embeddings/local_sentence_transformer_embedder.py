"""Local sentence-transformers embedder.

This embedder is used to generate vectors without external API keys.
It is LangChain-compatible via `get_langchain_embedder()`.

Notes:
- SentenceTransformer models expose `encode()` which returns numpy arrays.
- We convert to plain python lists[float] for JSON serialization.
"""

from __future__ import annotations

import asyncio
import hashlib
from functools import lru_cache
from typing import Any

from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

import threading

from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=4)
def _load_model(model_name: str):
    # Local import so the dependency is only required when this embedder is used.
    from sentence_transformers import SentenceTransformer

    logger.info(f"[LocalSentenceTransformerEmbedder] Loading model: {model_name}")
    return SentenceTransformer(model_name)


class LocalSentenceTransformerEmbedder:
    """Local embedding provider using sentence-transformers."""

    def __init__(
        self,
        model_name: str | None = None,
        cache_ttl: int | None = None,
    ):
        self.model_name = model_name or getattr(
            settings,
            "LOCAL_SENTENCE_TRANSFORMER_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        self.model = _load_model(self.model_name)

        ttl = cache_ttl or getattr(settings, "RAG_CACHE_TTL", settings.REDIS_SEMANTIC_CACHE_TTL)
        self._cache: TTLCache[str, list[float]] = TTLCache(maxsize=10000, ttl=ttl)
        self._lock = threading.Lock()

        # Best-effort: model.max_seq_length is not the same as vector dimension.
        # We determine dimension by embedding a short string if needed.
        self._dimension: int | None = None

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

    def _ensure_dimension(self) -> int:
        if self._dimension is not None:
            return self._dimension
        vec = self.embed_query("dimension_probe")
        self._dimension = len(vec)
        return self._dimension

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_query(self, text: str) -> list[float]:
        key = self._key(text)
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        
        vec = self.model.encode([text], normalize_embeddings=False)[0]
        result = [float(x) for x in vec]
        
        with self._lock:
            self._cache[key] = result
            return self._cache[key]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        outputs: list[list[float] | None] = [None] * len(texts)
        missing_texts: list[str] = []
        missing_indexes: list[int] = []

        with self._lock:
            for i, t in enumerate(texts):
                key = self._key(t)
                if key in self._cache:
                    outputs[i] = self._cache[key]
                else:
                    missing_texts.append(t)
                    missing_indexes.append(i)

        if missing_texts:
            vectors = self.model.encode(missing_texts, normalize_embeddings=False)
            with self._lock:
                for idx, vec in zip(missing_indexes, vectors):
                    outputs[idx] = [float(x) for x in vec]
                    self._cache[self._key(texts[idx])] = outputs[idx]

        return [vec if vec is not None else [] for vec in outputs]

    async def aembed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_query, text)

    async def aembed_documents(self, texts: list[str], batch_size: int | None = None) -> list[list[float]]:
        batch_size = batch_size or getattr(settings, "EMBEDDING_BATCH_SIZE", 32)
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(await asyncio.to_thread(self.embed_documents, batch))
        return vectors

    def get_langchain_embedder(self) -> Any:
        """Return an object LangChain FAISS can call.

        FAISS wrapper in this repo only needs `.embed_documents()` and `.embed_query()`.
        This class already provides those methods, so we return `self`.
        """

        # Ensure dimension once so early failures are visible.
        self._ensure_dimension()
        return self

