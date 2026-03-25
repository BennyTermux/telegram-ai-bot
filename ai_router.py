"""
services/ai_router.py
----------------------
Provider registry + factory.

To add a new provider:
  1. Create services/myprovider_provider.py  (subclass BaseAIProvider)
  2. Import it here and add it to PROVIDER_MAP
  3. Set AI_PROVIDER=myprovider in .env
"""

import logging
from typing import Optional

from config import settings
from .base_provider import BaseAIProvider

log = logging.getLogger(__name__)

# ── Registry ──────────────────────────────────────────────────────────────────
def _build_registry() -> dict[str, type[BaseAIProvider]]:
    registry: dict[str, type[BaseAIProvider]] = {}

    # Lazy imports so missing API keys only error when that provider is used
    try:
        from .openai_provider import OpenAIProvider
        registry["openai"] = OpenAIProvider
    except ImportError:
        pass

    try:
        from .anthropic_provider import AnthropicProvider
        registry["anthropic"] = AnthropicProvider
    except ImportError:
        pass

    try:
        from .gemini_provider import GeminiProvider
        registry["gemini"] = GeminiProvider
    except ImportError:
        pass

    return registry


PROVIDER_REGISTRY: dict[str, type[BaseAIProvider]] = _build_registry()

# ── Singleton cache ───────────────────────────────────────────────────────────
_instances: dict[str, BaseAIProvider] = {}


def get_provider(name: Optional[str] = None) -> BaseAIProvider:
    """
    Return a (cached) provider instance.
    Defaults to the AI_PROVIDER setting in .env.
    """
    provider_name = (name or settings.AI_PROVIDER).lower()

    if provider_name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys()) or "none installed"
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. "
            f"Available: {available}. "
            f"Check AI_PROVIDER in your .env."
        )

    if provider_name not in _instances:
        log.info("Initialising AI provider: %s", provider_name)
        _instances[provider_name] = PROVIDER_REGISTRY[provider_name]()

    return _instances[provider_name]
