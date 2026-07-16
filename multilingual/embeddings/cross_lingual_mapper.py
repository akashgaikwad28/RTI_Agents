"""Cross-lingual query mapping and expansion."""

from __future__ import annotations

import asyncio
from typing import Any

from multilingual.translation.translator_router import TranslatorRouter
from multilingual.transliteration.query_expansion import QueryExpansion
from llm_router.llm_router import get_llm
from observability.structured_logger import get_logger

logger = get_logger(__name__)


class CrossLingualMapper:
    # Fix: cache helper instances (not per-call) to avoid re-instantiation on every request
    def __init__(self):
        self._router = TranslatorRouter()
        self._expander = QueryExpansion()

    async def map_query(self, query: str, source_language: str, db: Any = None) -> dict:
        expansions = self._expander.expand(query, source_language)

        # Run all translations AND HyDE concurrently
        # Use named keys to avoid fragile index-based categorization (fixes translation bug)
        translate_tasks = [
            self._router.translate(query, target_language=target, source_language=source_language, db=db)
            for target in ["en", "hi", "mr"]
        ]
        hyde_task = self._generate_hyde(query, source_language)

        translate_results, hyde_doc = await asyncio.gather(
            asyncio.gather(*translate_tasks, return_exceptions=True),
            hyde_task,
            return_exceptions=False,
        )

        translations = []
        for res in translate_results:
            if isinstance(res, Exception):
                logger.warning(f"[CrossLingualMapper] Translation failed: {res}")
                continue
            translations.append(res["translated_text"])

        candidates = list(dict.fromkeys([query, hyde_doc, *expansions, *translations]))
        candidates = [c for c in candidates if c]
        return {"source_language": source_language, "queries": candidates, "translations": translations}

    async def _generate_hyde(self, query: str, source_language: str) -> str:
        try:
            llm = get_llm(task="generation")
            response = await llm.ainvoke(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are an expert on Indian RTI and government schemes. "
                            "Write a hypothetical, highly accurate, and detailed 1-paragraph factual answer to the following question. "
                            "The answer should be in English, regardless of the input language. "
                            "Do not include conversational filler, just the facts."
                        ),
                    },
                    {"role": "user", "content": f"Question: {query}"},
                ]
            )
            return response.content.strip()
        except Exception as exc:
            logger.warning(f"[CrossLingualMapper] HyDE generation failed: {exc}")
            return ""
