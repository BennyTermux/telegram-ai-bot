"""
bot/handlers.py
----------------
All Telegram command and message handlers.
Each handler is a standalone async function registered in bot/app.py.

Commands:
  /start   — welcome message
  /help    — usage instructions
  /reset   — clear conversation history
  /provider <name>  — switch AI provider at runtime
  /status  — show current provider and history length
  /about   — project info
"""

import logging

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from backend.ai_service import ai_service
from config import settings
from utils.helpers import is_rate_limited, split_long_message
from .middleware import log_update

log = logging.getLogger(__name__)

# ── /start ────────────────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    user = update.effective_user
    name = user.first_name if user else "there"
    await update.message.reply_text(
        f"👋 Hello, *{name}*! I'm your AI-powered assistant.\n\n"
        "Just send me a message and I'll reply using AI.\n\n"
        "Commands:\n"
        "  /help — usage guide\n"
        "  /reset — clear conversation history\n"
        "  /status — show current config\n"
        "  /about — project info",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── /help ─────────────────────────────────────────────────────────────────────

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    await update.message.reply_text(
        "*📖 Help*\n\n"
        "Send any text message to chat with the AI.\n\n"
        "*Commands:*\n"
        "  `/start` — welcome screen\n"
        "  `/help` — this message\n"
        "  `/reset` — clear your conversation history\n"
        "  `/status` — current AI provider and history\n"
        "  `/provider <name>` — switch provider (openai / anthropic / gemini)\n"
        "  `/about` — about this bot\n\n"
        "*Tips:*\n"
        "• The bot remembers the last conversation context.\n"
        "• Use /reset to start a fresh conversation.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── /reset ────────────────────────────────────────────────────────────────────

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    user_id = update.effective_user.id
    ai_service.clear_history(user_id)
    await update.message.reply_text(
        "🔄 Conversation history cleared. Let's start fresh!",
    )


# ── /status ───────────────────────────────────────────────────────────────────

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    user_id = update.effective_user.id
    history = ai_service.get_history(user_id)
    provider = ai_service._provider  # noqa: SLF001

    await update.message.reply_text(
        f"*🤖 Status*\n\n"
        f"Provider: `{provider.name}`\n"
        f"Model: `{getattr(provider, '_model', 'unknown')}`\n"
        f"History messages: `{len(history)}`\n"
        f"Max tokens: `{settings.MAX_TOKENS}`\n"
        f"Temperature: `{settings.TEMPERATURE}`",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── /provider ─────────────────────────────────────────────────────────────────

async def provider_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    if not context.args:
        await update.message.reply_text(
            "Usage: `/provider <name>`\nAvailable: openai, anthropic, gemini",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    name = context.args[0].lower()
    result = ai_service.switch_provider(name)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)


# ── /about ────────────────────────────────────────────────────────────────────

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)
    await update.message.reply_text(
        "*🛠 About*\n\n"
        "Telegram AI Bot — modular, Termux-compatible AI assistant.\n\n"
        "Built with:\n"
        "• `python-telegram-bot` v21\n"
        "• `httpx` for async HTTP\n"
        "• Pluggable AI providers (OpenAI / Anthropic / Gemini)\n\n"
        "Source: github.com/YOUR_USERNAME/telegram-ai-bot",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── Text message handler ──────────────────────────────────────────────────────

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_update(update)

    user_id = update.effective_user.id
    user_message = update.message.text or ""

    if not user_message.strip():
        return

    # Rate limiting
    if is_rate_limited(user_id, settings.RATE_LIMIT_SECONDS):
        await update.message.reply_text(
            "⏳ Please wait a moment before sending another message."
        )
        return

    # Show typing indicator while processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    # Call AI backend
    reply = await ai_service.chat(user_id=user_id, user_message=user_message)

    # Handle long responses by splitting them
    chunks = split_long_message(reply, max_length=settings.MAX_MESSAGE_LENGTH)
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)


# ── Error handler ─────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Unhandled exception in update %s", update, exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "⚠️ Something went wrong. Please try again."
        )
