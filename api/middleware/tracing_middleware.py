"""
api/middleware/tracing_middleware.py
-------------------------------------
Initializes contextvars for distributed tracing (Trace ID, Request ID).
Extracts correlation IDs from incoming HTTP headers if present.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from observability.context import (
    request_id_var, trace_id_var, session_id_var, 
    generate_trace_id, clear_context
)
import uuid

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract headers or generate new ones
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-ID", generate_trace_id())
        session_id = request.headers.get("X-Session-ID", "anonymous")
        
        # Set ContextVars for this async task/request lifecycle
        r_token = request_id_var.set(req_id)
        t_token = trace_id_var.set(trace_id)
        s_token = session_id_var.set(session_id)
        
        # Attach to request state for standard FastAPI access if needed
        request.state.request_id = req_id
        request.state.trace_id = trace_id
        
        try:
            response = await call_next(request)
            
            # Inject correlation IDs back into the HTTP response
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Trace-ID"] = trace_id
            
            return response
        finally:
            # Clean up context to prevent memory leaks in async workers
            request_id_var.reset(r_token)
            trace_id_var.reset(t_token)
            session_id_var.reset(s_token)
