"""
Analyzes the quality of individual retrieved chunks (e.g., too short, too long, poor formatting).
"""
import re
from typing import Dict, List

class ChunkQualityAnalyzer:
    def analyze(self, chunks: List[str]) -> Dict:
        issues = []
        for i, chunk in enumerate(chunks):
            chunk_issues = []
            word_count = len(chunk.split())
            
            if word_count < 20:
                chunk_issues.append("Too short (< 20 words)")
            if word_count > 1000:
                chunk_issues.append("Too long (> 1000 words)")
                
            # Check for excessive formatting characters
            if len(re.findall(r'[^a-zA-Z0-9\s.,!?]', chunk)) / len(chunk) > 0.2:
                chunk_issues.append("High special character density (poor extraction)")
                
            if chunk_issues:
                issues.append({"chunk_index": i, "issues": chunk_issues})
                
        return {
            "total_chunks": len(chunks),
            "chunks_with_issues": len(issues),
            "issues": issues
        }

"""
Detects semantic drift in embedding space over time.
"""
class EmbeddingDriftAnalyzer:
    def calculate_drift(self, old_embeddings, new_embeddings) -> float:
        import numpy as np
        # Simple cosine distance over the dataset
        dot_products = np.sum(old_embeddings * new_embeddings, axis=1)
        norms_old = np.linalg.norm(old_embeddings, axis=1)
        norms_new = np.linalg.norm(new_embeddings, axis=1)
        cosines = dot_products / (norms_old * norms_new)
        return float(1.0 - np.mean(cosines))
