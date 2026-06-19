"""Self-improving memory engine aggregating workflow learning signals."""

from __future__ import annotations

from datetime import datetime, timezone

from memory.learning.correction_memory import CorrectionMemory
from memory.learning.feedback_memory import FeedbackMemory
from memory.learning.policy_memory import PolicyMemory
from memory.learning.reasoning_memory import ReasoningMemory


class AdaptiveMemory:
    def __init__(self):
        self.feedback = FeedbackMemory()
        self.policy = PolicyMemory()
        self.reasoning = ReasoningMemory()
        self.corrections = CorrectionMemory()

    async def learn_from_state(self, db, state: dict) -> dict:
        if db is None:
            return {"stored": False, "reason": "db_unavailable"}
        request_id = state.get("request_id", "")
        await self.policy.learn_department_mapping(db, state.get("raw_query", ""), state.get("department", ""), state.get("confidence", ""))
        await self.reasoning.store_trace(db, request_id, state.get("reasoning_trace", []))
        if state.get("reflection_reason"):
            await self.corrections.store_correction(db, request_id, {"reason": state.get("reflection_reason")})
        record = {
            "request_id": request_id,
            "approval_status": state.get("approval_status"),
            "retrieval_confidence": state.get("retrieval_confidence", 0.0),
            "risk_score": state.get("ai_risk_score", 0.0),
            "created_at": datetime.now(timezone.utc),
        }
        await db["adaptive_memory_events"].insert_one(record)
        return {"stored": True, "signals": list(record.keys())}

