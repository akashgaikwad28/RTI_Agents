"""Assigns quantitative trust scores to document sources."""

from __future__ import annotations

from rag.types import DocumentMetadata

class SourceScorer:
    TRUST_SCORES = {
        "gazette": 1.0,
        "official_pdf": 0.95,
        "circular": 0.9,
        "government_html": 0.8,
        "scraped_table": 0.65,
        "dynamic_widget": 0.55
    }
    
    @staticmethod
    def evaluate(metadata: DocumentMetadata) -> float:
        """Determines the baseline source authority score."""
        doc_type = (metadata.document_type or "").lower()
        mime_type = (metadata.mime_type or "").lower()
        
        if "gazette" in doc_type:
            return SourceScorer.TRUST_SCORES["gazette"]
        if mime_type == "application/pdf":
            if "circular" in doc_type:
                return SourceScorer.TRUST_SCORES["circular"]
            return SourceScorer.TRUST_SCORES["official_pdf"]
        if "table" in doc_type:
            return SourceScorer.TRUST_SCORES["scraped_table"]
            
        return SourceScorer.TRUST_SCORES["government_html"]
