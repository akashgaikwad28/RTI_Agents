"""Planning agent for MCP-style tool execution."""

from __future__ import annotations

from tools.planning.execution_planner import ExecutionPlanner
from tools.planning.tool_selection_agent import ToolSelectionAgent


class PlanningAgent:
    def __init__(self):
        self.selector = ToolSelectionAgent()
        self.executor = ExecutionPlanner()

    async def plan(self, query: str, department: str = "", language: str = "en", permissions: list[str] | None = None, max_tools: int = 6) -> dict:
        selected = await self.selector.select(query, department, permissions, max_tools)
        calls = self.executor.build(query, selected, department, language)
        missing = []
        lowered = query.lower()
        if any(term in lowered for term in ["budget", "fund", "expenditure"]) and "budget_search" not in selected:
            missing.append("financial_data")
        confidence = 0.82 if calls else 0.35
        return {
            "execution_plan": {
                "strategy": "parallel_tool_execution_with_debate_validation",
                "missing_information": missing,
                "tool_calls": [call.model_dump() for call in calls],
                "confidence": confidence,
            },
            "selected_tools": selected,
            "reasoning_trace": [
                {
                    "agent": "planning_agent",
                    "decision": "selected_tools",
                    "selected_tools": selected,
                    "rationale": "Matched query intent, department, permissions, and available registry capabilities.",
                }
            ],
        }
