"""Translation memory for government terminology and prior translations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class TranslationMemory:
    async def remember(self, db: Any, source_text: str, translated_text: str, source_language: str, target_language: str, metadata: dict | None = None) -> dict:
        doc = {
            "source_text": source_text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }
        if db is not None:
            await db["translation_memory"].insert_one(doc)
        return {"stored": db is not None}

    async def lookup(self, db: Any, source_text: str, source_language: str, target_language: str) -> str | None:
        if db is None:
            return None
        doc = await db["translation_memory"].find_one(
            {"source_text": source_text, "source_language": source_language, "target_language": target_language},
            sort=[("created_at", -1)],
        )
        return doc.get("translated_text") if doc else None
