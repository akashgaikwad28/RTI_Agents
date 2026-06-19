# Discovered API Endpoints Catalog

This document provides a complete catalog of the 41 active API endpoints discovered within the **RTI-Agent** backend, grouped logically by their functional domain.

---

## 🔒 Global Security Policy
*   All endpoints prefixed with `/api/v1/` are protected and **require** the **`X-API-Key`** header.
*   Endpoints `/health`, `/ready`, `/live`, `/metrics`, and standard docs routes `/docs` are public and do not require authentication.

---

## 📋 Complete API Directory

### 1. Health Checks
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | Performs detailed liveness, dependency (MongoDB, Redis, FAISS, Neon PG) and graph compiling health checks. |
| `GET` | `/ready` | None | Kubernetes readiness probe (returns `{"ready": true}`). |
| `GET` | `/live` | None | Kubernetes liveness probe (returns `{"alive": true}`). |

### 2. Core RTI Workflows & Lifecycle
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/submit` | `X-API-Key` | Submits a new raw RTI request. Sanitizes the query, initializes the multi-agent graph, and executes asynchronously until approval interrupt. |
| `POST` | `/api/v1/approve/{request_id}` | `X-API-Key` | Human-in-the-loop interface. Resumes graph execution with an approval or rejection decision. |
| `GET` | `/api/v1/status/{tracking_id}` | `X-API-Key` | Retrieves the processing status, active node, and final drafted response for a completed application. |
| `GET` | `/api/v1/thread/{thread_id}` | `X-API-Key` | Fetches the full conversational multi-agent transcript history of a request. |
| `POST` | `/api/v1/feedback` | `X-API-Key` | Logs citizen experience rating and comment for auditing and RLHF refinement. |
| `GET` | `/api/v1/stream/{request_id}` | `X-API-Key` | SSE endpoint that streams token-by-token reasoning traces, node state mutations, and progress updates. |

### 3. RAG Knowledge Base APIs
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/rag/ingest` | `X-API-Key` | Ingests raw text or parsed documents directly into the active vector database (FAISS or MongoDB Atlas). |
| `POST` | `/api/v1/rag/scrape` | `X-API-Key` | Triggers the web scraping crawler to index public government portals. |
| `GET` | `/api/v1/rag/status` | `X-API-Key` | Retrieves vector database choice and number of indexed chunks. |
| `GET` | `/api/v1/rag/stats` | `X-API-Key` | Retrieves vector store metrics and pipeline latency stats. |
| `POST` | `/api/v1/rag/query-test` | `X-API-Key` | Direct similarity search checking against vector stores without triggering the full multi-agent logic. |
| `POST` | `/api/v1/rag/multilingual-query`| `X-API-Key` | Cross-lingual similarity retrieval (automatically translates and retrieves). |
| `GET` | `/api/v1/rag/document-history/{document_id}` | `X-API-Key` | Audit trail of updates, edits, and ingestion history of a document. |
| `GET` | `/api/v1/rag/document-version/{document_id}/{version}` | `X-API-Key` | Retrieves a historical snapshot version of a document text and vector chunks. |
| `GET` | `/api/v1/rag/corpus-health` | `X-API-Key` | Runs integrity checks on embedding dimensions and index fragmentation. |

### 4. Governance & Compliance Sandbox
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/governance/tools` | `X-API-Key` | Lists all tools registered in the secure governance database. |
| `POST` | `/api/v1/governance/tools/{tool_name}/execute` | `X-API-Key` | Executes a database search or retrieval tool inside a secure, audited compliance sandbox. |
| `GET` | `/api/v1/governance/events` | `X-API-Key` | Fetches system logs and agent decisions for compliance verification. |
| `GET` | `/api/v1/governance/dashboard` | `X-API-Key` | Provides high-level security charts, risk scores, and audit totals. |
| `POST` | `/api/v1/governance/evaluate` | `X-API-Key` | Forces compliance/safety check on active workflow state. |

### 5. System Tools & Runtime Tracing
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tools` | `X-API-Key` | Lists standard LLM tools registered in the agent registry. |
| `GET` | `/api/v1/tools/status` | `X-API-Key` | Health and connectivity status of external API tools. |
| `POST` | `/api/v1/tools/query` | `X-API-Key` | Search for relevant tool definitions based on user query intent. |
| `GET` | `/api/v1/tools/traces/{trace_id}` | `X-API-Key` | Detailed execution trace of external tool calls. |
| `GET` | `/api/v1/tools/metrics` | `X-API-Key` | Tool usage, success rates, and execution time metrics. |
| `POST` | `/api/v1/tools/benchmark` | `X-API-Key` | Runs automated benchmarks across different prompt/tool options. |
| `POST` | `/api/v1/tools/replay` | `X-API-Key` | Replays a tool trace to debug issues or latency. |

### 6. Multilingual Processing Engine
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/multilingual/detect` | `X-API-Key` | Detects language (ISO 639-1 code) of the input text payload. |
| `POST` | `/api/v1/multilingual/translate` | `X-API-Key` | Translates text between supported regional Indian and international languages. |
| `POST` | `/api/v1/multilingual/retrieve` | `X-API-Key` | Performs cross-lingual semantic query matching. |
| `POST` | `/api/v1/multilingual/ocr` | `X-API-Key` | Submits image links to OCR scan regional government notices. |
| `GET` | `/api/v1/multilingual/stats` | `X-API-Key` | Retrieves translation caching metrics and language breakdown stats. |

### 7. Evaluation & Benchmarking
| Method | Endpoint | Required Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/eval/run` | `X-API-Key` | Starts an evaluation sweep on a named dataset checking answer correctness and grounding. |
| `GET` | `/api/v1/eval/reports` | `X-API-Key` | Lists all evaluation run audit reports. |
| `GET` | `/api/v1/eval/metrics` | `X-API-Key` | RAGAS/system evaluation averages (faithfulness, answer relevance). |
| `POST` | `/api/v1/eval/hallucination-check`| `X-API-Key` | Evaluates output text against provided reference context for factual deviations. |
| `POST` | `/api/v1/eval/replay` | `X-API-Key` | Re-runs a specific report trace to reproduce and verify accuracy improvements. |
| `GET` | `/api/v1/eval/benchmarks` | `X-API-Key` | Lists standard test datasets compiled in the system database. |
