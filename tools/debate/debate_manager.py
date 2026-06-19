"""Multi-agent debate manager over tool outputs."""

from __future__ import annotations

from tools.debate.consensus_engine import ConsensusEngine
from tools.debate.critic_agent import CriticAgent
from tools.debate.defender_agent import DefenderAgent
from tools.debate.verifier_agent import VerifierAgent


class DebateManager:
    def run(self, tool_results: list[dict], rag_citations: list[str] | None = None) -> dict:
        critic = CriticAgent().critique(tool_results)
        defender = DefenderAgent().defend(tool_results)
        verifier = VerifierAgent().verify(tool_results, rag_citations)
        consensus = ConsensusEngine().decide(critic, defender, verifier)
        return {"critic": critic, "defender": defender, "verifier": verifier, "consensus": consensus}
