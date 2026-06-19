"""Devanagari cleanup helpers."""

from __future__ import annotations

import re

from multilingual.normalization.unicode_normalizer import UnicodeNormalizer


class DevanagariCleaner:
    def clean(self, text: str) -> str:
        normalized = UnicodeNormalizer().normalize(text)
        normalized = re.sub(r"([।॥])", r"\1 ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()
