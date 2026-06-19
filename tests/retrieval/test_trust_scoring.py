"""Tests for source trust scoring logic."""

import pytest
from rag.trust.source_scorer import SourceScorer
from rag.types import DocumentMetadata

@pytest.mark.unit
@pytest.mark.rag
def test_trust_scorer_gazette():
    meta = DocumentMetadata(document_type="gazette_notification")
    score = SourceScorer.evaluate(meta)
    assert score == 1.0

@pytest.mark.unit
def test_trust_scorer_official_pdf():
    meta = DocumentMetadata(document_type="report", mime_type="application/pdf")
    score = SourceScorer.evaluate(meta)
    assert score == 0.95

@pytest.mark.unit
def test_trust_scorer_html_fallback():
    meta = DocumentMetadata(document_type="news", mime_type="text/html")
    score = SourceScorer.evaluate(meta)
    assert score == 0.8
