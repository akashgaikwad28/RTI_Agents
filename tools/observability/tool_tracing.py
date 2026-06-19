"""OpenTelemetry-friendly trace annotations for tools."""

from __future__ import annotations

from contextlib import contextmanager


@contextmanager
def tool_span(_name: str, **_attributes):
    yield
