"""
Analyzes if the reranker incorrectly down-ranked highly relevant chunks.
"""
from typing import List, Dict

class RerankFailureDetector:
    def analyze(self, initial_ranking: List[Dict], final_ranking: List[Dict], golden_hashes: set[str]) -> Dict:
        """
        initial_ranking: [{"hash": "abc", "score": 0.8}, ...]
        final_ranking: [{"hash": "xyz", "score": 0.9}, ...]
        """
        initial_positions = {item["hash"]: i for i, item in enumerate(initial_ranking)}
        final_positions = {item["hash"]: i for i, item in enumerate(final_ranking)}
        
        failures = []
        for golden_hash in golden_hashes:
            init_pos = initial_positions.get(golden_hash, -1)
            final_pos = final_positions.get(golden_hash, -1)
            
            # If it was in top 5 initially but dropped out of top 5 after reranking
            if 0 <= init_pos < 5 and (final_pos >= 5 or final_pos == -1):
                failures.append({
                    "hash": golden_hash,
                    "initial_pos": init_pos,
                    "final_pos": final_pos,
                    "reason": "Reranker down-ranked relevant chunk"
                })
                
        return {
            "failure_count": len(failures),
            "failures": failures
        }
