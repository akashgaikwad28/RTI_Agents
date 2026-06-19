from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool


class RiskInput(BaseModel):
    confidence: float = 0.0
    hallucination_flags: list[str] = []
    missing_citations: int = 0
    department_confidence: str = "low"


class RiskAnalyzerTool(BaseTool):
    name = "risk_analyzer"
    description = "Compute escalation risk from confidence, citations, hallucination, and department signals."
    category = "analytics"
    permissions = ["read:rag"]
    capabilities = ["risk_analysis", "escalation"]
    input_schema = RiskInput

    async def execute(self, confidence: float = 0.0, hallucination_flags: list[str] = [], missing_citations: int = 0, department_confidence: str = "low"):
        risk = 1.0 - confidence
        risk += min(len(hallucination_flags) * 0.12, 0.3)
        risk += min(missing_citations * 0.08, 0.24)
        if department_confidence == "low":
            risk += 0.15
        return {"risk_score": round(min(risk, 1.0), 4), "escalation_required": risk >= 0.55}

