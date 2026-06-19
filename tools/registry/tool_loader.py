"""Dynamic tool loader.

The project uses explicit registration for reliability, but this loader can
register imported tool instances for extension packages.
"""

from __future__ import annotations

from tools.base.base_tool import BaseTool
from tools.base.tool_registry import ToolRegistry


class ToolLoader:
    def load(self, registry: ToolRegistry, tools: list[BaseTool]) -> None:
        for tool in tools:
            registry.register_tool(tool)
