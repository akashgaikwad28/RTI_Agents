"""Defender agent for justifying successful retrievals."""

from __future__ import annotations


class DefenderAgent:
    def defend(self, tool_results: list[dict]) -> dict:
        successes = [result for result in tool_results if result.get("status") == "success"]
        citations = sum((result.get("validation", {}).get("citation_check", {}).get("citations_found", 0) for result in successes), 0)
        return {"role": "defender", "successful_tools": [r.get("tool_name") for r in successes], "citations": citations, "confidence": min(0.95, 0.5 + citations * 0.08 + len(successes) * 0.05)}
