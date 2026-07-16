"""Production AI guardrails for agent/tool inputs and outputs."""

from __future__ import annotations

import re
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

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


def _log_security_violation(flags: list[str], engine: str, text: str):
    """Log security violations to structured log + Prometheus counter."""
    try:
        from observability.metrics import rti_security_events_total
        from observability.telemetry import telemetry
        from observability.telemetry_models import SecurityClassification, Outcome, LogLevel

        rti_security_events_total.labels(classification="prompt_injection").inc(len(flags))
        telemetry.log_security_event(
            classification=SecurityClassification.INJECTION,
            event="prompt_injection_detected",
            operation="guardrail_check",
            metadata={"flags": flags, "engine": engine, "query_preview": text[:100]},
            outcome=Outcome.FAILURE,
            level=LogLevel.WARNING,
        )
    except Exception as log_err:
        logger.warning(f"[SecurityGuard] Failed to log security event: {log_err}")


async def aguard_ai_input(text: str) -> dict:
    """Async security check using Llama Guard (if enabled) + Regex fallback."""
    flags = detect_prompt_injection(text)

    if flags:
        _log_security_violation(flags, "regex", text)

    if not settings.ENABLE_SECURITY_GUARDRAILS or not settings.GROQ_API_KEY:
        return {"allowed": not flags, "flags": flags, "engine": "regex"}

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage

        guard = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLAMA_GUARD_MODEL,
            temperature=0.0,
            max_retries=1
        )

        response = await guard.ainvoke([HumanMessage(content=text)])
        output = response.content.strip().lower()

        if output.startswith("unsafe"):
            # Llama guard returns "unsafe\n[category]"
            category = output.split("\n")[1] if "\n" in output else "prompt_injection"
            flags.append(f"llama_guard:{category}")
            _log_security_violation([f"llama_guard:{category}"], "llama-guard-3-8b", text)

        return {"allowed": not flags, "flags": flags, "engine": "llama-guard-3-8b"}

    except Exception as e:
        logger.warning(f"[SecurityGuard] Llama Guard failed, falling back to regex: {e}")
        return {"allowed": not flags, "flags": flags, "engine": "regex_fallback"}


def guard_ai_input(text: str) -> dict:
    """Sync version — always uses regex only to avoid blocking async event loops."""
    flags = detect_prompt_injection(text)
    if flags:
        _log_security_violation(flags, "regex", text)
    return {"allowed": not flags, "flags": flags, "engine": "regex"}


