"""Lightweight hallucination indicators for tool outputs."""

from __future__ import annotations

from typing import Any


class HallucinationChecker:
    def check(self, output: Any) -> dict[str, Any]:
        text = str(output).lower()
        flags = []
        if "as an ai" in text:
            flags.append("model_disclaimer_in_tool_output")
        if any(phrase in text for phrase in ["probably", "might be", "unverified claim"]):
            flags.append("uncertain_claim")
        if len(text) > 100 and not any(marker in text for marker in ["source", "citation", "url", ".gov.in", ".nic.in"]):
            flags.append("uncited_long_output")
        return {"flags": flags, "critical_flags": [flag for flag in flags if flag == "uncited_long_output"], "score": max(0.0, 1.0 - 0.2 * len(flags))}
