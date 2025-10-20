# utils/logger.py

import logging
from utils.logging_config import setup_logging

# Ensure logging configuration is set up
setup_logging()

def get_logger(name: str):
    """
    Returns a logger instance for the given module or class name.
    Automatically configured with centralized logging.
    """
    return logging.getLogger(name)
