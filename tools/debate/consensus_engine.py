"""Consensus engine for debate outputs."""

from __future__ import annotations


class ConsensusEngine:
    def decide(self, critic: dict, defender: dict, verifier: dict) -> dict:
        truth_score = round((critic.get("confidence", 0) * 0.25) + (defender.get("confidence", 0) * 0.35) + (verifier.get("confidence", 0) * 0.4), 4)
        risk = round(max(0.0, 1.0 - truth_score + 0.05 * len(critic.get("issues", []))), 4)
        return {
            "truth_score": truth_score,
            "risk_score": min(1.0, risk),
            "passed": truth_score >= 0.6 and verifier.get("passed", False),
            "recommended_action": "continue_to_review" if truth_score >= 0.6 else "reflection_retry",
        }
