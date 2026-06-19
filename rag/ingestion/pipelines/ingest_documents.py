"""Document ingestion pipeline for local PDF/HTML/TXT/JSON corpora."""

from __future__ import annotations

import asyncio
from pathlib import Path

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.ingestion.loaders.html_loader import load_html
from rag.ingestion.loaders.json_loader import load_json
from rag.ingestion.loaders.pdf_loader import load_pdf
from rag.types import IngestionReport, LoadedDocument
from rag.vectorstore.vector_manager import VectorManager

PROCESSED_DIR = Path("rag/ingestion/corpus/processed")


async def load_documents_from_paths(paths: list[str | Path], *, department: str = "") -> list[LoadedDocument]:
    documents: list[LoadedDocument] = []
    for input_path in paths:
        path = Path(input_path)
        if path.is_dir():
            nested = [item for item in path.rglob("*") if item.is_file()]
            documents.extend(await load_documents_from_paths(nested, department=department))
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            documents.extend(await load_pdf(path, department=department))
        elif suffix in {".html", ".htm"}:
            html = await asyncio.to_thread(path.read_text, encoding="utf-8", errors="ignore")
            documents.append(await load_html(html, source_url="", department=department))
        elif suffix == ".json":
            documents.extend(await load_json(path, default_department=department))
        elif suffix in {".txt", ".md"}:
            raw = await asyncio.to_thread(path.read_text, encoding="utf-8", errors="ignore")
            text = clean_text(raw)
            if text:
                metadata = build_metadata(text=text, source_path=str(path), department=department, title=path.stem)
                documents.append(LoadedDocument(text=text, metadata=metadata))
    return documents


async def ingest_documents(paths: list[str | Path], *, department: str = "", rebuild: bool = False) -> IngestionReport:
    documents = await load_documents_from_paths(paths, department=department)
    report = await VectorManager().ingest_documents(documents, rebuild=rebuild)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return report


def run(paths: list[str], *, department: str = "", rebuild: bool = False) -> IngestionReport:
    return asyncio.run(ingest_documents(paths, department=department, rebuild=rebuild))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Ingest RTI/government documents into FAISS.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--department", default="")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.paths, department=args.department, rebuild=args.rebuild).model_dump(), indent=2))

