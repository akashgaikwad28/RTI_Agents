"""Multilingual semantic memory facade."""

from __future__ import annotations

from typing import Any

from multilingual.embeddings.cross_lingual_mapper import CrossLingualMapper
from multilingual.memory.crosslingual_history import CrossLingualHistory


class MultilingualMemory:
    async def remember_query(self, db: Any, user_id: str | None, query: str, language: str) -> dict:
        mapped = await CrossLingualMapper().map_query(query, language, db=db)
        history = await CrossLingualHistory().record(db, user_id, query, language, mapped["translations"][0] if mapped["translations"] else None)
        return {"history": history, "expanded_queries": mapped["queries"]}
