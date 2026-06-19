# System Evaluation & Benchmarking API Testing

This guide explains how to test the automated evaluation loops, benchmark sweeps, factual alignment models, and execution replays inside the **Evaluation & Benchmarking** folder in the Postman collection.

---

## 📈 Rationale for Continuous Evaluation

Because generative AI outputs are inherently probabilistic, deploying them in government portals requires rigorous continuous auditing. The evaluation module assesses system responses on three pillars (derived from the RAGAS framework):
1. **Faithfulness**: Is the response derived *strictly* from the retrieved context (no hallucinations)?
2. **Answer Relevance**: Does the generated text *directly address* the citizen's query?
3. **Grounding Alignment**: Does the response contain concrete facts and citations, rather than generic speculation?

---

## 📋 Evaluation Testing Workflows

Here are the functional verification steps for each endpoint in the **Evaluation & Benchmarking** folder:

### 1. Running Evaluation Sweeps
*   **Request**: `POST /api/v1/eval/run`
*   **Purpose**: Triggers a batch evaluation sweep over a pre-loaded test dataset (benchmark) to calculate average quality scores.
*   **Body Example**:
    ```json
    {
      "dataset_name": "smart_city_benchmark",
      "eval_type": "grounding"
    }
    ```
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Verify the return payload contains `report_id`, `status` (started/queued), and `queries_count`.

### 2. Cataloging Evaluation Reports
*   **Request**: `GET /api/v1/eval/reports`
*   **Purpose**: Retrieves a list of all historical evaluation reports, showing date, dataset used, and accuracy metrics.
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Verify the response contains a `reports` array.

### 3. Factual Alignment / Hallucination Checks
*   **Request**: `POST /api/v1/eval/hallucination-check`
*   **Purpose**: Uses an isolated LLM evaluator or NLI model to check if a specific answer contradicts or adds ungrounded claims to the provided context.
*   **Body Example**:
    ```json
    {
      "query": "What is the transport budget for Pune?",
      "context": "The municipal budget allocated 600 Crores for transport and 400 Crores for sanitation.",
      "response": "The transport budget for Pune is 600 Crores."
    }
    ```
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert `hallucinated` is a boolean flag (`false` for safe outputs, `true` if facts are fabricated).

### 4. Fetching System Quality Metrics
*   **Request**: `GET /api/v1/eval/metrics`
*   **Purpose**: Retrieves average historical scores across the entire system.
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert response body contains floats for `average_faithfulness` and `average_relevance` metrics.

### 5. Replaying Evaluation Runs
*   **Request**: `POST /api/v1/eval/replay`
*   **Purpose**: Replays a historical execution trace to audit failure conditions or test if prompt tweaks successfully resolved an alignment issue.
*   **Body Example**:
    ```json
    {
      "report_id": "rep_12345"
    }
    ```

### 6. Listing Benchmarks Datasets
*   **Request**: `GET /api/v1/eval/benchmarks`
*   **Purpose**: Lists standard test datasets compiled in the database for regression testing.
