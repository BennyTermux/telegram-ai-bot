"""
bot/middleware.py
-----------------
Custom middleware for the Telegram bot.
  - RateLimitMiddleware  : throttle spammy users
  - LoggingMiddleware    : log every incoming update
"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from telegram import Update
from telegram.ext import BaseHandler, CallbackContext

from config import settings

log = logging.getLogger(__name__)

# user_id → last message timestamp (monotonic)
_user_timestamps: Dict[int, float] = {}


async def rate_limit_check(user_id: int) -> bool:
    """
    Returns True if the user is within the rate limit (request is allowed).
    Returns False if the user should be throttled.
    """
    now = time.monotonic()
    last = _user_timestamps.get(user_id, 0.0)
    if now - last < settings.RATE_LIMIT_SECONDS:
        return False
    _user_timestamps[user_id] = now
    return True


# ── python-telegram-bot v20+ doesn't have middleware in the classical sense.
# We use a decorator-style wrapper applied in handlers.py instead.
# This module exposes the guard function for handlers to call directly.

def log_update(update: Update) -> None:
    """Log basic metadata about an incoming update (no message content)."""
    user = update.effective_user
    chat = update.effective_chat
    text_len = (
        len(update.message.text) if update.message and update.message.text else 0
    )
    log.info(
        "Update | user=%s(%d) | chat=%d | text_len=%d",
        user.username or user.first_name if user else "unknown",
        user.id if user else 0,
        chat.id if chat else 0,
        text_len,
    )
