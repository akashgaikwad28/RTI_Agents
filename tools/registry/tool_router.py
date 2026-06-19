"""Capability-aware tool routing."""

from __future__ import annotations

from tools.base.tool_registry import get_tool_registry


class ToolRouter:
    def route(self, query: str, department: str = "", permissions: list[str] | None = None) -> list[str]:
        tools = get_tool_registry().auto_select_tools(query, department, permissions=permissions)
        return [tool.name for tool in tools]
