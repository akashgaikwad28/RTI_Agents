"""Timeout policy helpers."""

from __future__ import annotations


def effective_timeout(default_seconds: int, requested_seconds: int | None = None, maximum_seconds: int = 60) -> int:
    return min(maximum_seconds, requested_seconds or default_seconds)
