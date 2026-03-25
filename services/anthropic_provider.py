"""
services/anthropic_provider.py
--------------------------------
Anthropic (Claude) provider using the Messages API.
Supports claude-3-5-haiku-20241022, claude-3-5-sonnet-20241022, etc.
"""

import logging
from typing import Optional

import httpx

from config import settings
from .base_provider import AIResponse, BaseAIProvider, Message, ProviderError

log = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(BaseAIProvider):

    def __init__(self) -> None:
        self._api_key = settings.ANTHROPIC_API_KEY
        self._model = settings.ANTHROPIC_MODEL

        if not self._api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. Add it to your .env file."
            )

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        # Anthropic does not allow system messages inside the messages array.
        # The system prompt is a top-level field.
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]

        payload: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

        log.debug("Anthropic request → model=%s", self._model)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(ANTHROPIC_API_URL, json=payload, headers=headers)
            except httpx.RequestError as exc:
                raise ProviderError(self.name, f"Network error: {exc}") from exc

        if resp.status_code != 200:
            raise ProviderError(
                self.name,
                f"API error: {resp.text[:400]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        text = data["content"][0]["text"]
        usage = data.get("usage", {})

        return AIResponse(
            text=text,
            provider=self.name,
            model=data.get("model", self._model),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            raw=data,
        )
