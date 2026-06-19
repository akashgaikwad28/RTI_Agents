"""Offline RAG evaluation runner."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from rag.evaluation.retrieval_metrics import context_relevance, retrieval_precision, retrieval_recall
from rag.retrievers.hybrid_retriever import HybridRetriever


async def evaluate_queries(cases: list[dict[str, Any]], *, output_path: str | Path | None = None) -> dict:
    retriever = HybridRetriever()
    reports: list[dict[str, Any]] = []
    for case in cases:
        started = time.perf_counter()
        results, cache_hit, confidence = await retriever.retrieve(
            case["query"],
            department=case.get("department", ""),
            language=case.get("language", ""),
            k=case.get("k", 5),
            use_cache=False,
        )
        relevant = set(case.get("relevant_source_hashes", []))
        reports.append(
            {
                "query": case["query"],
                "department": case.get("department", ""),
                "retrieved": len(results),
                "cache_hit": cache_hit,
                "confidence": confidence,
                "retrieval_precision": retrieval_precision(results, relevant) if relevant else None,
                "retrieval_recall": retrieval_recall(results, relevant) if relevant else None,
                "context_relevance": context_relevance(results),
                "latency": time.perf_counter() - started,
                "citations": [result.citation for result in results],
            }
        )
    summary = {
        "cases": reports,
        "averages": _averages(reports),
    }
    if output_path:
        Path(output_path).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def _averages(reports: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["context_relevance", "latency", "confidence"]
    return {
        key: sum(report[key] for report in reports if report.get(key) is not None) / max(sum(1 for report in reports if report.get(key) is not None), 1)
        for key in keys
    }


def run_eval_file(path: str, *, output_path: str | None = None) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    return asyncio.run(evaluate_queries(cases, output_path=output_path))

