"""Tool benchmark runner."""

from __future__ import annotations

from tools.evaluation.latency_metrics import latency_summary
from tools.evaluation.reliability_metrics import reliability_score
from tools.evaluation.tool_accuracy import accuracy_score


def benchmark_results(results: list[dict]) -> dict:
    return {
        "accuracy": accuracy_score(results),
        "latency": latency_summary(results),
        "reliability": reliability_score(results),
    }
