"""
observability/audit_logger.py
------------------------------
Writes immutable audit trails for state transitions, approvals, and rejections.
"""

from observability.logger import audit_logger
from observability.telemetry_models import Component, Outcome
import time

def log_audit_action(
    actor: str,
    action: str,
    reason: str,
    before_state: dict = None,
    after_state: dict = None,
    department: str = "unknown"
):
    """
    Logs an action to the immutable audit stream.
    Requires before/after state to prove transitions.
    """
    
    audit_data = {
        "event": "audit_trail",
        "component": Component.AUDIT.value,
        "operation": "state_transition",
        "outcome": Outcome.SUCCESS.value,
        "actor": actor,
        "action": action,
        "reason": reason,
        "department": department,
        "timestamp": time.time(),
    }
    
    # Compress state for audit just like graph tracing to avoid huge files
    if before_state and after_state:
        changed_keys = [k for k in after_state if before_state.get(k) != after_state.get(k)]
        audit_data["changed_keys"] = changed_keys
        
    audit_logger.info(action, extra=audit_data)
