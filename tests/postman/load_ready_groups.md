# Command Line Automation & Load Testing Guide

This guide explains how to execute the Postman testing suite from your terminal, integrate it into CI/CD pipelines, and prepare requests for load and regression testing.

---

## 🏃 Running Tests from the Command Line (Newman)

**Newman** is the official command-line collection runner for Postman. It allows you to run your testing collections directly from terminal scripts, making it easy to automate regression checks.

### Step 1: Install Newman
Newman is built on Node.js. Install it globally using npm:
```bash
npm install -g newman
```

### Step 2: Execute the Test Suite
Navigate to your project root and run the collection, supplying the environment variables:
```bash
newman run tests/postman/RTI-Agent.postman_collection.json \
           -e tests/postman/RTI-Agent.postman_environment.json
```
Newman will run all 41+ requests sequentially, execute the embedded JavaScript tests, and print a comprehensive summary table showing successful and failed assertions directly in your terminal.

---

## 📂 Categorized Request Grouping for Performance Checks

When executing performance, stress, or load tests, endpoints must be treated differently based on their resource footprint.

```
┌────────────────────────────────────────────────────────┐
│              RTI-Agent API Load Groups                 │
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  [Group 1: Health]   [Group 2: REST]     [Group 3: Heavy]
  - /health           - /rag/status       - /submit
  - /ready            - /status/{id}      - /rag/ingest
  - /live             - /multilingual     - /eval/run
  (High Throughput)   (Medium Load)       (Low & Delayed)
```

### Group 1: High-Throughput Diagnostics (Health Checks)
*   **Endpoints**: `/health`, `/ready`, `/live`
*   **Behavior**: Fast, in-memory status returns (with occasional database pings).
*   **Load Profile**: Can be run at **high concurrency** (e.g. hundreds of requests/sec) to test server limits, uvicorn workers capacity, and load balancer readiness.

### Group 2: Standard REST Operations
*   **Endpoints**: `/api/v1/rag/status`, `/api/v1/status/{tracking_id}`, `/api/v1/multilingual/detect`
*   **Behavior**: Performs indexed database reads or localized operations.
*   **Load Profile**: Safe for **medium load** sweeps. Asserts database connection pooling remains healthy.

### Group 3: High-Resource Operations (Agent Workflow & RAG Ingest)
*   **Endpoints**: `POST /api/v1/submit`, `POST /api/v1/rag/ingest`, `POST /api/v1/eval/run`
*   **Behavior**: Invokes Groq/Gemini LLM calls, FAISS/MongoDB vector store writing, or complex LangGraph state processing.
*   **Load Profile**: **DO NOT load test these at high concurrency without delays.** Doing so will quickly hit LLM provider rate limits (TPM/RPM limits) or incur substantial API charges. Run these using realistic delay intervals (e.g., a ramp-up model simulating a few concurrent users with 5-10 second thinking-time delays between requests).

---

## 🚀 CI/CD Pipeline Integration

You can integrate the testing suite into your CI/CD runner (e.g. GitHub Actions) to prevent regressions.

### Example GitHub Actions Workflow (`.github/workflows/api-tests.yml`):
```yaml
name: API Regression Testing

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  api-test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017
      redis:
        image: redis:latest
        ports:
          - 6379:6379

    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-level: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Start FastAPI App
        env:
          MONGO_URI: mongodb://localhost:27017/
          REDIS_URL: redis://localhost:6379/0
          RTI_API_KEY: test-cicd-key
        run: |
          uvicorn api.main:app --port 8000 &
          sleep 5 # Wait for app startup

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Newman
        run: npm install -g newman

      - name: Run Postman Tests
        run: |
          newman run tests/postman/RTI-Agent.postman_collection.json \
            -e tests/postman/RTI-Agent.postman_environment.json \
            --env-var "API_KEY=test-cicd-key"
```
This guarantees that any changes to your routers, databases, or agent states will automatically be validated against the 41-endpoint assertion sweep before merging!
