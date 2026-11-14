---
title: Services and costs
---

# Services and costs

A **service** is a connection you configure once in **Tools › AutoCards › Services…**: name, base URL, API key, default model and price. Each generator points to one text service and, optionally, one audio service.

## Text services

Any service compatible with the **OpenAI chat format** works. Presets fill in the address:

| Preset | Base URL | Default model | Key |
|---|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | yes |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` | yes |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-8b-instant` | yes |
| Ollama (local) | `http://localhost:11434/v1` | `llama3.1` | no |
| LM Studio (local) | `http://localhost:1234/v1` | — | no |

AutoCards asks for structured JSON output. If the service doesn't support it, AutoCards asks for JSON in the prompt instead and validates every card.

## Audio services

| Service | Cost | Notes |
|---|---|---|
| **Edge** | free, no key | Microsoft's read-aloud voices. Unofficial: if Microsoft changes it, an add-on update may be needed. |
| **OpenAI TTS** | paid | Model `gpt-4o-mini-tts`; voices such as `alloy`, `nova`, `shimmer`. |
| **ElevenLabs** | paid | Paste the **voice ID** from your ElevenLabs account in the generator's *Voice* field. |

If the audio of a card fails, the card is still added, without audio, and the error goes to the log.

## Test connection

Every service has a **Test connection** button. Text services are checked by listing models; audio services by speaking "Hello".

## Costs

You pay the services directly, with your own account.

- With `gpt-4o-mini`, **10 cards a day cost a few US cents per month**. Edge audio is free. Local models cost nothing.
- Each service has price fields: per million tokens (input and output) for text, per thousand characters for audio. Presets come with estimates you can edit.
- These prices feed the **Spending cap** rule and the cost column of the log. **They are estimates**: check your provider's real prices.
