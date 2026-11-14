"""Cliente de chat no formato OpenAI, só com `requests` (que vem no Anki)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

import jsonschema
import requests


class LLMError(Exception):
    pass


@dataclass
class ChatResult:
    cards: list[dict]
    tokens_in: int
    tokens_out: int
    raw: str
    dropped_invalid: int


_FENCE = re.compile(r"^\s*```[a-zA-Z]*\s*\n?(.*?)\n?\s*```\s*$", re.S)


def _parse(content: str) -> list | None:
    m = _FENCE.match(content or "")
    text = m.group(1) if m else (content or "")
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        return None
    return data["cards"]


def _post(url: str, headers: dict, body: dict, timeout: float, http) -> "requests.Response":
    try:
        return http.post(url, headers=headers, json=body, timeout=timeout)
    except requests.RequestException as e:
        raise LLMError(f"network error: {e}") from e


def chat_cards(base_url: str, api_key: str, model: str, messages: list[dict], schema: dict,
               timeout: float = 60, http=requests) -> ChatResult:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    use_format = True
    item_schema = schema["properties"]["cards"]["items"]
    tokens_in = tokens_out = 0
    last_raw = ""
    json_attempts = 0
    while json_attempts < 2:
        body = {"model": model, "messages": messages}
        if use_format:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "cards", "schema": schema},
            }
        resp = _post(url, headers, body, timeout, http)
        if resp.status_code == 400 and use_format:
            use_format = False  # serviço sem saída estruturada: pede JSON só pelo prompt
            continue
        if resp.status_code >= 400:
            raise LLMError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise LLMError(f"unexpected response: {resp.text[:300]}") from e
        usage = data.get("usage") or {}
        tokens_in += int(usage.get("prompt_tokens") or 0)
        tokens_out += int(usage.get("completion_tokens") or 0)
        last_raw = content or ""
        items = _parse(last_raw)
        json_attempts += 1
        if items is None:
            continue
        valid = []
        for it in items:
            try:
                jsonschema.validate(it, item_schema)
                valid.append(it)
            except jsonschema.ValidationError:
                pass
        return ChatResult(valid, tokens_in, tokens_out, last_raw, len(items) - len(valid))
    raise LLMError(f"invalid JSON from model after 2 attempts: {last_raw[:300]}")
