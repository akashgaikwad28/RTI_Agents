"""Simple dependency graph for tool execution plans."""

from __future__ import annotations

from tools.base.tool_schemas import ToolCallPlan


class DependencyGraph:
    def order(self, calls: list[ToolCallPlan]) -> list[ToolCallPlan]:
        remaining = {call.tool_name: call for call in calls}
        ordered: list[ToolCallPlan] = []
        while remaining:
            progressed = False
            done = {call.tool_name for call in ordered}
            for name, call in list(remaining.items()):
                if set(call.depends_on).issubset(done):
                    ordered.append(call)
                    remaining.pop(name)
                    progressed = True
            if not progressed:
                ordered.extend(remaining.values())
                break
        return ordered
