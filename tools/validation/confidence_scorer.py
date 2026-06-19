"""Tool confidence scoring heuristics."""

from __future__ import annotations

from typing import Any


class ConfidenceScorer:
    def score(self, output: Any, citations: dict, hallucination: dict) -> float:
        base = 0.55 if output else 0.0
        base += min(0.25, citations.get("official_citations", 0) * 0.08)
        base += 0.1 if citations.get("citations_found", 0) else 0.0
        base -= len(hallucination.get("flags", [])) * 0.12
        return round(max(0.0, min(1.0, base)), 4)
