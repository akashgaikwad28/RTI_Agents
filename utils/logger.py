# utils/logger.py
import logging
from utils.logging_config import setup_logging

setup_logging()

def get_logger(name: str):
    """
    Returns a logger instance for the given module or class name.
    """
    return logging.getLogger(name)


logger = get_logger("RTI_Agents")
