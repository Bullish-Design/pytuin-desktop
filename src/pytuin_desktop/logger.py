# path: pytuin_desktop/logger.py
"""Logging utilities."""
from __future__ import annotations
import logging, os
from logging import Logger

def get_logger(name: str = "pytuin.desktop") -> Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())
    level_name = os.getenv("PYTUIN_LOG_LEVEL", "WARNING").upper()
    try:
        logger.setLevel(getattr(logging, level_name, logging.WARNING))
    except Exception:
        logger.setLevel(logging.WARNING)
    logger.propagate = False
    return logger

logger = get_logger()
