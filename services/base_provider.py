"""
services/base_provider.py
--------------------------
Abstract base class that every AI provider must implement.
Adding a new provider = subclass BaseAIProvider + register in ai_router.py.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    """A single conversation message."""
    role: str           # "user" | "assistant" | "system"
    content: str


@dataclass
class AIResponse:
    """Standardised response envelope returned to the bot layer."""
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: Optional[dict] = field(default=None, repr=False)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BaseAIProvider(ABC):
    """
    All AI providers must implement this interface.
    The bot layer only depends on this abstraction — never on a concrete provider.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier, e.g. 'openai', 'anthropic'."""

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """
        Send messages to the AI API and return a standardised AIResponse.
        Raise ProviderError on any API-level failure.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.name!r}>"


class ProviderError(Exception):
    """Raised when an AI provider returns an error or is unreachable."""

    def __init__(self, provider: str, message: str, status_code: int = 0):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message} (HTTP {status_code})")
