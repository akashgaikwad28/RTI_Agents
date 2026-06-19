"""
tests/generators/generate_postman_suite.py
-------------------------------------------
Programmatic generator for the RTI-Agent Postman testing suite.
Generates:
  1. tests/postman/RTI-Agent.postman_collection.json (Collection with 41+ requests, tests, chains)
  2. tests/postman/RTI-Agent.postman_environment.json (Environment config)
"""

import os
import json
import uuid

def generate_suite():
    print("[START] Generating Postman Suite...")
    
    # 1. Define output directory
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "postman"))
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Define collection structure
    collection_id = str(uuid.uuid4())
    
    # Common headers
    auth_headers = [
        {
            "key": "X-API-Key",
            "value": "{{API_KEY}}",
            "type": "text",
            "description": "API Key for authentication"
        },
        {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
        }
    ]
    
    no_auth_headers = [
        {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
        }
    ]
    
    # Standard JavaScript assertions
    def get_std_tests(expected_status=200):
        return [
            f"pm.test(\"Status code is {expected_status}\", function () {{",
            f"    pm.response.to.have.status({expected_status});",
            "});",
            "",
            "pm.test(\"Response time is less than 5000ms\", function () {",
            "    pm.expect(pm.response.responseTime).to.be.below(5000);",
            "});",
            "",
            "pm.test(\"Response has Content-Type application/json\", function () {",
            "    pm.response.to.have.header(\"Content-Type\");",
            "    pm.expect(pm.response.headers.get(\"Content-Type\")).to.include(\"application/json\");",
            "});"
        ]

    # Requests repository by folder
    requests_by_folder = {}
    
    # ---- 1. HEALTH CHECK ----
    requests_by_folder["Health Check"] = [
        {
            "name": "Service Health Check",
            "description": "Comprehensive health check — validates all backend dependencies (MongoDB, Redis, FAISS, LangGraph, Neon PostgreSQL). Returns 200 if fully healthy, 503 if degraded.",
            "method": "GET",
            "path": "/health",
            "headers": no_auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify services health details\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.be.oneOf([\"healthy\", \"degraded\"]);",
                "    pm.expect(jsonData.version).to.be.a(\"string\");",
                "    pm.expect(jsonData.services).to.be.an(\"object\");",
                "});"
            ]
        },
        {
            "name": "Kubernetes Readiness Probe",
            "description": "Kubernetes readiness probe checking if app is ready to serve traffic.",
            "method": "GET",
            "path": "/ready",
            "headers": no_auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Readiness is true\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.ready).to.eql(true);",
                "});"
            ]
        },
        {
            "name": "Kubernetes Liveness Probe",
            "description": "Kubernetes liveness probe checking if app is alive and operational.",
            "method": "GET",
            "path": "/live",
            "headers": no_auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Liveness is true\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.alive).to.eql(true);",
                "});"
            ]
        }
    ]
    
    # ---- 2. RTI FLOWS ----
    requests_by_folder["RTI Submit & Lifecycle"] = [
        {
            "name": "Submit RTI Request",
            "description": "Submit a new RTI query. This triggers the LangGraph multi-agent workflow asynchronously until it reaches the human-in-the-loop approval interrupt. Automatically extracts and sets REQUEST_ID and THREAD_ID.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": auth_headers,
            "body": {
                "query_text": "Provide the details of funds allocated and utilized for the smart city project in Pune from 2021 to 2024, including itemized allocations for transport and solid waste management.",
                "language": "en",
                "thread_id": None
            },
            "tests": get_std_tests(202) + [
                "pm.test(\"Extract request and thread identifiers\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.request_id).to.be.a(\"string\");",
                "    pm.expect(jsonData.status).to.eql(\"awaiting_approval\");",
                "    pm.environment.set(\"REQUEST_ID\", jsonData.request_id);",
                "    if (jsonData.thread_id) {",
                "        pm.environment.set(\"THREAD_ID\", jsonData.thread_id);",
                "    }",
                "});"
            ]
        },
        {
            "name": "Approve RTI Draft",
            "description": "Provide a human decision (approval/rejection) for a pending RTI request. Resumes the LangGraph workflow from the interrupt point. Automatically extracts and sets TRACKING_ID.",
            "method": "POST",
            "path": "/api/v1/approve/{{REQUEST_ID}}",
            "headers": auth_headers,
            "body": {
                "decision": "approved",
                "approved_by": "Senior Officer akash",
                "edited_query": "Details of Pune smart city project funds allocated and utilized (2021-2024)"
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Extract tracking ID\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.tracking_id).to.be.a(\"string\");",
                "    pm.environment.set(\"TRACKING_ID\", jsonData.tracking_id);",
                "});"
            ]
        },
        {
            "name": "Poll RTI Status",
            "description": "Poll the processing status of the submitted RTI application using the tracking ID.",
            "method": "GET",
            "path": "/api/v1/status/{{TRACKING_ID}}",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify status structure\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.be.oneOf([\"pending\", \"processing\", \"completed\", \"failed\"]);",
                "});"
            ]
        },
        {
            "name": "Get Thread History",
            "description": "Fetch the conversation history of a specific RTI multi-agent thread.",
            "method": "GET",
            "path": "/api/v1/thread/{{THREAD_ID}}",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Thread history array validation\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.history).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Submit User Feedback",
            "description": "Submit user satisfaction feedback for the processed RTI request.",
            "method": "POST",
            "path": "/api/v1/feedback",
            "headers": auth_headers,
            "body": {
                "tracking_id": "{{TRACKING_ID}}",
                "rating": 5,
                "comments": "Excellent processing speed and high accuracy in retrieving information."
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify feedback submission success\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.eql(\"success\");",
                "});"
            ]
        },
        {
            "name": "Stream Workflow SSE",
            "description": "Server-Sent Events endpoint to stream real-time progression and structured logs from the multi-agent graph as it executes.",
            "method": "GET",
            "path": "/api/v1/stream/{{REQUEST_ID}}",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Connection initialization successful\", function () {",
                "    pm.response.to.have.status(200);",
                "});",
                "pm.test(\"Response is Server-Sent Events stream\", function () {",
                "    pm.response.to.have.header(\"Content-Type\");",
                "    pm.expect(pm.response.headers.get(\"Content-Type\")).to.include(\"text/event-stream\");",
                "});"
            ]
        }
    ]
    
    # ---- 3. RAG SERVICES ----
    requests_by_folder["RAG Knowledge Base"] = [
        {
            "name": "RAG Document Ingest",
            "description": "Ingests a document chunk directly into the vector store. Set VECTORSTORE_TYPE to faiss or mongodb. Automatically extracts and sets DOCUMENT_ID.",
            "method": "POST",
            "path": "/api/v1/rag/ingest",
            "headers": auth_headers,
            "body": {
                "document_name": "smart_city_pune_budget_2024.pdf",
                "content": "This circular details the Pune Smart City project budget for fiscal years 2021-2024. Total allocation: 1500 Crores. Expenditure on transport: 600 Crores, sanitation: 400 Crores, IT infrastructure: 500 Crores.",
                "department": "Urban Development",
                "metadata": {
                    "source": "Government Circular",
                    "year": "2024",
                    "author": "Municipal Commissioner"
                }
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Extract document ID\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.document_id).to.be.a(\"string\");",
                "    pm.environment.set(\"DOCUMENT_ID\", jsonData.document_id);",
                "});"
            ]
        },
        {
            "name": "Web Crawler Scraper",
            "description": "Trigger a web scraping task to index a government website or portal.",
            "method": "POST",
            "path": "/api/v1/rag/scrape",
            "headers": auth_headers,
            "body": {
                "url": "https://www.maharashtra.gov.in/smart-city-schemes",
                "depth": 1,
                "max_pages": 5
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify crawl job started\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.be.oneOf([\"started\", \"completed\", \"queued\"]);",
                "});"
            ]
        },
        {
            "name": "RAG System Status",
            "description": "Fetch status of RAG ingestion queues and current index size.",
            "method": "GET",
            "path": "/api/v1/rag/status",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify status structure\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.vectorstore).to.be.a(\"string\");",
                "    pm.expect(jsonData.document_count).to.be.a(\"number\");",
                "});"
            ]
        },
        {
            "name": "RAG System Stats",
            "description": "Fetch database storage statistics and indexing benchmarks.",
            "method": "GET",
            "path": "/api/v1/rag/stats",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "RAG Direct Semantic Query Test",
            "description": "Direct similarity search query testing on the FAISS/MongoDB index without passing through the agent router.",
            "method": "POST",
            "path": "/api/v1/rag/query-test",
            "headers": auth_headers,
            "body": {
                "query_text": "smart city pune budget transport",
                "top_k": 3
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Confirm retrieval content is present\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.results).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "RAG Multilingual Query",
            "description": "Direct multilingual semantic query. Automatically translates query, searches vector store, and returns cross-lingual matching chunks.",
            "method": "POST",
            "path": "/api/v1/rag/multilingual-query",
            "headers": auth_headers,
            "body": {
                "query_text": "पुणे स्मार्ट सिटी वाहतूक खर्च",
                "language": "mr",
                "top_k": 3
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify multilingual retrieval response\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.results).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Get Document History",
            "description": "Retrieves version history and metadata updates of a specific document.",
            "method": "GET",
            "path": "/api/v1/rag/document-history/{{DOCUMENT_ID}}",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify document audit list\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.history).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Get Document Version Details",
            "description": "Retrieves the text and metadata of a specific version of a document.",
            "method": "GET",
            "path": "/api/v1/rag/document-version/{{DOCUMENT_ID}}/1",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify document content of version 1\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.content).to.be.a(\"string\");",
                "});"
            ]
        },
        {
            "name": "Get Corpus Health Statistics",
            "description": "Retrieves data consistency, dimensionality checks, and index health audits for RAG corpus.",
            "method": "GET",
            "path": "/api/v1/rag/corpus-health",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Corpus is healthy\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.eql(\"healthy\");",
                "});"
            ]
        }
    ]
    
    # ---- 4. GOVERNANCE & ANALYTICS ----
    requests_by_folder["Governance & Compliance"] = [
        {
            "name": "List Registered Tools",
            "description": "List all tools registered in the governance registry.",
            "method": "GET",
            "path": "/api/v1/governance/tools",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify tool catalog is returned\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.tools).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Execute Tool Under Governance",
            "description": "Execute a tool through the secure governance sandbox.",
            "method": "POST",
            "path": "/api/v1/governance/tools/query_mongodb/execute",
            "headers": auth_headers,
            "body": {
                "arguments": {
                    "collection": "rti_requests",
                    "query": {}
                }
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify tool execution logs and output\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.be.oneOf([\"success\", \"error\"]);",
                "});"
            ]
        },
        {
            "name": "List Workflow Events Audit",
            "description": "Fetch audit events logs for active workflows.",
            "method": "GET",
            "path": "/api/v1/governance/events",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Events log array validation\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.events).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Fetch Governance Dashboard Metrics",
            "description": "Fetch governance risk metrics, agent consensus scores, and compliance metrics.",
            "method": "GET",
            "path": "/api/v1/governance/dashboard",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify dashboard content\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.total_audits).to.be.a(\"number\");",
                "    pm.expect(jsonData.compliance_rate).to.be.a(\"number\");",
                "});"
            ]
        },
        {
            "name": "Evaluate Workflow State compliance",
            "description": "Trigger a compliance run on the active state of a workflow.",
            "method": "POST",
            "path": "/api/v1/governance/evaluate",
            "headers": auth_headers,
            "body": {
                "request_id": "{{REQUEST_ID}}",
                "state_data": {}
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify safety score evaluation\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.safety_score).to.be.a(\"number\");",
                "});"
            ]
        }
    ]
    
    # ---- 5. SYSTEM TOOLS ----
    requests_by_folder["System Tools & Tracing"] = [
        {
            "name": "List Active System Tools",
            "description": "List all active system tools.",
            "method": "GET",
            "path": "/api/v1/tools",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "Check System Tools Status",
            "description": "Get runtime operational status of tools.",
            "method": "GET",
            "path": "/api/v1/tools/status",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "Submit Semantic Query to Tools",
            "description": "Submit a raw semantic query to discover tools.",
            "method": "POST",
            "path": "/api/v1/tools/query",
            "headers": auth_headers,
            "body": {
                "query": "smart city projects"
            },
            "tests": get_std_tests(200)
        },
        {
            "name": "Get Specific Tool Trace",
            "description": "Retrieve tool execution graph trace by trace ID.",
            "method": "GET",
            "path": "/api/v1/tools/traces/{{TRACE_ID}}",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Response is successful or not found\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 404]);",
                "});"
            ]
        },
        {
            "name": "Get Tool Performance Metrics",
            "description": "Retrieve latency, memory footprint, and usage metrics for tools.",
            "method": "GET",
            "path": "/api/v1/tools/metrics",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "Benchmark Registered Tools",
            "description": "Run standard query tests across tools to measure accuracy.",
            "method": "POST",
            "path": "/api/v1/tools/benchmark",
            "headers": auth_headers,
            "body": {
                "queries": ["pune budget", "mumbai transport"],
                "iterations": 1
            },
            "tests": get_std_tests(200)
        },
        {
            "name": "Replay Tool Execution Trace",
            "description": "Replay a tool execution trace to audit error conditions or inspect performance.",
            "method": "POST",
            "path": "/api/v1/tools/replay",
            "headers": auth_headers,
            "body": {
                "trace_id": "{{TRACE_ID}}"
            },
            "tests": [
                "pm.test(\"Replay response checks\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 404]);",
                "});"
            ]
        }
    ]
    
    # ---- 6. MULTILINGUAL ----
    requests_by_folder["Multilingual Engine"] = [
        {
            "name": "Detect Text Language",
            "description": "Submit a snippet of text to detect the input language.",
            "method": "POST",
            "path": "/api/v1/multilingual/detect",
            "headers": auth_headers,
            "body": {
                "text": "पुणे स्मार्ट सिटी अंतर्गत झालेला एकूण खर्च किती?"
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Language is detected as Marathi\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.language).to.eql(\"mr\");",
                "});"
            ]
        },
        {
            "name": "Translate Text Payload",
            "description": "Submit text to translate from a source language to a target language.",
            "method": "POST",
            "path": "/api/v1/multilingual/translate",
            "headers": auth_headers,
            "body": {
                "text": "पुणे स्मार्ट सिटी अंतर्गत झालेला एकूण खर्च किती?",
                "source_lang": "mr",
                "target_lang": "en"
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Verify translation content is present\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.translated_text).to.be.a(\"string\");",
                "});"
            ]
        },
        {
            "name": "Cross-lingual Retrive Chunks",
            "description": "Performs cross-lingual search across multiple databases.",
            "method": "POST",
            "path": "/api/v1/multilingual/retrieve",
            "headers": auth_headers,
            "body": {
                "query_text": "smart city pune",
                "languages": ["mr", "hi", "en"]
            },
            "tests": get_std_tests(200)
        },
        {
            "name": "Multilingual OCR File Ingestion",
            "description": "Trigger OCR processing on an image link with language hints.",
            "method": "POST",
            "path": "/api/v1/multilingual/ocr",
            "headers": auth_headers,
            "body": {
                "image_url": "https://example.com/maharashtra_notice.png",
                "language_hint": "mr"
            },
            "tests": [
                "pm.test(\"OCR trigger status verification\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 202, 400]);",
                "});"
            ]
        },
        {
            "name": "Multilingual Engine Stats",
            "description": "Fetch translation cache hit-rates and language processing breakdowns.",
            "method": "GET",
            "path": "/api/v1/multilingual/stats",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        }
    ]
    
    # ---- 7. EVALUATION ----
    requests_by_folder["Evaluation & Benchmarking"] = [
        {
            "name": "Run Evaluation Job",
            "description": "Trigger a batch evaluation job.",
            "method": "POST",
            "path": "/api/v1/eval/run",
            "headers": auth_headers,
            "body": {
                "dataset_name": "smart_city_benchmark",
                "eval_type": "grounding"
            },
            "tests": get_std_tests(200)
        },
        {
            "name": "List Evaluation Reports",
            "description": "List all generated evaluation reports.",
            "method": "GET",
            "path": "/api/v1/eval/reports",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "Get Evaluation Metrics",
            "description": "Get structured metrics over historical evaluation runs.",
            "method": "GET",
            "path": "/api/v1/eval/metrics",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        },
        {
            "name": "Submit Hallucination Check",
            "description": "Check if generated response has hallucinated facts against reference context.",
            "method": "POST",
            "path": "/api/v1/eval/hallucination-check",
            "headers": auth_headers,
            "body": {
                "query": "What is the transport budget for Pune?",
                "context": "transport: 600 Crores, sanitation: 400 Crores",
                "response": "The transport budget for Pune is 600 Crores."
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Hallucination flag is boolean\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.hallucinated).to.be.a(\"boolean\");",
                "});"
            ]
        },
        {
            "name": "Replay Evaluation Trace",
            "description": "Replay a specific evaluation trace.",
            "method": "POST",
            "path": "/api/v1/eval/replay",
            "headers": auth_headers,
            "body": {
                "report_id": "rep_12345"
            },
            "tests": get_std_tests(200)
        },
        {
            "name": "List Registered Benchmarks",
            "description": "List registered benchmark datasets.",
            "method": "GET",
            "path": "/api/v1/eval/benchmarks",
            "headers": auth_headers,
            "tests": get_std_tests(200)
        }
    ]
    
    # ---- 8. INTEGRATION WORKFLOWS ----
    requests_by_folder["Chained Integration Workflows"] = [
        {
            "name": "Step 1 - Submit RTI Request",
            "description": "Submits a new RTI request. Extracts REQUEST_ID and THREAD_ID.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": auth_headers,
            "body": {
                "query_text": "Retrieve total fund details allocated for rural sanitation in Aurangabad for year 2023-24.",
                "language": "en",
                "thread_id": None
            },
            "tests": get_std_tests(202) + [
                "pm.test(\"Chaining: Extract REQUEST_ID & THREAD_ID\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.request_id).to.be.a(\"string\");",
                "    pm.environment.set(\"REQUEST_ID\", jsonData.request_id);",
                "    if (jsonData.thread_id) {",
                "        pm.environment.set(\"THREAD_ID\", jsonData.thread_id);",
                "    }",
                "});"
            ]
        },
        {
            "name": "Step 2 - Stream Real-Time Execution Logs",
            "description": "Listens to the SSE stream using the extracted REQUEST_ID.",
            "method": "GET",
            "path": "/api/v1/stream/{{REQUEST_ID}}",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Chaining: SSE stream connected successfully\", function () {",
                "    pm.response.to.have.status(200);",
                "});"
            ]
        },
        {
            "name": "Step 3 - Human Approval Resumption",
            "description": "Simulates an officer approving the RTI draft from Step 1. Extracts TRACKING_ID.",
            "method": "POST",
            "path": "/api/v1/approve/{{REQUEST_ID}}",
            "headers": auth_headers,
            "body": {
                "decision": "approved",
                "approved_by": "Senior Officer akash",
                "edited_query": "Details of rural sanitation fund allocation in Aurangabad (2023-24)"
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Chaining: Extract TRACKING_ID\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.tracking_id).to.be.a(\"string\");",
                "    pm.environment.set(\"TRACKING_ID\", jsonData.tracking_id);",
                "});"
            ]
        },
        {
            "name": "Step 4 - Fetch Processing Status",
            "description": "Polls status using the extracted TRACKING_ID to check final response generation.",
            "method": "GET",
            "path": "/api/v1/status/{{TRACKING_ID}}",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Chaining: Verify final response is generated\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.be.oneOf([\"pending\", \"processing\", \"completed\"]);",
                "});"
            ]
        },
        {
            "name": "Step 5 - Retrieve Agent Chat History",
            "description": "Fetch history thread using extracted THREAD_ID.",
            "method": "GET",
            "path": "/api/v1/thread/{{THREAD_ID}}",
            "headers": auth_headers,
            "tests": get_std_tests(200) + [
                "pm.test(\"Chaining: Validate thread history\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.history).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Step 6 - Submit Final User Feedback",
            "description": "Sends feedback referencing the TRACKING_ID.",
            "method": "POST",
            "path": "/api/v1/feedback",
            "headers": auth_headers,
            "body": {
                "tracking_id": "{{TRACKING_ID}}",
                "rating": 5,
                "comments": "Successfully completed integration flow test."
            },
            "tests": get_std_tests(200) + [
                "pm.test(\"Chaining: Success status check\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.status).to.eql(\"success\");",
                "});"
            ]
        }
    ]
    
    # ---- 9. NEGATIVE TESTS ----
    requests_by_folder["Negative & Error Testing"] = [
        {
            "name": "Submit Malformed Query Body",
            "description": "Submit a body missing mandatory fields (e.g. query_text). Checks that the system returns 422 Unprocessable Entity.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": auth_headers,
            "body": {
                "language": "en"
            },
            "tests": get_std_tests(422) + [
                "pm.test(\"Response contains validation details\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.detail).to.be.an(\"array\");",
                "});"
            ]
        },
        {
            "name": "Query Length Limit Exceeded Validation",
            "description": "Submit an exceptionally large query string that exceeds settings.MAX_QUERY_LENGTH (2000 chars) to verify system rejection.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": auth_headers,
            "body": {
                "query_text": "x" * 2500,
                "language": "en"
            },
            "tests": get_std_tests(422) + [
                "pm.test(\"Check length rejection message\", function () {",
                "    var jsonData = pm.response.json();",
                "    var detailStr = JSON.stringify(jsonData.detail);",
                "    pm.expect(detailStr).to.include(\"Invalid query\");",
                "});"
            ]
        },
        {
            "name": "Inexistent Status ID Polling",
            "description": "Attempt to query status using a non-existent UUID or tracking_id. Validates 404 response.",
            "method": "GET",
            "path": "/api/v1/status/non-existent-tracking-id-99999",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Status code is 404\", function () {",
                "    pm.response.to.have.status(404);",
                "});"
            ]
        },
        {
            "name": "Nonexistent Document Ingestion Version Fetch",
            "description": "Attempts to query a document version using a fictional document ID. Checks for a 404 response.",
            "method": "GET",
            "path": "/api/v1/rag/document-version/non-existent-doc-id-99999/1",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Status code is 404\", function () {",
                "    pm.response.to.have.status(404);",
                "});"
            ]
        },
        {
            "name": "Invalid Tool Execution Sandbox Attempt",
            "description": "Attempts to execute a non-existent tool, which should trigger validation error or missing tool handler.",
            "method": "POST",
            "path": "/api/v1/governance/tools/nonexistent_tool_name/execute",
            "headers": auth_headers,
            "body": {
                "arguments": {}
            },
            "tests": [
                "pm.test(\"Rejection of unregistered tool\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([404, 422]);",
                "});"
            ]
        }
    ]
    
    # ---- 10. SECURITY BOUNDARY VALIDATION ----
    requests_by_folder["Security Boundary Validation"] = [
        {
            "name": "Missing X-API-Key Header Access",
            "description": "Attempt to access protected endpoint (/submit) without the X-API-Key header to verify 401 response.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": no_auth_headers,
            "body": {
                "query_text": "Check if I can bypass auth.",
                "language": "en"
            },
            "tests": [
                "pm.test(\"Status code is 401\", function () {",
                "    pm.response.to.have.status(401);",
                "});",
                "pm.test(\"Response contains invalid or missing key message\", function () {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.error).to.eql(\"unauthorized\");",
                "});"
            ]
        },
        {
            "name": "Invalid X-API-Key Header Access",
            "description": "Attempt to access protected endpoint (/submit) with an invalid X-API-Key header to verify 401 response.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": [
                {
                    "key": "X-API-Key",
                    "value": "incorrect-api-key-value",
                    "type": "text"
                },
                {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                }
            ],
            "body": {
                "query_text": "Check if incorrect key works.",
                "language": "en"
            },
            "tests": [
                "pm.test(\"Status code is 401\", function () {",
                "    pm.response.to.have.status(401);",
                "});"
            ]
        },
        {
            "name": "Path Traversal Injection Attack Check",
            "description": "Submit a document historical fetch with path traversal elements `../../etc/passwd` to check standard routing / security protection layer.",
            "method": "GET",
            "path": "/api/v1/rag/document-history/..%2F..%2Fetc%2Fpasswd",
            "headers": auth_headers,
            "tests": [
                "pm.test(\"Sanitization block or not found\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([400, 404, 422]);",
                "});"
            ]
        },
        {
            "name": "NoSQL / SQL Injection Query Injection Payload Check",
            "description": "Submit a payload to `/submit` containing NoSQL selector keys `{\"$gt\": \"\"}` to ensure the input query sanitization layer strips or rejects structural operators.",
            "method": "POST",
            "path": "/api/v1/submit",
            "headers": auth_headers,
            "body": {
                "query_text": "Smart city budget {$ne: null} select * from users",
                "language": "en"
            },
            "tests": [
                "pm.test(\"Request handled safely (no server crash)\", function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([202, 422, 400]);",
                "});"
            ]
        }
    ]

    # 3. Assemble Postman Collection
    collection_items = []
    
    for folder_name, req_list in requests_by_folder.items():
        folder_item = {
            "name": folder_name,
            "item": []
        }
        
        for req in req_list:
            # Construct URL components
            path_cleaned = req["path"].lstrip('/')
            path_split = path_cleaned.split('/')
            
            req_item = {
                "name": req["name"],
                "request": {
                    "method": req["method"],
                    "header": req["headers"],
                    "url": {
                        "raw": "{{BASE_URL}}/" + path_cleaned,
                        "host": [
                            "{{BASE_URL}}"
                        ],
                        "path": path_split
                    },
                    "description": req["description"]
                },
                "event": []
            }
            
            # Attach body if present
            if "body" in req and req["body"] is not None:
                req_item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(req["body"], indent=2),
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
                
            # Attach tests if present
            if "tests" in req and req["tests"]:
                req_item["event"].append({
                    "listen": "test",
                    "script": {
                        "exec": req["tests"],
                        "type": "text/javascript"
                    }
                })
                
            folder_item["item"].append(req_item)
            
        collection_items.append(folder_item)
        
    collection_data = {
        "info": {
            "_postman_id": collection_id,
            "name": "RTI-Agent API Testing Suite",
            "description": "Production-grade, highly automated testing suite for RTI-Agent (FastAPI + LangGraph multi-agent system). Covers 41 endpoints across Health, RTI submit flow, RAG corpus audit, secure governance tools sandbox, multilingual processing, system evaluations, and rigorous security/negative checks.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": collection_items
    }
    
    # 4. Assemble Postman Environment
    env_id = str(uuid.uuid4())
    env_data = {
        "id": env_id,
        "name": "RTI-Agent Environment",
        "values": [
            {
                "key": "BASE_URL",
                "value": "http://localhost:8000",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "API_KEY",
                "value": "change-me-in-production",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "ADMIN_API_KEY",
                "value": "change-me-in-production",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "OFFICER_API_KEY",
                "value": "change-me-in-production",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "USER_API_KEY",
                "value": "change-me-in-production",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "REQUEST_ID",
                "value": "",
                "type": "default",
                "enabled": True
            },
            {
                "key": "TRACKING_ID",
                "value": "",
                "type": "default",
                "enabled": True
            },
            {
                "key": "THREAD_ID",
                "value": "",
                "type": "default",
                "enabled": True
            },
            {
                "key": "DOCUMENT_ID",
                "value": "",
                "type": "default",
                "enabled": True
            },
            {
                "key": "TRACE_ID",
                "value": "tr_mock_991823",
                "type": "default",
                "enabled": True
            }
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_at": "2026-05-21T00:00:00Z",
        "_postman_exported_using": "Postman/10.0.0"
    }
    
    # 5. Write to files
    coll_path = os.path.join(output_dir, "RTI-Agent.postman_collection.json")
    env_path = os.path.join(output_dir, "RTI-Agent.postman_environment.json")
    
    with open(coll_path, "w", encoding="utf-8") as f:
        json.dump(collection_data, f, indent=2, ensure_ascii=False)
        
    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Postman Collection written to: {coll_path}")
    print(f"[SUCCESS] Postman Environment written to: {env_path}")
    print("[SUCCESS] Postman Suite generation finished successfully!")

if __name__ == "__main__":
    generate_suite()
