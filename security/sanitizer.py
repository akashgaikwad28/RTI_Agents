"""
security/sanitizer.py
----------------------
Input sanitization and prompt injection protection.
All user queries pass through this before any LLM call.
"""

import re
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from observability.structured_logger import get_logger
from config.settings import settings
from observability.telemetry import telemetry
from observability.telemetry_models import SecurityClassification

logger = get_logger(__name__)

# ── Known injection patterns ──────────────────────────────────────
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"system\s*:\s*",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\bprompt\s+injection\b",
    r"jailbreak",
    r"act as (DAN|an? AI without|a different AI)",
    r"disregard (your|the) (previous|system|original)",
    r"you are now",
    r"new persona",
    r"override (your|the) (instructions?|programming)",
    r"forget (everything|all|your training)",
    r"admin\s*override",
    r"--ignore",
    r"###\s*(system|instruction|override)",
    r"\[INST\]",
    r"<system>",
]

# ── SQL / NoSQL injection ─────────────────────────────────────────
SQL_PATTERNS = [
    r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b)",
    r"--\s*$",
    r";\s*$",
    r"\$where",
    r"\$ne",
    r"\$gt",
]

_COMPILED_INJECTION = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
_COMPILED_SQL = [re.compile(p, re.IGNORECASE) for p in SQL_PATTERNS]


def sanitize_query(query: str) -> str:
    """
    Sanitize user query:
    1. Enforce maximum length
    2. Strip HTML/script tags
    3. Remove known prompt injection patterns
    4. Remove SQL/NoSQL injection patterns
    5. Normalize whitespace

    Returns:
        Cleaned query string.

    Raises:
        ValueError if query is empty after sanitization.
    """
    if not query:
        raise ValueError("Query is empty.")

    query = UnicodeNormalizer().normalize(query)
    original = query

    # 1. Max length enforcement
    if len(query) > settings.MAX_QUERY_LENGTH:
        logger.warning(f"[Sanitizer] Query truncated from {len(query)} to {settings.MAX_QUERY_LENGTH} chars")
        query = query[:settings.MAX_QUERY_LENGTH]

    # 2. Strip HTML/script
    query = re.sub(r"<[^>]+>", " ", query)
    query = re.sub(r"&[a-zA-Z]+;", " ", query)

    # 3. Prompt injection removal
    for pattern in _COMPILED_INJECTION:
        if pattern.search(query):
            logger.warning(f"[Sanitizer] Injection pattern detected: {pattern.pattern[:40]}")
            telemetry.log_security_event(
                classification=SecurityClassification.PROMPT_INJECTION,
                event="prompt_injection_blocked",
                operation="sanitize_query",
                metadata={"pattern": pattern.pattern[:40]}
            )
            query = pattern.sub("[REMOVED]", query)

    # 4. SQL injection removal
    for pattern in _COMPILED_SQL:
        if pattern.search(query):
            logger.warning(f"[Sanitizer] SQL injection pattern detected: {pattern.pattern[:40]}")
            telemetry.log_security_event(
                classification=SecurityClassification.UNAUTHORIZED_ACCESS,
                event="sql_injection_blocked",
                operation="sanitize_query",
                metadata={"pattern": pattern.pattern[:40]}
            )
            query = pattern.sub("[REMOVED]", query)

    # 5. Normalize whitespace
    query = re.sub(r"\s+", " ", query).strip()

    if not query or query == "[REMOVED]":
        raise ValueError("Query was entirely composed of unsafe content.")

    if query != original:
        logger.info(f"[Sanitizer] Query modified during sanitization.")

    return query


def is_safe(query: str) -> tuple[bool, list[str]]:
    """
    Check query safety without modifying it.

    Returns:
        (is_safe: bool, detected_issues: list[str])
    """
    issues = []
    for pattern in _COMPILED_INJECTION:
        if pattern.search(query):
            issues.append(f"Prompt injection: {pattern.pattern[:30]}")
    for pattern in _COMPILED_SQL:
        if pattern.search(query):
            issues.append(f"SQL injection: {pattern.pattern[:30]}")
    if len(query) > settings.MAX_QUERY_LENGTH:
        issues.append(f"Query too long: {len(query)} chars")
    return (len(issues) == 0, issues)
