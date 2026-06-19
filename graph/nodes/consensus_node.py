from __future__ import annotations
from observability.node_logger import trace_node

import time

from graph.state import RTIAgentState
from observability.metrics import rti_agent_duration
from security.escalation_rules import should_escalate


@trace_node('consensus_node')
async def consensus_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    review_score = state.get("review_score", 0.0)
    retrieval_confidence = state.get("retrieval_confidence", 0.0)
    grounding = state.get("grounding_score", 0.0)
    debate_consensus = state.get("agent_debate", {}).get("consensus", {})
    debate_truth = debate_consensus.get("truth_score", 0.0)
    confidence = round((review_score * 0.25) + (retrieval_confidence * 0.3) + (grounding * 0.2) + (debate_truth * 0.25), 4)
    missing_citations = 0 if state.get("retrieval_citations") else 1
    risk = min(1.0, (1 - confidence) + missing_citations * 0.15 + len(state.get("hallucination_flags", [])) * 0.12)
    escalation = should_escalate(risk_score=risk, hallucination_flags=state.get("hallucination_flags", []), approval_status=state.get("approval_status", ""))
    decision = {
        "confidence": confidence,
        "risk_score": round(risk, 4),
        "escalation_required": escalation,
        "recommended_action": "human_review" if escalation else "approve_for_human_queue",
        "tool_truth_score": debate_truth,
    }
    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="consensus_node").observe(duration_ms / 1000)
    return {
        "consensus_result": decision,
        "final_ai_decision": decision,
        "ai_risk_score": decision["risk_score"],
        "escalation_required": escalation,
        "governance_notes": [*state.get("governance_notes", []), f"Consensus action: {decision['recommended_action']}"],
        "reasoning_trace": [*state.get("reasoning_trace", []), {"node": "consensus_node", **decision}],
        "workflow_path": [*state.get("workflow_path", []), "consensus_node"],
        "agent_durations": {**state.get("agent_durations", {}), "consensus_node": duration_ms},
    }
