# Observability, Metrics & Telemetry Architecture

This document defines the telemetry standards, Prometheus metrics collector, structured JSON logging framework, and LangSmith tracing integrations of the RTI-Agent multi-agent system.

---

## 1. Observability Framework Overview

The system is equipped with a complete, production-grade telemetry framework:

```mermaid
graph TD
    GraphRun[LangGraph Execution Run] --> Prometheus[1. Prometheus Telemetry counters/gauges/histograms]
    GraphRun --> JSONLogs[2. Structured JSON Logger log_level/stdout]
    GraphRun --> LangSmith[3. LangSmith Tracing correlation tracing]
    GraphRun --> TraceStore[4. ExecutionTraceStore Tool calling details]
```

These observability tiers ensure that system operations are transparent, trackable, and easy to debug in production.

---

## 2. Prometheus Instrumentation Specification

* **Real Code File**: [observability/metrics.py](file:///C:/Users/akash/RTI_Agents/observability/metrics.py)

The system exposes operational metrics via standard Prometheus collectors:

### 1. Latency Metrics
* **`rti_agent_duration`** (Histogram):
  * **Labels**: `agent` (e.g. `router_node`, `formatter_node`, `retrieval_node`).
  * **Purpose**: Tracks the execution time of each graph node, enabling precise latency profiling and bottleneck detection.

### 2. Retrieval Telemetry
* **`faiss_search_duration`** (Histogram):
  * **Purpose**: Measures raw FAISS index query latency.
* **`rti_retrieval_score`** (Histogram):
  * **Purpose**: Observes similarity scores for incoming queries, indicating knowledge base alignment.

### 3. Classification Metrics
* **`rti_classification_confidence`** (Counter):
  * **Labels**: `confidence` (`high`, `medium`, `low`).
  * **Purpose**: Monitors the confidence distribution of target department classifications.

### 4. Quality Control
* **`rti_hallucination_flags_total`** (Counter):
  * **Purpose**: Tracks the volume of hallucination issues flagged by the reviewer node, alerting developers to potential model regression.

### 5. Loop Tracking
* **`rti_retry_total`** (Counter):
  * **Labels**: `agent`.
  * **Purpose**: Tracks self-correction loop counts across nodes.

### 6. HITL Decisions
* **`rti_approval_decisions`** (Counter):
  * **Labels**: `decision` (`approved`, `rejected`).
  * **Purpose**: Monitors human reviewer validation rates.

---

## 3. Correlation Request Tracing

To trace a user query as it flows through the multi-agent graph, external tools, database inserts, and background tasks, the system implements a **correlation tracing strategy**:

```mermaid
sequenceDiagram
    autonumber
    participant Client as API Client
    participant Node as Graph Node (e.g. retrieval_node)
    participant Tool as Tool Executor
    participant DB as MongoDB
    
    Client->>Node: POST /submit (Generates request_id & thread_id)
    Node->>Tool: execute_tool(name, payload, context)
    Note over Tool: Injects request_id into ToolContext
    Tool->>DB: Save tool result with request_id
    Node->>DB: Save request document with request_id & thread_id
```

1. **Request Tracking**: Every new submission generates a unique `request_id` (UUID) and `thread_id` that are populated in the starting state.
2. **Context Propagation**: When a node invokes a tool, the `ToolExecutor` wraps the call in a `ToolContext`, injecting the `request_id` into the tool's execution thread.
3. **Audit Trail**: This correlation token is written to every JSON log entry and database insert, allowing developers to trace the complete end-to-end execution of a request across all systems.

---

## 4. Structured JSON Logging

* **Real Code File**: [observability/structured_logger.py](file:///C:/Users/akash/RTI_Agents/observability/structured_logger.py)

The system rejects traditional text streams in favor of structured JSON logging. This output is easily parsed by central logging tools (e.g., Elasticsearch, Datadog):
```json
{
  "timestamp": "2026-05-20T16:08:12.345Z",
  "level": "INFO",
  "logger": "graph.nodes.retrieval_node",
  "message": "[RetrievalNode] done | request_id=8f2b3c7a-92e1 | chunks=5 | cache_hit=false | confidence=0.884 | latency_ms=452",
  "request_id": "8f2b3c7a-92e1-4c3e-8b1a-85d72b21c432",
  "thread_id": "thread_8372"
}
```

---

## 5. LangSmith Integration

* **Configuration**: Managed via `LANGCHAIN_TRACING_V2` settings in [config/settings.py](file:///C:/Users/akash/RTI_Agents/config/settings.py).

When enabled (`LANGCHAIN_TRACING_V2=true`), the LangChain orchestrator automatically sends execution traces to the central LangSmith dashboard. This records nested tool invocations, prompt variations, output schemas, and API raw tokens, facilitating deep, visual debugging of agent chains.
