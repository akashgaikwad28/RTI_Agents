from __future__ import annotations

from rag.evaluation.retrieval_metrics import hallucination_rate
from tools.analytics.grounding_score_tool import GroundingInput
from tools.base.base_tool import BaseTool


class HallucinationDetectorTool(BaseTool):
    name = "hallucination_detector"
    description = "Detect likely unsupported claims from answer/context overlap."
    category = "analytics"
    permissions = ["read:rag"]
    capabilities = ["hallucination_detection", "safety"]
    input_schema = GroundingInput

    async def execute(self, answer: str, contexts: list[str]):
        rate = hallucination_rate(answer, contexts)
        return {"hallucination_rate": rate, "flags": ["low_grounding"] if rate > 0.45 else []}

