"""
utils/helpers.py
----------------
Miscellaneous helper utilities used across the project.
"""

import time
from typing import Dict


# ── Simple in-process rate limiter ───────────────────────────────────────────

_last_request: Dict[int, float] = {}   # user_id → last request timestamp


def is_rate_limited(user_id: int, min_interval_seconds: int) -> bool:
    """
    Return True if the user sent a request too recently.
    Simple single-instance rate limiter; replace with Redis for multi-process.
    """
    now = time.monotonic()
    last = _last_request.get(user_id, 0.0)
    if now - last < min_interval_seconds:
        return True
    _last_request[user_id] = now
    return False


# ── Text utilities ────────────────────────────────────────────────────────────

def split_long_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Split text into chunks that fit within Telegram's message size limit.
    Tries to split on newlines to keep context readable.
    """
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        # Find a good split point (last newline before limit)
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def truncate(text: str, max_length: int = 200) -> str:
    """Truncate a string for display in logs."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + e texd
