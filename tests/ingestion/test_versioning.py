"""Tests for soft lineage and version management."""

import pytest
from rag.types import DocumentMetadata
from rag.versioning.version_manager import VersionManager
from rag.versioning.metadata_versioner import apply_version_update

@pytest.mark.unit
def test_apply_version_update_creates_new_lineage():
    old_meta = {"version": 1, "document_id": "doc_123", "lineage_id": "lin_456"}
    new_meta = DocumentMetadata(source_url="http://test.com")
    
    changed = apply_version_update(old_meta, new_meta, "Old text", "New text with changes")
    
    assert changed is True
    assert new_meta.version == 2
    assert new_meta.supersedes == "doc_123"
    assert new_meta.lineage_id == "lin_456"
    assert new_meta.is_latest is True
    assert "Detected" in new_meta.change_summary
