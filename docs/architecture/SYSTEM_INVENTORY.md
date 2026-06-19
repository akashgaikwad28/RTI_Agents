# System Inventory: Resource Registry & Matrix Tables

This document provides a complete registry of all logical, operational, data, and telemetry resources in the RTI-Agent enterprise system. It catalogs the graph nodes, registered MCP tools, database schemas, REST API endpoints, Redis cache topologies, and Prometheus metric suites.

---

## 1. Multi-Agent Graph Nodes Matrix (15 Nodes)

Below is the inventory of all 15 logical nodes compiled within the LangGraph StateGraph, detailing their primary python entry points and concrete duties.

| # | Node Identifier | Python Module | Input State Keys | Output State Keys | Technology / Model |
|---|---|---|---|---|---|
| **1** | `router_node` | `graph/nodes/router_node.py` | `raw_query`, `language` | `intent`, `sanitized_query`, `detected_language` | Llama 3.1 8B (Groq) |
| **2** | `planner_node` | `graph/nodes/planner_node.py` | `sanitized_query` | `execution_plan`, `selected_tools` | Custom Planner LLM |
| **3** | `formatter_node` | `graph/nodes/formatter_node.py` | `sanitized_query` | `formal_query`, `rti_template` | Llama 3.3 70B (Groq) |
| **4** | `classifier_node` | `graph/nodes/classifier_node.py` | `formal_query` | `department`, `sub_department`, `confidence` | Gemini 1.5 Pro |
| **5** | `tool_selection_node` | `graph/nodes/tool_selection_node.py` | `selected_tools` | `tool_results` | Parallel Tool Executor |
| **6** | `retrieval_node` | `graph/nodes/retrieval_node.py` | `formal_query`, `department` | `retrieved_context`, `retrieval_scores` | Multilingual Hybrid RAG |
| **7** | `debate_node` | `graph/nodes/debate_node.py` | `tool_results`, `formal_query` | `agent_debate` | Llama 3.3 70B (Groq) |
| **8** | `critic_node` | `graph/nodes/critic_node.py` | `formal_query`, `department` | `critic_feedback` | Rules Engine / Critic LLM |
| **9** | `verifier_node` | `graph/nodes/verifier_node.py` | `retrieved_context`, `formal_query` | `verification_report` | Custom Policy Verifier |
| **10** | `reviewer_node` | `graph/nodes/reviewer_node.py` | `formal_query`, `retrieved_context` | `review_passed`, `review_score`, `hallucination_flags` | Gemini 1.5 Pro |
| **11** | `approval_node` | `graph/nodes/approval_node.py` | `review_passed`, `approval_status` | `approval_timestamp`, `edited_query` | Human-in-the-Loop Gate |
| **12** | `reflection_node` | `graph/nodes/reflection_node.py` | `review_feedback`, `hallucination_flags` | `retry_count`, `sanitized_query` | Llama 3.3 70B (Groq) |
| **13** | `consensus_node` | `graph/nodes/consensus_node.py` | `review_score`, `grounding_score` | `consensus_result`, `ai_risk_score` | Analytics Engine |
| **14** | `memory_learning_node` | `graph/nodes/memory_learning_node.py` | `formal_query`, `tracking_id` | `learning_feedback` | FAISS Episodic Store |
| **15** | `tracker_node` | `graph/nodes/tracker_node.py` | `formal_query`, `consensus_result` | `tracking_id`, `final_response`, `status` | SMTP / MongoDB |

---

## 2. Model Context Protocol (MCP) Tools Registry (26 Tools)

RTI-Agent exposes **26 registered sandbox-safe tools** categorized into four key execution bundles. These tools are invoked by the `tool_selection_node` during the RAG phase.

### A. Government & Directory Services (8 Tools)
1. `department_lookup`: Maps queries to matching municipal directories.
2. `public_officer_lookup`: Fetches contact details of the active Public Information Officer (PIO).
3. `pune_smart_city_directory`: Queries Pimpri Chinchwad and Pune Municipal Corporation directory endpoints.
4. `section_rule_mapping`: Resolves statutory rules matching user grievances under the RTI Act, 2005.
5. `state_pio_resolver`: Resolves state-level vs. central-level PIO assignments.
6. `fees_calculator`: Resolves the required court fee stamps or transaction amounts per department.
7. `postal_address_resolver`: Returns precise office locations and PIN codes for physical submittals.
8. `appeal_officer_directory`: Identifies the correct First Appellate Authority (FAA) for escalation.

### B. Retrieval & Semantic Search (6 Tools)
9. `hybrid_search`: Executes concurrent keyword and semantic vectors lookup.
10. `policy_search`: Queries the local policy PDF registry for matching government circulars.
11. `citation_resolver`: Resolves document page numbers and matches quotes.
12. `historical_claims_search`: Evaluates past successful query templates.
13. `cross_lingual_expansion`: Translates and expands search tokens to regional languages (Hindi, Marathi).
14. `table_extractor`: Parses structured table files from document indexes.

### C. Utility & Text Analytics (6 Tools)
15. `translate_tool`: Standardizes inputs to English and localized targets.
16. `pii_redactor`: Scrubs inputs for mobile numbers, Aadhaar numbers, and addresses.
17. `unicode_normalizer`: Normalizes character encodings and handles ligature compositions.
18. `lang_detector`: Resolves mixed language compositions (Hinglish/Devanagari).
19. `transliterate_tool`: Transliterates Latin script strings to phonetic Devanagari.
20. `text_ocr_cleaner`: Corrects spelling mistakes in OCR-parsed text.

### D. Verification & Learning (6 Tools)
21. `grounding_scorer`: Computes overlap scores between drafts and source document text.
22. `policy_compliance_checker`: Assures the query matches Section 6(1) structural boundaries.
23. `hallucination_evaluator`: Flags ungrounded variables in legal drafts.
24. `episodic_memory_fetch`: Retrieves past user interactions.
25. `learning_feedback_logger`: Records execution success and failure vectors.
26. `smtp_dispatcher`: Sends mail alerts via secure TLS connection.

---

## 3. Database Schema & Collections

RTI-Agent uses a hybrid, multi-tier database setup featuring **MongoDB** (for workflow documents and Atlas Vector Search), **PostgreSQL** (Neon Serverless for resilient production checkpointers), **SQLite** (for local development checkpointers and diagnostics telemetry), and a **Dynamic Vector Store Factory** (which abstracts MongoDB Atlas Vector Search and local FAISS).

### Dynamic Vector Store Infrastructure
The system implements a unified vector database interface (`BaseVectorStore`) resolved dynamically at runtime by `rag.vectorstore.factory.get_vector_store()` depending on `VECTORSTORE_TYPE` in environment settings:
* **MongoDB Atlas Vector Search (`mongodb`)**: Cloud-native production RAG, utilizing a dedicated search index on `vector_chunks` with high-performance Python fallback.
* **FAISS (`faiss`)**: Local developer RAG, persisting vector structures to a serialized binary layout at `data/faiss_index`.
* **Embedding Space**: All vectors are calculated using `models/gemini-embedding-001` yielding **3,072 dimensions**.

### MongoDB Collections (`rti_database`)
* `rti_requests`: Stores complete workflow documents, current statuses, and historical user inputs.
  * *Indexes*: `request_id (Unique)`, `tracking_id (Sparse)`, `status`, `created_at`.
* `vector_chunks`: Stores RAG document chunks, active state indicators, and computed embeddings.
  * *Document Fields*: `_id` (String UUID), `chunk_id` (String), `text` (String), `embedding` (Array of floats, 3072 dims), `metadata` (Object including `chunk_index`, `content_hash`, `is_active`, `source`), `created_at` (Float timestamp).
  * *Indexes*: `chunk_id (Unique)`, `content_hash (Sparse)`, `metadata.is_active`, and a MongoDB Atlas **Vector Search Index** utilizing Cosine similarity.
* `episodic_memory`: Stores successful past applications formatted as vector-friendly documents.
  * *Indexes*: `embedding_hash`, `department`.
* `audit_logs`: Governance collection capturing system-wide changes, approvals, and error traces.
* `mcp_registry`: Stores available tools, sandbox boundaries, and authorization permissions.

### Checkpointers & Telemetry Databases
* **Neon Serverless PostgreSQL (Production State)**: Enabled when `CHECKPOINTER_TYPE=postgres`. Multi-instance, highly resilient LangGraph state saving, managed asynchronously via the custom `LazyPostgresCheckpointer` connection pool.
* **SQLite Checkpoint DB (`data/checkpoints/rti_checkpoints.db`)**: Local fallback enabled when `CHECKPOINTER_TYPE=sqlite`. Stores thread snapshots written by the `SqliteSaver` checkpointer. Used to freeze execution during HITL (Human-in-the-Loop) pause periods.
* **SQLite Diagnostics DB (`data/retrieval_traces.db`)**: Maintained by `RetrievalTraceLogger` to store high-fidelity diagnostics of vector search performance and retrieval validation telemetry.

---

## 4. REST API Endpoint Catalog

All REST API endpoints are exposed on port `8000` under the `/api/v1` route prefix.

| Method | Endpoint | Description | Payload Schema | Response Schema |
|---|---|---|---|---|
| **POST** | `/rti/submit` | Starts a new asynchronous RTI generation workflow. | `RTISubmitRequest` | `RTISubmitResponse` (202 Accepted) |
| **POST** | `/rti/approve/{request_id}` | Resumes a suspended workflow with approval or rejection. | `ApprovalRequest` | `ApprovalResponse` (200 OK) |
| **GET** | `/rti/status/{request_id}` | Polls the current workflow path and values. | *None* | `RTIStatusResponse` |
| **GET** | `/stream/{request_id}` | Event stream (Server-Sent Events) for live graph execution. | *None* | `text/event-stream` |
| **GET** | `/health` | Live-check system and database connectivity. | *None* | `HealthCheckResponse` |
| **GET** | `/eval/run` | Triggers a non-destructive retrieval validation benchmark. | *None* | `EvalReportResponse` |

---

## 5. Cache Topologies (Redis Cache)

* **Semantic Cache (`SemanticCache`)**:
  * **Engine**: Redis v7.2 (Async client `redis.asyncio`).
  * **Keyspace Pattern**: `rti:rag:<sha256_hash>`
  * **TTL**: `3600 seconds` (1 hour).
  * **Purpose**: Caches final deduplicated reranked retrieval results to avoid duplicate FAISS/LLM lookups for similar semantic queries.

---

## 6. Telemetry & Metrics (Prometheus)

All execution metrics are compiled and exposed on `/metrics` for scraping by Prometheus.

| Metric Identifier | Metric Type | Labels | Description |
|---|---|---|---|
| `rti_requests_total` | Counter | `intent` | Cumulative count of submitted RTI requests. |
| `rti_active_requests` | Gauge | *None* | Number of requests actively processing in the StateGraph. |
| `rti_agent_duration` | Histogram | `agent` | Latency distribution of individual agent node runs in seconds. |
| `rti_approval_decisions` | Counter | `decision` | Count of human choices: `"approved"` vs. `"rejected"`. |
| `rti_hallucination_flags_total` | Counter | *None* | Total number of hallucination flags raised by `reviewer_node`. |
| `rti_retry_total` | Counter | `agent` | Number of times the reflection loop has been executed. |
| `rag_retrieval_latency` | Histogram | *None* | Latency of the hybrid retrieval process. |
| `retrieval_hit_rate` | Counter | `source` | Count of search source paths: `"cache"`, `"faiss"`, or `"miss"`. |
