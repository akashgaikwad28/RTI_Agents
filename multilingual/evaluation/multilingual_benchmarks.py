"""Benchmark suite for multilingual capabilities."""

from __future__ import annotations

from multilingual.detection.language_detector import LanguageDetector
from multilingual.evaluation.translation_quality import translation_quality


BENCHMARK_QUERIES = [
    ("I need road budget information", "en"),
    ("मुझे सड़क बजट की जानकारी चाहिए", "hi"),
    ("मला रस्ता बजेटची माहिती पाहिजे", "mr"),
    ("mala road budget mahiti pahije", "mr"),
]


def run_language_benchmark() -> dict:
    detector = LanguageDetector()
    rows = []
    for text, expected in BENCHMARK_QUERIES:
        detected = detector.detect(text)
        rows.append({"query": text, "expected": expected, "detected": detected.language, "passed": detected.language == expected, "confidence": detected.confidence})
    return {"accuracy": sum(1 for row in rows if row["passed"]) / len(rows), "cases": rows}


def score_translation(source: str, translated: str) -> dict:
    return translation_quality(source, translated)
