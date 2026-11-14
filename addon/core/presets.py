"""Atalhos de serviço (spec §7.6). Preços são estimativas, sempre editáveis."""
TEXT_PRESETS = {
    "OpenAI": {"base_url": "https://api.openai.com/v1", "default_model": "gpt-4o-mini",
               "price_in_per_m": 0.15, "price_out_per_m": 0.60},
    "OpenRouter": {"base_url": "https://openrouter.ai/api/v1", "default_model": "openai/gpt-4o-mini",
                   "price_in_per_m": 0.15, "price_out_per_m": 0.60},
    "Groq": {"base_url": "https://api.groq.com/openai/v1", "default_model": "llama-3.1-8b-instant",
             "price_in_per_m": 0.05, "price_out_per_m": 0.08},
    "Ollama (local)": {"base_url": "http://localhost:11434/v1", "default_model": "llama3.1",
                       "price_in_per_m": 0.0, "price_out_per_m": 0.0},
    "LM Studio (local)": {"base_url": "http://localhost:1234/v1", "default_model": "",
                          "price_in_per_m": 0.0, "price_out_per_m": 0.0},
}
TTS_PRESETS = {
    "Edge (free)": {"provider": "edge", "base_url": "", "default_model": "", "price_per_k_chars": 0.0},
    "OpenAI TTS": {"provider": "openai", "base_url": "https://api.openai.com/v1",
                   "default_model": "gpt-4o-mini-tts", "price_per_k_chars": 0.015},
    "ElevenLabs": {"provider": "elevenlabs", "base_url": "https://api.elevenlabs.io/v1",
                   "default_model": "eleven_multilingual_v2", "price_per_k_chars": 0.30},
}
