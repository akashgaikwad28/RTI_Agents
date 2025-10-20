# utils/exception_handler.py

import traceback
from functools import wraps
from utils.logger import logger

def exception_handler(func):
    """
    Decorator that logs detailed exception information with traceback.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            if tb:
                filename, line, func_name, _ = tb[-1]
                logger.error(
                    f"Exception occurred in {filename}, line {line}, in {func_name}: {str(e)}",
                    exc_info=True
                )
            else:
                logger.error(f"Exception: {str(e)}", exc_info=True)
            raise  # Re-raise the exception after logging
    return wrapper
