"""Applies versioning metadata to incoming documents."""

from __future__ import annotations

import uuid
from typing import Any

from rag.types import DocumentMetadata
from rag.versioning.diff_detector import DiffDetector
from rag.versioning.supersession_tracker import SupersessionTracker

def assign_initial_version(metadata: DocumentMetadata) -> None:
    """Assigns initial versioning fields to a completely new document."""
    metadata.document_id = f"doc_{uuid.uuid4().hex[:12]}"
    metadata.version = 1
    metadata.is_latest = True
    metadata.lineage_id = SupersessionTracker.generate_lineage_id()
    metadata.version_reason = "Initial ingestion"
    metadata.change_summary = "First version"
    metadata.content_delta_hash = ""

def apply_version_update(old_metadata: dict[str, Any], new_metadata: DocumentMetadata, old_text: str, new_text: str) -> bool:
    """
    Compares texts and updates metadata if changes occurred.
    Returns True if a new version was created, False if identical.
    """
    diff_result = DiffDetector.compute_diff(old_text, new_text)
    
    new_metadata.document_id = f"doc_{uuid.uuid4().hex[:12]}"
    new_metadata.is_latest = True
    
    if not diff_result["has_changes"]:
        new_metadata.document_id = old_metadata.get("document_id", new_metadata.document_id)
        new_metadata.version = old_metadata.get("version", 1)
        new_metadata.lineage_id = old_metadata.get("lineage_id", "")
        return False
        
    SupersessionTracker.link_versions(old_metadata, new_metadata, reason="Semantic changes detected")
    new_metadata.change_summary = diff_result["change_summary"]
    new_metadata.content_delta_hash = diff_result["content_delta_hash"]
    
    return True
