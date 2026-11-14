"""Arquivo de gerador para trocar/vender (spec §9): tudo menos chaves, serviços, baralho e estado."""
from __future__ import annotations

import uuid
from datetime import date

from .model import generator_from_dict, to_dict, Generator

FORMAT = "autocards-generator"
FORMAT_VERSION = 1
EXTENSION = ".autocards.json"
_PRIVATE = ("id", "deck", "text_service_id", "audio_service_id", "last_success", "attempts_today", "created")
_RULE_STATE = ("topics_done",)
_RULE_FLAGS = ("ramp_enabled", "weekdays_enabled", "brake_enabled", "no_repeat", "spend_cap_enabled",
               "approval_enabled", "reinforce_enabled", "topics_enabled")


class ExchangeError(Exception):
    pass


def export_generator(gen: Generator) -> dict:
    g = to_dict(gen)
    for k in _PRIVATE:
        g.pop(k, None)
    for k in _RULE_STATE:
        g.get("rules", {}).pop(k, None)
    return {"format": FORMAT, "format_version": FORMAT_VERSION, "generator": g}


def _check(data) -> dict:
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ExchangeError("not an AutoCards generator file")
    version = data.get("format_version")
    if not isinstance(version, int) or version > FORMAT_VERSION:
        raise ExchangeError(f"file format version {version} is newer than this add-on supports")
    g = data.get("generator")
    if not isinstance(g, dict) or not g.get("name"):
        raise ExchangeError("generator data missing")
    return g


def summary(data) -> dict:
    g = _check(data)
    rules = g.get("rules") or {}
    return {
        "name": g.get("name"), "template": g.get("template"), "format": g.get("card_format", "basic"),
        "fields": len(g.get("prompt_fields") or []), "audio": bool(g.get("audio_enabled")),
        "rules": [k.removesuffix("_enabled") for k in _RULE_FLAGS if rules.get(k)],
    }


def import_generator(data, deck: str, text_service_id: str, audio_service_id: str, today: date) -> Generator:
    g = dict(_check(data))
    for k in _PRIVATE:
        g.pop(k, None)
    try:
        gen = generator_from_dict({**g, "id": uuid.uuid4().hex[:12], "deck": deck,
                                   "text_service_id": text_service_id, "audio_service_id": audio_service_id,
                                   "created": today.isoformat()})
    except Exception as e:
        raise ExchangeError(f"invalid generator data: {e}") from e
    gen.rules.topics_done = []
    return gen
