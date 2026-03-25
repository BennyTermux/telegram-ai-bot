"""
config/settings.py
------------------
Central configuration loader. All secrets come from environment variables via .env.
Never hardcode secrets here.
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (works whether you run from root or a subdir)
load_dotenv()


def _require(key: str) -> str:
    """Return env var value or raise a clear error if missing."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in the value."
        )
    return value


# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")

# Optional: only needed if you use Telegram's MTProto client (pyrogram / telethon)
TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")

# ── AI Provider selection ──────────────────────────────────────────────────────
# Set AI_PROVIDER to "openai", "anthropic", "gemini", etc.
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai").lower()

# ── OpenAI ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# ── Anthropic ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── Generation defaults ───────────────────────────────────────────────────────
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
SYSTEM_PROMPT: str = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful, concise, and friendly AI assistant.",
)

# ── Bot behaviour ─────────────────────────────────────────────────────────────
MAX_MESSAGE_LENGTH: int = 4096          # Telegram hard limit
RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "2"))

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
