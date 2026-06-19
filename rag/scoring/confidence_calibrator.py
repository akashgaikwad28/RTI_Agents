"""Calibrates final retrieval confidence and hallucination risk."""

from __future__ import annotations

from typing import TypedDict

class ConfidenceMetrics(TypedDict):
    retrieval_confidence: float
    hallucination_risk: float
    citation_reliability: float

class ConfidenceCalibrator:
    @staticmethod
    def calibrate(
        semantic_score: float,
        trust_score: float,
        document_recency: float,
        retrieval_consistency: float,
        reranker_margin: float
    ) -> ConfidenceMetrics:
        """Mathematically combines signals into absolute bounds."""
        
        # 1. Base confidence combines semantic relevance and source trust
        retrieval_confidence = (semantic_score * 0.5) + (trust_score * 0.3) + (document_recency * 0.2)
        
        # 2. Hallucination risk spikes if trust is low or margin is extremely tight
        risk_base = 1.0 - trust_score
        margin_penalty = max(0.0, 0.2 - reranker_margin) * 2.0
        hallucination_risk = min(1.0, (risk_base * 0.6) + (margin_penalty * 0.4) + ((1.0 - retrieval_consistency) * 0.2))
        
        # 3. Citation reliability is strictly tied to source trust and recency
        citation_reliability = (trust_score * 0.7) + (document_recency * 0.3)
        
        return {
            "retrieval_confidence": round(min(1.0, max(0.0, retrieval_confidence)), 4),
            "hallucination_risk": round(min(1.0, max(0.0, hallucination_risk)), 4),
            "citation_reliability": round(min(1.0, max(0.0, citation_reliability)), 4)
        }
