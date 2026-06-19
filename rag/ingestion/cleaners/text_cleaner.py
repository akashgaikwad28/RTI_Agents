"""
Production text cleaning for government HTML/PDF content.

The cleaner is intentionally language-preserving: it normalizes Unicode and
layout noise without transliterating Marathi/Hindi text.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections import Counter

BOILERPLATE_PATTERNS = [
    r"skip\s+to\s+main\s+content",
    r"screen\s+reader\s+access",
    r"last\s+updated\s*:?",
    r"copyright\s+.*?(government|department|ministry)",
    r"terms\s+and\s+conditions",
    r"privacy\s+policy",
    r"cookie\s+policy",
    r"enable\s+javascript",
    r"you\s+are\s+here\s*:?",
    r"home\s*/\s*",
]

DATE_PATTERNS = [
    (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", "{yyyy}-{mm}-{dd}"),
]


def normalize_unicode(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\ufeff", " ").replace("\u200b", "")
    text = text.replace("\xa0", " ")
    return text


def remove_broken_control_chars(text: str) -> str:
    return "".join(ch if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C") else " " for ch in text)


def remove_boilerplate_lines(text: str, min_line_len: int = 3) -> str:
    lines = [line.strip() for line in text.splitlines()]
    line_counts = Counter(line.lower() for line in lines if line)
    cleaned: list[str] = []
    for line in lines:
        if len(line) < min_line_len:
            continue
        lowered = line.lower()
        if any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in BOILERPLATE_PATTERNS):
            continue
        if line_counts[lowered] > 3 and len(line) < 120:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def normalize_dates(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        day, month, year = match.groups()
        if len(year) == 2:
            year = f"20{year}" if int(year) < 50 else f"19{year}"
        return f"{year.zfill(4)}-{month.zfill(2)}-{day.zfill(2)}"

    return re.sub(DATE_PATTERNS[0][0], repl, text)


def collapse_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_language(text: str) -> str:
    if not text:
        return "unknown"
    devanagari = len(re.findall(r"[\u0900-\u097F]", text))
    ascii_letters = len(re.findall(r"[A-Za-z]", text))
    if devanagari > max(20, ascii_letters * 0.25):
        marathi_markers = ["आहे", "महाराष्ट्र", "शासन", "पुणे", "विभाग"]
        hindi_markers = ["है", "सरकार", "मंत्रालय", "योजना", "सूचना"]
        mr_hits = sum(marker in text for marker in marathi_markers)
        hi_hits = sum(marker in text for marker in hindi_markers)
        return "mr" if mr_hits >= hi_hits else "hi"
    if ascii_letters > 20:
        return "en"
    return "unknown"


def clean_text(text: str) -> str:
    text = normalize_unicode(text)
    text = remove_broken_control_chars(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = remove_boilerplate_lines(text)
    text = normalize_dates(text)
    return collapse_whitespace(text)

