"""
security/pii_masker.py
-----------------------
PII (Personally Identifiable Information) detection and masking.
Masks sensitive data before LLM calls and logging.
"""

import re
from observability.structured_logger import get_logger

logger = get_logger(__name__)

# ── PII Patterns ──────────────────────────────────────────────────
_PII_PATTERNS = [
    # Aadhaar number (12 digits)
    (r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[AADHAAR_MASKED]"),
    # PAN card (ABCDE1234F format)
    (r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[PAN_MASKED]"),
    # Phone numbers (Indian mobile)
    (r"\b(?:\+91|0)?[6-9]\d{9}\b", "[PHONE_MASKED]"),
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_MASKED]"),
    # Bank account numbers (basic pattern)
    (r"\b\d{9,18}\b", "[ACCOUNT_MASKED]"),
    # Credit/debit card numbers
    (r"\b(?:\d[ -]?){13,16}\b", "[CARD_MASKED]"),
]

_COMPILED_PII = [(re.compile(pattern), replacement) for pattern, replacement in _PII_PATTERNS]


def mask_pii(text: str) -> str:
    """
    Mask PII in text before logging or LLM calls.
    Returns text with PII replaced by placeholder tokens.
    """
    masked = text
    for pattern, replacement in _COMPILED_PII:
        masked = pattern.sub(replacement, masked)
    if masked != text:
        logger.info("[PIIMasker] PII detected and masked in text")
    return masked


def has_pii(text: str) -> bool:
    """Check if text contains detectable PII."""
    return any(pattern.search(text) for pattern, _ in _COMPILED_PII)
