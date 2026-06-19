"""Cross-lingual user history persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class CrossLingualHistory:
    async def record(self, db: Any, user_id: str | None, query: str, language: str, translated_query: str | None = None) -> dict:
        doc = {
            "user_id": user_id,
            "query": query,
            "language": language,
            "translated_query": translated_query,
            "created_at": datetime.now(timezone.utc),
        }
        if db is not None:
            await db["crosslingual_history"].insert_one(doc)
        return {"stored": db is not None}
