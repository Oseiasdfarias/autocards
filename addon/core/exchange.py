"""Arquivo de gerador para trocar/vender (spec §9).

Lista fixa de campos permitidos nos dois sentidos: só sai e só entra o que está declarado abaixo.
Nunca saem chaves, serviços, baralho, modelo de IA nem estado de execução; o que entra é checado
por tipo e os números são limitados às faixas da tela.
"""
from __future__ import annotations

import uuid
from datetime import date

from .model import Generator, PromptField, Rules

FORMAT = "autocards-generator"
FORMAT_VERSION = 1
EXTENSION = ".autocards.json"

# campo: (tipo, faixa para números | None)
GEN_FIELDS = {
    "name": (str, None), "template": (str, None), "topic": (str, None), "level": (str, None),
    "cards_per_day": (int, (1, 200)), "card_format": (str, None), "context_field": (bool, None),
    "audio_enabled": (bool, None), "audio_side": (str, None), "voice": (str, None),
    "native_lang": (str, None), "target_lang": (str, None),
}
RULE_FIELDS = {
    "ramp_enabled": (bool, None), "ramp_start": (int, (1, 200)), "ramp_end": (int, (1, 200)),
    "ramp_weeks": (int, (1, 52)), "weekdays_enabled": (bool, None), "weekdays": ("days", None),
    "brake_enabled": (bool, None), "brake_limit": (int, (0, 10000)), "no_repeat": (bool, None),
    "spend_cap_enabled": (bool, None), "spend_cap_usd": (float, (0, 1000)),
    "approval_enabled": (bool, None), "reinforce_enabled": (bool, None),
    "reinforce_min_lapses": (int, (1, 100)), "reinforce_per_day": (int, (1, 50)),
    "topics_enabled": (bool, None), "topics": ("strs", None), "topics_per_day": (int, (1, 50)),
}
FIELD_FIELDS = {"key": (str, None), "title": (str, None), "text": (str, None), "enabled": (bool, None)}
_CHOICES = {"card_format": {"basic", "reversed", "cloze"}, "audio_side": {"front", "back"},
            "level": {"basic", "intermediate", "advanced"}}
_FLAGS = [k for k, (t, _r) in RULE_FIELDS.items() if k.endswith("_enabled")]


class ExchangeError(Exception):
    pass


def _pick(obj, spec: dict) -> dict:
    return {k: getattr(obj, k) for k in spec}


def export_generator(gen: Generator) -> dict:
    g = _pick(gen, GEN_FIELDS)
    g["prompt_fields"] = [_pick(f, FIELD_FIELDS) for f in gen.prompt_fields]
    g["rules"] = _pick(gen.rules, RULE_FIELDS)
    return {"format": FORMAT, "format_version": FORMAT_VERSION, "generator": g}


def _value(name: str, v, kind, rng):
    if kind == "days":
        if not isinstance(v, list) or not all(isinstance(d, int) and not isinstance(d, bool) and 0 <= d <= 6
                                              for d in v):
            raise ExchangeError(f"invalid value for {name}")
        return sorted(set(v))
    if kind == "strs":
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise ExchangeError(f"invalid value for {name}")
        return [x[:500] for x in v[:5000]]
    if kind is bool:
        ok = isinstance(v, bool)
    elif kind is int:
        ok = isinstance(v, int) and not isinstance(v, bool)
    elif kind is float:
        ok = isinstance(v, (int, float)) and not isinstance(v, bool)
    else:
        ok = isinstance(v, str)
    if not ok:
        raise ExchangeError(f"invalid value for {name}")
    if rng is not None:
        v = kind(min(max(v, rng[0]), rng[1]))
    if kind is str:
        v = v[:20000]
        if name in _CHOICES and v not in _CHOICES[name]:
            raise ExchangeError(f"invalid value for {name}")
    return v


def _clean(data: dict, spec: dict, where: str) -> dict:
    if not isinstance(data, dict):
        raise ExchangeError(f"invalid {where}")
    return {k: _value(k, data[k], *spec[k]) for k in spec if k in data}


def _validated(data) -> dict:
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ExchangeError("not an AutoCards generator file")
    version = data.get("format_version")
    if not isinstance(version, int) or isinstance(version, bool) or version > FORMAT_VERSION:
        raise ExchangeError(f"file format version {version} is newer than this add-on supports")
    raw = data.get("generator")
    if not isinstance(raw, dict) or not isinstance(raw.get("name"), str) or not raw["name"].strip():
        raise ExchangeError("generator data missing")
    g = _clean(raw, GEN_FIELDS, "generator")
    fields = raw.get("prompt_fields", [])
    if not isinstance(fields, list):
        raise ExchangeError("invalid prompt_fields")
    g["prompt_fields"] = [_clean(f, FIELD_FIELDS, "prompt field") for f in fields[:100]]
    g["rules"] = _clean(raw.get("rules", {}), RULE_FIELDS, "rules")
    return g


def summary(data) -> dict:
    g = _validated(data)
    r = g["rules"]
    return {
        "name": g["name"], "template": g.get("template", ""), "format": g.get("card_format", "basic"),
        "fields": len(g["prompt_fields"]), "audio": g.get("audio_enabled", False),
        "cards_per_day": g.get("cards_per_day", Generator(id="", name="").cards_per_day),
        "spend_cap_usd": r.get("spend_cap_usd", Rules().spend_cap_usd) if r.get("spend_cap_enabled", True) else None,
        "rules": [k.removesuffix("_enabled") for k in _FLAGS if r.get(k)],
    }


def import_generator(data, deck: str, text_service_id: str, audio_service_id: str, today: date) -> Generator:
    g = _validated(data)
    fields = [PromptField(**{"key": f"field_{i}", "title": "", **f}) for i, f in enumerate(g.pop("prompt_fields"))]
    rules = Rules(**g.pop("rules"))
    return Generator(id=uuid.uuid4().hex[:12], deck=deck, text_service_id=text_service_id,
                     audio_service_id=audio_service_id, created=today.isoformat(), text_model="",
                     prompt_fields=fields, rules=rules, **g)
