"""Transliteration adapter with optional indic-transliteration support."""

from __future__ import annotations

from multilingual.transliteration.phonetic_mapper import PhoneticMapper


class Transliterator:
    def transliterate(self, text: str, target_script: str = "devanagari", language: str = "hi") -> str:
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate

            target = sanscript.DEVANAGARI if target_script == "devanagari" else sanscript.ITRANS
            return transliterate(text, sanscript.ITRANS, target)
        except Exception:
            return self._fallback_expand(text)

    def _fallback_expand(self, text: str) -> str:
        mapper = PhoneticMapper()
        parts = []
        for token in text.split():
            expansions = mapper.expand_token(token)
            parts.append(token)
            parts.extend(expansions[:1])
        return " ".join(parts)
