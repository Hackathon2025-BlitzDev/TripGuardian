"""Centralized logging helpers for the TripGuardian backend."""

import logging
import os
from typing import Optional

_LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
_DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging(level: Optional[str] = None) -> None:
    """Configure root logging once with a consistent format."""

    log_level = (level or _DEFAULT_LEVEL).upper()
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.setLevel(log_level)
        return

    logging.basicConfig(level=log_level, format=_LOG_FORMAT)
