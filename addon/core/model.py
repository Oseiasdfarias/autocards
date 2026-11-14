"""Modelo de dados do AutoCards: geradores, serviços e config, com (de)serialização tolerante.

Campos desconhecidos (de versões futuras, como as regras da 1.1) vão para `extra` e voltam
intactos ao salvar; campos ausentes recebem o valor padrão.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = 1


@dataclass
class PromptField:
    key: str
    title: str
    text: str = ""
    enabled: bool = True


@dataclass
class Rules:
    ramp_enabled: bool = True
    ramp_start: int = 2
    ramp_end: int = 10
    ramp_weeks: int = 4
    weekdays_enabled: bool = False
    weekdays: list[int] = field(default_factory=lambda: list(range(7)))
    brake_enabled: bool = True
    brake_limit: int = 30
    no_repeat: bool = True
    spend_cap_enabled: bool = True
    spend_cap_usd: float = 2.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Generator:
    id: str
    name: str
    template: str = "blank"
    topic: str = ""
    level: str = "intermediate"
    cards_per_day: int = 5
    deck: str = "AutoCards"
    text_service_id: str = ""
    text_model: str = ""
    prompt_fields: list[PromptField] = field(default_factory=list)
    card_format: str = "basic"  # basic | reversed | cloze
    context_field: bool = False
    audio_enabled: bool = False
    audio_side: str = "front"  # front | back
    audio_service_id: str = ""
    voice: str = ""
    native_lang: str = ""
    target_lang: str = ""
    rules: Rules = field(default_factory=Rules)
    created: str = ""  # ISO date
    last_success: str | None = None
    attempts_today: dict[str, int] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Service:
    id: str
    name: str
    kind: str = "text"  # text | tts
    provider: str = "openai"
    base_url: str = ""
    api_key: str = ""
    default_model: str = ""
    price_in_per_m: float = 0.0
    price_out_per_m: float = 0.0
    price_per_k_chars: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    schema_version: int = SCHEMA_VERSION
    generators: list[Generator] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    post_run_command: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def service(self, service_id: str) -> Service | None:
        return next((s for s in self.services if s.id == service_id), None)


def to_dict(obj: Any) -> Any:
    """Serializa dataclasses em dicts simples; `extra` é achatado no próprio dict."""
    if dataclasses.is_dataclass(obj):
        out: dict[str, Any] = {}
        for f in dataclasses.fields(obj):
            if f.name == "extra":
                continue
            out[f.name] = to_dict(getattr(obj, f.name))
        for k, v in getattr(obj, "extra", {}).items():
            out.setdefault(k, v)
        return out
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def _build(cls: type, data: dict[str, Any], nested: dict[str, Any]) -> Any:
    names = {f.name for f in dataclasses.fields(cls)}
    kwargs: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    for k, v in (data or {}).items():
        if k in nested:
            kwargs[k] = nested[k](v)
        elif k in names and k != "extra":
            kwargs[k] = v
        else:
            extra[k] = v
    if "extra" in names:
        kwargs["extra"] = extra
    return cls(**kwargs)


def generator_from_dict(d: dict[str, Any]) -> Generator:
    return _build(Generator, d, {
        "prompt_fields": lambda v: [_build(PromptField, x, {}) for x in v or []],
        "rules": lambda v: _build(Rules, v, {}),
    })


def service_from_dict(d: dict[str, Any]) -> Service:
    return _build(Service, d, {})


def app_config_from_dict(d: dict[str, Any]) -> AppConfig:
    return _build(AppConfig, d, {
        "generators": lambda v: [generator_from_dict(x) for x in v or []],
        "services": lambda v: [service_from_dict(x) for x in v or []],
    })
