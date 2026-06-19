from observability.node_logger import trace_node
"""
graph/nodes/classifier_node.py
-------------------------------
ClassifierNode — predicts the target government department
using Gemini Pro with structured output.
Falls back to Groq if Gemini fails.
"""

import time
from pydantic import BaseModel
from graph.state import RTIAgentState
from llm_router.llm_router import get_llm
from tools.department_lookup import get_valid_departments
from prompts.classifier import build_classifier_prompt
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration, rti_classification_confidence

logger = get_logger(__name__)


class ClassificationOutput(BaseModel):
    department: str
    sub_department: str = ""
    confidence: str          # "high" | "medium" | "low"
    notes: str = ""


@trace_node('classifier_node')
async def classifier_node(state: RTIAgentState) -> dict:
    """
    Identifies the government department for RTI routing.
    Uses structured output to guarantee valid JSON schema.
    Validates department name against known department list.
    """
    start_time = time.time()
    request_id = state.get("request_id")
    logger.info(f"[ClassifierNode] start | request_id={request_id}")

    formal_query = state.get("formal_query", state.get("sanitized_query", ""))

    # ── Load valid departments ─────────────────────────────────────
    valid_departments = get_valid_departments()
    dept_list_str = "\n".join(f"- {d}" for d in valid_departments)

    prompt = build_classifier_prompt(
        query=formal_query,
        valid_departments=dept_list_str,
    )

    # ── Primary: Gemini Pro (better reasoning) ────────────────────
    department = "Unknown Department"
    sub_department = ""
    confidence = "low"
    notes = ""
    model_used = "unknown"

    try:
        llm = get_llm(task="classification")  # Gemini Pro
        structured_llm = llm.with_structured_output(ClassificationOutput)
        result: ClassificationOutput = await structured_llm.ainvoke([
            {"role": "user", "content": f"{prompt['system']}\n\n{prompt['user']}"},
        ])
        department = result.department
        sub_department = result.sub_department
        confidence = result.confidence
        notes = result.notes
        model_used = "gemini-1.5-pro"

    except Exception as e:
        err_str = str(e).lower()
        is_quota_429 = "429" in err_str or "quota" in err_str or "rate limit" in err_str
        if is_quota_429:
            logger.warning(f"[ClassifierNode] Gemini rate-limited (429); falling back to Groq immediately. Error: {e}")
        else:
            logger.warning(f"[ClassifierNode] Gemini failed: {e}. Trying Groq fallback...")

        try:
            llm_fallback = get_llm(task="classification_fallback")  # Groq fallback
            structured_llm = llm_fallback.with_structured_output(ClassificationOutput)
            result: ClassificationOutput = await structured_llm.ainvoke([
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ])
            department = result.department
            sub_department = result.sub_department
            confidence = result.confidence
            notes = result.notes
            model_used = "llama-3.3-70b-versatile"
        except Exception as e2:
            logger.error(f"[ClassifierNode] Both LLMs failed: {e2}")


    # ── Validate department ────────────────────────────────────────
    if department not in valid_departments:
        logger.warning(f"[ClassifierNode] Dept '{department}' not in valid list. Keeping anyway.")

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="classifier_node").observe(duration_ms / 1000)
    rti_classification_confidence.labels(confidence=confidence).inc()

    workflow_path = list(state.get("workflow_path", [])) + ["classifier_node"]

    logger.info(
        f"[ClassifierNode] done | dept={department} | "
        f"confidence={confidence} | {duration_ms:.0f}ms"
    )

    return {
        "department": department,
        "sub_department": sub_department,
        "confidence": confidence,
        "classification_notes": notes,
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "classifier_node": duration_ms},
        "llm_models_used": {**state.get("llm_models_used", {}), "classifier_node": model_used},
        "tools_used": [*state.get("tools_used", []), "department_lookup"],
    }
