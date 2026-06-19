"""Automated retrieval benchmarking and precision calculations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from observability.structured_logger import get_logger

logger = get_logger(__name__)

class RetrievalBenchmark:
    def __init__(self, dataset_path: str = "evaluation/datasets/golden_queries.json"):
        self.dataset_path = Path(dataset_path)
        self.queries = self._load_queries()

    def _load_queries(self) -> list[dict[str, Any]]:
        if not self.dataset_path.exists():
            return []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def calculate_precision_at_k(self, expected_docs: list[str], retrieved_docs: list[str], k: int) -> float:
        """Calculates Precision@K."""
        if not expected_docs or k == 0:
            return 0.0
        retrieved_k = retrieved_docs[:k]
        hits = sum(1 for doc in retrieved_k if doc in expected_docs)
        return hits / len(retrieved_k) if retrieved_k else 0.0

    def calculate_recall_at_k(self, expected_docs: list[str], retrieved_docs: list[str], k: int) -> float:
        """Calculates Recall@K."""
        if not expected_docs:
            return 0.0
        retrieved_k = retrieved_docs[:k]
        hits = sum(1 for doc in retrieved_k if doc in expected_docs)
        return hits / len(expected_docs)
