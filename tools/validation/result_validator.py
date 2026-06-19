"""Validation pipeline for tool outputs."""

from __future__ import annotations

from typing import Any

from tools.base.base_tool import BaseTool
from tools.validation.citation_validator import CitationValidator
from tools.validation.confidence_scorer import ConfidenceScorer
from tools.validation.hallucination_checker import HallucinationChecker


class ResultValidator:
    def __init__(self):
        self._citation_validator = CitationValidator()
        self._hallucination_checker = HallucinationChecker()
        self._confidence = ConfidenceScorer()

    async def validate(self, tool: BaseTool, output: Any) -> dict[str, Any]:
        citations = self._citation_validator.validate(output)
        hallucination = self._hallucination_checker.check(output)
        confidence = self._confidence.score(output, citations, hallucination)
        valid = not hallucination["critical_flags"] and citations["credible"]
        return {
            "valid": valid,
            "citation_check": citations,
            "hallucination_check": hallucination,
            "confidence": confidence,
            "tool": tool.name,
        }
