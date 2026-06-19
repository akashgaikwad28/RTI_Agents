from __future__ import annotations

from pydantic import BaseModel

from rag.evaluation.retrieval_metrics import grounding_score
from tools.base.base_tool import BaseTool


class GroundingInput(BaseModel):
    answer: str
    contexts: list[str]


class GroundingScoreTool(BaseTool):
    name = "grounding_score"
    description = "Compute lexical grounding score against retrieved context."
    category = "analytics"
    permissions = ["read:rag"]
    capabilities = ["grounding", "evaluation"]
    input_schema = GroundingInput

    async def execute(self, answer: str, contexts: list[str]):
        return {"grounding_score": grounding_score(answer, contexts)}

