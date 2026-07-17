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
        markers = ["source", "citation", "url", ".gov.in", ".nic.in"]
        if len(text) > 100 and not any(marker in text for marker in markers):
            flags.append("uncited_long_output")
        critical_flags = [
            flag for flag in flags if flag == "uncited_long_output"
        ]
        score = max(0.0, 1.0 - 0.2 * len(flags))
        return {
            "flags": flags,
            "critical_flags": critical_flags,
            "score": score
        }
