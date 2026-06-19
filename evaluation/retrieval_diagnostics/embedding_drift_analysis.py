"""
Detects semantic drift in embedding space over time.
"""
from typing import List
import numpy as np

class EmbeddingDriftAnalyzer:
    def calculate_drift(self, old_embeddings: List[List[float]], new_embeddings: List[List[float]]) -> float:
        """Calculates drift between two sets of embeddings of the same dataset."""
        if not old_embeddings or not new_embeddings or len(old_embeddings) != len(new_embeddings):
            return 0.0
            
        old_np = np.array(old_embeddings)
        new_np = np.array(new_embeddings)
        
        dot_products = np.sum(old_np * new_np, axis=1)
        norms_old = np.linalg.norm(old_np, axis=1)
        norms_new = np.linalg.norm(new_np, axis=1)
        
        # Avoid division by zero
        valid = (norms_old > 0) & (norms_new > 0)
        cosines = np.zeros_like(dot_products)
        cosines[valid] = dot_products[valid] / (norms_old[valid] * norms_new[valid])
        
        return float(1.0 - np.mean(cosines))
