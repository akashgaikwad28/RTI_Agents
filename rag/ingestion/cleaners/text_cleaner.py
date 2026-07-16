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

# Pre-compile boilerplate patterns once at module load time (fixes TC2)
_BOILERPLATE_PATTERNS_RAW = [
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
BOILERPLATE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _BOILERPLATE_PATTERNS_RAW]

# Date regex: only match patterns that look like genuine dates
_DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})(?!\d)")


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


def remove_boilerplate_lines(text: str, min_line_len: int = 3, language: str = "en") -> str:
    lines = [line.strip() for line in text.splitlines()]
    # Only apply frequency-based dedup for English text (fixes Marathi legal phrase stripping)
    line_counts: Counter = Counter()
    if language == "en":
        line_counts = Counter(line.lower() for line in lines if line)

    cleaned: list[str] = []
    for line in lines:
        if len(line) < min_line_len:
            continue
        lowered = line.lower()
        if any(p.search(lowered) for p in BOILERPLATE_PATTERNS):
            continue
        # Frequency-based dedup: only for English
        if language == "en" and line_counts[lowered] > 3 and len(line) < 120:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def normalize_dates(text: str) -> str:
    """Normalize Indian government date formats (DD/MM/YYYY) to ISO 8601.
    Only rewrites patterns with a plausible 4-digit year to avoid mangling section refs.
    """
    def repl(match: re.Match[str]) -> str:
        day_part, month_part, year_part = match.groups()
        year_str = year_part

        if len(year_str) <= 2:
            year_int = int(year_str)
            year_str = f"20{year_str}" if year_int < 50 else f"19{year_str}"
        else:
            year_int = int(year_str)
            # Avoid replacing section-like refs (e.g. 5/6/200 not a valid year)
            if year_int < 1900:
                return match.group(0)

        day, month = int(day_part), int(month_part)
        if not (1 <= day <= 31 and 1 <= month <= 12):
            return match.group(0)

        return f"{year_str.zfill(4)}-{month_part.zfill(2)}-{day_part.zfill(2)}"

    return _DATE_RE.sub(repl, text)


def collapse_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_language(text: str) -> str:
    if not text:
        return "unknown"
    devanagari = len(re.findall(r"[\u0900-\u097F]", text))
    ascii_letters = len(re.findall(r"[A-Za-z]", text))
    # Lowered threshold from 20 to 10 chars for short Marathi/Hindi snippets (fixes TC4)
    if devanagari > max(10, ascii_letters * 0.2):
        marathi_markers = ["आहे", "महाराष्ट्र", "शासन", "पुणे", "विभाग"]
        hindi_markers = ["है", "सरकार", "मंत्रालय", "योजना", "सूचना"]
        mr_hits = sum(marker in text for marker in marathi_markers)
        hi_hits = sum(marker in text for marker in hindi_markers)
        return "mr" if mr_hits >= hi_hits else "hi"
    if ascii_letters > 20:
        return "en"
    return "unknown"


def clean_text(text: str, language: str | None = None) -> str:
    text = normalize_unicode(text)
    text = remove_broken_control_chars(text)
    # HTML tag stripping removed: text has already been extracted from HTML (fixes TC5)
    detected_lang = language or detect_language(text)
    text = remove_boilerplate_lines(text, language=detected_lang)
    text = normalize_dates(text)
    return collapse_whitespace(text)
