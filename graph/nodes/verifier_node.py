from __future__ import annotations
from observability.node_logger import trace_node

import time

from graph.state import RTIAgentState
from observability.metrics import rti_agent_duration
from security.policy_enforcer import enforce_department_policy


@trace_node('verifier_node')
async def verifier_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    citations = state.get("retrieval_citations", [])
    policy = enforce_department_policy(state.get("department", ""), state.get("confidence", "low"), state.get("retrieval_confidence", 0.0))
    report = {
        "citations_verified": bool(citations),
        "citation_count": len(citations),
        "department_policy": policy,
        "grounding_score": state.get("grounding_score", 0.0),
        "passed": bool(citations) and not policy["escalation_required"],
    }
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="verifier_node").observe(duration_ms / 1000)
    return {
        "verification_report": report,
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "verifier_node", **report}],
        "workflow_path": [*state.get("workflow_path", []), "verifier_node"],
        "agent_durations": {**state.get("agent_durations", {}), "verifier_node": duration_ms},
    }

