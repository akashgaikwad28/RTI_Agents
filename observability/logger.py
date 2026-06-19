"""
observability/logger.py
------------------------
Configures standard logging handlers with TimedRotatingFileHandler.
Sets up multiple streams: app, error, security, etc.
Replaces the old structured_logger.py.
"""

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from observability.json_formatter import TelemetryJsonFormatter
from observability.log_sampling import should_sample

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

class SamplingFilter(logging.Filter):
    """Filters logs based on sampling rules."""
    def filter(self, record: logging.LogRecord) -> bool:
        # Check if it has an event category (e.g., passed via extra)
        category = getattr(record, "component", None)
        return should_sample(record.levelname, category)

def _create_handler(filename: str, level: int = logging.INFO) -> logging.FileHandler:
    """Creates a file handler. Uses rotation on Linux, but flat files on Windows to avoid WinError 32 lock conflicts."""
    filepath = os.path.join(LOGS_DIR, filename)
    
    if os.name == "nt":
        # Windows multi-process (uvicorn reload) locks prevent TimedRotatingFileHandler from rotating.
        handler = logging.FileHandler(filename=filepath, encoding="utf-8")
    else:
        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(
            filename=filepath,
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8"
        )
        
    handler.setLevel(level)
    
    fmt = TelemetryJsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(fmt)
    handler.addFilter(SamplingFilter())
    return handler

def _create_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = TelemetryJsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(fmt)
    handler.addFilter(SamplingFilter())
    return handler


_loggers: dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with standard handlers.
    (This function exists for backward compatibility, but domain facades should be preferred).
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Let handlers decide

    if not logger.handlers:
        logger.addHandler(_create_console_handler(logging.INFO))
        logger.addHandler(_create_handler("app.log", logging.INFO))
        
        # Dedicated error stream
        err_handler = _create_handler("error.log", logging.ERROR)
        logger.addHandler(err_handler)
        
        logger.propagate = False

    _loggers[name] = logger
    return logger

# Dedicated loggers for specialized streams
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)
if not security_logger.handlers:
    security_logger.addHandler(_create_console_handler(logging.INFO))
    security_logger.addHandler(_create_handler("security.log", logging.INFO))
    security_logger.propagate = False

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
if not audit_logger.handlers:
    audit_logger.addHandler(_create_handler("audit.log", logging.INFO))
    audit_logger.propagate = False
    
retrieval_logger = logging.getLogger("retrieval")
retrieval_logger.setLevel(logging.INFO)
if not retrieval_logger.handlers:
    retrieval_logger.addHandler(_create_handler("retrieval.log", logging.INFO))
    retrieval_logger.propagate = False
