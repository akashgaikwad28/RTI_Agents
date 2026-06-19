"""Cross-lingual retrieval accuracy metrics."""

from __future__ import annotations


def retrieval_accuracy(results: list[dict], expected_language: str | None = None) -> dict:
    if not results:
        return {"score": 0.0, "coverage": 0.0}
    top = max(float(result.get("score", 0)) for result in results)
    lang_hits = 0
    if expected_language:
        lang_hits = sum(1 for result in results if result.get("metadata", {}).get("language") == expected_language)
    return {"score": round(top, 4), "coverage": round(len(results) / 5, 4), "language_hits": lang_hits}
