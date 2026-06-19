# Governance, Audit & Analytics API Testing

This guide explains how to test the security sandbox, compliance registry, audit logs, and analytical charts using the **Governance & Compliance** folder in the Postman collection.

---

## 🏛️ Rationale for System Governance

Operating an AI-powered agent platform inside public administrative offices requires absolute compliance, traceability, and safety safeguards. The governance module provides:
1. **Audited Tools sandbox**: Ensures database queries or web searches are restricted to verified, non-destructive tools.
2. **Security Compliance Audits**: Monitors token allocations, safety risk scores, and hallucinatory check sweeps.
3. **Traceability Dashboards**: Records every agent consensus decision and reflection loop.

---

## 🔍 API Testing Guidelines & Steps

Here are the functional verification steps for each endpoint in the **Governance & Compliance** folder:

### 1. Cataloging Registered Tools
*   **Request**: `GET /api/v1/governance/tools`
*   **Purpose**: Validates that only officially vetted tools (e.g., `query_mongodb`, `web_scraper`, `text_translator`) are active.
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Verify the response contains a `tools` array list.
    *   Verify each tool definition has a `name`, `description`, and `required_args` dictionary structure.

### 2. Audited Sandbox Execution
*   **Request**: `POST /api/v1/governance/tools/query_mongodb/execute`
*   **Purpose**: Validates that administrators or authorized officers can safely run a tool directly in an isolated, monitored environment to audit its output.
*   **Body Example**:
    ```json
    {
      "arguments": {
        "collection": "rti_requests",
        "query": {}
      }
    }
    ```
*   **Expected Results**: Validates that the sandbox runs successfully and logs the raw output. If illegal parameters are supplied (e.g. attempting to drop a database), the query validator should intercept and raise a `400 Bad Request` or return a safe execution error.

### 3. Fetching Workflow Audit Logs
*   **Request**: `GET /api/v1/governance/events`
*   **Purpose**: Retrieves chronological operational events and state transitions logged across all agent operations.
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert response body contains an `events` array.
    *   Verify fields: `event_id`, `timestamp`, `level`, `node_name`, and `details` are fully populated.

### 4. Fetching Dashboard Analytics
*   **Request**: `GET /api/v1/governance/dashboard`
*   **Purpose**: Checks the health, workload, and performance summaries of the system (e.g., database sizes, total requests processed, average reflection counts, and overall compliance ratings).
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert response includes numerical statistics: `total_audits`, `compliance_rate` (0.0 to 1.0), and `average_risk_score`.

### 5. Compliance Workflow Evaluations
*   **Request**: `POST /api/v1/governance/evaluate`
*   **Purpose**: Forces a real-time safety evaluation on the active graph state of a request.
*   **Body Example**:
    ```json
    {
      "request_id": "{{REQUEST_ID}}",
      "state_data": {}
    }
    ```
*   **Expected Results**: The engine checks the query and drafted response, calculates compliance variables (grounding alignment, prompt safety checks, and data leakage), and returns an overall safety score.
