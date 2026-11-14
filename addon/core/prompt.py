"""Monta o prompt: os campos do usuário (system) + o bloco fixo do add-on (user), em inglês."""
from __future__ import annotations

import json

from .model import Generator


def response_schema(card_format: str, context_field: bool) -> dict:
    if card_format == "cloze":
        props = {
            "text": {"type": "string", "description": "Sentence with {{c1::...}} cloze deletions"},
            "back_extra": {"type": "string"},
        }
    else:
        props = {"front": {"type": "string"}, "back": {"type": "string"}}
    if context_field:
        props["context"] = {"type": "string", "description": "One short sentence on when this is used"}
    item = {
        "type": "object",
        "properties": props,
        "required": list(props),
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"cards": {"type": "array", "items": item}},
        "required": ["cards"],
        "additionalProperties": False,
    }


def render_field(gen: Generator, text: str) -> str:
    """Troca só os marcadores conhecidos; chaves soltas no texto do usuário ficam intactas."""
    values = {"topic": gen.topic, "level": gen.level,
              "target_lang": gen.target_lang, "native_lang": gen.native_lang}
    for k, v in values.items():
        text = text.replace("{" + k + "}", v or "")
    return text


def user_part(gen: Generator) -> str:
    parts = [f"## {f.title}\n{render_field(gen, f.text.strip())}"
             for f in gen.prompt_fields if f.enabled and f.text.strip()]
    return "\n\n".join(parts)


def fixed_block(gen: Generator, count: int, existing: list[str], extras: list[str]) -> str:
    lines = [f"Generate exactly {count} cards."]
    if gen.target_lang:
        lines.append(
            f"The learner studies {gen.target_lang}"
            + (f" and speaks {gen.native_lang}." if gen.native_lang else ".")
        )
    if existing:
        lines.append("Do not repeat these:")
        lines.extend(f"- {e}" for e in existing)
    for extra in extras:
        lines.append(extra)
    lines.append(
        "Reply with JSON only, no markdown, matching this JSON Schema:\n"
        + json.dumps(response_schema(gen.card_format, gen.context_field))
    )
    return "\n".join(lines)


def build_messages(gen: Generator, count: int, existing: list[str], extras: list[str]) -> list[dict]:
    return [
        {"role": "system", "content": user_part(gen)},
        {"role": "user", "content": fixed_block(gen, count, existing, extras)},
    ]
