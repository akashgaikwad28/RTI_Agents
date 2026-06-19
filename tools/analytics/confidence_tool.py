from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool


class ConfidenceInput(BaseModel):
    retrieval_scores: list[float] = []
    grounding_score: float = 0.0
    review_score: float = 0.0


class ConfidenceTool(BaseTool):
    name = "confidence_calculator"
    description = "Aggregate retrieval, grounding, and review scores into an AI confidence score."
    category = "analytics"
    permissions = ["read:rag"]
    capabilities = ["confidence"]
    input_schema = ConfidenceInput

    async def execute(self, retrieval_scores: list[float] = [], grounding_score: float = 0.0, review_score: float = 0.0):
        retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
        confidence = round((retrieval * 0.4) + (grounding_score * 0.35) + (review_score * 0.25), 4)
        return {"confidence": confidence}

