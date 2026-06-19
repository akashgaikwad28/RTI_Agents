"""Reliability summaries for tool runs."""

from __future__ import annotations


def reliability_score(results: list[dict]) -> float:
    if not results:
        return 0.0
    successes = sum(1 for r in results if r.get("status") == "success")
    return round(successes / len(results), 4)
