"""Tipos de nota próprios do AutoCards, com campos de nome fixo (independe do idioma do Anki)."""
from __future__ import annotations

NAMES = {"basic": "AutoCards Basic", "reversed": "AutoCards Reversed", "cloze": "AutoCards Cloze"}
BASIC_FIELDS = ["Front", "Back", "Context", "FrontAudio", "BackAudio"]
CLOZE_FIELDS = ["Text", "Back Extra", "Context", "FrontAudio", "BackAudio"]

CSS = """.card { font-family: system-ui, sans-serif; font-size: 22px; text-align: center;
  color: black; background-color: white; }
.nightMode .card { color: white; background-color: #222; }
.context { font-size: 16px; opacity: .7; margin-top: 12px; font-style: italic; }
.cloze { font-weight: bold; color: #1565c0; }
.nightMode .cloze { color: #90caf9; }"""

_CONTEXT = "{{#Context}}<div class=context>{{Context}}</div>{{/Context}}"


def _templates(card_format: str) -> list[tuple[str, str, str]]:
    if card_format == "cloze":
        return [("Cloze", "{{cloze:Text}}{{FrontAudio}}",
                 "{{cloze:Text}}<br>{{Back Extra}}" + _CONTEXT + "{{BackAudio}}")]
    card1 = ("Card 1", "{{Front}}{{FrontAudio}}",
             "{{FrontSide}}<hr id=answer>{{Back}}" + _CONTEXT + "{{BackAudio}}")
    if card_format == "reversed":
        card2 = ("Card 2", "{{Back}}{{BackAudio}}",
                 "{{FrontSide}}<hr id=answer>{{Front}}" + _CONTEXT + "{{FrontAudio}}")
        return [card1, card2]
    return [card1]


def ensure_notetype(col, card_format: str) -> int:
    name = NAMES[card_format]
    existing = col.models.by_name(name)
    if existing:
        return existing["id"]
    mm = col.models
    nt = mm.new(name)
    if card_format == "cloze":
        from anki.models import MODEL_CLOZE
        nt["type"] = MODEL_CLOZE
    nt["css"] = CSS
    for fname in CLOZE_FIELDS if card_format == "cloze" else BASIC_FIELDS:
        mm.add_field(nt, mm.new_field(fname))
    for tname, q, a in _templates(card_format):
        t = mm.new_template(tname)
        t["qfmt"], t["afmt"] = q, a
        mm.add_template(nt, t)
    mm.add(nt)
    return col.models.by_name(name)["id"]
