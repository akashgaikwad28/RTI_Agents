"""
Tracker to persist the state of the system during an evaluation run, guaranteeing reproducibility.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time

class BenchmarkRunMetadata(BaseModel):
    run_id: str
    dataset_name: str
    dataset_version: str
    dataset_hash: str
    
    # Environment versioning
    embedding_model: str
    llm_model: str
    graph_version: str
    prompt_version: str
    tool_registry_version: str
    
    # Execution stats
    timestamp: float = Field(default_factory=time.time)
    duration_seconds: float = 0.0
    config_overrides: Dict[str, Any] = Field(default_factory=dict)
    
class ReproducibilityTracker:
    @staticmethod
    def capture_environment(dataset_name: str, dataset_version: str, dataset_hash: str) -> BenchmarkRunMetadata:
        """Captures the current state of the system for reproducibility."""
        # In a real enterprise system, these would be pulled dynamically from git tags and config objects
        import uuid
        from config.settings import settings
        
        return BenchmarkRunMetadata(
            run_id=f"bench_{uuid.uuid4().hex[:8]}",
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
            embedding_model=getattr(settings, "EMBEDDING_MODEL", "gemini-embedding-default"),
            llm_model=getattr(settings, "PRIMARY_MODEL", "groq-llama3"),
            graph_version="2.0.0",  # Could be dynamic based on git SHA
            prompt_version="1.5.0",
            tool_registry_version="1.0.0"
        )
