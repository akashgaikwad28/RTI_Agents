"""
graph/state.py
--------------
Master TypedDict state schema for the RTI-Agent LangGraph StateGraph.
This is the single source of truth that flows through every node.
All fields are Optional where appropriate to support partial hydration.
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class RTIAgentState(TypedDict):

    # ── Identity ──────────────────────────────────────────────────
    request_id: str          # UUID for this specific request
    thread_id: str           # Persistent conversation thread ID
    session_id: str          # Short-lived session (Redis-backed)

    # ── User Input ────────────────────────────────────────────────
    user_input: dict         # Raw validated RTIRequestSchema.dict()
    raw_query: str           # Original text from user
    language: str            # ISO language code: "en", "hi", "mr", etc.
    uploaded_documents: list[str]  # File paths of uploaded documents

    # ── Conversation ──────────────────────────────────────────────
    conversation_history: Annotated[list[dict], add_messages]
    active_request_id: str   # Currently active RTI in this thread

    # ── Translation / Preprocessing ───────────────────────────────
    translated_query: str    # Query normalized to English
    sanitized_query: str     # After PII masking + injection removal
    detected_language: str
    detected_script: str
    normalized_query: str
    transliterated_query: str
    multilingual_context: dict
    response_language: str
    mixed_language: bool
    language_confidence: float

    # ── Formatting ────────────────────────────────────────────────
    formal_query: str        # Structured RTI draft by FormatterNode
    rti_template: dict       # Full RTI template fields (name, address, etc.)

    # ── Classification ────────────────────────────────────────────
    department: str          # Predicted government department
    sub_department: str      # Sub-department if applicable
    confidence: str          # "high" | "medium" | "low"
    classification_notes: str

    # ── RAG / Retrieval ───────────────────────────────────────────
    retrieved_context: list[str]    # Top-k document chunks
    retrieval_scores: list[float]   # Similarity scores (0-1)
    retrieval_sources: list[str]    # Document source metadata
    retrieval_citations: list[str]  # Human-readable source citations
    retrieval_metadata: list[dict]  # Full metadata per retrieved chunk
    retrieval_confidence: float     # Aggregate retriever confidence
    tools_used: list[str]           # Tools invoked during retrieval
    cache_hit: bool                 # Whether semantic cache was used

    # ── Quality Control ───────────────────────────────────────────
    review_passed: bool
    review_feedback: str
    review_score: float             # 0.0 - 1.0
    grounding_score: float          # RAG grounding quality
    hallucination_flags: list[str]  # Detected hallucination indicators

    # ── Reflection / Self-Correction ──────────────────────────────
    reflection_needed: bool
    reflection_reason: str
    retry_count: int
    max_retries: int                # Default: 2

    # ── Human-in-the-Loop ─────────────────────────────────────────
    approval_required: bool
    approval_status: str            # "pending" | "approved" | "rejected" | "expired"
    approved_by: str                # User/admin who approved
    approval_timestamp: str
    edited_query: str               # Human-edited version of formal_query

    # ── Tracking / Output ─────────────────────────────────────────
    tracking_id: str                # Final RTI tracking number (e.g., RTI-2024-XXXXX)
    final_response: str             # Response returned to user
    status: str                     # "pending"|"classified"|"awaiting_approval"|"submitted"|"failed"
    error: str | None               # Error message if any
    info_available: bool            # Whether the requested info is already public


    # ── Routing ───────────────────────────────────────────────────
    next_agent: str                 # Name of next node to execute
    intent: str                     # "new_request" | "status_check" | "followup"
    workflow_path: list[str]        # Ordered list of nodes visited (audit trail)

    # ── Observability ─────────────────────────────────────────────
    agent_durations: dict[str, float]   # {agent_name: duration_ms}
    token_counts: dict[str, int]        # {agent_name: total_tokens}
    llm_models_used: dict[str, str]     # {agent_name: model_name}

    # Phase C: advanced agent ecosystem / governance
    execution_plan: dict
    selected_tools: list[str]
    tool_results: list[dict]
    agent_debate: dict
    critic_feedback: dict
    verification_report: dict
    consensus_result: dict
    final_ai_decision: dict
    ai_risk_score: float
    escalation_required: bool
    learning_feedback: dict
    reasoning_trace: list[dict]
    live_events: list[dict]
    governance_notes: list[str]
