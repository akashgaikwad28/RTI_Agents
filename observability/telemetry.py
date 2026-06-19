"""
observability/telemetry.py
---------------------------
Central Telemetry Facade for RTI-Agent.
All business code should use these methods rather than logging directly.
This abstracts the backend, allowing a future swap to LangSmith, Datadog, etc.
"""

from typing import Optional, List, Dict, Any
import logging
from observability.logger import get_logger, security_logger, audit_logger, retrieval_logger
from observability.telemetry_models import (
    GraphExecutionEvent, NodeExecutionEvent, LLMEvent, 
    RetrievalEvent, SecurityEvent, SecurityClassification,
    Component, Outcome, LogLevel
)

app_logger = get_logger("rti-agent")
err_logger = get_logger("error")

class TelemetryFacade:
    
    @staticmethod
    def _emit(logger_instance: logging.Logger, event_model: Any, msg: str = ""):
        """Converts pydantic model to dict and pushes to logger."""
        extra = event_model.dict(exclude_none=True)
        level_value = getattr(logging, event_model.level.value, logging.INFO)
        # We pass the event name as the message if none provided, 
        # but the real meat is in the `extra` dict which gets flattened by JSON formatter.
        logger_instance.log(level_value, msg or event_model.event, extra=extra)

    @classmethod
    def log_graph_event(
        cls, 
        event: str, 
        operation: str, 
        outcome: Outcome = Outcome.SUCCESS,
        execution_time_ms: Optional[float] = None,
        hitl_enabled: bool = False,
        state_hash: Optional[str] = None,
        changed_keys: Optional[List[str]] = None,
        level: LogLevel = LogLevel.INFO
    ):
        model = GraphExecutionEvent(
            event=event,
            operation=operation,
            outcome=outcome,
            execution_time_ms=execution_time_ms,
            hitl_enabled=hitl_enabled,
            state_hash=state_hash,
            changed_keys=changed_keys,
            level=level
        )
        cls._emit(app_logger, model)

    @classmethod
    def log_node_event(
        cls,
        node_name: str,
        event: str,
        operation: str,
        outcome: Outcome = Outcome.SUCCESS,
        execution_time_ms: Optional[float] = None,
        estimated_cost_usd: float = 0.0,
        tool_calls: int = 0,
        level: LogLevel = LogLevel.INFO
    ):
        model = NodeExecutionEvent(
            node_name=node_name,
            event=event,
            operation=operation,
            outcome=outcome,
            execution_time_ms=execution_time_ms,
            estimated_cost_usd=estimated_cost_usd,
            tool_calls=tool_calls,
            level=level
        )
        cls._emit(app_logger, model)

    @classmethod
    def log_llm_call(
        cls,
        event: str,
        operation: str,
        provider: str,
        model_name: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        outcome: Outcome = Outcome.SUCCESS,
        level: LogLevel = LogLevel.INFO
    ):
        model = LLMEvent(
            event=event,
            operation=operation,
            outcome=outcome,
            provider=provider,
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=estimated_cost_usd,
            latency_ms=latency_ms,
            level=level
        )
        cls._emit(app_logger, model)

    @classmethod
    def log_retrieval(
        cls,
        event: str,
        operation: str,
        query: str,
        latency_ms: float = 0.0,
        retrieved_documents: int = 0,
        reranked_documents: int = 0,
        final_context_docs: int = 0,
        dropped_documents: int = 0,
        cache_hit: bool = False,
        outcome: Outcome = Outcome.SUCCESS,
        level: LogLevel = LogLevel.INFO
    ):
        model = RetrievalEvent(
            event=event,
            operation=operation,
            query=query,
            latency_ms=latency_ms,
            retrieved_documents=retrieved_documents,
            reranked_documents=reranked_documents,
            final_context_docs=final_context_docs,
            dropped_documents=dropped_documents,
            cache_hit=cache_hit,
            outcome=outcome,
            level=level
        )
        cls._emit(retrieval_logger, model)

    @classmethod
    def log_security_event(
        cls,
        classification: SecurityClassification,
        event: str,
        operation: str,
        metadata: Dict[str, Any],
        outcome: Outcome = Outcome.FAILURE,
        level: LogLevel = LogLevel.CRITICAL
    ):
        model = SecurityEvent(
            classification=classification,
            event=event,
            operation=operation,
            metadata=metadata,
            outcome=outcome,
            level=level
        )
        cls._emit(security_logger, model)
        
    @classmethod
    def log_error(cls, exc: Exception, operation: str = "unknown"):
        """Central method to log exceptions."""
        from observability.exception_logger import format_exception_dict
        err_data = format_exception_dict(exc)
        exc_message = err_data.pop("message", str(exc))
        err_logger.error(f"Exception during {operation}: {exc_message}", extra={
            "event": "exception_raised",
            "component": "api",
            "operation": operation,
            "outcome": Outcome.FAILURE.value,
            "error_message": exc_message,
            **err_data
        })

telemetry = TelemetryFacade()
