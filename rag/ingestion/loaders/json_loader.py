"""JSON corpus loader for already-structured government documents."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.types import LoadedDocument


async def load_json(path: str | Path, *, default_department: str = "") -> list[LoadedDocument]:
    file_path = Path(path)
    raw = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
    data = json.loads(raw)
    records = data if isinstance(data, list) else data.get("documents", data.get("items", [data]))
    documents: list[LoadedDocument] = []
    for item in records:
        if not isinstance(item, dict):
            item = {"text": str(item)}
        text = clean_text(str(item.get("text") or item.get("content") or item.get("body") or ""))
        if not text:
            continue
        metadata = build_metadata(
            text=text,
            source_url=str(item.get("source_url", "")),
            source_path=str(file_path),
            department=str(item.get("department") or default_department),
            document_type=str(item.get("document_type") or item.get("category") or "json"),
            title=str(item.get("title", "")),
            extra={k: _json_safe(v) for k, v in item.items() if k not in {"text", "content", "body"}},
        )
        documents.append(LoadedDocument(text=text, metadata=metadata))
    return documents


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)

