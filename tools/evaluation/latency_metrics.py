"""Latency summaries for tool runs."""

from __future__ import annotations


def latency_summary(results: list[dict]) -> dict:
    values = [float(r.get("latency_ms", 0)) for r in results]
    if not values:
        return {"avg_ms": 0, "max_ms": 0}
    return {"avg_ms": round(sum(values) / len(values), 2), "max_ms": round(max(values), 2)}
