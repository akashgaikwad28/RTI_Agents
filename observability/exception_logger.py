"""
observability/exception_logger.py
----------------------------------
Taxonomy for exceptions allowing structured error logging.
"""

import traceback
from typing import Optional

class BaseRTIException(Exception):
    """Base exception class for RTI-Agent with structured metadata."""
    def __init__(self, message: str, severity: str = "ERROR", retryable: bool = False, root_cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.retryable = retryable
        self.root_cause = root_cause

class ValidationError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="WARNING", retryable=False, **kwargs)

class RetrievalError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="ERROR", retryable=True, **kwargs)

class EmbeddingError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="ERROR", retryable=True, **kwargs)

class OCRFailure(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="WARNING", retryable=True, **kwargs)

class ToolExecutionError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="ERROR", retryable=True, **kwargs)

class GraphExecutionError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="CRITICAL", retryable=False, **kwargs)

class SecurityViolation(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="CRITICAL", retryable=False, **kwargs)

class HallucinationRiskError(BaseRTIException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity="WARNING", retryable=True, **kwargs)

def format_exception_dict(exc: Exception) -> dict:
    """Formats an exception into a structured dictionary for logging."""
    error_dict = {
        "error_type": exc.__class__.__name__,
        "message": str(exc),
        "stack_trace": traceback.format_exc(),
    }
    
    if isinstance(exc, BaseRTIException):
        error_dict["severity"] = exc.severity
        error_dict["retryable"] = exc.retryable
        if exc.root_cause:
            error_dict["root_cause"] = str(exc.root_cause)
            
    return error_dict
