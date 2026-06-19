"""
observability/structured_logger.py
------------------------------------
JSON-structured logging for production observability.
Every log entry includes: timestamp, level, logger_name,
message, and optional request_id / agent context.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from config.settings import settings


class RTIJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter adding service metadata to every log."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "rti-agent"
        log_record["environment"] = settings.APP_ENV
        log_record["level"] = record.levelname


_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger with JSON formatting.
    Uses a registry to avoid duplicate handlers.
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # File handler
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/rti_agent.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
        )

        if settings.LOG_FORMAT == "json":
            fmt = RTIJsonFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        else:
            fmt = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        console_handler.setFormatter(fmt)
        file_handler.setFormatter(fmt)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.propagate = False

    _loggers[name] = logger
    return logger
