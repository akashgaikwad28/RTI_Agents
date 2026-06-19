"""Production AI guardrails for agent/tool inputs and outputs."""

from __future__ import annotations

import re

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"developer\s+mode",
    r"system\s+prompt",
    r"exfiltrate",
    r"disable\s+safety",
]


def detect_prompt_injection(text: str) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in INJECTION_PATTERNS if re.search(pattern, lowered)]


def guard_ai_input(text: str) -> dict:
    flags = detect_prompt_injection(text)
    return {"allowed": not flags, "flags": flags}

