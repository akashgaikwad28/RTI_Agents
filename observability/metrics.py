"""
observability/metrics.py
-------------------------
Prometheus metrics registry for RTI-Agent.
Import individual metrics into nodes/agents as needed.
"""

from prometheus_client import Counter, Histogram, Gauge


# ── Request Counters ──────────────────────────────────────────────
rti_requests_total = Counter(
    "rti_requests_total",
    "Total RTI requests processed",
    ["intent"],  # labels: new_request | status_check | followup
)

rti_submissions_total = Counter(
    "rti_submissions_total",
    "Total RTI applications submitted",
    ["status"],  # labels: submitted | failed | escalated
)

# ── Agent Duration (Histogram) ────────────────────────────────────
rti_agent_duration = Histogram(
    "rti_agent_duration_seconds",
    "Agent execution duration in seconds",
    ["agent"],  # labels: router_node | formatter_node | ...
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# ── Classification ────────────────────────────────────────────────
rti_classification_confidence = Counter(
    "rti_classification_confidence_total",
    "Department classification confidence distribution",
    ["confidence"],  # labels: high | medium | low
)

# ── Retrieval ─────────────────────────────────────────────────────
rti_retrieval_score = Histogram(
    "rti_retrieval_score",
    "Average semantic retrieval similarity score",
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0],
)

rti_cache_hits_total = Counter(
    "rti_cache_hits_total",
    "Semantic cache hits for retrieval",
)

documents_ingested_total = Counter(
    "documents_ingested_total",
    "Total RAG document chunks ingested",
    ["source"],
)

scrape_failures_total = Counter(
    "scrape_failures_total",
    "Total government scraper failures",
    ["target"],
)

rag_retrieval_latency = Histogram(
    "rag_retrieval_latency_seconds",
    "End-to-end RAG retrieval latency in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
)

faiss_search_duration = Histogram(
    "faiss_search_duration_seconds",
    "FAISS similarity search duration in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
)

retrieval_hit_rate = Counter(
    "retrieval_hit_rate_total",
    "RAG retrieval outcomes by source",
    ["source"],
)

cache_hit_rate = Counter(
    "cache_hit_rate_total",
    "Cache hits by cache name",
    ["cache"],
)

tool_executions_total = Counter(
    "tool_executions_total",
    "Tool executions by tool and status",
    ["tool", "status"],
)

tool_execution_duration = Histogram(
    "tool_execution_duration_seconds",
    "Tool execution latency in seconds",
    ["tool"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30],
)

agent_reasoning_events_total = Counter(
    "agent_reasoning_events_total",
    "Auditable reasoning events emitted by agents",
    ["agent"],
)

# ── Quality / Hallucination ───────────────────────────────────────
rti_hallucination_flags_total = Counter(
    "rti_hallucination_flags_total",
    "Total hallucination flags detected by ReviewerNode",
)

rti_review_score = Histogram(
    "rti_review_score",
    "ReviewerNode quality score distribution",
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0],
)

# ── HITL Approval ─────────────────────────────────────────────────
rti_approval_decisions = Counter(
    "rti_approval_decisions_total",
    "Human approval decisions",
    ["decision"],  # labels: approved | rejected
)

# ── Retry / Reflection ────────────────────────────────────────────
rti_retry_total = Counter(
    "rti_retry_total",
    "Total reflection/retry cycles",
    ["agent"],
)

# ── LLM Token Usage ───────────────────────────────────────────────
rti_token_usage_total = Counter(
    "rti_token_usage_total",
    "Total LLM tokens consumed",
    ["model"],  # labels: groq | gemini | openai
)

# ── Active Requests ───────────────────────────────────────────────
rti_active_requests = Gauge(
    "rti_active_requests",
    "Number of RTI requests currently being processed",
)

multilingual_requests_total = Counter(
    "multilingual_requests_total",
    "Multilingual requests by language and operation",
    ["language", "operation"],
)

translation_latency = Histogram(
    "translation_latency_seconds",
    "Translation latency by source and target language",
    ["source_language", "target_language"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30],
)

multilingual_retrieval_confidence = Histogram(
    "multilingual_retrieval_confidence",
    "Cross-lingual retrieval confidence by language",
    ["language"],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0],
)

ocr_accuracy_score = Histogram(
    "ocr_accuracy_score",
    "OCR confidence score by language set",
    ["languages"],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0],
)

# ── Financial & Costs ─────────────────────────────────────────────
rti_estimated_cost_usd = Counter(
    "rti_estimated_cost_usd_total",
    "Estimated LLM token cost in USD",
    ["model", "provider"],
)

rti_graph_cost_usd = Histogram(
    "rti_graph_cost_usd",
    "Total cost per graph execution in USD",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

# ── Queue Monitoring ──────────────────────────────────────────────
rti_embedding_queue_depth = Gauge(
    "rti_embedding_queue_depth",
    "Current depth of the async embedding queue",
)

rti_worker_utilization = Gauge(
    "rti_worker_utilization_percent",
    "Worker pool utilization percentage",
)

# ── System Performance ────────────────────────────────────────────
rti_memory_usage_mb = Gauge(
    "rti_memory_usage_mb",
    "Current memory usage of the RTI Agent process in MB",
)

rti_cpu_usage_percent = Gauge(
    "rti_cpu_usage_percent",
    "Current CPU usage of the RTI Agent process",
)

rti_event_loop_lag = Gauge(
    "rti_event_loop_lag_seconds",
    "Asyncio event loop lag / blocking time",
)

rti_redis_latency = Histogram(
    "rti_redis_latency_seconds",
    "Latency of Redis operations",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5],
)

rti_mongodb_latency = Histogram(
    "rti_mongodb_latency_seconds",
    "Latency of MongoDB operations",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5],
)

# ── Security Events ───────────────────────────────────────────────
rti_security_events_total = Counter(
    "rti_security_events_total",
    "Total security events detected by taxonomy",
    ["classification"],
)

