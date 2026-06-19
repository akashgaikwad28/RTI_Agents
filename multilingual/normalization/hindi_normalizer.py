"""Hindi-specific normalization."""

from __future__ import annotations

from multilingual.normalization.devanagari_cleaner import DevanagariCleaner


class HindiNormalizer:
    def normalize(self, text: str) -> str:
        return DevanagariCleaner().clean(text)
