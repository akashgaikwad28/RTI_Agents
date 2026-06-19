"""
Dataset manifest schema for versioning and reproducibility.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class BenchmarkQuery(BaseModel):
    id: str
    query: str
    expected_department: Optional[str] = None
    expected_facts: List[str] = Field(default_factory=list)
    expected_hallucination: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DatasetManifest(BaseModel):
    dataset_name: str
    version: str
    description: str
    language: str = "en"
    created_at: float = Field(default_factory=time.time)
    queries: List[BenchmarkQuery]
    hash: Optional[str] = None
