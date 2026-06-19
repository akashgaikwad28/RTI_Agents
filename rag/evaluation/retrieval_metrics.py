"""Retrieval metric helpers for offline RAG evaluation."""

from __future__ import annotations

from rag.types import RetrievalResult


def retrieval_precision(results: list[RetrievalResult], relevant_source_hashes: set[str]) -> float:
    if not results:
        return 0.0
    hits = sum(1 for result in results if result.metadata.source_hash in relevant_source_hashes)
    return hits / len(results)


def retrieval_recall(results: list[RetrievalResult], relevant_source_hashes: set[str]) -> float:
    if not relevant_source_hashes:
        return 0.0
    hits = {result.metadata.source_hash for result in results if result.metadata.source_hash in relevant_source_hashes}
    return len(hits) / len(relevant_source_hashes)


def context_relevance(results: list[RetrievalResult]) -> float:
    if not results:
        return 0.0
    return sum(result.score for result in results) / len(results)


def grounding_score(answer: str, contexts: list[str]) -> float:
    if not answer or not contexts:
        return 0.0
    answer_terms = {term.lower() for term in answer.split() if len(term) > 3}
    context_text = " ".join(contexts).lower()
    if not answer_terms:
        return 0.0
    grounded = sum(1 for term in answer_terms if term in context_text)
    return grounded / len(answer_terms)


def hallucination_rate(answer: str, contexts: list[str]) -> float:
    return max(0.0, 1.0 - grounding_score(answer, contexts))

