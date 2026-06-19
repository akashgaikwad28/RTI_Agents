"""
observability/log_sampling.py
------------------------------
Determines if a given log event should be sampled (persisted) based on traffic volume rules.
"""

import random
from typing import Optional

# ── Sampling Rules ────────────────────────────────────────────────
# 1.0 = 100%, 0.1 = 10%
SAMPLING_RATES = {
    "error": 1.0,           # 100% of errors
    "critical": 1.0,        # 100% of criticals
    "security": 1.0,        # 100% of security events
    "hitl": 1.0,            # 100% of Human-in-the-loop interactions
    "audit": 1.0,           # 100% of audit trails
    "retrieval": 1.0,       # 100% of retrieval events
    "default": 0.2          # 20% of standard traffic
}

def should_sample(level: str, event_category: Optional[str] = None) -> bool:
    """
    Determines if a log should be written.
    """
    level_lower = level.lower()
    
    if level_lower in ["error", "critical", "warning"]:
        return True
        
    if event_category in ["security", "hitl", "audit", "retrieval"]:
        return True
        
    # Standard sampling
    return random.random() <= SAMPLING_RATES.get("default", 1.0)
