"""Fallback selection when primary tools fail."""

from __future__ import annotations


FALLBACKS = {
    "gazette_search": ["policy_search", "hybrid_search"],
    "budget_search": ["policy_search", "hybrid_search"],
    "government_website_search": ["government_live_fetch", "hybrid_search"],
}


def fallback_tools(tool_name: str) -> list[str]:
    return FALLBACKS.get(tool_name, [])
