"""Tests for hallucination classification and calibration."""

import pytest
from rag.scoring.confidence_calibrator import ConfidenceCalibrator

@pytest.mark.unit
@pytest.mark.hallucination
def test_confidence_calibrator_high_trust():
    metrics = ConfidenceCalibrator.calibrate(
        semantic_score=0.9,
        trust_score=0.95,
        document_recency=0.8,
        retrieval_consistency=0.9,
        reranker_margin=0.3
    )
    assert metrics["retrieval_confidence"] > 0.8
    assert metrics["hallucination_risk"] < 0.2
    assert metrics["citation_reliability"] > 0.8

@pytest.mark.unit
@pytest.mark.hallucination
def test_confidence_calibrator_high_risk():
    metrics = ConfidenceCalibrator.calibrate(
        semantic_score=0.6,
        trust_score=0.4,
        document_recency=0.2,
        retrieval_consistency=0.4,
        reranker_margin=0.05
    )
    assert metrics["hallucination_risk"] > 0.5
    assert metrics["retrieval_confidence"] < 0.6
