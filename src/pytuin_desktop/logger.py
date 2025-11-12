"""Logging utilities (v3 Step 2)."""
from __future__ import annotations

import logging
import os
from logging import Logger


def get_logger(name: str = "pytuin.desktop") -> Logger:
    """Return a library logger that is silent by default.

    - Attaches a NullHandler so library logging never writes to stdout/stderr
      unless the caller configures handlers explicitly.
    - Disables propagation to the root logger to avoid pytest/root handlers
      picking messages up implicitly.
    - Level defaults to PYTUIN_LOG_LEVEL (default WARNING).
    """
    logger = logging.getLogger(name)
    # Ensure exactly one NullHandler is present
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())
    # Silence by default; caller can override
    level_name = os.getenv("PYTUIN_LOG_LEVEL", "WARNING").upper()
    try:
        logger.setLevel(getattr(logging, level_name, logging.WARNING))
    except Exception:
        logger.setLevel(logging.WARNING)
    # Prevent bubbling to root handlers by default
    logger.propagate = False
    return logger


# Module-level default logger
logger = get_logger()
