"""
Logger Configuration.

Configures application-wide logging for the Memora simulator.

Log output:
    - Console: INFO level and above.
    - File: DEBUG level and above, written to results/logs/memora.log.

Usage:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Simulation started.")

Implementation: Phase 2 (full integration). Logger setup is functional.
"""

import logging
import os

# Project root detection
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(PROJECT_ROOT, "results", "logs")
LOG_FILE = os.path.join(LOG_DIR, "memora.log")


def get_logger(name):
    """
    Get a configured logger instance.

    Args:
        name (str): Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler — INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(levelname)s] %(name)s: %(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler — DEBUG and above
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger
