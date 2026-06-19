"""
observability/security_logger.py
---------------------------------
High-level wrappers for structured security event logging.
"""

from typing import Dict, Any
from observability.telemetry import telemetry
from observability.telemetry_models import SecurityClassification, Outcome
from observability.metrics import rti_security_events_total

def log_security_incident(
    classification: SecurityClassification,
    event_name: str,
    metadata: Dict[str, Any],
    operation: str = "security_check"
):
    """
    Logs a security event to the dedicated security logger.
    Automatically increments Prometheus counters.
    """
    # Increment metrics
    rti_security_events_total.labels(classification=classification.value).inc()
    
    # Write structured log
    telemetry.log_security_event(
        classification=classification,
        event=event_name,
        operation=operation,
        metadata=metadata,
        outcome=Outcome.FAILURE
    )
