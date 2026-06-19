from __future__ import annotations

from datetime import datetime, timezone


class FeedbackMemory:
    async def store_feedback(self, db, feedback: dict) -> None:
        if db is not None:
            await db["learning_feedback"].insert_one({**feedback, "created_at": datetime.now(timezone.utc)})

