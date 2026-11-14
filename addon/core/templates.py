"""Modelos iniciais de gerador (spec §7.1). `{topic}`, `{level}`, `{target_lang}` e `{native_lang}`
são trocados pelos valores do gerador na hora de montar o prompt (prompt.render_field)."""
from __future__ import annotations

import uuid
from datetime import date

from .model import Generator, PromptField, Rules

FIELD_TITLES = [
    ("role", "AI role"), ("topic", "Topic"), ("level", "Level and audience"),
    ("front", "Card front"), ("back", "Card back"), ("avoid", "What to avoid"),
    ("examples", "Examples of good cards"),
]

_TOPIC = "The cards are about: {topic}"
_LEVEL = "Level: {level}."

TEMPLATES: dict[str, dict] = {
    "language": {
        "texts": {
            "role": ("You are a linguist who teaches {target_lang} to {native_lang} speakers. "
                     "Phrases must sound like something a native speaker would actually say."),
            "topic": _TOPIC,
            "level": (_LEVEL + " basic: common words, present and past, no idioms; intermediate: phrasal "
                      "verbs, conditionals, common idioms; advanced: nuanced register, idiomatic expressions."),
            "front": "A short, natural phrase in {target_lang}, as actually spoken (up to 15 words).",
            "back": ("The translation in natural, colloquial {native_lang}, not literal. "
                     "Example: 'Let me know' -> 'Me avisa'. "
                     "Context (if requested): one sentence in {native_lang} about the situation where the phrase is used."),
            "avoid": "Textbook or overly formal phrasing. Repeating the same sentence structure.",
            "examples": "Front: Can you take a look? / Back: Pode dar uma olhada?",
        },
        "context_field": True, "audio_enabled": True, "audio_side": "front",
    },
    "interview": {
        "texts": {
            "role": "You are a senior engineer preparing a candidate for technical interviews.",
            "topic": _TOPIC,
            "level": _LEVEL,
            "front": "A question an interviewer would actually ask.",
            "back": "A correct, objective answer in up to 4 sentences, with the key term first.",
            "avoid": "Opinion questions, trivia nobody asks, answers longer than 4 sentences.",
            "examples": "Front: What is overfitting? / Back: When a model fits training noise and generalizes poorly...",
        },
    },
    "concepts": {
        "texts": {
            "role": "You are a teacher who writes clear, accurate flashcards.",
            "topic": _TOPIC,
            "level": _LEVEL,
            "front": "The name of one concept, or a short question about it.",
            "back": "A precise definition in 1-2 sentences, plus one concrete example.",
            "avoid": "Vague definitions, several concepts in one card, factual claims you are not sure of.",
            "examples": "",
        },
    },
    "blank": {"texts": {}},
}


def new_generator(template: str, name: str, deck: str, text_service_id: str, today: date) -> Generator:
    t = TEMPLATES[template]
    fields = [PromptField(k, title, t["texts"].get(k, "")) for k, title in FIELD_TITLES]
    return Generator(
        id=uuid.uuid4().hex[:12], name=name, template=template, deck=deck,
        text_service_id=text_service_id, prompt_fields=fields,
        context_field=t.get("context_field", False), audio_enabled=t.get("audio_enabled", False),
        audio_side=t.get("audio_side", "front"), rules=Rules(), created=today.isoformat(),
    )
