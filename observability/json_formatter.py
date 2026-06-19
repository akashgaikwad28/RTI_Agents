"""
observability/json_formatter.py
--------------------------------
Advanced JSON formatter for enterprise telemetry.
Injects contextvars (request_id, trace_id, graph_run_id) automatically.
Applies PII redaction pipeline before formatting to JSON string.
"""

import logging
from pythonjsonlogger import jsonlogger
from observability.context import get_context_dict
from observability.pii_redactor import redact_log_record
from config.settings import settings

class TelemetryJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with context propagation and PII redaction."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # 1. Inject Service Metadata
        log_record["service"] = "rti-agent"
        log_record["environment"] = settings.APP_ENV
        
        # 2. Map standard Python logging levels to our taxonomy
        log_record["level"] = record.levelname
        
        # 3. Inject ContextVars
        ctx = get_context_dict()
        for key, value in ctx.items():
            if value:  # Only inject if populated
                log_record[key] = value

    def format(self, record: logging.LogRecord) -> str:
        """Applies PII redaction to the dict before serialization."""
        # Get the standard formatted dictionary
        # jsonlogger does this via format -> process_log_record -> serialize
        # Let's intercept process_log_record instead
        return super().format(record)

    def process_log_record(self, log_record: dict) -> dict:
        """Hook into pythonjsonlogger to redact before JSON stringification."""
        redacted_record = redact_log_record(log_record)
        return super().process_log_record(redacted_record)
