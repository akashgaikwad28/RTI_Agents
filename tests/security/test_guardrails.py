"""Tests for security guardrails and priority overrides."""

import pytest
from rag.guardrails.policy_priority import PolicyPriority
from rag.types import DocumentMetadata

@pytest.mark.unit
@pytest.mark.security
def test_policy_priority_gazette_over_notice():
    gazette_meta = DocumentMetadata(document_type="official_gazette")
    notice_meta = DocumentMetadata(document_type="local_notice")
    
    gazette_score = PolicyPriority.get_priority_score(gazette_meta)
    notice_score = PolicyPriority.get_priority_score(notice_meta)
    
    assert gazette_score > notice_score
    assert gazette_score == 1.0
