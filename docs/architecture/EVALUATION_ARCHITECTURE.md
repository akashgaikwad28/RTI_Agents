# RAG Evaluation & Benchmarks (RAGAS)

This document defines the evaluation framework, metrics, judge architectures, and testing pipelines used to audit generation quality and prevent hallucinations in the RTI-Agent multi-agent system.

---

## 1. RAGAS Evaluation Framework

To ensure that legal references and governmental instructions drafted by the agents are 100% accurate, we integrate **Ragas v0.4.3** (Retrieval Augmented Generation Assessment).

Our implementation leverages the modern single-turn scoring interfaces. Instead of loading heavy dataset structures or dataframes, the system executes metrics concurrently using direct asynchronous `.ascore()` calls, making it suitable for live production sampling.

### Judge Configuration:
* **Primary Judge LLM**: Groq client patched with `instructor` using `llama-3.3-70b-versatile`.
* **Embedding Model**: Ragas' native `GoogleEmbeddings` using `text-embedding-004`.

---

## 2. Evaluation Metrics

The system implements the following metrics depending on the presence of a reference answer (ground truth):

### Real-time Production Metrics (No Ground Truth):
* **Faithfulness** (`Faithfulness`):
  * **Requires**: `user_input`, `response`, `retrieved_contexts`.
  * **Description**: Measures the factual consistency of the generated response against the retrieved context. This is the primary guard against hallucinations.
* **Answer Relevancy** (`AnswerRelevancy`):
  * **Requires**: `user_input`, `response`.
  * **Description**: Evaluates if the generated answer directly addresses the query or contains redundant details.

### Offline Benchmarking Metrics (With Ground Truth):
* **Context Precision** (`ContextPrecision`):
  * **Requires**: `user_input`, `reference`, `retrieved_contexts`.
  * **Description**: Measures whether the retrieved context chunks containing the ground truth are ranked higher.
* **Context Recall** (`ContextRecall`):
  * **Requires**: `user_input`, `retrieved_contexts`, `reference`.
  * **Description**: Measures if the retriever fetched all the information necessary to construct the ground-truth answer.
* **Answer Correctness** (`AnswerCorrectness`):
  * **Requires**: `user_input`, `response`, `reference`.
  * **Description**: Measures the semantic similarity and factual accuracy of the generated answer compared to the reference.

---

## 3. Asynchronous Live Sampling

For live monitoring, we implement a **10% random sampling** background task in the submit API.

* **Code File**: [api/routers/rti.py](file:///C:/Users/akash/RTI_Agents/api/routers/rti.py)
* **Runner File**: [evaluation/retrieval_eval.py](file:///C:/Users/akash/RTI_Agents/evaluation/retrieval_eval.py)

```python
# live evaluation trigger in api/routers/rti.py
if random.random() < 0.10:
    ragas_scores = await evaluate_ragas_async(
        query=sanitized_query,
        answer=enriched.get("formal_query", ""),
        contexts=enriched.get("retrieved_context", []),
    )
```

The returned scores are recorded in the `ragas_scores` MongoDB collection and exposed via `/api/v1/eval/metrics` for dashboard telemetry.

---

## 4. Golden Dataset & CI/CD

To prevent regressions, the code includes:
- **Manifest Versioning**: Curated dataset schema with expected departments, facts, and ground truths defined in `evaluation/datasets/`.
- **CI Assertion**: PyTest suite blocks deployment if aggregate Faithfulness falls below **0.95**.
