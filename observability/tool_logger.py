"""
observability/tool_logger.py
-----------------------------
Tracks LangChain/custom tool execution latency and outcome.
"""

from observability.telemetry import telemetry
from observability.telemetry_models import Outcome, LogLevel
from observability.metrics import tool_executions_total, tool_execution_duration
import time
from functools import wraps

def trace_tool(tool_name: str):
    """Decorator to automatically trace tool execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                
                tool_executions_total.labels(tool=tool_name, status="success").inc()
                tool_execution_duration.labels(tool=tool_name).observe(latency_ms / 1000)
                
                telemetry.log_node_event(
                    node_name=tool_name,
                    event="tool_execution_success",
                    operation="tool_call",
                    outcome=Outcome.SUCCESS,
                    execution_time_ms=latency_ms
                )
                return result
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                
                tool_executions_total.labels(tool=tool_name, status="error").inc()
                
                telemetry.log_node_event(
                    node_name=tool_name,
                    event="tool_execution_failure",
                    operation="tool_call",
                    outcome=Outcome.FAILURE,
                    execution_time_ms=latency_ms,
                    level=LogLevel.ERROR
                )
                telemetry.log_error(e, operation=f"tool_execution_{tool_name}")
                raise
        return wrapper
    return decorator
