# Server-Sent Events (SSE) Streaming Guide

This guide explains how to test and monitor the real-time **Server-Sent Events (SSE)** endpoint (`GET /api/v1/stream/{request_id}`) using Postman and terminal-based alternatives.

---

## 📡 Understanding the SSE Endpoint

As the multi-agent LangGraph runs, it can take 10 to 30 seconds to complete due to complex processing, direct database lookups, and multi-agent coordination. Instead of making citizens wait for a single delayed HTTP response, the platform streams real-time state changes, active agents, and token-by-token generation logs.

*   **Endpoint**: `GET /api/v1/stream/{request_id}`
*   **Header**: `X-API-Key: {{API_KEY}}`
*   **Content-Type**: `text/event-stream`
*   **Protocol**: Unidirectional HTTP stream (server-to-client).

---

## 🖥️ Testing SSE inside Postman

In Postman v10+, the platform fully supports Server-Sent Events and streaming responses out of the box.

### Execution Steps:
1. Ensure you have successfully run **Submit RTI Request** to populate the `{{REQUEST_ID}}` environment variable.
2. Open **Stream Workflow SSE** inside the collection.
3. Verify that the URL is configured as `{{BASE_URL}}/api/v1/stream/{{REQUEST_ID}}` and the header `X-API-Key` is active.
4. Click **Send**.
5. Postman will establish a persistent connection. Instead of waiting for completion, you will see a stream of events appearing in the **Response Body** panel in real-time!

### Expected Payload Structure:
The stream returns standard SSE formatted chunks (`data: {...}\n\n`). Each event JSON details active agent states:
```json
data: {"event": "node_start", "node": "router_node", "timestamp": "2026-05-21T13:59:00Z"}

data: {"event": "node_end", "node": "router_node", "next": "classification_node"}

data: {"event": "token", "node": "drafting_node", "text": "Under the Right to Information..."}
```

### Assertions run by Postman:
1. **Status Assertion**: Validates the response code is `200 OK` indicating successful stream handshake.
2. **Content-Type Assertion**: Validates `Content-Type` header includes `text/event-stream` to ensure it is not buffered as standard static JSON.

---

## 💻 Testing SSE via CLI & Scripts

Postman is excellent for functional testing, but developers may want to verify streaming stability using terminal or scripting clients:

### 1. Verification via curl
Run this command in your terminal to inspect raw bytes:
```bash
curl -N -H "X-API-Key: change-me-in-production" \
     http://localhost:8000/api/v1/stream/45c799d9-31a6-29fe-61b5-9da79420
```
*(Note: The `-N` flag disables output buffering, ensuring you receive the events in real-time.)*

### 2. Verification via Python Client
You can verify streaming programmatically using Python's `httpx` client:
```python
import httpx

headers = {"X-API-Key": "change-me-in-production"}
url = "http://localhost:8000/api/v1/stream/45c799d9-31a6-29fe-61b5-9da79420"

with httpx.stream("GET", url, headers=headers, timeout=60.0) as r:
    r.raise_for_status()
    print("Connected successfully! Reading events:")
    for line in r.iter_lines():
        if line.startswith("data:"):
            print(line)
```
