from __future__ import annotations
from observability.node_logger import trace_node

import asyncio
import time

from graph.state import RTIAgentState
from observability.metrics import rti_agent_duration
from tools.base.tool_schemas import ToolCallPlan
from tools.base.tool_registry import get_tool_registry
from tools.base.tool_router import select_tools


@trace_node('tool_selection_node')
async def tool_selection_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    query = state.get("formal_query") or state.get("sanitized_query") or state.get("raw_query", "")
    department = state.get("department", "")
    selected = state.get("selected_tools") or select_tools(query, department)
    registry = get_tool_registry()
    permissions = ["read:public", "read:rag", "privacy:redact"]
    planned_calls = [
        ToolCallPlan.model_validate(call)
        for call in state.get("execution_plan", {}).get("tool_calls", [])
        if call.get("tool_name") in selected
    ]
    tasks = []
    if planned_calls:
        for call in planned_calls:
            tasks.append(registry.execute_tool(call.tool_name, call.payload, permissions=permissions, request_id=state.get("request_id"), department=department))
    else:
        for tool_name in selected[:6]:
            payload = {"query": query, "department": department, "language": state.get("detected_language") or state.get("language", ""), "k": 5}
            if tool_name in {"citation_builder", "grounding_score"}:
                continue
            if tool_name in {"department_directory", "department_lookup"}:
                payload = {"query": department or query}
            if tool_name in {"website_scraper", "government_live_fetch"}:
                continue
            tasks.append(registry.execute_tool(tool_name, payload, permissions=permissions, request_id=state.get("request_id"), department=department))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    serialized = [r.model_dump() if hasattr(r, "model_dump") else {"status": "error", "error": str(r)} for r in results]
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="tool_selection_node").observe(duration_ms / 1000)
    return {
        "selected_tools": selected,
        "tool_results": [*state.get("tool_results", []), *serialized],
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "tool_selection_node", "selected_tools": selected, "parallel_calls": len(tasks)}],
        "workflow_path": [*state.get("workflow_path", []), "tool_selection_node"],
        "agent_durations": {**state.get("agent_durations", {}), "tool_selection_node": duration_ms},
    }
