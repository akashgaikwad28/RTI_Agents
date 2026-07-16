"""
observability/context.py
-------------------------
Context propagation for distributed tracing and observability.
Uses contextvars to maintain request and graph run context across async boundaries.
"""

import uuid
from contextvars import ContextVar, Token
from typing import Optional, Dict

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

def set_request_context(
    request_id: str = "",
    trace_id: str = "",
    session_id: str = "",
    user_id: str = ""
) -> Dict[str, Token]:
    """Sets request-level context variables. Returns tokens for resetting."""
    return {
        "request_id": request_id_var.set(request_id),
        "trace_id": trace_id_var.set(trace_id),
        "session_id": session_id_var.set(session_id),
        "user_id": user_id_var.set(user_id),
    }

def set_graph_context(graph_run_id: str, node_id: str = "") -> Dict[str, Token]:
    """Sets graph-level context variables. Returns tokens for resetting.
    Call this from graph_builder before ainvoke and reset after.
    """
    return {
        "graph_run_id": graph_run_id_var.set(graph_run_id),
        "node_id": node_id_var.set(node_id),
    }

def set_node_context(node_id: str) -> Token:
    """Sets the current node ID. Call from @trace_node decorator."""
    return node_id_var.set(node_id)

def reset_context(tokens: Dict[str, Token]):
    """Resets context variables using their reset tokens (proper async-safe reset)."""
    for var_name, token in tokens.items():
        if var_name == "request_id":
            request_id_var.reset(token)
        elif var_name == "trace_id":
            trace_id_var.reset(token)
        elif var_name == "session_id":
            session_id_var.reset(token)
        elif var_name == "user_id":
            user_id_var.reset(token)
        elif var_name == "graph_run_id":
            graph_run_id_var.reset(token)
        elif var_name == "node_id":
            node_id_var.reset(token)

def clear_context():
    """Clears context for the current thread/task using set('') — use reset_context for async safety."""
    request_id_var.set("")
    trace_id_var.set("")
    session_id_var.set("")
    user_id_var.set("")
    graph_run_id_var.set("")
    node_id_var.set("")

def generate_trace_id() -> str:
    """Generates a UUIDv4 trace ID."""
    return str(uuid.uuid4())
