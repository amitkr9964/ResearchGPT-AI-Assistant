"""Structured logging configuration."""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "researchgpt", level: Optional[int] = None) -> logging.Logger:
    log_level = level or (logging.DEBUG if __debug__ else logging.INFO)
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(log_level)
    return logger


logger = setup_logger()
