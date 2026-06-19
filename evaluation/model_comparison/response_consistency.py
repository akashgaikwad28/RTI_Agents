"""
Analyzes LLM consistency by querying the same model multiple times with different temperatures.
"""
import numpy as np

class ConsistencyAnalyzer:
    def analyze(self, responses: list[str]) -> float:
        # Simplified: Check if all responses are identical
        if not responses:
            return 0.0
        unique_responses = set(responses)
        # 1.0 = perfectly consistent, approaches 0 as variation increases
        return 1.0 / len(unique_responses)

"""
Cost vs Quality analyzer.
"""
class CostQualityAnalyzer:
    def rank(self, benchmark_results: dict, quality_scores: dict) -> dict:
        rankings = []
        for model, res in benchmark_results.items():
            cost = res.get("tokens_used", 0) * 0.0001 # dummy rate
            quality = quality_scores.get(model, 0.0)
            
            # ROI score: higher is better
            roi = quality / max(0.0001, cost)
            rankings.append({
                "model": model,
                "cost": cost,
                "quality": quality,
                "roi_score": roi
            })
        return sorted(rankings, key=lambda x: x["roi_score"], reverse=True)

class PromptComparison:
    pass
    
class ModelRanker:
    pass
