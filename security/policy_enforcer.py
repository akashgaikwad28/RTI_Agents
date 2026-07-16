"""Department and RTI policy enforcement."""

from __future__ import annotations
from config.settings import settings


def enforce_department_policy(department: str, confidence: str, retrieval_confidence: float) -> dict:
    threshold = settings.RAG_SIMILARITY_THRESHOLD * 0.6  # Allow slightly lower confidence for escalation
    escalation_required = confidence == "low" or retrieval_confidence < threshold or department in {"", "Unknown Department"}
    return {
        "allowed": not escalation_required,
        "escalation_required": escalation_required,
        "reason": "department_or_retrieval_uncertain" if escalation_required else "policy_ok",
    }
