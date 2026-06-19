"""Cross-lingual and transliteration-aware query expansion."""

from __future__ import annotations

from multilingual.transliteration.phonetic_mapper import PhoneticMapper


class QueryExpansion:
    def expand(self, query: str, language: str = "en") -> list[str]:
        expansions = [query]
        token_expansions = []
        mapper = PhoneticMapper()
        for token in query.split():
            token_expansions.extend(mapper.expand_token(token))
        if token_expansions:
            expansions.append(" ".join([query, *token_expansions]))
        if language == "hi":
            expansions.append(f"{query} सूचना अधिकार आवेदन विभाग जानकारी")
        elif language == "mr":
            expansions.append(f"{query} माहिती अधिकार अर्ज विभाग माहिती")
        else:
            expansions.append(f"{query} RTI information department records")
        return list(dict.fromkeys(item.strip() for item in expansions if item.strip()))
