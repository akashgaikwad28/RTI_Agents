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
from observability.metrics import rti_agent_duration
from observability.llm_telemetry import track_llm_call
from pydantic import BaseModel
from multilingual.detection.mixed_language_detector import MixedLanguageDetector
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from multilingual.transliteration.transliterator import Transliterator

logger = get_logger(__name__)

ROUTER_SYSTEM_PROMPT = """You are an RTI (Right to Information) workflow router.

Analyze the user's input and classify the INTENT into exactly one category:

- "new_request"   : User wants to file a new RTI application or is asking for ANY government information, data, funds, or records.
- "status_check"  : User is explicitly asking about the status, update, or progress of a previously filed RTI application (e.g. "where is my application").
- "followup"      : User has a follow-up question or wants to modify a previous RTI.

If the user is asking a question about government funds, schemes, data, or policies, it is a "new_request"!

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

    # Security: use already-sanitized query from state (sanitized in api/routers/rti.py)
    sanitized = state.get("sanitized_query") or normalized_query

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
    # NOTE: rti_requests_total is incremented in api/routers/rti.py — not here to avoid double-counting
    # Track LLM cost
    track_llm_call(
        operation="router_node",
        provider="groq",
        model_name="llama-3.1-8b-instant",
        prompt_tokens=0,  # actual tokens not exposed by LangChain structured output here
        completion_tokens=0,
        latency_ms=duration_ms,
        success=True
    )

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
