"""
services/gemini_provider.py
-----------------------------
Google Gemini provider using the generateContent REST API.
Supports gemini-2.0-flash, gemini-1.5-pro, etc.
"""

import logging
from typing import Optional

import httpx

from config import settings
from .base_provider import AIResponse, BaseAIProvider, Message, ProviderError

log = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(BaseAIProvider):

    def __init__(self) -> None:
        self._api_key = settings.GEMINI_API_KEY
        self._model = settings.GEMINI_MODEL

        if not self._api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

    @property
    def name(self) -> str:
        return "gemini"

    async def complete(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        # Gemini uses "contents" with "parts"
        contents = []
        for msg in messages:
            if msg.role == "system":
                continue  # handled below via systemInstruction
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        if system_prompt:
            payload["system_instruction"] = {
                "parts": [{"text": system_prompt}]
            }

        url = (
            f"{GEMINI_BASE_URL}/{self._model}:generateContent"
            f"?key={self._api_key}"
        )

        log.debug("Gemini request → model=%s", self._model)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(url, json=payload)
            except httpx.RequestError as exc:
                raise ProviderError(self.name, f"Network error: {exc}") from exc

        if resp.status_code != 200:
            raise ProviderError(
                self.name,
                f"API error: {resp.text[:400]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})

        return AIResponse(
            text=text,
            provider=self.name,
            model=self._model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            raw=data,
        )
