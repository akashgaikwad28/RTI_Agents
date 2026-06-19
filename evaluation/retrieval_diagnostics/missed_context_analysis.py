"""
Analyzes whether a relevant context existed in the database but was not retrieved.
"""
from typing import List, Dict

class MissedContextAnalyzer:
    def __init__(self):
        pass
        
    def analyze(self, query: str, retrieved_hashes: List[str], expected_hashes: List[str]) -> Dict[str, Any]:
        missed = set(expected_hashes) - set(retrieved_hashes)
        return {
            "missed_count": len(missed),
            "missed_hashes": list(missed),
            "retrieval_recall": 1.0 - (len(missed) / len(expected_hashes) if expected_hashes else 0.0)
        }
