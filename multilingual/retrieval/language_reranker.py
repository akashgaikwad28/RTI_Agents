"""Language-aware reranking for cross-lingual retrieval."""

from __future__ import annotations

from rag.types import RetrievalResult


class LanguageReranker:
    def rerank(self, results: list[RetrievalResult], query_language: str, preferred_language: str | None = None) -> list[RetrievalResult]:
        preferred = preferred_language or query_language
        for result in results:
            doc_lang = result.metadata.language
            if doc_lang == preferred:
                result.score = round(min(1.0, result.score + 0.08), 4)
            elif doc_lang in {"en", "hi", "mr"}:
                result.score = round(min(1.0, result.score + 0.03), 4)
        return sorted(results, key=lambda item: item.score, reverse=True)
