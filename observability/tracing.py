"""
observability/tracing.py
-------------------------
LangSmith tracing setup for LangGraph execution observability.
"""

import os
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)


def setup_tracing():
    """
    Configure LangSmith tracing environment.
    Call once at application startup.
    """
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info(f"[Tracing] LangSmith enabled | project={settings.LANGCHAIN_PROJECT}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("[Tracing] LangSmith disabled (set LANGCHAIN_TRACING_V2=true to enable)")
