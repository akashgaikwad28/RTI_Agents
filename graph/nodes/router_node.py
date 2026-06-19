from observability.node_logger import trace_node
"""
graph/nodes/router_node.py
--------------------------
RouterNode — the entry point of the LangGraph.
Detects intent from the user query using a fast LLM call
and sets the routing direction for the rest of the graph.
"""

import time
from graph.state import RTIAgentState
from llm_router.llm_router import get_llm
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import (
    rti_agent_duration,
    rti_requests_total,
)
from security.sanitizer import sanitize_query
from pydantic import BaseModel
from multilingual.detection.mixed_language_detector import MixedLanguageDetector
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from multilingual.transliteration.transliterator import Transliterator

logger = get_logger(__name__)

ROUTER_SYSTEM_PROMPT = """You are an RTI (Right to Information) workflow router.

Analyze the user's input and classify the INTENT into exactly one category:

- "new_request"   : User wants to file a new RTI application
- "status_check"  : User is asking about the status of an existing RTI
- "followup"      : User has a follow-up question or wants to modify a previous RTI

Respond ONLY with a valid JSON object:
{"intent": "<new_request|status_check|followup>", "reason": "<one sentence explanation>"}"""


class RouterOutput(BaseModel):
    intent: str
    reason: str


@trace_node('router_node')
async def router_node(state: RTIAgentState) -> dict:
    """
    Detects user intent and sets routing state.
    Uses fast Groq model for minimal latency.
    """
    start_time = time.time()
    logger.info(f"[RouterNode] Processing request_id={state.get('request_id')}")

    raw_query = state.get("raw_query", "")
    normalized_query = UnicodeNormalizer().normalize(raw_query)
    language_profile = MixedLanguageDetector().analyze(normalized_query)
    transliterated_query = ""
    if language_profile.get("needs_transliteration"):
        transliterated_query = Transliterator().transliterate(normalized_query, language=language_profile.get("language", "hi"))

    # Security: sanitize before any LLM call
    sanitized = sanitize_query(normalized_query)

    try:
        llm = get_llm(task="routing")  # Returns fast Groq model
        structured_llm = llm.with_structured_output(RouterOutput)

        result: RouterOutput = await structured_llm.ainvoke([
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Query: {sanitized}"},
        ])

        intent = result.intent
        reason = result.reason

    except Exception as e:
        logger.error(f"[RouterNode] LLM call failed: {e}. Defaulting to new_request.")
        intent = "new_request"
        reason = "Defaulted due to LLM error"

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="router_node").observe(duration_ms / 1000)
    rti_requests_total.labels(intent=intent).inc()

    workflow_path = list(state.get("workflow_path", [])) + ["router_node"]

    logger.info(f"[RouterNode] Intent={intent} | Reason={reason} | {duration_ms:.0f}ms")

    return {
        "intent": intent,
        "next_agent": "formatter_node" if intent != "status_check" else "tracker_node",
        "sanitized_query": sanitized,
        "normalized_query": normalized_query,
        "detected_language": language_profile.get("language", "unknown"),
        "detected_script": language_profile.get("script", "unknown"),
        "mixed_language": language_profile.get("mixed_language", False),
        "language_confidence": language_profile.get("confidence", 0.0),
        "transliterated_query": transliterated_query,
        "response_language": state.get("response_language") or state.get("language") or language_profile.get("language", "en"),
        "multilingual_context": {**state.get("multilingual_context", {}), "language_profile": language_profile},
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "router_node": duration_ms},
        "llm_models_used": {**state.get("llm_models_used", {}), "router_node": "llama-3.1-8b-instant"},
    }
