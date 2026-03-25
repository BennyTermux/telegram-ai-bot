#!/usr/bin/env python3
"""
main.py
--------
Entry point for the Telegram AI Bot.
Run with:  python main.py

The bot uses long-polling (no webhook required), which works perfectly in
Termux without a public domain or SSL certificate.
"""

import asyncio
import logging
import sys

from utils.logger import get_logger

# Initialise the root logger before any other import that might log
log = get_logger("main")


def _check_python_version() -> None:
    if sys.version_info < (3, 10):
        sys.exit(
            "Python 3.10+ is required. "
            "In Termux run: pkg install python"
        )


def _validate_config() -> None:
    """Eagerly validate required settings so we fail fast with a clear message."""
    try:
        from config import settings  # noqa: F401 — import triggers validation
        log.info("Config loaded | provider=%s", settings.AI_PROVIDER)
    except EnvironmentError as exc:
        log.critical("Configuration error: %s", exc)
        sys.exit(1)


def main() -> None:
    _check_python_version()
    _validate_config()

    # Import here so config is fully validated before any provider init
    from bot import build_app

    log.info("Starting Telegram AI Bot…")
    app = build_app()

    log.info("Bot is running. Press Ctrl+C to stop.")
    # run_polling blocks until Ctrl+C or SIGTERM
    app.run_polling(
        poll_interval=1.0,
        timeout=20,
        drop_pending_updates=True,   # ignore updates that piled up while offline
        allowed_updates=["message"],
    )
    log.info("Bot stopped.")


if __name__ == "__main__":
    main()
