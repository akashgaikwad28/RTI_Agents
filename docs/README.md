# RTI-Agent Technical Documentation Suite

Welcome to the **RTI-Agent Technical Documentation Portal**. This repository contains a comprehensive, enterprise-grade documentation suite describing the Right to Information (RTI) multi-agent orchestrator powered by LangGraph.

This suite consists of **25 technical manuals** that reflect the actual implemented python production code, schemas, and pipelines. It provides system engineers, policy administrators, and developers with everything required to operate, evaluate, and scale the RTI drafting ecosystem.

---

## 🚀 Navigation Quick Links

To explore the codebase and architecture, choose one of the index entries below:

* 🗣️ **[Plain-English System Guide](file:///C:/Users/akash/RTI_Agents/docs/SYSTEM_PLAIN_ENGLISH_GUIDE.md)** — A comprehensive, non-technical explanation of the entire workflow, perfect for users and administrators with basic AI knowledge.
* 🗺️ **[System Map & Directory](file:///C:/Users/akash/RTI_Agents/docs/SYSTEM_MAP.md)** — Interactive map and visual topological layout of the entire system.
* 📦 **[Resource & Resource Inventory](file:///C:/Users/akash/RTI_Agents/docs/architecture/SYSTEM_INVENTORY.md)** — Core matrix tables detailing all 15 graph nodes, 26 registered MCP tools, SQLite/MongoDB structures, API routes, Redis configurations, and Prometheus metric catalogs.
* 🔄 **[LangGraph Execution Flow](file:///C:/Users/akash/RTI_Agents/docs/architecture/LANGGRAPH_EXECUTION_FLOW.md)** — Graph setup, StateGraph compilation, node connections, and execution loops.
* 🛡️ **[Security & Policy Controls](file:///C:/Users/akash/RTI_Agents/docs/architecture/SECURITY_ARCHITECTURE.md)** — Regex input checks, PII redaction, rate limits, and network boundary rules.

---

## 📂 Documentation Suite Directory

```
docs/
├── SYSTEM_MAP.md                       # Topological visual directory
├── README.md                           # Landing portal (This file)
│
├── agents/                             # Agent & Node operational manuals
│   ├── AGENT_SYSTEM_OVERVIEW.md        # Master 15-node orchestration design
│   ├── router_agent.md                 # Sanitizer and intent classification gate
│   ├── planner_agent.md                # Task planning and tool discovery
│   ├── formatter_agent.md              # Section 6(1) legal draft formatter
│   ├── classifier_agent.md             # Department mapping directory classifier
│   ├── retrieval_agent.md              # Multilingual RAG context fetcher
│   ├── reviewer_agent.md               # Senior QA groundedness evaluator
│   ├── reflection_agent.md             # Autonomous query rewriting loop
│   ├── approval_agent.md               # Human-in-the-loop pause-resume gate
│   └── tracker_agent.md                # Submittal ID tracker and dispatcher
│
├── architecture/                       # System platform internals
│   ├── LANGGRAPH_EXECUTION_FLOW.md     # StateGraph and router engine
│   ├── RAG_RETRIEVAL_FLOW.md           # FAISS index and PDF ingestion OCR
│   ├── SECURITY_ARCHITECTURE.md        # Input sanitization and redaction
│   └── SYSTEM_INVENTORY.md             # Master registry of system resources
│
├── state/
│   └── STATE_ARCHITECTURE.md           # RTIAgentState property schemas
│
├── memory/
│   └── MEMORY_ARCHITECTURE.md          # FAISS Episodic and Redis semantic caches
│
├── tools/
│   └── TOOL_CALLING_ARCHITECTURE.md    # MCP registry and sandbox gather
│
├── governance/
│   └── HITL_GOVERNANCE_FLOW.md         # Risk threshold escalations
│
├── observability/
│   └── OBSERVABILITY_ARCHITECTURE.md   # Prometheus metrics and JSON trace logs
│
└── workflows/                          # Interactive execution walkthrough traces
    ├── new_rti_submission_flow.md      # Trace: Standard user submission
    ├── multilingual_query_flow.md      # Trace: Hinglish query to Marathi response
    ├── hallucination_recovery_flow.md  # Trace: Quality gate failure self-correction
    ├── approval_resume_flow.md         # Trace: HITL paused thread resume path
    └── retrieval_debug_flow.md         # Trace: RAG diagnostics and offline sqlite logs
```

---

## 🛠️ System Overview & Tech Stack

The RTI-Agent is built on a modern, robust agentic architecture designed for maximum reliability, transparency, and safety:

* **Core Framework**: LangGraph v0.2 / v3 + LangChain core.
* **State Management**: Resilient state thread persistence utilizing LangGraph checkpointers, supporting both Neon Serverless PostgreSQL (`LazyPostgresCheckpointer`) for production and SQLite for local development.
* **Semantic Vector Databases**: Dynamic vector search resolved by a unified factory supporting MongoDB Atlas Vector Search (`vector_chunks` collection) and local hybrid indexes compiled with FAISS.
* **NoSQL Persistence**: MongoDB Atlas for workflow request tracking, audit logging, and active vector search chunks.
* **Fast Caching**: Redis-backed semantic caching wrapper for low-latency searches.
* **Primary LLMs**: Gemini 1.5 Pro (Classification and Quality Gates), Llama 3.3 70B (Orchestration, Planner, and Reflection loops), Llama 3.1 8B (Router).
* **Metrics Telemetry**: Custom metric endpoints exposed for Prometheus scraping + Grafana visualizer integration.
* **Trace Logging**: Structured JSON logging and localized SQLite trace logs (`data/retrieval_traces.db`) for diagnostic replays.
