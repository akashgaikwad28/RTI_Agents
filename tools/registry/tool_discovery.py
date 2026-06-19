"""Tool discovery facade used by planning agents."""

from __future__ import annotations

from tools.base.tool_registry import get_tool_registry
from tools.base.tool_schemas import ToolMetadata


class ToolDiscovery:
    def discover(self, query: str, department: str = "", permissions: list[str] | None = None, limit: int = 6) -> list[ToolMetadata]:
        return get_tool_registry().auto_select_tools(query, department, permissions=permissions, limit=limit)
