"""Áudio no formato OpenAI (POST /audio/speech)."""
from __future__ import annotations

import requests

from .base import TTSError


class OpenAITTS:
    def __init__(self, base_url: str, api_key: str, model: str = "gpt-4o-mini-tts", timeout: float = 60):
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key
        self.model = model or "gpt-4o-mini-tts"
        self.timeout = timeout

    def synthesize(self, text: str, voice: str) -> bytes:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {"model": self.model, "input": text, "voice": voice or "alloy", "response_format": "mp3"}
        try:
            r = requests.post(f"{self.base_url}/audio/speech", headers=headers, json=body, timeout=self.timeout)
        except requests.RequestException as e:
            raise TTSError(f"network error: {e}") from e
        if r.status_code >= 400:
            raise TTSError(f"HTTP {r.status_code}: {r.text[:300]}")
        return r.content
