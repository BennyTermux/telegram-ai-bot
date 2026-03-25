"""
backend/ai_service.py
----------------------
The AIService sits between the Telegram bot handlers and the raw AI providers.
It manages:
  - Per-user conversation history (in-memory; swap for Redis/SQLite if needed)
  - System prompt injection
  - Token/length guards
  - Graceful error handling
"""

import logging
from collections import defaultdict, deque
from typing import Optional

from config import settings
from services import AIResponse, Message, ProviderError, get_provider

log = logging.getLogger(__name__)

# Max messages kept per user in conversation history
MAX_HISTORY_MESSAGES = 20


class AIService:
    """
    Stateful AI service with per-user conversation history.
    One instance is shared across all bot handlers.
    """

    def __init__(self) -> None:
        # deque keeps the last N messages; acts as a sliding window
        self._history: dict[int, deque[Message]] = defaultdict(
            lambda: deque(maxlen=MAX_HISTORY_MESSAGES)
        )
        self._provider = get_provider()
        log.info(
            "AIService ready | provider=%s | system_prompt_len=%d",
            self._provider.name,
            len(settings.SYSTEM_PROMPT),
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def chat(self, user_id: int, user_message: str) -> str:
        """
        Process a user message and return the assistant's reply as a string.
        Raises nothing — errors are returned as friendly messages.
        """
        # Append user message to history
        self._history[user_id].append(Message(role="user", content=user_message))

        try:
            response: AIResponse = await self._provider.complete(
                messages=list(self._history[user_id]),
                system_prompt=settings.SYSTEM_PROMPT,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
            )
        except ProviderError as exc:
            log.error("Provider error for user %d: %s", user_id, exc)
            return (
                "⚠️ The AI service returned an error. Please try again in a moment.\n"
                f"_(Error: {exc})_"
            )
        except Exception as exc:  # noqa: BLE001
            log.exception("Unexpected error for user %d", user_id)
            return "⚠️ An unexpected error occurred. The error has been logged."

        reply = response.text

        # Append assistant reply to history
        self._history[user_id].append(Message(role="assistant", content=reply))

        log.info(
            "user=%d | provider=%s | in=%d out=%d tokens",
            user_id,
            response.provider,
            response.input_tokens,
            response.output_tokens,
        )
        return reply

    def clear_history(self, user_id: int) -> None:
        """Wipe conversation history for a user (e.g. /reset command)."""
        self._history.pop(user_id, None)
        log.info("History cleared for user %d", user_id)

    def get_history(self, user_id: int) -> list[Message]:
        """Return a snapshot of the user's current conversation history."""
        return list(self._history.get(user_id, []))

    def switch_provider(self, provider_name: str) -> str:
        """
        Hot-swap the active AI provider at runtime (e.g. /provider openai).
        Returns a status message.
        """
        try:
            self._provider = get_provider(provider_name)
            log.info("Switched to provider: %s", provider_name)
            return f"✅ Switched to provider: *{provider_name}*"
        except ValueError as exc:
            return f"❌ {exc}"


# ── Module-level singleton ────────────────────────────────────────────────────
# Import this wherever you need AI: `from backend.ai_service import ai_service`
ai_service = AIService()
