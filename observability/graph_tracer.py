"""
observability/graph_tracer.py
------------------------------
Traces full LangGraph runs.
Includes state snapshot compression to prevent massive log explosions.
"""

import hashlib
import json
from typing import Dict, Any, List, Tuple
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome

def compress_state(old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Tuple[List[str], str]:
    """
    Computes changed keys and a hash of the new state.
    Prevents massive object graphs from blowing up log files.
    """
    changed_keys = []
    
    # Simple top-level diff
    for key, val in new_state.items():
        if old_state.get(key) != val:
            changed_keys.append(key)
            
    # Serialize state for hashing (handle non-serializable objects gracefully)
    def default_serializer(obj):
        if hasattr(obj, "dict"): return obj.dict()
        if hasattr(obj, "model_dump"): return obj.model_dump()
        return str(obj)
        
    try:
        state_str = json.dumps(new_state, default=default_serializer, sort_keys=True)
        state_hash = hashlib.sha256(state_str.encode('utf-8')).hexdigest()[:16]
    except Exception:
        state_hash = "unhashable"
        
    return changed_keys, state_hash

def log_graph_start(graph_name: str, hitl_enabled: bool = False):
    telemetry.log_graph_event(
        event=f"{graph_name}_started",
        operation="graph_execution",
        hitl_enabled=hitl_enabled
    )

def log_graph_end(graph_name: str, execution_time_ms: float, outcome: Outcome = Outcome.SUCCESS):
    telemetry.log_graph_event(
        event=f"{graph_name}_completed",
        operation="graph_execution",
        execution_time_ms=execution_time_ms,
        outcome=outcome
    )
