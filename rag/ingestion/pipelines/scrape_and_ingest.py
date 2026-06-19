"""Scrape configured government sites and ingest discovered documents."""

from __future__ import annotations

import asyncio

from rag.ingestion.loaders.gov_scraper import GovernmentScraper
from rag.types import IngestionReport
from rag.vectorstore.vector_manager import VectorManager


async def scrape_and_ingest(
    *,
    target_names: list[str] | None = None,
    max_depth: int | None = None,
    rebuild: bool = False,
) -> dict:
    scraper = GovernmentScraper()
    scrape_results = await scraper.scrape_targets(names=target_names, max_depth=max_depth)
    documents = [document for result in scrape_results for document in result.documents]
    ingestion_report: IngestionReport = await VectorManager().ingest_documents(documents, rebuild=rebuild)
    return {
        "scrape": [result.model_dump() | {"documents": len(result.documents)} for result in scrape_results],
        "ingestion": ingestion_report.model_dump(),
    }


def run(target_names: list[str] | None = None, *, max_depth: int | None = None, rebuild: bool = False) -> dict:
    return asyncio.run(scrape_and_ingest(target_names=target_names, max_depth=max_depth, rebuild=rebuild))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Scrape government portals and ingest into FAISS.")
    parser.add_argument("--target", action="append", dest="targets")
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.targets, max_depth=args.max_depth, rebuild=args.rebuild), indent=2))

