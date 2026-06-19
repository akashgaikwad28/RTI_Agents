"""Language detection for English, Hindi, Marathi, and romanized Indic text."""

from __future__ import annotations

import re
from dataclasses import dataclass

from multilingual.detection.script_detector import ScriptDetector


HINDI_MARKERS = {
    "है", "हैं", "क्या", "मुझे", "जानकारी", "सड़क", "विभाग", "आवेदन", "कृपया", "में", "का", "की",
}
MARATHI_MARKERS = {
    "आहे", "आहेत", "मला", "माहिती", "रस्ता", "विभाग", "अर्ज", "कृपया", "मध्ये", "चा", "ची", "चे",
}
ROMAN_HINDI = {"mujhe", "chahiye", "sadak", "jaankari", "jankari", "vibhag", "sarkar", "yojana", "pani"}
ROMAN_MARATHI = {"mala", "mahiti", "pahije", "rasta", "vikas", "nagar", "mahanagar", "kharcha", "anudan"}


@dataclass(frozen=True)
class LanguageDetection:
    language: str
    confidence: float
    script: str
    is_mixed: bool
    romanized_language: str | None = None
    evidence: list[str] | None = None

    def model_dump(self) -> dict:
        return {
            "language": self.language,
            "confidence": self.confidence,
            "script": self.script,
            "is_mixed": self.is_mixed,
            "romanized_language": self.romanized_language,
            "evidence": self.evidence or [],
        }


class LanguageDetector:
    def __init__(self):
        self.script_detector = ScriptDetector()

    def detect(self, text: str) -> LanguageDetection:
        script = self.script_detector.detect(text)
        tokens = set(re.findall(r"[\w\u0900-\u097F]+", text.lower(), flags=re.UNICODE))
        evidence: list[str] = []

        hindi = len(tokens & HINDI_MARKERS)
        marathi = len(tokens & MARATHI_MARKERS)
        roman_hi = len(tokens & ROMAN_HINDI)
        roman_mr = len(tokens & ROMAN_MARATHI)
        latin_words = len(re.findall(r"[a-zA-Z]+", text))
        devanagari_words = len(re.findall(r"[\u0900-\u097F]+", text))

        if hindi:
            evidence.append(f"hindi_markers={hindi}")
        if marathi:
            evidence.append(f"marathi_markers={marathi}")
        if roman_hi:
            evidence.append(f"roman_hindi_markers={roman_hi}")
        if roman_mr:
            evidence.append(f"roman_marathi_markers={roman_mr}")

        is_mixed = latin_words > 0 and devanagari_words > 0
        if script["primary_script"] == "devanagari":
            if marathi > hindi:
                return LanguageDetection("mr", min(0.95, 0.62 + marathi * 0.08), "devanagari", is_mixed, evidence=evidence)
            if hindi > marathi:
                return LanguageDetection("hi", min(0.95, 0.62 + hindi * 0.08), "devanagari", is_mixed, evidence=evidence)
            return LanguageDetection("hi", 0.58, "devanagari", is_mixed, evidence=evidence)

        if roman_mr or roman_hi:
            if roman_mr >= roman_hi:
                return LanguageDetection("mr", min(0.88, 0.5 + roman_mr * 0.1), "latin", is_mixed, romanized_language="mr", evidence=evidence)
            return LanguageDetection("hi", min(0.88, 0.5 + roman_hi * 0.1), "latin", is_mixed, romanized_language="hi", evidence=evidence)

        if latin_words and not devanagari_words:
            return LanguageDetection("en", 0.84, "latin", False, evidence=evidence)
        return LanguageDetection("unknown", 0.2, script["primary_script"], is_mixed, evidence=evidence)
