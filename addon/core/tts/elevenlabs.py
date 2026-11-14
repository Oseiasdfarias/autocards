"""Áudio pela ElevenLabs (POST /text-to-speech/{voice_id})."""
from __future__ import annotations

from urllib.parse import quote

import requests

from .base import TTSError

DEFAULT_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsTTS:
    def __init__(self, base_url: str, api_key: str, model: str = "eleven_multilingual_v2", timeout: float = 60):
        self.base_url = (base_url or DEFAULT_URL).rstrip("/")
        self.api_key = api_key
        self.model = model or "eleven_multilingual_v2"
        self.timeout = timeout

    def synthesize(self, text: str, voice: str) -> bytes:
        if not (voice or "").strip():
            raise TTSError("ElevenLabs needs a voice ID (Format & audio tab)")
        voice = quote(voice.strip(), safe="")
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        try:
            r = requests.post(f"{self.base_url}/text-to-speech/{voice}", headers=headers,
                              json={"text": text, "model_id": self.model}, timeout=self.timeout)
        except requests.RequestException as e:
            raise TTSError(f"network error: {e}") from e
        if r.status_code >= 400:
            raise TTSError(f"HTTP {r.status_code}: {r.text[:300]}")
        return r.content
