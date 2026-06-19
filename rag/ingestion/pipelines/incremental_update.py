"""Incremental RAG update entry point."""

from __future__ import annotations

from pathlib import Path

from rag.ingestion.pipelines.ingest_documents import ingest_documents
from rag.ingestion.pipelines.scrape_and_ingest import scrape_and_ingest


async def incremental_update(
    *,
    paths: list[str | Path] | None = None,
    target_names: list[str] | None = None,
    max_depth: int | None = None,
) -> dict:
    reports: dict = {}
    if paths:
        reports["documents"] = (await ingest_documents(paths, rebuild=False)).model_dump()
    if target_names is not None:
        reports["scrape"] = await scrape_and_ingest(target_names=target_names, max_depth=max_depth, rebuild=False)
    return reports

