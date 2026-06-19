"""Converts selected tools into executable tool-call plans."""

from __future__ import annotations

from tools.base.tool_schemas import ToolCallPlan
from tools.planning.dependency_graph import DependencyGraph


class ExecutionPlanner:
    def build(self, query: str, selected_tools: list[str], department: str = "", language: str = "en") -> list[ToolCallPlan]:
        calls = []
        for tool_name in selected_tools:
            payload = {"query": query, "department": department, "language": language, "k": 5}
            if tool_name in {"department_directory", "department_lookup"}:
                payload = {"query": department or query}
            elif tool_name in {"website_scraper", "government_live_fetch"}:
                continue
            elif tool_name == "municipal_data":
                payload = {"query": query, "city": department if "municipal" in department.lower() else "", "topic": ""}
            calls.append(ToolCallPlan(tool_name=tool_name, payload=payload, reason=f"Selected to satisfy query capability via {tool_name}"))
        return DependencyGraph().order(calls)
