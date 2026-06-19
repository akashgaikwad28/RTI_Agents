"""Lineage tracking and supersession management."""

from __future__ import annotations

import uuid
from typing import Any

from rag.types import DocumentMetadata

class SupersessionTracker:
    @staticmethod
    def generate_lineage_id() -> str:
        """Generates a unique tracking ID for a new document lineage."""
        return f"lin_{uuid.uuid4().hex[:12]}"
        
    @staticmethod
    def link_versions(old_metadata: dict[str, Any], new_metadata: DocumentMetadata, reason: str = "Automated scrape update") -> None:
        """Links the new document as superseding the old document."""
        old_version = old_metadata.get("version", 1)
        new_metadata.version = old_version + 1
        
        # Link lineage
        lineage = old_metadata.get("lineage_id") or SupersessionTracker.generate_lineage_id()
        new_metadata.lineage_id = lineage
        
        # Link IDs
        old_id = old_metadata.get("document_id")
        if old_id:
            new_metadata.supersedes = old_id
            
        new_metadata.version_reason = reason
