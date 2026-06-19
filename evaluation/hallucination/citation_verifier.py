"""
Verifies that citations within a generated response correctly map to the retrieved documents.
"""
from pydantic import BaseModel
import re

class CitationVerificationResult(BaseModel):
    total_citations: int
    valid_citations: int
    invalid_citations: list[str]
    score: float

class CitationVerifier:
    def __init__(self):
        # We expect citations in the format [1], [2], etc.
        self.citation_pattern = re.compile(r'\[(\d+)\]')
        
    def verify(self, text: str, retrieved_chunks: list[str]) -> CitationVerificationResult:
        citations = self.citation_pattern.findall(text)
        if not citations:
            return CitationVerificationResult(
                total_citations=0,
                valid_citations=0,
                invalid_citations=[],
                score=1.0 # No citations to invalidate
            )
            
        invalid = []
        for c in citations:
            idx = int(c) - 1
            if idx < 0 or idx >= len(retrieved_chunks):
                invalid.append(f"[{c}] (Out of bounds)")
                
        valid_count = len(citations) - len(invalid)
        score = valid_count / len(citations)
        
        return CitationVerificationResult(
            total_citations=len(citations),
            valid_citations=valid_count,
            invalid_citations=invalid,
            score=score
        )
