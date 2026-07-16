"""Language-aware reranking for cross-lingual retrieval."""

from __future__ import annotations

from rag.types import RetrievalResult


class LanguageReranker:
    def rerank(self, results: list[RetrievalResult], query_language: str, preferred_language: str | None = None) -> list[RetrievalResult]:
        preferred = preferred_language or query_language
        reranked = []
        for result in results:
            doc_lang = result.metadata.language
            new_score = result.score
            if doc_lang == preferred:
                # Boost documents in the preferred language
                new_score = round(min(1.0, new_score + 0.08), 4)
            # Fix: do NOT boost other languages — only the preferred language gets a boost
            # Use model_copy to avoid in-place mutation of shared objects
            reranked.append(result.model_copy(update={"score": new_score}))
        return sorted(reranked, key=lambda item: item.score, reverse=True)

