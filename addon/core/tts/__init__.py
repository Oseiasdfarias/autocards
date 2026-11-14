"""Serviços de áudio: Edge (grátis) e formato OpenAI."""
from __future__ import annotations

from ..model import Service
from .base import TTSError, TTSProvider

EDGE_VOICES: dict[str, list[str]] = {
    "en-US": ["en-US-AriaNeural", "en-US-GuyNeural", "en-US-JennyNeural", "en-US-EmmaMultilingualNeural"],
    "en-GB": ["en-GB-SoniaNeural", "en-GB-RyanNeural"],
    "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
    "es-ES": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
    "fr-FR": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
    "de-DE": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
    "it-IT": ["it-IT-ElsaNeural", "it-IT-DiegoNeural"],
    "ja-JP": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
}
OPENAI_VOICES = ["alloy", "ash", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]


def make_tts(service: Service) -> TTSProvider:
    if service.provider == "edge":
        from .edge import EdgeTTS
        return EdgeTTS()
    if service.provider == "openai":
        from .openai_tts import OpenAITTS
        return OpenAITTS(service.base_url, service.api_key, service.default_model)
    raise TTSError(f"unknown audio provider: {service.provider}")
