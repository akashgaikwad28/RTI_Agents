"""Tool accuracy scoring."""

from __future__ import annotations


def accuracy_score(results: list[dict]) -> float:
    if not results:
        return 0.0
    valid = [r for r in results if r.get("validation", {}).get("valid") or r.get("status") == "success"]
    return round(len(valid) / len(results), 4)
