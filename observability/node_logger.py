"""
observability/node_logger.py
-----------------------------
Provides the @trace_node decorator to automatically log LangGraph node execution.
"""

import time
from functools import wraps
from typing import Callable, Any
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome
from observability.graph_tracer import compress_state

def trace_node(node_name: str):
    """
    Decorator for LangGraph nodes.
    Logs entry, exit, execution time, and state changes (compressed).
    """
    def decorator(func: Callable):
        def _get_state_dict(state: Any):
            return state.copy() if isinstance(state, dict) else (
                state.dict() if hasattr(state, "dict") else {}
            )

        def _handle_result(start_time, old_state_dict, result):
            latency_ms = (time.time() - start_time) * 1000
            
            # Compress state changes
            new_state_dict = result.copy() if isinstance(result, dict) else (
                result.dict() if hasattr(result, "dict") else {}
            )
            
            # LangGraph nodes often return just the updates to the state
            # If they return a partial dict, we compute diff against what they returned
            changed_keys, state_hash = compress_state(old_state_dict, new_state_dict)
            
            telemetry.log_node_event(
                node_name=node_name,
                event=f"{node_name}_completed",
                operation="node_execution",
                outcome=Outcome.SUCCESS,
                execution_time_ms=latency_ms
            )
            
            # Also log the state diff to graph tracer context
            telemetry.log_graph_event(
                event=f"{node_name}_state_updated",
                operation="state_transition",
                state_hash=state_hash,
                changed_keys=changed_keys
            )
            return result

        def _handle_error(start_time, e):
            latency_ms = (time.time() - start_time) * 1000
            telemetry.log_node_event(
                node_name=node_name,
                event=f"{node_name}_failed",
                operation="node_execution",
                outcome=Outcome.FAILURE,
                execution_time_ms=latency_ms
            )
            telemetry.log_error(e, operation=f"node_{node_name}")
            raise e

        @wraps(func)
        async def async_wrapper(state: Any, *args, **kwargs):
            start_time = time.time()
            old_state_dict = _get_state_dict(state)
            
            telemetry.log_node_event(
                node_name=node_name,
                event=f"{node_name}_started",
                operation="node_execution",
            )
            
            try:
                res = await func(state, *args, **kwargs)
                return _handle_result(start_time, old_state_dict, res)
            except Exception as e:
                _handle_error(start_time, e)
            
        @wraps(func)
        def sync_wrapper(state: Any, *args, **kwargs):
            start_time = time.time()
            old_state_dict = _get_state_dict(state)
            
            telemetry.log_node_event(
                node_name=node_name,
                event=f"{node_name}_started",
                operation="node_execution",
            )
            
            try:
                res = func(state, *args, **kwargs)
                return _handle_result(start_time, old_state_dict, res)
            except Exception as e:
                _handle_error(start_time, e)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
