# utils/logging_config.py

import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os
import json
from datetime import datetime

# Create logs directory if not exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "rti_system.log")

# JSON Formatter for structured logs
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)

def get_logging_config():
    """Return a complete logging configuration dictionary."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - [%(levelname)s] - %(name)s: %(message)s"
            },
            "json": {
                "()": JSONFormatter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "DEBUG",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "level": "INFO",
                "filename": LOG_FILE_PATH,
                "maxBytes": 5 * 1024 * 1024,  # 5 MB
                "backupCount": 3,
                "encoding": "utf-8"
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO"
        },
        "loggers": {
            "agents": {"level": "DEBUG", "propagate": True},
            "chains": {"level": "INFO", "propagate": True},
            "mcp_clients": {"level": "INFO", "propagate": True},
            "memory": {"level": "INFO", "propagate": True},
        }
    }

def setup_logging():
    """Set up logging configuration."""
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
