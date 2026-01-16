import logging
import sys
from logging import Logger
from typing import Optional

LOG_FORMAT = "%(asctime)s | " "%(levelname)s | " "%(name)s | " "%(message)s"


def setup_logging(log_level: str = "INFO") -> None:
    """Configure global logging handlers and level for the application.

    Call this once during application startup (e.g., before launching the ASGI server).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove default handlers (important when using uvicorn)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> Logger:
    """Return a configured Logger instance for the given module name.

    Args:
        name (Optional[str]): optional logger name, defaults to root.

    Returns:
        Logger: configured Python logger.
    """
    return logging.getLogger(name)
