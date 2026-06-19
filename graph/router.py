"""Conditional edge functions for the LangGraph StateGraph."""

from graph.state import RTIAgentState
from observability.structured_logger import get_logger

logger = get_logger(__name__)


def route_after_router(state: RTIAgentState) -> str:
    intent = state.get("intent", "new_request")
    logger.info(f"[Router] Intent detected: {intent}")
    if intent == "status_check":
        return "tracker_node"
    return "planner_node"


def route_after_reviewer(state: RTIAgentState) -> str:
    review_passed = state.get("review_passed", False)
    confidence = state.get("confidence", "low")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    logger.info(f"[Router] Review passed={review_passed}, confidence={confidence}, retries={retry_count}/{max_retries}")
    if retry_count >= max_retries:
        return "approval_node"
    if review_passed and confidence in ("high", "medium"):
        return "approval_node"
    return "reflection_node"


def route_after_approval(state: RTIAgentState) -> str:
    approval_status = state.get("approval_status", "pending")
    logger.info(f"[Router] Approval status: {approval_status}")
    if approval_status == "rejected":
        return "reflection_node"
    elif approval_status == "approved":
        return "consensus_node"
    # If still pending (e.g. during astream_events re-entry), loop back to approval_node to trigger interrupt
    return "approval_node"


def route_after_reflection(state: RTIAgentState) -> str:
    reflection_needed = state.get("reflection_needed", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    logger.info(f"[Router] Reflection needed={reflection_needed}, retries={retry_count}/{max_retries}")
    if reflection_needed and retry_count < max_retries:
        return "formatter_node"
    return "tracker_node"


def route_after_consensus(state: RTIAgentState) -> str:
    return "memory_learning_node"


def route_after_info_fetcher(state: RTIAgentState) -> str:
    info_available = state.get("info_available", False)
    logger.info(f"[Router] info_available={info_available}")
    if info_available:
        return "tracker_node"
    return "classifier_node"


