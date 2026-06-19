# RTI-Agent Postman API Testing Suite

Welcome to the production-grade Postman API Testing Suite for the **RTI-Agent** backend platform (built with FastAPI and LangGraph multi-agent architecture). This suite is designed to fully test health checks, core RTI submission workflows, Server-Sent Events (SSE) streaming, RAG knowledge ingestion/retrieval, secure governance sandboxes, evaluation metrics, multilingual processes, and robust security/boundary validation.

---

## 📂 Testing Package Contents

The testing suite consists of the following components inside [tests/postman/](file:///C:/Users/akash/RTI_Agents/tests/postman):

### 1. JSON Exports
*   📁 **[RTI-Agent.postman_collection.json](file:///C:/Users/akash/RTI_Agents/tests/postman/RTI-Agent.postman_collection.json)**: The complete testing collection with all 41+ requests, customized realistic bodies, pre-request scripts, and automated assertions (`pm.test`).
*   ⚙️ **[RTI-Agent.postman_environment.json](file:///C:/Users/akash/RTI_Agents/tests/postman/RTI-Agent.postman_environment.json)**: The default environment file preconfigured with local endpoints and placeholders for API keys and runtime variables.

### 2. Deep-Dive Guides
*   📘 **[README.md](file:///C:/Users/akash/RTI_Agents/tests/postman/README.md)**: This master guide.
*   📊 **[generated_endpoints.md](file:///C:/Users/akash/RTI_Agents/tests/postman/generated_endpoints.md)**: Catalog of all 41+ discovered APIs, auth requirements, methods, and descriptions.
*   🔐 **[auth_flow.md](file:///C:/Users/akash/RTI_Agents/tests/postman/auth_flow.md)**: Details on role-based access control and `X-API-Key` headers inside Postman.
*   🔄 **[workflow_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/workflow_testing.md)**: Chained end-to-end integration flow testing (Submit ➔ Stream ➔ Approve ➔ Poll Status).
*   📡 **[sse_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/sse_testing.md)**: Guidelines for testing real-time Server-Sent Events `/stream/{request_id}` inside Postman.
*   🏛️ **[admin_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/admin_testing.md)**: Compliance monitoring, audit logs, and governance analytics testing.
*   🧠 **[rag_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/rag_testing.md)**: Knowledge ingestion, scrape crawlers, semantic searches, and document histories.
*   📈 **[evaluation_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/evaluation_testing.md)**: System quality, benchmarking, hallucination check, and trace replay tests.
*   ⚠️ **[failure_testing.md](file:///C:/Users/akash/RTI_Agents/tests/postman/failure_testing.md)**: Negative tests, validation errors, security limits, and injection defenses.
*   🚀 **[load_ready_groups.md](file:///C:/Users/akash/RTI_Agents/tests/postman/load_ready_groups.md)**: Collection runner and Newman automation guidelines for load and regression testing.

---

## 🚀 Getting Started

Follow these steps to import and run the testing suite:

### Step 1: Import Assets
1. Open **Postman** (Desktop app recommended).
2. Click the **Import** button in the top-left corner.
3. Drag and drop the two JSON files:
    *   `RTI-Agent.postman_collection.json`
    *   `RTI-Agent.postman_environment.json`
4. Confirm import. You will see the **RTI-Agent API Testing Suite** in your Collections tab and **RTI-Agent Environment** in your Environments tab.

### Step 2: Configure the Environment
1. In the top-right corner of Postman, select **RTI-Agent Environment** from the environment dropdown.
2. Edit the environment variables:
    *   Set **`BASE_URL`** to your running FastAPI instance URL (default: `http://localhost:8000`).
    *   Set **`API_KEY`** to your configured `RTI_API_KEY` (e.g., from `.env`, defaulting to `change-me-in-production` in development).
    *   (Optional) Modify role keys: `ADMIN_API_KEY`, `OFFICER_API_KEY`, `USER_API_KEY` (currently mapped to `API_KEY` for local validations).

### Step 3: Run Your First Test
1. Expand the **Health Check** folder in the collection.
2. Open the **Service Health Check** request.
3. Click **Send**.
4. In the response panel, click the **Test Results** tab. You should see 4 passing assertions!

---

## ⚙️ Automated Variables Chaining

This suite uses Postman scripting to automate complex multi-agent execution flows:
1. **`REQUEST_ID`**: Extracted from `POST /api/v1/submit` and used in subsequent streaming, approval, and compliance evaluations.
2. **`THREAD_ID`**: Extracted from `POST /api/v1/submit` and used to pull historical agent conversation transcripts.
3. **`TRACKING_ID`**: Extracted from `POST /api/v1/approve/{request_id}` and used to poll the final RTI document status and submit user feedback.
4. **`DOCUMENT_ID`**: Extracted from `POST /api/v1/rag/ingest` and used to fetch document history audits and versions.

---

## 📈 Latency Policy & Standards

All successful tests strictly assert:
*   **Response Status**: Exactly match the expected status (200, 202, 401, 404, or 422).
*   **Response Format**: Assert `Content-Type: application/json`.
*   **Response Latency**: Tested against a **5000ms threshold** to accommodate cold starts and deep LLM reasoning times in complex multi-agent loops (e.g., routing, self-reflection, drafting).
