# Security Boundary & Negative API Testing

This guide explains how to test negative error conditions, sanitization layers, payload limits, and security boundaries using the **Negative & Error Testing** and **Security Boundary Validation** folders in the Postman collection.

---

## 🛡️ Rationale for Failure & Boundary Testing

A production-grade system must not only behave correctly on successful paths, but also maintain stability, data integrity, and strict access controls when confronted with incorrect bodies, oversized inputs, and malicious injection payloads. 

Our testing suite validates that:
1. The server **fails gracefully** (returning proper `4xx` error codes instead of throwing unhandled `500` server exceptions).
2. Input sanitizers strip out hazardous structural tags.
3. Access blocks immediately when credentials are missing or corrupted.

---

## 📋 Failure Test Folders & Operations

### Folder 1: Negative & Error Testing

This folder contains requests designed to verify standard input validations and non-existent resource requests.

#### 1. Malformed Ingestion Body Validation
*   **Request**: `POST /api/v1/submit` (missing mandatory `query_text`)
*   **Expected Response**: **`422 Unprocessable Entity`**
*   **Postman Automated Tests**:
    *   Assert status is `422`.
    *   Verify the return payload contains a `detail` array mapping the missing field.

#### 2. Query Size Constraints Verification
*   **Request**: `POST /api/v1/submit` (payload containing a query exceeding the `MAX_QUERY_LENGTH` setting, which is 2000 characters).
*   **Expected Response**: **`422 Unprocessable Entity`**
*   **Postman Automated Tests**:
    *   Assert status is `422`.
    *   Assert detail string includes `"Invalid query"` or size violation messages.

#### 3. Inexistent Status Polling Check
*   **Request**: `GET /api/v1/status/non-existent-tracking-id-99999`
*   **Expected Response**: **`404 Not Found`**
*   **Postman Automated Tests**:
    *   Assert status is exactly `404`.

#### 4. Invalid Tool Execution Sandbox Check
*   **Request**: `POST /api/v1/governance/tools/nonexistent_tool/execute`
*   **Expected Response**: **`404 Not Found`** or **`422 Unprocessable Entity`**
*   **Postman Automated Tests**:
    *   Assert status code is either `404` or `422`.

---

### Folder 2: Security Boundary Validation

This folder contains requests verifying role-based blocks and sanitization protections against malicious actors.

#### 1. Anonymous Access Interception
*   **Request**: Protected endpoint (e.g. `/submit`) executed with **no authentication header**.
*   **Expected Response**: **`401 Unauthorized`**
*   **Postman Automated Tests**:
    *   Assert status is `401`.
    *   Verify response reads `{"error": "unauthorized", "message": "Invalid or missing X-API-Key header"}`.

#### 2. Invalid Token Interception
*   **Request**: Protected endpoint executed with an **incorrect X-API-Key value**.
*   **Expected Response**: **`401 Unauthorized`**
*   **Postman Automated Tests**:
    *   Assert status is `401`.

#### 3. Path Traversal Injections Defense
*   **Request**: `GET /api/v1/rag/document-history/..%2F..%2Fetc%2Fpasswd` (attempting to read parent system files using relative directory traversal).
*   **Expected Response**: **`400 Bad Request`** or **`404 Not Found`** or **`422 Unprocessable Entity`**
*   **Postman Automated Tests**:
    *   Assert the request is successfully intercepted and does not return parent directory structure.

#### 4. Structured Operator Injection Defense
*   **Request**: `POST /api/v1/submit` with NoSQL dictionary selectors `{"$ne": null}` and SQL statements `select * from users`.
*   **Expected Response**: **`202 Accepted`** or **`422 Unprocessable Entity`** (the system must sanitize and strip structural commands through `sanitize_query` without server crashes).
*   **Postman Automated Tests**:
    *   Assert status is not `500`.
    *   Verify that query input did not corrupt backend operational states.
