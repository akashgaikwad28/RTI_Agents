"""Cross-lingual query mapping and expansion."""

from __future__ import annotations

from typing import Any

from multilingual.translation.translator_router import TranslatorRouter
from multilingual.transliteration.query_expansion import QueryExpansion


class CrossLingualMapper:
    async def map_query(self, query: str, source_language: str, db: Any = None) -> dict:
        expansions = QueryExpansion().expand(query, source_language)
        translations = []
        for target in ["en", "hi", "mr"]:
            translated = await TranslatorRouter().translate(query, target_language=target, source_language=source_language, db=db)
            translations.append(translated["translated_text"])
        candidates = list(dict.fromkeys([query, *expansions, *translations]))
        return {"source_language": source_language, "queries": candidates, "translations": translations}
