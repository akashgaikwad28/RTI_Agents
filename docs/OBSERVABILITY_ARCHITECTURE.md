# RTI-Agent Enterprise Observability Architecture

This document describes the newly upgraded, enterprise-grade, event-oriented observability system for RTI-Agent.

## Architecture Overview

The system transitions from standard "message-logging" to structured "event-logging", where every action emits a strict JSON payload governed by Pydantic models. 

### Core Pillars
1. **Context Propagation (`contextvars`)**: `request_id`, `trace_id`, and `graph_run_id` flow through the entire stack, meaning you can trace a single API request down to the deepest LLM prompt or FAISS similarity search.
2. **Central Telemetry Facade**: All application code calls `observability.telemetry.telemetry` (e.g. `telemetry.log_node_event()`). This abstracts the logging backend, allowing easy future migration to Datadog, LangSmith, or OpenTelemetry.
3. **PII Redaction Pipeline**: Emails, phone numbers, Aadhaar, and PAN cards are automatically scrubbed from logs via regex patterns *before* being written to disk by `pii_redactor.py`.
4. **State Compression**: LangGraph states can become massive (MBs of data). `graph_tracer.py` computes state diffs (`changed_keys`) and SHA-256 hashes instead of logging full JSON dumps.

## Streams & Log Rotation

Logs are written to the `logs/` directory. They are rotated daily at midnight and kept for 14 days.

- `app.log`: Standard application lifecycle and HTTP request events.
- `error.log`: Exception taxonomy traces (e.g., `SecurityViolation`, `RetrievalError`).
- `security.log`: Dedicated audit trail for prompt injections, unauthorized access, and rate limiting.
- `audit.log`: Immutable state transition logs indicating when a human approved/rejected a workflow.
- `retrieval.log`: RAG provenance (which docs were retrieved, reranked, and eventually dropped).

## Trace Sampling

To prevent explosive storage costs, logs are sampled:
- **Errors, Security, HITL**: 100% recorded.
- **Standard Node Executions**: ~20% recorded.

## Grafana & Metrics

Prometheus metrics are exposed via `/metrics`.
A comprehensive Grafana dashboard is located at `observability/grafana/dashboard.json`, providing out-of-the-box panels for:
- API Request Latency
- Node-by-Node Graph Execution Time
- LLM Token Costs (Cumulative USD Tracker)
- Async Embedding Queue Depth
- Security Events / Prompt Injections per Hour
