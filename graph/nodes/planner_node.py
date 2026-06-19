from __future__ import annotations
from observability.node_logger import trace_node

import time

from communication.event_bus import get_event_bus
from graph.state import RTIAgentState
from observability.metrics import agent_reasoning_events_total, rti_agent_duration
from tools.planning.planning_agent import PlanningAgent


@trace_node('planner_node')
async def planner_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    query = state.get("sanitized_query") or state.get("raw_query", "")
    department = state.get("department", "")
    planning = await PlanningAgent().plan(
        query,
        department=department,
        language=state.get("language", "en"),
        permissions=["read:public", "read:rag", "network:gov", "privacy:redact"],
    )
    plan = planning["execution_plan"] | {
        "subtasks": ["format_rti", "classify_department", "tool_execution", "retrieve_evidence", "debate_quality", "verify_citations", "human_governance"],
        "retrieval_strategy": "hybrid_plus_live_government_tools",
        "debate_required": True,
    }
    selected = planning["selected_tools"]
    trace = {**plan, "node": "planner_node", "rationale": "Dynamic registry selected tools using query intent, department, permissions, and capabilities."}
    await get_event_bus().publish("node.finished", trace, request_id=state.get("request_id"), node="planner_node")
    agent_reasoning_events_total.labels(agent="planner_node").inc()
    duration_ms = (time.perf_counter() - started) * 1000
    return {
        "execution_plan": plan,
        "selected_tools": selected,
        "reasoning_trace": [*state.get("reasoning_trace", []), *planning["reasoning_trace"], trace],
        "workflow_path": [*state.get("workflow_path", []), "planner_node"],
        "agent_durations": {**state.get("agent_durations", {}), "planner_node": duration_ms},
    }
