"""
bot/app.py
-----------
Builds and returns the configured python-telegram-bot Application instance.
Handlers are registered here; main.py calls build_app() to get it.
"""

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import settings
from .handlers import (
    about_handler,
    error_handler,
    help_handler,
    message_handler,
    provider_handler,
    reset_handler,
    start_handler,
    status_handler,
)

log = logging.getLogger(__name__)


def build_app() -> Application:
    """Construct and return the Telegram Application with all handlers wired."""
    app = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # ── Command handlers ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("reset", reset_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("provider", provider_handler))
    app.add_handler(CommandHandler("about", about_handler))

    # ── Text message handler (catch-all for non-commands) ─────────────────────
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    # ── Error handler ─────────────────────────────────────────────────────────
    app.add_error_handler(error_handler)

    log.info("Telegram Application built with %d handlers", len(app.handlers[0]))
    return app
