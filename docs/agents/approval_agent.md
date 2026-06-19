# Approval Agent Manual: Human-in-the-Loop (HITL) Gatekeeper

The **Approval Agent** (implemented as `approval_node`) manages the human governance boundary. It acts as an execution barrier, suspending the autonomous graph flow to secure manual validation, incorporating human edits, and processing approval or rejection outcomes.

---

## 1. Why this Agent Exists

### Problem Solved
Autonomous AI systems can draft high-quality letters, but in enterprise or legal contexts, submitting AI-generated documents directly to government authorities without human verification is a significant liability. Administrative laws, fees, and official correspondence require human oversight to guarantee compliance, verify spelling, and confirm intent.

### Failure Impact
Without the Approval Agent:
* The system would submit applications directly to government databases without human review.
* Users would have no opportunity to edit the AI-generated drafted text before submission.
* The system would lack an audit trail of which legal professional or citizen verified and approved the submission.

---

## 2. Agent Metadata

* **Real Code File**: [graph/nodes/approval_node.py](file:///C:/Users/akash/RTI_Agents/graph/nodes/approval_node.py)
* **Execution Boundary**: Triggered via `interrupt_before=["approval_node"]` compilation flags in the StateGraph builder.
* **Database Target**: `rti_requests` collection in MongoDB.

---

## 3. Operational State Boundaries

```mermaid
graph TD
    subgraph Pause Stage (First Entry)
        InputState1([RTIAgentState Inputs]) --> PauseNode[Approval Node]
        PauseNode --> SaveMongo[(Save Pending to Mongo)]
        PauseNode --> MailTrigger[Trigger Approval Email]
        PauseNode --> PausedState[Suspend Thread SQLite Checkpointer]
    end
    
    subgraph Resume Stage (Human Action)
        PausedState --> ResumeAPI[API /approve POST]
        ResumeAPI --> ResumeNode[Approval Node Resume]
        ResumeNode --> ApplyEdits{Apply edited_query?}
        ApplyEdits -->|Yes| UpdateDraft[Override formal_query]
        ApplyEdits -->|No| KeepDraft[Keep formal_query]
        UpdateDraft --> OutputState([RTIAgentState Outputs])
        KeepDraft --> OutputState
    end
```

### Input State Fields
* `request_id` (str): Unique request UUID.
* `formal_query` (str): AI drafted RTI application text.
* `department` (str): Predicted department classification.
* `confidence` (str): Classification confidence level.
* `review_score` (float): Legal review score.
* `approval_status` (str): Initialized to `"pending"`.
* `user_input` (dict): Profiles dictionary containing candidate email details.

### Output State Fields
* `formal_query` (str): Holds the final query (the original draft or the human's inline edits).
* `approval_status` (str): Resumed status: `"approved"` or `"rejected"`.
* `approved_by` (str): Entity or reviewer ID who authorized the request.
* `edited_query` (str): Optional inline edits made by the human reviewer.
* `approval_timestamp` (str): ISO timestamp of human action.
* `workflow_path` (list[str]): Appends `"approval_node:pending"` or `"approval_node:approved" / "approval_node:rejected"`.

---

## 4. Interrupt & Resume Lifecycle

The Approval Agent operates in a two-stage split lifecycle:

### Stage 1: Pause & Persist (First Entry)
1. **Status Trigger**: When the graph enters the node and sees `approval_status == "pending"`, it initiates a suspension protocol.
2. **MongoDB Persistence**: The agent connects to MongoDB via `get_mongo_client()` and updates the target request in `rti_requests` with a status of `"awaiting_approval"`, writing all drafted content and quality scores to disk.
3. **SMTP Notification**: The agent fires an asynchronous email notification to the user/admin via `send_approval_notification()`. This email contains the drafted text, target department, confidence rating, and an approval action link.
4. **Execution Interrupt**: Having saved the state, the node returns the status. Because LangGraph is compiled with `interrupt_before=["approval_node"]`, the runtime engine halts execution and saves the exact state in the SQLite checkpointer. The execution thread enters an idle wait state.

### Stage 2: Human Resumption
1. **API Trigger**: A human reviews the draft and calls the API endpoint (e.g. `POST /api/v1/approve/{request_id}`), passing an optional `edited_query` and a decision (`approved` or `rejected`).
2. **State Hydration**: The API loads the execution checkpointer using the `thread_id` and updates `approval_status` (to `"approved"` or `"rejected"`), `approved_by`, and optionally `edited_query`.
3. **Graph Resume**: The API calls `.resume()` on the graph.
4. **State Realignment**: The node executes a second time. Since `approval_status` is no longer `"pending"`, the agent bypasses Stage 1. It extracts the `edited_query` and, if present, overrides the drafted `formal_query` with the human's edits.
5. **Metric Logging**: The agent increments the Prometheus counter (`rti_approval_decisions`) based on the decision and proceeds.

---

## 5. Security, Trust, and Routing Rules

* **Human Override Guarantee**: If the human provides an `edited_query`, it overrides the drafted query. This serves as a critical safety valve, allowing humans to correct errors, add facts, or redact private details before submission.
* **Downstream Routing**:
  * **Approved**: Routes to `consensus_node` for final risk aggregation and submission.
  * **Rejected**: Routes to `reflection_node` to trigger automated correction loops.
  * *Code Reference*: `route_after_approval(state)` inside [graph/router.py](file:///C:/Users/akash/RTI_Agents/graph/router.py#L31-L36)

---

## 6. Observability & Downstream Consumers

### Emitted Metrics
* `rti_approval_decisions`: Labels: `decision=approval_status` (`"approved"` or `"rejected"`). Tracks human approval rates.
* `rti_agent_duration`: Labels: `agent="approval_node"`. Logs processing latency.

### Downstream Consumers
* **Downstream Nodes**: Routes conditionally to `consensus_node` or `reflection_node` based on the approval outcome.
