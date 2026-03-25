"""
utils/logger.py
---------------
Configures a single shared logger used across the whole project.
Writes to both stdout (coloured) and a rotating log file.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from config import settings


def _ensure_log_dir(log_path: str) -> None:
    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)


def get_logger(name: str = "telegram-ai-bot") -> logging.Logger:
    """
    Return a logger that writes to stdout and to a rotating file.
    Call this once at startup; all modules should use logging.getLogger(__name__).
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times if called more than once
    if logger.handlers:
        return logger

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Stdout handler ────────────────────────────────────────────────────────
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    # ── Rotating file handler ─────────────────────────────────────────────────
    try:
        _ensure_log_dir(settings.LOG_FILE)
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("Could not create log file (%s). File logging disabled.", exc)

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    return logger


# Module-level convenience logger
log = get_logger()
