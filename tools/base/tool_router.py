"""Select tools from a query, department, and requested capabilities."""

from __future__ import annotations

from tools.base.tool_registry import get_tool_registry


def select_tools(query: str, department: str = "") -> list[str]:
    registry = get_tool_registry()
    permissions = ["read:public", "read:rag", "network:gov", "privacy:redact"]
    dynamic = [tool.name for tool in registry.auto_select_tools(query, department, permissions=permissions, limit=8)]
    baseline = ["hybrid_search", "citation_builder", "grounding_score"]
    return [name for name in dict.fromkeys([*dynamic, *baseline]) if name in {tool.name for tool in registry.list_tools(permissions=permissions)}]
