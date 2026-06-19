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
    async def retrieve(self, query: str, department: str = "", response_language: str | None = None, k: int = 5, db: Any = None) -> dict:
        normalized = UnicodeNormalizer().normalize(query)
        detection = LanguageDetector().detect(normalized)
        mapped = await CrossLingualMapper().map_query(normalized, detection.language, db=db)
        results, cache_hit, confidence = await CrossLingualSearch().search(mapped["queries"], department=department, k=k)
        language = response_language or detection.language if detection.language != "unknown" else "en"
        reranked = LanguageReranker().rerank(results, detection.language, preferred_language=language)[:k]
        localizer = CitationLocalizer()
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
                    "citation": localizer.localize(result, language),
                    "metadata": result.metadata.model_dump(),
                }
                for result in reranked
            ],
        }
