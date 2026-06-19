"""
observability/pii_redactor.py
------------------------------
Middleware logic to detect and redact Personally Identifiable Information (PII)
such as emails, phone numbers, Aadhaar, and PAN cards before logs are written.
"""

import re
from typing import Any, Dict, Union

# ── PII Patterns ──────────────────────────────────────────────────
# Note: These are heuristic patterns for log redaction.
PII_PATTERNS = {
    "EMAIL": re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
    "PHONE": re.compile(r'(?:\+91|0)?[ -]?[6-9]\d{9}'),
    "AADHAAR": re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b'),
    "PAN": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
}

REDACTION_STRING = "[REDACTED]"

def redact_string(text: str) -> str:
    """Redacts PII from a single string."""
    if not isinstance(text, str):
        return text
    
    redacted_text = text
    for pii_type, pattern in PII_PATTERNS.items():
        redacted_text = pattern.sub(f"[{pii_type}_REDACTED]", redacted_text)
    return redacted_text

def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redacts PII from dictionaries."""
    redacted_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted_data[key] = redact_string(value)
        elif isinstance(value, dict):
            redacted_data[key] = redact_dict(value)
        elif isinstance(value, list):
            redacted_data[key] = [
                redact_dict(item) if isinstance(item, dict) else 
                redact_string(item) if isinstance(item, str) else item 
                for item in value
            ]
        else:
            redacted_data[key] = value
    return redacted_data

def redact_log_record(record: dict) -> dict:
    """Main entry point for log formatter PII scrubbing."""
    return redact_dict(record)
