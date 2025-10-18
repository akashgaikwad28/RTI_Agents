import traceback
from utils.logger import logger

def handle_exception(e):
    """
    Logs detailed exception information with traceback.
    """
    tb = traceback.extract_tb(e.__traceback__)
    if tb:
        filename, line, func, _ = tb[-1]
        logger.error(
            f"Exception occurred in {filename}, line {line}, in {func}: {str(e)}",
            exc_info=True
        )
    else:
        logger.error(f"Exception: {str(e)}", exc_info=True)
