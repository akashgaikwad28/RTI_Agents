"""Unicode script detection for Indian multilingual queries."""

from __future__ import annotations

import unicodedata
from collections import Counter


DEVANAGARI_START = 0x0900
DEVANAGARI_END = 0x097F


class ScriptDetector:
    def detect(self, text: str) -> dict:
        counts: Counter[str] = Counter()
        for char in text:
            if char.isspace() or unicodedata.category(char).startswith("P"):
                continue
            code = ord(char)
            if DEVANAGARI_START <= code <= DEVANAGARI_END:
                counts["devanagari"] += 1
            elif "LATIN" in unicodedata.name(char, ""):
                counts["latin"] += 1
            elif char.isdigit():
                counts["numeric"] += 1
            else:
                counts["other"] += 1
        total = sum(counts.values()) or 1
        primary = counts.most_common(1)[0][0] if counts else "unknown"
        return {
            "primary_script": primary,
            "scripts": dict(counts),
            "script_confidence": round((counts[primary] / total) if primary != "unknown" else 0.0, 4),
        }
