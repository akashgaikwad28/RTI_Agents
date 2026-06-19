from __future__ import annotations
from observability.node_logger import trace_node

import time

from communication.event_bus import get_event_bus
from graph.state import RTIAgentState
from memory.learning.adaptive_memory import AdaptiveMemory
from mcp_clients.mongo_client import get_mongo_client
from observability.metrics import rti_agent_duration
from tools.memory.tool_memory import ToolMemory


@trace_node('memory_learning_node')
async def memory_learning_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    try:
        mongo = await get_mongo_client()
        result = await AdaptiveMemory().learn_from_state(mongo.db, dict(state))
        tool_result = await ToolMemory().record_workflow(
            mongo.db,
            state.get("request_id"),
            state.get("execution_plan", {}),
            state.get("tool_results", []),
            state.get("consensus_result", {}),
        )
        result = {**result, "tool_memory": tool_result}
    except Exception as exc:
        result = {"stored": False, "reason": str(exc)}
    await get_event_bus().publish("memory.learned", result, request_id=state.get("request_id"), node="memory_learning_node")
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="memory_learning_node").observe(duration_ms / 1000)
    return {
        "learning_feedback": result,
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "memory_learning_node", **result}],
        "workflow_path": [*state.get("workflow_path", []), "memory_learning_node"],
        "agent_durations": {**state.get("agent_durations", {}), "memory_learning_node": duration_ms},
    }
