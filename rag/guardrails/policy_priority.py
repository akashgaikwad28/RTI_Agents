"""Policy priority engine for conflict resolution."""

from __future__ import annotations

from rag.types import DocumentMetadata

class PolicyPriority:
    PRIORITY_WEIGHTS = {
        "gazette": 1.0,
        "circular": 0.8,
        "memo": 0.6,
        "notice": 0.4,
        "unknown": 0.2
    }

    @staticmethod
    def get_priority_score(metadata: DocumentMetadata) -> float:
        """Calculates policy authority score based on document type."""
        doc_type = (metadata.document_type or "").lower()
        
        if "gazette" in doc_type:
            return PolicyPriority.PRIORITY_WEIGHTS["gazette"]
        if "circular" in doc_type:
            return PolicyPriority.PRIORITY_WEIGHTS["circular"]
        if "memo" in doc_type:
            return PolicyPriority.PRIORITY_WEIGHTS["memo"]
        if "notice" in doc_type:
            return PolicyPriority.PRIORITY_WEIGHTS["notice"]
            
        return PolicyPriority.PRIORITY_WEIGHTS["unknown"]
