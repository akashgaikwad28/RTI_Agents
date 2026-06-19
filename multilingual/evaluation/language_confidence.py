"""Language confidence scoring."""

from __future__ import annotations


def language_confidence(detection: dict) -> float:
    return float(detection.get("confidence", 0.0))
