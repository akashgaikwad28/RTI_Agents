from __future__ import annotations
from observability.node_logger import trace_node

import time

from graph.state import RTIAgentState
from observability.metrics import rti_agent_duration


@trace_node('critic_node')
async def critic_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    citations = state.get("retrieval_citations", [])
    scores = state.get("retrieval_scores", [])
    issues = []
    if not citations:
        issues.append("No citations available for reviewer.")
    if scores and max(scores) < 0.55:
        issues.append("Low top retrieval score.")
    if state.get("confidence") == "low":
        issues.append("Department classification confidence is low.")
    feedback = {"issues": issues, "severity": "high" if len(issues) > 1 else "medium" if issues else "low"}
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="critic_node").observe(duration_ms / 1000)
    return {
        "critic_feedback": feedback,
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "critic_node", **feedback}],
        "workflow_path": [*state.get("workflow_path", []), "critic_node"],
        "agent_durations": {**state.get("agent_durations", {}), "critic_node": duration_ms},
    }

