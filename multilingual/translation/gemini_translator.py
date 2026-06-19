"""Gemini translation adapter with graceful fallback."""

from __future__ import annotations

from llm_router.llm_router import get_llm


class GeminiTranslator:
    async def translate(self, text: str, source_language: str, target_language: str) -> str:
        if source_language == target_language:
            return text
        try:
            llm = get_llm(task="translation")
            response = await llm.ainvoke(
                [
                    {
                        "role": "system",
                        "content": (
                            "Translate the user text for an Indian RTI governance workflow. "
                            "Preserve department names, legal terms, numbers, dates, citations, and proper nouns. "
                            "Return only the translated text."
                        ),
                    },
                    {"role": "user", "content": f"Source: {source_language}\nTarget: {target_language}\nText:\n{text}"},
                ]
            )
            return response.content.strip() or text
        except Exception:
            return text
