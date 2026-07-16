"""Aggregate AI evaluation runner."""

from __future__ import annotations

from evaluation.compliance_eval import rti_compliance_score
from evaluation.reasoning_eval import reasoning_completeness
from rag.evaluation.retrieval_metrics import context_relevance, grounding_score, hallucination_rate


def evaluate_workflow(state: dict) -> dict:
    contexts = state.get("retrieved_context", [])
    formal_query = state.get("formal_query", "")
    # Use actual retrieval metadata from the graph state instead of empty list
    retrieval_metadata = state.get("retrieval_metadata", [])
    return {
        "hallucination_rate": hallucination_rate(formal_query, contexts),
        "citation_grounding_score": grounding_score(formal_query, contexts),
        "context_relevance": context_relevance(retrieval_metadata),
        "reasoning_completeness": reasoning_completeness(state.get("reasoning_trace", [])),
        "compliance_score": rti_compliance_score(formal_query),
        "approval_success": state.get("approval_status") == "approved",
        "latency_ms": sum(state.get("agent_durations", {}).values()),
    }

