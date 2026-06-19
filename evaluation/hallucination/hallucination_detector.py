"""
Master hallucination detector that orchestrates grounding, contradiction, unsupported claims, and citations.
"""
from pydantic import BaseModel
from evaluation.hallucination.grounding_checker import GroundingChecker
from evaluation.hallucination.contradiction_detector import ContradictionDetector
from evaluation.hallucination.unsupported_claims import UnsupportedClaimsDetector
from evaluation.hallucination.citation_verifier import CitationVerifier

class HallucinationReport(BaseModel):
    is_hallucination: bool
    grounding_score: float
    has_contradiction: bool
    unsupported_claims: list[str]
    citation_score: float
    risk_score: float # 0.0 (safe) to 1.0 (severe hallucination)

class HallucinationDetector:
    def __init__(self):
        self.grounding_checker = GroundingChecker()
        self.contradiction_detector = ContradictionDetector()
        self.unsupported_detector = UnsupportedClaimsDetector()
        self.citation_verifier = CitationVerifier()
        
    async def analyze(self, statement: str, facts: list[str]) -> HallucinationReport:
        grounding_score = await self.grounding_checker.check_grounding(statement, facts)
        has_contradiction = await self.contradiction_detector.has_contradiction(statement)
        unsupported = await self.unsupported_detector.detect(statement, facts)
        citation_result = self.citation_verifier.verify(statement, facts)
        
        # Calculate overall risk score
        risk_score = 0.0
        risk_score += (1.0 - grounding_score) * 0.4
        risk_score += (1.0 if has_contradiction else 0.0) * 0.3
        risk_score += (min(1.0, len(unsupported) * 0.2)) * 0.2
        risk_score += (1.0 - citation_result.score) * 0.1
        
        is_hallucination = risk_score > 0.4 or has_contradiction or len(unsupported) > 0
        
        return HallucinationReport(
            is_hallucination=is_hallucination,
            grounding_score=grounding_score,
            has_contradiction=has_contradiction,
            unsupported_claims=unsupported,
            citation_score=citation_result.score,
            risk_score=risk_score
        )
