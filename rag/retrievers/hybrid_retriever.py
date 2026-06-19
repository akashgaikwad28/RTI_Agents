"""Hybrid retriever: FAISS semantic search plus metadata and lightweight reranking."""

from __future__ import annotations

import hashlib
import json
import time

from config.settings import settings
from observability.metrics import rag_retrieval_latency, retrieval_hit_rate
from observability.structured_logger import get_logger
from rag.retrievers.metadata_filter import apply_recency_boost, infer_department, keyword_overlap_score
from rag.retrievers.semantic_retriever import SemanticRetriever
from rag.types import RetrievalResult
from rag.vectorstore.semantic_cache import get_semantic_cache

logger = get_logger(__name__)


class HybridRetriever:
    def __init__(self, semantic_retriever: SemanticRetriever | None = None):
        self.semantic = semantic_retriever or SemanticRetriever()

    async def retrieve(
        self,
        query: str,
        *,
        department: str = "",
        language: str = "",
        k: int | None = None,
        use_cache: bool = True,
    ) -> tuple[list[RetrievalResult], bool, float]:
        started = time.perf_counter()
        k = k or getattr(settings, "FAISS_TOP_K", settings.RAG_TOP_K)
        normalized_department = infer_department(query, department)
        cache_key = _cache_key(query, normalized_department, language, k)

        if use_cache:
            cached = await self._cache_get(cache_key)
            if cached is not None:
                rag_retrieval_latency.observe(time.perf_counter() - started)
                retrieval_hit_rate.labels(source="cache").inc()
                return cached, True, _confidence(cached)

        candidates = await self.semantic.retrieve(
            query,
            department=normalized_department,
            language=language,
            k=max(k * 4, k),
        )
        if not candidates and normalized_department:
            candidates = await self.semantic.retrieve(query, language=language, k=max(k * 4, k))

        reranked = self._rerank(query, candidates, normalized_department)[:k]
        if reranked:
            retrieval_hit_rate.labels(source="faiss").inc()
            await self._cache_set(cache_key, reranked)
        else:
            retrieval_hit_rate.labels(source="miss").inc()
        rag_retrieval_latency.observe(time.perf_counter() - started)
        return reranked, False, _confidence(reranked)

    def _rerank(self, query: str, results: list[RetrievalResult], department: str) -> list[RetrievalResult]:
        deduped: dict[str, RetrievalResult] = {}
        for result in results:
            key = result.metadata.source_hash or hashlib.sha256(result.text[:500].encode()).hexdigest()
            existing = deduped.get(key)
            if existing is None or result.score > existing.score:
                deduped[key] = result

        ranked: list[RetrievalResult] = []
        for result in deduped.values():
            score = result.score
            if department and result.metadata.department.lower() == department.lower():
                score += 0.1
            score += keyword_overlap_score(query, result.text)
            score += apply_recency_boost(result)
            result.score = round(min(score, 1.0), 4)
            ranked.append(result)
        return sorted(ranked, key=lambda item: item.score, reverse=True)

    async def _cache_get(self, key: str) -> list[RetrievalResult] | None:
        try:
            cache = await get_semantic_cache()
            raw = await cache.get(key)
            if not raw:
                return None
            return [RetrievalResult.model_validate(item) for item in json.loads(raw)]
        except Exception as exc:
            logger.warning(f"[HybridRetriever] Cache get failed: {exc}")
            return None

    async def _cache_set(self, key: str, results: list[RetrievalResult]) -> None:
        try:
            cache = await get_semantic_cache()
            payload = json.dumps([item.model_dump() for item in results], ensure_ascii=False)
            await cache.set(key, payload, ttl=getattr(settings, "RAG_CACHE_TTL", settings.REDIS_SEMANTIC_CACHE_TTL))
        except Exception as exc:
            logger.warning(f"[HybridRetriever] Cache set failed: {exc}")


def _cache_key(query: str, department: str, language: str, k: int) -> str:
    content = f"{query.lower().strip()}|{department.lower()}|{language}|{k}"
    return f"rti:rag:{hashlib.sha256(content.encode()).hexdigest()[:24]}"


def _confidence(results: list[RetrievalResult]) -> float:
    if not results:
        return 0.0
    top = results[0].score
    coverage = min(len(results) / max(getattr(settings, "FAISS_TOP_K", settings.RAG_TOP_K), 1), 1.0)
    return round((top * 0.75) + (coverage * 0.25), 4)

