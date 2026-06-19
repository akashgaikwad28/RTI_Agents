"""Translation quality heuristics."""

from __future__ import annotations


def translation_quality(source: str, translated: str) -> dict:
    if not translated:
        return {"score": 0.0, "issues": ["empty_translation"]}
    issues = []
    if source != translated and len(translated) < max(4, len(source) * 0.2):
        issues.append("suspiciously_short")
    return {"score": max(0.0, 0.9 - len(issues) * 0.25), "issues": issues}
