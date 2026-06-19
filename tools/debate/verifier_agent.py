"""Verifier agent for cross-checking source credibility."""

from __future__ import annotations


class VerifierAgent:
    def verify(self, tool_results: list[dict], rag_citations: list[str] | None = None) -> dict:
        official = []
        for result in tool_results:
            official.extend(result.get("validation", {}).get("citation_check", {}).get("official_sources", []))
        return {
            "role": "verifier",
            "official_sources": official[:20],
            "rag_citation_count": len(rag_citations or []),
            "passed": bool(official or rag_citations),
            "confidence": 0.8 if official else 0.55 if rag_citations else 0.35,
        }
