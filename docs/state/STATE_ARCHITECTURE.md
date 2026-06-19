# State Management & Lifecycle Architecture

This document defines the schema, field boundaries, ownership matrix, and serialization lifecycle of `RTIAgentState`, the single source of truth for the RTI-Agent multi-agent workflow.

---

## 1. RTIAgentState Schema Overview

* **Real Code File**: [graph/state.py](file:///C:/Users/akash/RTI_Agents/graph/state.py)
* **Design Pattern**: Shared-state blackboard pattern. Nodes are functional transformers: they read state fields, perform operations, and return state deltas that the LangGraph orchestrator patches back into the main state.

---

## 2. Field Classification Matrix

State fields are partitioned into logical domains. They are classified as **Immutable** (set once at startup and never changed) or **Mutable** (updated by nodes during execution).

| Domain | Field Name | Type | Mutability | Primary Owner | Description |
|---|---|---|---|---|---|
| **Identity** | `request_id` | `str` | **Immutable** | API Client | Global unique request UUID |
| | `thread_id` | `str` | **Immutable** | API Client | Conversation thread correlation token |
| | `session_id` | `str` | **Immutable** | API Client | Short-lived session tracker |
| **User Input** | `user_input` | `dict` | **Immutable** | API Client | Validated user profile parameters |
| | `raw_query` | `str` | **Immutable** | API Client | Original text query submitted by the user |
| | `language` | `str` | **Immutable** | API Client | User-asserted language code |
| | `uploaded_documents` | `list[str]` | **Immutable** | API Client | File paths of uploaded candidate docs |
| **Conversation**| `conversation_history`| `Annotated[list, add_messages]` | **Mutable** | LangGraph Engine | Appended chat messages history |
| | `active_request_id` | `str` | **Mutable** | TrackerNode | Active RTI reference in thread |
| **Translation** | `translated_query` | `str` | **Mutable** | FormatterNode | Query translated to English for RAG |
| | `sanitized_query` | `str` | **Mutable** | Router / Reflector | Prompt-scrubbed or amended query instructions |
| | `detected_language` | `str` | **Mutable** | RouterNode | Primary detected script/language |
| **Formatting** | `formal_query` | `str` | **Mutable** | Formatter / Approval | legalese structured drafted query |
| | `rti_template` | `dict` | **Mutable** | FormatterNode | Extracted key-value form fields |
| **Classification**| `department` | `str` | **Mutable** | ClassifierNode | Target government ministry or body |
| | `sub_department` | `str` | **Mutable** | ClassifierNode | Sub-branch or target office |
| | `confidence` | `str` | **Mutable** | ClassifierNode | Classification confidence level |
| **RAG** | `retrieved_context` | `list[str]` | **Mutable** | RetrievalNode | Top-k document chunks extracted |
| | `retrieval_scores` | `list[float]` | **Mutable** | RetrievalNode | Chunk similarity scores |
| | `retrieval_sources` | `list[str]` | **Mutable** | RetrievalNode | Source URLs/paths of chunks |
| | `retrieval_citations` | `list[str]` | **Mutable** | RetrievalNode | Formatted text citation references |
| **QC Gate** | `review_passed` | `bool` | **Mutable** | ReviewerNode | Quality assurance pass indicator |
| | `review_score` | `float` | **Mutable** | ReviewerNode | Quality score graded |
| | `grounding_score` | `float` | **Mutable** | Reviewer / Verifier | RAG grounding score index |
| | `hallucination_flags`| `list[str]` | **Mutable** | ReviewerNode | Detected factual drift issues |
| **HITL** | `approval_status` | `str` | **Mutable** | ApprovalNode | Interrupt decision: approved/rejected |
| | `edited_query` | `str` | **Mutable** | ApprovalNode | Human inline overrides and corrections |
| **Tracking** | `tracking_id` | `str` | **Mutable** | TrackerNode | Final assigned RTI-YYYYMM-XXXXXX ID |
| | `final_response` | `str` | **Mutable** | TrackerNode | User-facing terminal text output |
| | `status` | `str` | **Mutable** | TrackerNode | Final lifecycle state of the request |

---

## 3. Node-to-State Dependency Matrix

The following table maps which nodes read (**Consumer**) or write (**Producer**) specific state fields.

| Node Name | Field Inputs (Consumers) | Field Outputs (Producers) |
|---|---|---|
| `router_node` | `raw_query`, `language`, `request_id` | `intent`, `sanitized_query`, `normalized_query`, `detected_language`, `detected_script`, `mixed_language`, `transliterated_query`, `response_language` |
| `planner_node` | `sanitized_query`, `department`, `language` | `execution_plan`, `selected_tools` |
| `formatter_node` | `sanitized_query`, `detected_language`, `response_language`, `user_input` | `translated_query`, `formal_query`, `rti_template` |
| `classifier_node` | `formal_query`, `sanitized_query` | `department`, `sub_department`, `confidence`, `classification_notes` |
| `tool_selection_node` | `formal_query`, `sanitized_query`, `department`, `execution_plan`, `selected_tools` | `tool_results` |
| `retrieval_node` | `formal_query`, `department`, `detected_language` | `retrieved_context`, `retrieval_scores`, `retrieval_sources`, `retrieval_citations`, `retrieval_metadata`, `retrieval_confidence`, `cache_hit` |
| `debate_node` | `tool_results`, `retrieval_citations` | `agent_debate` |
| `critic_node` | `retrieval_citations`, `retrieval_scores`, `confidence` | `critic_feedback` |
| `verifier_node` | `retrieval_citations`, `department`, `confidence`, `retrieval_confidence` | `verification_report` |
| `reviewer_node` | `formal_query`, `department`, `confidence`, `retrieved_context`, `raw_query` | `review_passed`, `review_score`, `grounding_score`, `hallucination_flags`, `review_feedback` |
| `approval_node` | `request_id`, `approval_status`, `edited_query`, `formal_query`, `department`, `confidence`, `review_score`, `user_input` | `formal_query`, `approval_timestamp`, `status` |
| `reflection_node` | `raw_query`, `formal_query`, `review_feedback`, `hallucination_flags`, `approval_status`, `retry_count`, `max_retries` | `reflection_needed`, `reflection_reason`, `retry_count`, `sanitized_query`, `approval_status` |
| `consensus_node` | `review_score`, `retrieval_confidence`, `grounding_score`, `agent_debate`, `retrieval_citations`, `hallucination_flags`, `approval_status` | `consensus_result`, `final_ai_decision`, `ai_risk_score`, `escalation_required` |
| `memory_learning_node`| `request_id`, `execution_plan`, `tool_results`, `consensus_result` | `learning_feedback` |
| `tracker_node` | `request_id`, `intent`, `sanitized_query`, `approval_status`, `thread_id`, `user_input`, `raw_query`, `formal_query`, `rti_template`, `department`, `sub_department`, `confidence`, `retrieval_sources`, `review_score`, `grounding_score`, `agent_durations`, `llm_models_used` | `tracking_id`, `final_response`, `status`, `active_request_id` |

---

## 4. State Persistence & Serialization Boundary

### LangGraph State Checkpointing (SQLite & Neon PostgreSQL)
Every state change triggers an automatic snapshot inside the active checkpoint database (dynamically configured via `CHECKPOINTER_TYPE` env variable):
1. **SQLite Checkpointer (`sqlite`)**: Saves snapshots locally in `data/checkpoints/rti_checkpoints.db` for zero-setup offline development.
2. **Neon PostgreSQL Checkpointer (`postgres`)**: Leverages Neon Serverless PostgreSQL in production for multi-instance, highly available, resilient state saving, managed asynchronously via the custom `LazyPostgresCheckpointer` that initializes pooling inside the FastAPI lifecycle.
3. **Thread Isolation**: States are indexed in the database using the unique `thread_id`.
4. **Step Verification**: Each transition writes an entry mapping `thread_id`, the active node name, and a serialized blob of all state fields.
5. **Interrupt Boundaries**: When the graph interrupts before `approval_node`, the state is safely saved. The API can query or update this state using standard LangGraph configuration keys:
   ```python
   config = {"configurable": {"thread_id": "thread-123", "checkpoint_id": "step-xxx"}}
   current_state = await graph.aget_state(config)
   ```

### MongoDB Synchronization
While the transient execution state is stored in SQLite or PostgreSQL checkpoints, the finalized, audit-compliant document is persisted to MongoDB. This includes node latency statistics (`agent_durations`), model tracking (`llm_models_used`), and the complete list of tools executed (`tools_used`).

