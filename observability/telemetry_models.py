"""
observability/telemetry_models.py
----------------------------------
Strict JSON schemas for enterprise observability logs.
Enforces event-oriented logging taxonomy.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

# ── Taxonomy Enums ────────────────────────────────────────────────
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SecurityClassification(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    PII_DETECTED = "PII_DETECTED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    RATE_LIMIT_VIOLATION = "RATE_LIMIT_VIOLATION"
    TOOL_MISUSE = "TOOL_MISUSE"
    INVALID_TOKEN = "INVALID_TOKEN"

class Component(str, Enum):
    API = "api"
    GRAPH = "graph"
    NODE = "node"
    LLM = "llm"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    SECURITY = "security"
    AUDIT = "audit"

class Outcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DEGRADED = "degraded"

# ── Base Event Model ──────────────────────────────────────────────
class BaseTelemetryEvent(BaseModel):
    level: LogLevel = LogLevel.INFO
    event: str
    component: Component
    operation: str
    outcome: Outcome = Outcome.SUCCESS
    
    # Injected by formatter later, but declared for structure
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    graph_run_id: Optional[str] = None
    
class GraphExecutionEvent(BaseTelemetryEvent):
    component: Component = Component.GRAPH
    execution_time_ms: Optional[float] = None
    hitl_enabled: bool = False
    state_hash: Optional[str] = None
    changed_keys: Optional[List[str]] = None

class NodeExecutionEvent(BaseTelemetryEvent):
    component: Component = Component.NODE
    node_name: str
    execution_time_ms: Optional[float] = None
    estimated_cost_usd: float = 0.0
    tool_calls: int = 0
    
class LLMEvent(BaseTelemetryEvent):
    component: Component = Component.LLM
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: float = 0.0

class RetrievalEvent(BaseTelemetryEvent):
    component: Component = Component.RETRIEVAL
    query: str
    latency_ms: float = 0.0
    retrieved_documents: int = 0
    reranked_documents: int = 0
    final_context_docs: int = 0
    dropped_documents: int = 0
    cache_hit: bool = False

class SecurityEvent(BaseTelemetryEvent):
    component: Component = Component.SECURITY
    classification: SecurityClassification
    metadata: Dict[str, Any] = Field(default_factory=dict)
