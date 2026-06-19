"""Mixed language detection for Hindi/Marathi/English queries."""

from __future__ import annotations

from multilingual.detection.language_detector import LanguageDetector
from multilingual.detection.script_detector import ScriptDetector


class MixedLanguageDetector:
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.script_detector = ScriptDetector()

    def analyze(self, text: str) -> dict:
        detection = self.language_detector.detect(text)
        script = self.script_detector.detect(text)
        return {
            **detection.model_dump(),
            "script_distribution": script["scripts"],
            "mixed_language": detection.is_mixed or bool(detection.romanized_language),
            "needs_translation": detection.language not in {"en", "unknown"},
            "needs_transliteration": bool(detection.romanized_language),
        }
