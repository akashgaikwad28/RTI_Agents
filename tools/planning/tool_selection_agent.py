"""Autonomous tool selection agent."""

from __future__ import annotations

from tools.registry.tool_discovery import ToolDiscovery


class ToolSelectionAgent:
    def __init__(self):
        self.discovery = ToolDiscovery()

    async def select(self, query: str, department: str = "", permissions: list[str] | None = None, max_tools: int = 6) -> list[str]:
        tools = self.discovery.discover(query, department, permissions, max_tools)
        return [tool.name for tool in tools]
