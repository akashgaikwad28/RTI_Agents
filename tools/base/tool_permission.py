"""Permission model for read-only government tool execution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPermissionDecision:
    allowed: bool
    reason: str = ""


class ToolPermission:
    READ_PUBLIC = "read:public"
    READ_RAG = "read:rag"
    NETWORK_GOV = "network:gov"
    PRIVACY_REDACT = "privacy:redact"
    BENCHMARK = "tool:benchmark"


class ToolPermissionChecker:
    def check(self, required: list[str], granted: list[str]) -> ToolPermissionDecision:
        missing = sorted(set(required) - set(granted))
        if missing:
            return ToolPermissionDecision(False, f"Missing permissions: {', '.join(missing)}")
        return ToolPermissionDecision(True)
