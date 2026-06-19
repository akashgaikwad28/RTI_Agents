"""
Evaluates how effectively the agent selected tools.
"""
from typing import List, Dict

class ToolSelectionEvaluator:
    def evaluate(self, expected_tools: List[str], actual_tools_called: List[str]) -> Dict:
        expected = set(expected_tools)
        actual = set(actual_tools_called)
        
        missing_tools = expected - actual
        unnecessary_tools = actual - expected
        
        score = 1.0
        if expected:
            score -= (len(missing_tools) / len(expected)) * 0.5
        if actual:
            score -= (len(unnecessary_tools) / len(actual)) * 0.5
            
        return {
            "score": max(0.0, score),
            "missing_tools": list(missing_tools),
            "unnecessary_tools": list(unnecessary_tools)
        }
