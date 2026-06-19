"""Backward-compatible ingestion entry point.

Phase B ingestion lives in rag.ingestion.pipelines.ingest_documents.
"""

from __future__ import annotations

from pathlib import Path

from rag.ingestion.pipelines.ingest_documents import run


def run_ingestion(paths: list[str] | None = None, rebuild: bool = True):
    selected = paths or [str(Path("rag/ingestion/corpus/raw")), str(Path("data/documents"))]
    return run(selected, rebuild=rebuild)


if __name__ == "__main__":
    run_ingestion()

