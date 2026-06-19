"""Department and RTI policy enforcement."""

from __future__ import annotations


def enforce_department_policy(department: str, confidence: str, retrieval_confidence: float) -> dict:
    escalation_required = confidence == "low" or retrieval_confidence < 0.45 or department in {"", "Unknown Department"}
    return {
        "allowed": not escalation_required,
        "escalation_required": escalation_required,
        "reason": "department_or_retrieval_uncertain" if escalation_required else "policy_ok",
    }

