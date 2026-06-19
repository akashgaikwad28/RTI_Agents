"""
Replay Engine for LangGraph Executions.
Pulls from SQLite Checkpoint Saver and allows step-by-step trace analysis.
"""
from typing import Dict, Any, Optional

class GraphReplayEngine:
    def __init__(self, checkpointer):
        # In RTI-Agent, checkpointer is usually SqliteSaver
        self.checkpointer = checkpointer
        
    def fetch_trace(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Fetches the entire execution trace for a thread_id."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get all states
        states = list(self.checkpointer.list(config))
        if not states:
            return None
            
        # Reconstruct execution
        trace = []
        for state in reversed(states):
            trace.append({
                "timestamp": state.created_at,
                "node": state.next,
                "state_snapshot": state.values
            })
            
        return {
            "thread_id": thread_id,
            "total_steps": len(trace),
            "trace": trace
        }
        
    def analyze_failures(self, thread_id: str) -> Dict[str, Any]:
        """Detects if the graph hit a reflection loop or failed state."""
        trace_data = self.fetch_trace(thread_id)
        if not trace_data:
            return {"status": "not_found"}
            
        reflection_count = sum(1 for step in trace_data["trace"] if "reflection_node" in step.get("node", []))
        
        return {
            "thread_id": thread_id,
            "reflection_loops": reflection_count,
            "failed": reflection_count > 3, # arbitrary failure threshold
            "success": reflection_count <= 3
        }
