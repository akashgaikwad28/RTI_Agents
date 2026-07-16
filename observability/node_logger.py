"""
observability/node_logger.py
-----------------------------
Provides the @trace_node decorator to automatically log LangGraph node execution.
"""

import asyncio
import time
from functools import wraps
from typing import Callable, Any
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome
from observability.graph_tracer import compress_state
from observability.context import set_node_context, node_id_var
from observability.metrics import rti_agent_duration

def trace_node(node_name: str):
    """
    Decorator for LangGraph nodes.
    Logs entry, exit, execution time, and state changes (compressed).
    Also sets node_id ContextVar so all log entries are correlated.
    Also updates rti_agent_duration Prometheus histogram.
    """
    def decorator(func: Callable):
        def _get_state_dict(state: Any):
            if isinstance(state, dict):
                return state.copy()
            if hasattr(state, "model_dump"):
                return state.model_dump()
            if hasattr(state, "dict"):
                return state.dict()
            return {}

        def _handle_result(start_time, old_state_dict, result):
            latency_ms = (time.time() - start_time) * 1000

            # Compress state changes
            if isinstance(result, dict):
                new_state_dict = result.copy()
            elif hasattr(result, "model_dump"):
                new_state_dict = result.model_dump()
            elif hasattr(result, "dict"):
                new_state_dict = result.dict()
            else:
                new_state_dict = {}

            # LangGraph nodes often return just the updates to the state
            changed_keys, state_hash = compress_state(old_state_dict, new_state_dict)

            # Update Prometheus histogram with node duration
            rti_agent_duration.labels(agent=node_name).observe(latency_ms / 1000)

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
            rti_agent_duration.labels(agent=node_name).observe(latency_ms / 1000)
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

            # Set node ID in ContextVar for log correlation
            token = set_node_context(node_name)

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
            finally:
                node_id_var.reset(token)

        @wraps(func)
        def sync_wrapper(state: Any, *args, **kwargs):
            start_time = time.time()
            old_state_dict = _get_state_dict(state)

            token = set_node_context(node_name)

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
            finally:
                node_id_var.reset(token)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
