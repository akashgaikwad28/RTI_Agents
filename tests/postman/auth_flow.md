# Role-Based Authentication Guide in Postman

This guide explains how authentication and role-based validation are simulated, tested, and audited using the **RTI-Agent API Testing Suite** inside Postman.

---

## 🔐 The Authentication Mechanism

The RTI-Agent backend utilizes a production-grade FastAPI middleware named **`APIKeyMiddleware`** to secure all non-public routes (prefixed with `/api/v1/`).

*   **Header Name**: `X-API-Key`
*   **Verification**: The middleware extracts the value and validates it against **`settings.RTI_API_KEY`** (set via the `.env` configuration file).
*   **Rejection**: Any missing or mismatching header results in a immediate **`401 Unauthorized`** response:
    ```json
    {
      "error": "unauthorized",
      "message": "Invalid or missing X-API-Key header"
    }
  ```

---

## 👥 Simulated Roles in the Postman Environment

While local development uses a single global `RTI_API_KEY` validated by the middleware, real-world systems separate permissions by roles. The Postman testing suite initializes three distinct role keys to simulate full enterprise segregation:

### 1. Citizen Role (`{{USER_API_KEY}}`)
*   **Permitted Operations**:
    *   `POST /api/v1/submit` (Submit raw RTI requests)
    *   `GET /api/v1/status/{tracking_id}` (Poll application progress)
    *   `POST /api/v1/feedback` (Log experience ratings)
*   **Verification Context**: Mimics external public access.

### 2. Officer Role (`{{OFFICER_API_KEY}}`)
*   **Permitted Operations**:
    *   Citizen operations
    *   `POST /api/v1/approve/{request_id}` (Interrupt resolution / resumptions)
    *   `GET /api/v1/thread/{thread_id}` (Audit transcript histories)
    *   `GET /api/v1/stream/{request_id}` (Stream graph events)
*   **Verification Context**: Internal officers responsible for verifying and modifying AI drafts.

### 3. Administrator Role (`{{ADMIN_API_KEY}}`)
*   **Permitted Operations**:
    *   All Citizen & Officer operations
    *   `POST /api/v1/rag/ingest` & `POST /api/v1/rag/scrape` (Corpus ingestion management)
    *   `GET /api/v1/governance/dashboard` (Compliance and risk reports)
    *   `POST /api/v1/eval/run` (Batch system performance benchmarking)
*   **Verification Context**: Technical administrators managing pipeline vectorstores and LLM evaluations.

---

## 🛠️ Configuring Credentials in Postman

When you import the **`RTI-Agent Environment`**, it includes pre-defined placeholders for these roles.

### How to set the credentials:
1. In the left panel of Postman, navigate to **Environments** and select **RTI-Agent Environment**.
2. Locate the keys:
    *   `API_KEY` (Global fallback key)
    *   `ADMIN_API_KEY`
    *   `OFFICER_API_KEY`
    *   `USER_API_KEY`
3. Enter your active `RTI_API_KEY` (e.g., `change-me-in-production`) in the **Current Value** field for each variable.
4. Click **Save** in the top right.

> [!TIP]
> **Postman Security Best Practice**: Always set confidential credentials in the **Current Value** column rather than the **Initial Value** column. Current Values are kept local to your active desktop app and are not synced to shared cloud workspaces, avoiding accidental leakage of secret keys.

---

## 🚨 Security Boundary Testing

The collection includes a dedicated **Security Boundary Validation** folder containing pre-written tests to ensure authentication boundaries are robust. These tests assert:
*   Access without the `X-API-Key` header results in `401 Unauthorized` (Passing).
*   Access with an incorrect `X-API-Key` value results in `401 Unauthorized` (Passing).
*   These tests are fully integrated into automated collection runners to guarantee security regressions never slip into production builds.
