"""
observability/context.py
-------------------------
Context propagation for distributed tracing and observability.
Uses contextvars to maintain request and graph run context across async boundaries.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# ── FastAPI Request Context ─────────────────────────────────────────
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
session_id_var: ContextVar[str] = ContextVar("session_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")

# ── LangGraph Context ─────────────────────────────────────────────
graph_run_id_var: ContextVar[str] = ContextVar("graph_run_id", default="")
node_id_var: ContextVar[str] = ContextVar("node_id", default="")

# ── Utility Functions ─────────────────────────────────────────────

def get_context_dict() -> dict:
    """Extracts all observability context into a dictionary for logging."""
    return {
        "request_id": request_id_var.get(),
        "trace_id": trace_id_var.get(),
        "session_id": session_id_var.get(),
        "user_id": user_id_var.get(),
        "graph_run_id": graph_run_id_var.get(),
        "node_id": node_id_var.get(),
    }

def clear_context():
    """Clears context for the current thread/task."""
    request_id_var.set("")
    trace_id_var.set("")
    session_id_var.set("")
    user_id_var.set("")
    graph_run_id_var.set("")
    node_id_var.set("")

def generate_trace_id() -> str:
    """Generates a UUIDv4 trace ID."""
    return str(uuid.uuid4())
