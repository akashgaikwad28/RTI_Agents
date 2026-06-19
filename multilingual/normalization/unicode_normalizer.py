"""Unicode-safe text normalization for multilingual RTI workflows."""

from __future__ import annotations

import re
import unicodedata


class UnicodeNormalizer:
    def normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFC", text or "")
        text = text.replace("\u200c", "").replace("\u200d", "")
        text = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def validate_encoding(self, text: str) -> dict:
        try:
            text.encode("utf-8")
            return {"valid": True, "encoding": "utf-8"}
        except UnicodeEncodeError as exc:
            return {"valid": False, "error": str(exc)}
