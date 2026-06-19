from __future__ import annotations
from observability.node_logger import trace_node

import time

from communication.event_bus import get_event_bus
from graph.state import RTIAgentState
from observability.metrics import agent_reasoning_events_total, rti_agent_duration
from tools.debate.debate_manager import DebateManager


@trace_node('debate_node')
async def debate_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    debate = DebateManager().run(state.get("tool_results", []), state.get("retrieval_citations", []))
    challenges = [issue["issue"] for issue in debate["critic"]["issues"]]
    debate["summary"] = "Critic, defender, and verifier agents completed tool-output debate."
    await get_event_bus().publish("debate.finished", debate, request_id=state.get("request_id"), node="debate_node")
    agent_reasoning_events_total.labels(agent="debate_node").inc()
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="debate_node").observe(duration_ms / 1000)
    return {
        "agent_debate": debate,
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "debate_node", "summary": debate["summary"], "challenges": challenges}],
        "workflow_path": [*state.get("workflow_path", []), "debate_node"],
        "agent_durations": {**state.get("agent_durations", {}), "debate_node": duration_ms},
    }
