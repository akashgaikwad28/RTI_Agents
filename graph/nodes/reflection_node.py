from observability.node_logger import trace_node
"""
graph/nodes/reflection_node.py
-------------------------------
ReflectionNode — autonomous self-correction agent.
Analyzes review_feedback and decides how to improve
the RTI draft in the next retry attempt.
Increments retry_count and amends the sanitized_query
with targeted improvement instructions.
"""

import time
from pydantic import BaseModel
from graph.state import RTIAgentState
from llm_router.llm_router import get_llm
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration, rti_retry_total

logger = get_logger(__name__)

REFLECTION_SYSTEM_PROMPT = """You are a self-reflection AI agent for an RTI (Right to Information) system.

You receive:
1. The original user query
2. The drafted RTI application that was REJECTED
3. The reviewer's feedback explaining why it failed
4. The hallucination flags (if any)

Your task is to produce an IMPROVED query instruction for the Formatter Agent.
Analyze what went wrong and produce a targeted correction instruction.

Respond with valid JSON only:
{
  "reflection_needed": true|false,
  "amended_query": "<enhanced query instruction for the formatter>",
  "correction_summary": "<what was wrong and what needs fixing>",
  "specific_additions": ["list of specific facts/details that must be added"],
  "tone_corrections": ["tone/language issues to fix"]
}"""


class ReflectionOutput(BaseModel):
    reflection_needed: bool
    amended_query: str
    correction_summary: str
    specific_additions: list[str] = []
    tone_corrections: list[str] = []


@trace_node('reflection_node')
async def reflection_node(state: RTIAgentState) -> dict:
    """
    Self-correction: analyzes why review failed and
    prepares an improved instruction set for the next
    formatter run.
    """
    start_time = time.time()
    request_id = state.get("request_id")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    logger.info(f"[ReflectionNode] start | request_id={request_id} | retry {retry_count}/{max_retries}")

    raw_query = state.get("raw_query", "")
    formal_query = state.get("formal_query", "")
    review_feedback = state.get("review_feedback", "No feedback provided.")
    hallucination_flags = state.get("hallucination_flags", [])
    approval_status = state.get("approval_status", "")

    # Build context for reflection
    flags_str = "\n".join(f"- {f}" for f in hallucination_flags) or "None"
    rejection_reason = (
        f"HUMAN REJECTED: {approval_status}"
        if approval_status == "rejected"
        else f"REVIEW FAILED: {review_feedback}"
    )

    user_message = (
        f"ORIGINAL QUERY: {raw_query}\n\n"
        f"DRAFTED RTI (REJECTED):\n{formal_query}\n\n"
        f"REJECTION REASON:\n{rejection_reason}\n\n"
        f"HALLUCINATION FLAGS:\n{flags_str}"
    )

    # ── Self-reflection LLM call ───────────────────────────────────
    reflection_needed = True
    amended_query = raw_query  # fallback to original
    correction_summary = "Retrying with original query."

    try:
        llm = get_llm(task="reflection")  # Groq 70B
        structured_llm = llm.with_structured_output(ReflectionOutput)
        result: ReflectionOutput = await structured_llm.ainvoke([
            {"role": "system", "content": REFLECTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ])
        reflection_needed = result.reflection_needed
        amended_query = result.amended_query
        correction_summary = result.correction_summary

        logger.info(f"[ReflectionNode] Correction: {correction_summary[:100]}")

    except Exception as e:
        logger.error(f"[ReflectionNode] LLM failed: {e}")

    # Increment retry counter
    new_retry_count = retry_count + 1
    rti_retry_total.labels(agent="reflection_node").inc()

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="reflection_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + [f"reflection_node:retry_{new_retry_count}"]

    logger.info(
        f"[ReflectionNode] done | retry={new_retry_count} | "
        f"will_retry={reflection_needed and new_retry_count < max_retries} | {duration_ms:.0f}ms"
    )

    return {
        "reflection_needed": reflection_needed,
        "reflection_reason": correction_summary,
        "retry_count": new_retry_count,
        # Override sanitized_query so FormatterNode gets improved instructions
        "sanitized_query": amended_query,
        # Reset approval status so it can go through approval again
        "approval_status": "pending",
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "reflection_node": duration_ms},
        "llm_models_used": {**state.get("llm_models_used", {}), "reflection_node": "llama-3.3-70b-versatile"},
    }
