"""
services/openai_provider.py
----------------------------
OpenAI (and OpenAI-compatible) provider.
Works with GPT-4o, GPT-4o-mini, and any endpoint that uses the OpenAI Chat
Completions schema (e.g. Together AI, Groq, local LM Studio, Ollama).
"""

import logging
from typing import Optional

import httpx

from config import settings
from .base_provider import AIResponse, BaseAIProvider, Message, ProviderError

log = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    Calls the OpenAI Chat Completions API.
    Override OPENAI_BASE_URL in .env to point at any compatible endpoint.
    """

    def __init__(self) -> None:
        self._api_key = settings.OPENAI_API_KEY
        self._model = settings.OPENAI_MODEL
        self._base_url = settings.OPENAI_BASE_URL.rstrip("/")

        if not self._api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )

    @property
    def name(self) -> str:
        return "openai"

    async def complete(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        payload_messages = []

        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            payload_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self._model,
            "messages": payload_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/chat/completions"
        log.debug("OpenAI request → model=%s tokens=%d", self._model, max_tokens)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.RequestError as exc:
                raise ProviderError(self.name, f"Network error: {exc}") from exc

        if resp.status_code != 200:
            raise ProviderError(
                self.name,
                f"API error: {resp.text[:400]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return AIResponse(
            text=choice,
            provider=self.name,
            model=data.get("model", self._model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            raw=data,
        )"