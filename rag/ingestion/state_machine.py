"""Formal state machine for the document ingestion lifecycle."""

from __future__ import annotations

from enum import Enum
from typing import Any

class IngestionState(str, Enum):
    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    PARSED = "PARSED"
    OCR_COMPLETE = "OCR_COMPLETE"
    CHUNKED = "CHUNKED"
    EMBEDDED = "EMBEDDED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"

class IngestionLifecycle:
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.state: IngestionState = IngestionState.DISCOVERED
        self.history: list[dict[str, Any]] = []
        
    def transition(self, new_state: IngestionState, reason: str = "") -> None:
        """Transitions to a new state and records the history."""
        import time
        self.state = new_state
        self.history.append({
            "state": new_state.value,
            "timestamp": time.time(),
            "reason": reason
        })
