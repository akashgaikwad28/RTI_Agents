"""Mandatory human escalation rules for governance workflows."""

from __future__ import annotations


def should_escalate(*, risk_score: float, hallucination_flags: list[str], approval_status: str = "") -> bool:
    return risk_score >= 0.55 or bool(hallucination_flags) or approval_status == "rejected"

