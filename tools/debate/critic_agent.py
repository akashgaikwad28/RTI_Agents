"""Critic agent for challenging tool outputs."""

from __future__ import annotations


class CriticAgent:
    def critique(self, tool_results: list[dict]) -> dict:
        issues = []
        for result in tool_results:
            if result.get("status") != "success":
                issues.append({"tool": result.get("tool_name"), "issue": result.get("error") or result.get("status")})
            if result.get("confidence", 0) < 0.45:
                issues.append({"tool": result.get("tool_name"), "issue": "low_confidence"})
        return {"role": "critic", "issues": issues, "confidence": max(0.2, 1 - 0.12 * len(issues))}
