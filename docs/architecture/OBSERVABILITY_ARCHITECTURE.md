# Observability, Metrics & Telemetry Architecture

This document defines the telemetry standards, Prometheus metrics collector, structured JSON logging framework, and tracing integrations of the RTI-Agent multi-agent system.

---

## 1. Tracing Frameworks

To monitor both API performance and complex agent reasoning, we implement dual tracing:
* **LangSmith (`langchain_tracing_v2`)**: Configured in `observability/tracing.py`. It traces the LangGraph execution flow. It visualizes the multi-agent decision steps, inputs, outputs, tool invocations, and intermediate states. 
* **OpenTelemetry (`opentelemetry-sdk`)**: Instruments the FastAPI backend to capture standard distributed tracing and performance metrics across API routes and background tasks.

---

## 2. Monitoring & Metrics (Prometheus)

The system exposes operational metrics via standard Prometheus collectors defined in `observability/metrics.py`. These can be scraped by Prometheus and visualized in Grafana dashboards.

### Core Metrics Exposing:
* **`rti_requests_total`** (Counter): Tracks incoming requests.
* **`rti_agent_duration_seconds`** (Histogram): Tracks the execution time of each graph node, enabling precise latency profiling.
* **`faiss_search_duration`** (Histogram): Measures raw FAISS index query latency.
* **`rti_retrieval_score`** (Histogram): Observes similarity scores for incoming queries.
* **`rti_cache_hits_total`** (Counter): Monitors semantic cache efficiency.

---

## 3. Structured JSON Logging

The system rejects traditional text logs in favor of structured JSON logging using `python-json-logger`. This makes logs highly searchable in Datadog or ELK.

### Logging Modules:
* **`audit_logger.py`**: Logs major business events (e.g., successful PDF generation).
* **`security_logger.py`**: Logs security violations (e.g., prompt injections caught by Llama Guard).
* **`exception_logger.py`**: Handles and formats stack traces for system crashes.

### PII Log Redaction
Crucially, before any log is written to stdout or a file, the `observability/pii_redactor.py` module scrubs sensitive data (Aadhaar, Phone numbers) to ensure that PII is never leaked into the logging infrastructure.

### Example JSON Log:
```json
{
  "timestamp": "2026-05-20T16:08:12.345Z",
  "level": "INFO",
  "logger": "graph.nodes.retrieval_node",
  "message": "[RetrievalNode] done | request_id=8f2b3c7a-92e1 | chunks=5 | cache_hit=false | confidence=0.884 | latency_ms=452",
  "request_id": "8f2b3c7a-92e1-4c3e-8b1a-85d72b21c432"
}
```

---

## 4. Correlation Request Tracing

To trace a user query as it flows through the multi-agent graph, external tools, database inserts, and background tasks, the system implements a **correlation tracing strategy**:

1. **Request Tracking**: Every new submission generates a unique `request_id` (UUID).
2. **Context Propagation**: When a node invokes a tool, the `request_id` is injected into the tool's execution thread.
3. **Audit Trail**: This correlation token is written to every JSON log entry and database insert, allowing developers to trace the complete end-to-end execution.
