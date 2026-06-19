# NVIDIA INDIA AGENTIC AI OPEN HACKATHON

## Slide 1 — Cover
**Team Name:** Team Antigravity
**Track Selection:** Agentic AI for Governance & Public Sector
**Project Title:** RTI-Agent
**One-line Project Summary:** An autonomous, multi-agent AI platform that simplifies Right to Information (RTI) filing by seamlessly navigating government complexity, retrieving verifiable data, and ensuring human-in-the-loop governance.

***Speaker Notes:***
*Welcome the judges. Introduce the project as a paradigm shift in how citizens interact with government bureaucracy using Agentic AI.*

---

## Slide 2 — Team Introduction
**Our Team:**
We are a dedicated team of AI engineers and full-stack developers passionate about using agentic workflows to solve real-world public sector challenges.

**Expertise:**
* **AI Engineering:** Deep experience designing multi-agent workflows, managing LLM hallucinations, and building production-grade RAG pipelines.
* **Full Stack Development:** Expertise in scalable architectures using FastAPI, Next.js, and event-driven backends.
* **Agentic AI:** Advanced orchestration using LangGraph, handling dynamic tool selection, consensus building, and state management.
* **Open-Source & Hackathons:** Active contributors to the open-source AI ecosystem with a strong track record of delivering working prototypes under strict deadlines.

***Speaker Notes:***
*Highlight the balance between AI research skills and practical software engineering. Emphasize that this isn't just a wrapper—it's a deeply engineered agentic system.*

---

## Slide 3 — Skillset & Experience

| Category | Skills & Technologies |
| :--- | :--- |
| **Agentic Frameworks** | LangGraph, LangChain, Multi-Agent Systems |
| **Backend & APIs** | FastAPI, Python, AsyncIO |
| **Frontend** | Next.js, React, TypeScript |
| **Data & Vector Stores** | MongoDB, PostgreSQL, Redis, FAISS, RAG |
| **Security & Identity** | JWT Authentication, Role-Based Access Control (RBAC) |
| **Observability** | Prometheus, Grafana, Custom JSON Telemetry |
| **AI Evaluation** | Faithfulness & Relevancy Evaluation Frameworks |

**Current AI Deployment Architecture:**
Containerized microservices via Docker Compose, bridging an asynchronous FastAPI AI worker with a Next.js client, backed by MongoDB for state and Redis for caching.

***Speaker Notes:***
*Quickly run through the tech stack. Point out that the architecture is enterprise-ready, utilizing Prometheus/Grafana for observability and Redis for latency reduction.*

---

## Slide 4 — Problem Statement
**The Transparency Bottleneck:**
* **Information Discovery:** Citizens struggle to navigate fragmented, dense government websites to find public data.
* **Filing Complexity:** Drafting a legally sound RTI requires specific language and formatting that the average citizen lacks.
* **Department Identification:** Routing an RTI to the correct Public Information Officer (PIO) is confusing and often results in immediate rejection.
* **Document Navigation:** Parsing 100-page budgets, circulars, and notifications to find a single clause is practically impossible for non-experts.
* **Transparency Challenges:** The manual RTI response process is slow, opaque, and heavily burdened by bureaucratic backlog.

***Speaker Notes:***
*Tell a story here. Imagine a citizen trying to find out why a local infrastructure project is delayed. They don't know who to ask or how to ask it. RTI-Agent solves this.*

---

## Slide 5 — Project Overview
**Project Title:** RTI-Agent

**Executive Summary:**
RTI-Agent is an intelligent, multi-agent platform designed to democratize government transparency. It autonomously researches government corpora, drafts precise RTI requests, routes them to the correct departments, and empowers government officers to approve AI-generated responses through a Human-In-The-Loop (HITL) interface.

**Core Value Proposition:**
Reducing RTI resolution time from 30 days to minutes by augmenting public officers with Agentic AI, while providing citizens an effortless, conversational interface to their government.

**Stakeholders:**
1. **Citizens:** Effortless querying and drafting.
2. **Public Information Officers (PIOs):** AI-augmented drafting and approval.
3. **Administrators:** Full oversight via the Governance Console.

**Impact:**
Democratized transparency, reduced bureaucratic backlog, and restored public trust.

***Speaker Notes:***
*Focus on the dual-sided nature of the platform: it helps citizens draft, but critically, it helps government officers respond, ensuring adoption on both sides.*

---

## Slide 6 — System Architecture
**Citizen**
? *(Submits conversational query via Next.js UI)*
**AI Workflow (LangGraph Orchestrator)**
? *(Parses intent, selects tools, and manages agent state)*
**Department Routing**
? *(Identifies the correct jurisdictional department)*
**Government Knowledge Retrieval**
? *(FAISS-powered RAG against scraped government corpora)*
**Human Approval (HITL)**
? *(LangGraph interrupt; awaits PIO approval via Admin Dashboard)*
**Response Generation**
? *(Final formatting and streaming response back to the citizen)*

***Speaker Notes:***
*Walk through the data flow. Emphasize the "Human Approval" step—this is a strict LangGraph interrupt ensuring AI never speaks on behalf of the government without an officer's sign-off.*

---

## Slide 7 — Agentic AI Architecture
Our LangGraph implementation utilizes a highly specialized, multi-node architecture where each agent has a distinct persona and operational boundary.

* **outer_node**: Directs the flow based on intent (e.g., immediate answer vs. complex drafting).
* **planner_node**: Deconstructs complex citizen queries into actionable research steps.
* **info_fetcher_node & 	ool_selection_node**: Selects and executes specific API tools to gather live data.
* **etrieval_node**: Interfaces with the FAISS vector store to fetch relevant government context.
* **classifier_node**: Categorizes the request and infers the correct government department.
* **critic_node & debate_node**: Internal peer-review agents that challenge the retrieved facts for accuracy and bias.
* **erifier_node & eviewer_node**: Fact-checks the drafted response against original citations to prevent hallucinations.
* **consensus_node**: Aggregates internal debate into a unified, factual stance.
* **ormatter_node**: Formats the final draft into legally compliant RTI structures.
* **eflection_node**: Analyzes failures or low-confidence outputs and triggers re-planning.
* **memory_learning_node**: Extracts preferences and past context to improve future routing.
* **	racker_node**: Maintains the global state, tracking duration, token usage, and metadata.
* **pproval_node**: Halts the graph, sending a webhook to the Admin Dashboard for human authorization.

***Speaker Notes:***
*Highlight the debate_node and critic_node. This internal adversarial architecture ensures high factual accuracy before a human ever sees the draft.*

---

## Slide 8 — RAG Architecture
**Data Ingestion & Scraping:**
Custom web scrapers continuously ingest .gov.in domains, targeting structured notifications, circulars, and HTML content.
**Cleaning & Chunking:**
Documents are stripped of HTML/metadata, normalized, and split into semantically meaningful chunks to preserve legal context.
**Embeddings & Vector Store:**
Chunks are passed through dense embedding models and indexed locally into FAISS for ultra-fast, offline-capable vector searches.
**Retrieval & Re-ranking:**
User queries retrieve the top-K chunks. We apply department-level metadata filtering and re-ranking to prioritize highly relevant clauses over generic text.
**Citations & Confidence Scoring:**
Every generated sentence is strictly mapped to a source URL/Document, outputting a quantifiable "Retrieval Confidence Score" to the Admin dashboard.

***Speaker Notes:***
*Explain that standard RAG isn't enough for legal text. Our pipeline uses strict metadata filtering (by department) and absolute citation mapping so officers can instantly verify the source.*

---

## Slide 9 — Dataset Strategy
**Corpus Sources:**
* Government Portals & Departmental Websites (.gov.in)
* Publicly available PDFs (Budgets, Circulars, Notifications, Acts)
* Departmental FAQs and historical RTI responses.

**Dataset Scale & Roadmap:**
* **Current Dataset:** Seeded with localized, high-value government circulars and procedural PDFs demonstrating the pipeline.
* **Planned Scale:** Continuous scraping of major ministries (Finance, Transport, Infrastructure).
* **Licensing:** All data is assumed open-access under the Open Data Policy of India (NDSAP).

***Speaker Notes:***
*Acknowledge that government data is messy. Our scraping architecture is built to handle broken PDFs and unstructured HTML, structuring it for the vector database.*

---

## Slide 10 — Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | FastAPI, Python 3.10+, AsyncIO |
| **Frontend** | Next.js, React, Vanilla CSS, TypeScript |
| **AI Orchestration** | LangGraph, LangChain |
| **RAG & Vector Store** | FAISS, HuggingFace Embeddings |
| **Database** | MongoDB (State/Users), Redis (Caching) |
| **Observability** | Prometheus, Grafana, Custom Python Telemetry |
| **Authentication** | JWT, Role-Based Access Control (Admin/Citizen) |
| **Deployment** | Docker, Docker Compose |

***Speaker Notes:***
*Keep this brief. Emphasize that everything is containerized and ready for cloud-native deployment. We built our own custom telemetry to track Agent operations.*

---

## Slide 11 — Current Achievements
* **Multi-Agent Orchestration:** Successfully implemented a 16-node LangGraph architecture capable of planning, debating, and formatting.
* **Human-in-the-Loop Approval:** Hard-coded graph interrupts requiring JWT-authenticated Admin approval before finalizing responses.
* **Web Scraping & Retrieval:** End-to-end FAISS RAG pipeline ingesting real PDF/HTML government data with exact citations.
* **Admin Governance Console:** Built a Next.js dashboard tracking active agents, RAG corpus health, and system telemetry in real-time.
* **Advanced Security:** Custom PII redactors and prompt injection sanitizers integrated directly into the middleware.
* **Streaming Architecture:** Real-time token streaming from the FastAPI worker to the Next.js client for immediate user feedback.

***Speaker Notes:***
*These are not planned features—these are implemented, working achievements in our repository today.*

---

## Slide 12 — Innovation & Differentiators
**Why RTI-Agent is Different:**
* **Adversarial Agent Design:** Instead of a single LLM, we use critic and debate agents to argue over the facts, dramatically reducing hallucinations.
* **Explainable Retrieval:** We don't just provide an answer; we provide an "AI Risk Score" and exact document citations for the government officer.
* **Mandatory Human-in-the-Loop:** The AI is strictly an *augmenter*, not a *decider*. It drafts the response, but a human PIO must click 'Approve'.
* **Enterprise Telemetry:** Built-in JSON loggers specifically tracking LangGraph node execution times, tool usage, and prompt-injection attempts.
* **Government-Focused:** Optimized specifically for Indian bureaucratic structures, departmental routing, and legal formatting.

***Speaker Notes:***
*Focus on the 'Adversarial Agent Design' and 'HITL'. In government contexts, trust and safety are paramount. Our architecture guarantees both.*

---

## Slide 13 — Results & Metrics
Our custom observability pipeline (	elemetry.py & Prometheus) allows us to track deep operational metrics:

* **Retrieval Confidence:** Tracks the cosine similarity of fetched documents, flagging responses that fall below safe thresholds.
* **Agent Latency & Execution:** Logs exact millisecond execution times per LangGraph node (e.g., etrieval_node vs. debate_node).
* **Security Interventions:** Captures and counts blocked prompt injection and SQL injection attempts.
* **Approval Rates:** Monitors how often human PIOs accept, edit, or reject the AI-generated drafts.
* **Evaluation Scores:** Tracks Faithfulness and Answer Relevancy through our automated evaluation service framework.

***Speaker Notes:***
*We built the dashboard to prove the AI is working. Transparency isn't just for the citizens; the admins need transparency into the AI's "brain".*

---

## Slide 14 — Roadmap
**Current State:**
Fully functional multi-agent drafting, FAISS vector retrieval, and Human-in-the-Loop approval dashboard.

**Next Milestones:**
* **Multilingual Support:** Integrate translation nodes to support Hindi and regional languages natively.
* **Advanced RAG:** Migrate from FAISS to a scalable vector database like Qdrant or Milvus for billion-scale document querying.
* **Expanded Tool Ecosystem:** Give agents live API access to check train statuses, passport application statuses, and localized weather.

**Future Expansion:**
* **NVIDIA Ecosystem Integration:** Deploying on NVIDIA NIM microservices to drastically accelerate local LLM inference and embedding generation.
* **Direct Government Integrations:** Integrating directly with state portals via secure APIs.

***Speaker Notes:***
*We designed this locally but architected it to scale. Integrating NVIDIA NIMs will be our next major infrastructure leap.*

---

## Slide 15 — Long-Term Vision
**Building India's AI-Powered Government Intelligence Platform**

* **Citizen Empowerment:** Erasing the friction between the public and their constitutional right to information.
* **Public-Sector Transformation:** Freeing government officers from hours of bureaucratic backlog through intelligent, agentic augmentation.
* **Agentic Governance:** Proving that Multi-Agent Systems, bound by strict explainability and Human-In-The-Loop controls, can safely operate in the highest-stakes legal and public environments.

***Speaker Notes:***
*End on a high note. We aren't just building a chatbot; we are building a fundamental infrastructure layer for transparent governance.*
