"""High-level interface for document version lifecycle management."""

from __future__ import annotations

from typing import Any

from rag.types import DocumentMetadata
from rag.versioning.metadata_versioner import assign_initial_version
from rag.versioning.supersession_tracker import SupersessionTracker

class VersionManager:
    """Manages document versioning during ingestion to vector stores."""
    
    def __init__(self, manifest: dict[str, Any]):
        self.manifest = manifest
        
    def process_document(self, new_metadata: DocumentMetadata) -> dict[str, Any]:
        """
        Determines versioning for an incoming document against the active manifest.
        Returns a dict of actions (e.g. {'status': 'new'}, {'status': 'updated', 'superseded_id': '...'}).
        """
        existing_doc_metadata = self._find_existing_document(new_metadata)
        
        if not existing_doc_metadata:
            assign_initial_version(new_metadata)
            return {"status": "new"}
            
        old_hash = existing_doc_metadata.get("source_hash")
        if old_hash == new_metadata.source_hash:
            # Same content
            new_metadata.document_id = existing_doc_metadata.get("document_id", new_metadata.document_id)
            new_metadata.version = existing_doc_metadata.get("version", 1)
            new_metadata.lineage_id = existing_doc_metadata.get("lineage_id", "")
            return {"status": "unchanged"}
            
        SupersessionTracker.link_versions(existing_doc_metadata, new_metadata, reason="Source hash changed")
        new_metadata.change_summary = f"Content hash changed from {old_hash} to {new_metadata.source_hash}"
        new_metadata.content_delta_hash = new_metadata.source_hash
        
        return {
            "status": "updated",
            "superseded_document_id": existing_doc_metadata.get("document_id")
        }

    def _find_existing_document(self, metadata: DocumentMetadata) -> dict[str, Any] | None:
        """Find the latest version of a document by URL or path."""
        matches = []
        for chunk_meta in self.manifest.values():
            if chunk_meta.get("is_latest") is False:
                continue
            if metadata.source_url and chunk_meta.get("source_url") == metadata.source_url:
                matches.append(chunk_meta)
            elif metadata.source_path and chunk_meta.get("source_path") == metadata.source_path:
                matches.append(chunk_meta)
                
        if not matches:
            return None
            
        return max(matches, key=lambda m: m.get("version", 1))
