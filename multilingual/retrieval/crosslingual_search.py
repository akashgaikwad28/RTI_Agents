"""Cross-lingual semantic retrieval over existing RAG infrastructure."""

from __future__ import annotations

import asyncio
import hashlib

from rag.retriever import retrieve_rag_results
from rag.types import RetrievalResult


class CrossLingualSearch:
    async def search(self, queries: list[str], department: str = "", languages: list[str] | None = None, k: int = 5) -> tuple[list[RetrievalResult], bool, float]:
        all_results: list[RetrievalResult] = []
        cache_hits = []
        confidences = []
        search_languages = languages or ["", "en", "hi", "mr"]
        
        tasks = []
        for query in queries:
            for language in search_languages:
                tasks.append(retrieve_rag_results(query, department=department, language=language, k=k))
                
        task_results = await asyncio.gather(*tasks)
        
        for results, cache_hit, confidence in task_results:
            all_results.extend(results)
            cache_hits.append(cache_hit)
            confidences.append(confidence)
        deduped: dict[str, RetrievalResult] = {}
        for result in all_results:
            key = result.metadata.source_hash or hashlib.sha256((result.text[:300] + result.citation).encode("utf-8", errors="ignore")).hexdigest()
            if key not in deduped or result.score > deduped[key].score:
                deduped[key] = result
        ranked = sorted(deduped.values(), key=lambda item: item.score, reverse=True)[:k]
        confidence = round(max(confidences or [0.0]), 4)
        return ranked, any(cache_hits), confidence
