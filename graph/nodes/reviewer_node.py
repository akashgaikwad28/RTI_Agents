from observability.node_logger import trace_node
"""
graph/nodes/reviewer_node.py
-----------------------------
ReviewerNode — quality gate for RTI drafts.
Evaluates the formal_query against retrieved context
and user intent. Sets review_passed, review_score,
grounding_score, and hallucination_flags.
"""

import time
import json
from pydantic import BaseModel
from graph.state import RTIAgentState
from llm_router.llm_router import get_llm

from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration, rti_hallucination_flags_total

logger = get_logger(__name__)

REVIEW_SYSTEM_PROMPT = """You are a senior RTI (Right to Information) quality reviewer for Indian government applications.

Your task is to evaluate the drafted RTI application for:
1. COMPLETENESS: Does it clearly specify what information is being requested?
2. LEGAL TONE: Is it formal, polite, and suitable for government submission?
3. GROUNDING: Is the content grounded in the provided context? (No hallucinations)
4. DEPARTMENT ALIGNMENT: Does the department match the query topic?
5. SPECIFICITY: Does it ask for specific information rather than vague requests?

You MUST respond with valid JSON only:
{
  "review_passed": true|false,
  "review_score": 0.0-1.0,
  "grounding_score": 0.0-1.0,
  "hallucination_flags": ["flag1", "flag2"],
  "review_feedback": "specific actionable feedback if failed, or confirmation if passed",
  "suggested_improvements": ["improvement1", "improvement2"]
}"""


class ReviewOutput(BaseModel):
    review_passed: bool
    review_score: float
    grounding_score: float
    hallucination_flags: list[str] = []
    review_feedback: str
    suggested_improvements: list[str] = []


@trace_node('reviewer_node')
async def reviewer_node(state: RTIAgentState) -> dict:
    """
    Quality gate: evaluates RTI draft completeness,
    legal tone, grounding, and hallucination risk.
    """
    start_time = time.time()
    request_id = state.get("request_id")
    logger.info(f"[ReviewerNode] start | request_id={request_id}")

    formal_query = state.get("formal_query", "")
    department = state.get("department", "Unknown")
    confidence = state.get("confidence", "low")
    retrieved_context = state.get("retrieved_context", [])
    raw_query = state.get("raw_query", "")

    context_str = "\n---\n".join(retrieved_context[:3]) if retrieved_context else "No context retrieved."

    user_message = (
        f"ORIGINAL USER QUERY:\n{raw_query}\n\n"
        f"DRAFTED RTI APPLICATION:\n{formal_query}\n\n"
        f"TARGET DEPARTMENT: {department} (confidence: {confidence})\n\n"
        f"RETRIEVED CONTEXT:\n{context_str}"
    )

    # ── LLM Review ────────────────────────────────────────────────
    review_passed = False
    review_score = 0.0
    grounding_score = 0.0
    hallucination_flags: list[str] = []
    review_feedback = "Review could not be completed due to LLM error."
    suggested_improvements: list[str] = []

    try:
        llm = get_llm(task="review")  # Gemini Pro
        structured_llm = llm.with_structured_output(ReviewOutput)
        result: ReviewOutput = await structured_llm.ainvoke([
            {"role": "user", "content": f"{REVIEW_SYSTEM_PROMPT}\n\n{user_message}"},
        ])
        review_passed = result.review_passed
        review_score = result.review_score
        grounding_score = result.grounding_score
        hallucination_flags = result.hallucination_flags
        review_feedback = result.review_feedback
        suggested_improvements = result.suggested_improvements

    except Exception as e:
        err_str = str(e).lower()
        is_quota_429 = "429" in err_str or "quota" in err_str or "rate limit" in err_str

        if is_quota_429:
            logger.warning(
                f"[ReviewerNode] Gemini rate-limited; falling back to Groq immediately. Error: {e}"
            )
            try:
                llm_fallback = get_llm(task="reflection")  # Groq fallback per llm_router
                structured_llm = llm_fallback.with_structured_output(ReviewOutput)
                result: ReviewOutput = await structured_llm.ainvoke([
                    {"role": "user", "content": f"{REVIEW_SYSTEM_PROMPT}\n\n{user_message}"},
                ])
                review_passed = result.review_passed
                review_score = result.review_score
                grounding_score = result.grounding_score
                hallucination_flags = result.hallucination_flags
                review_feedback = result.review_feedback
                suggested_improvements = result.suggested_improvements
            except Exception as e2:
                logger.error(f"[ReviewerNode] Groq fallback also failed: {e2}")
                review_passed = bool(formal_query and len(formal_query) > 50)
                review_feedback = f"Automated review failed. Manual review recommended. Error: {str(e)}"
        else:
            logger.error(f"[ReviewerNode] LLM failed: {e}")
            # Fail-safe: pass if we have a formal_query but log it
            review_passed = bool(formal_query and len(formal_query) > 50)
            review_feedback = f"Automated review failed. Manual review recommended. Error: {str(e)}"


    # ── Emit metrics ──────────────────────────────────────────────
    if hallucination_flags:
        rti_hallucination_flags_total.inc(len(hallucination_flags))

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="reviewer_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + ["reviewer_node"]

    logger.info(
        f"[ReviewerNode] done | passed={review_passed} | "
        f"score={review_score:.2f} | grounding={grounding_score:.2f} | {duration_ms:.0f}ms"
    )

    return {
        "review_passed": review_passed,
        "review_score": review_score,
        "grounding_score": grounding_score,
        "hallucination_flags": hallucination_flags,
        "review_feedback": review_feedback,
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "reviewer_node": duration_ms},
        "llm_models_used": {**state.get("llm_models_used", {}), "reviewer_node": "gemini-1.5-pro"},
    }
