"""Multilingual RAG flow: detect, normalize, expand, retrieve, rerank, localize."""

from __future__ import annotations

from typing import Any

from multilingual.detection.language_detector import LanguageDetector
from multilingual.embeddings.cross_lingual_mapper import CrossLingualMapper
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from multilingual.retrieval.citation_localizer import CitationLocalizer
from multilingual.retrieval.crosslingual_search import CrossLingualSearch
from multilingual.retrieval.language_reranker import LanguageReranker


class MultilingualRetriever:
    # Fix: instantiate helpers once per retriever instance, not once per request call
    def __init__(self):
        self._normalizer = UnicodeNormalizer()
        self._detector = LanguageDetector()
        self._mapper = CrossLingualMapper()
        self._search = CrossLingualSearch()
        self._reranker = LanguageReranker()
        self._localizer = CitationLocalizer()

    async def retrieve(self, query: str, department: str = "", response_language: str | None = None, k: int = 5, db: Any = None) -> dict:
        normalized = self._normalizer.normalize(query)
        detection = self._detector.detect(normalized)
        mapped = await self._mapper.map_query(normalized, detection.language, db=db)
        results, cache_hit, confidence = await self._search.search(mapped["queries"], department=department, k=k)

        # Fix operator precedence bug: response_language must override even when detection is "unknown"
        if response_language:
            language = response_language
        elif detection.language != "unknown":
            language = detection.language
        else:
            language = "en"

        reranked = self._reranker.rerank(results, detection.language, preferred_language=language)[:k]
        return {
            "query": query,
            "normalized_query": normalized,
            "detected_language": detection.model_dump(),
            "expanded_queries": mapped["queries"],
            "cache_hit": cache_hit,
            "confidence": confidence,
            "response_language": language,
            "results": [
                {
                    "text": result.text,
                    "score": result.score,
                    "citation": self._localizer.localize(result, language),
                    "metadata": result.metadata.model_dump(),
                }
                for result in reranked
            ],
        }

