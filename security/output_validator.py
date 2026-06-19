"""Validate AI outputs before approval/submission."""

from __future__ import annotations


def validate_grounded_output(text: str, citations: list[str], confidence: float) -> dict:
    issues: list[str] = []
    if len(text.strip()) < 40:
        issues.append("output_too_short")
    if not citations:
        issues.append("missing_citations")
    if confidence < 0.55:
        issues.append("low_confidence")
    return {"valid": not issues, "issues": issues}

