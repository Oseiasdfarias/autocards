"""Operações na coleção do Anki (sem interface): vencidos, frentes existentes, inserir notas, mídia."""
from __future__ import annotations

import html

from anki.collection import SearchNode

from .notetypes import ensure_notetype


def _deck_search(col, deck: str, *extra: str) -> str:
    base = col.build_search_string(SearchNode(deck=deck))
    return " ".join([base, *extra])


def overdue_count(col, deck: str) -> int:
    return len(col.find_cards(_deck_search(col, deck, "is:due", "is:review")))


def existing_fronts(col, deck: str) -> list[str]:
    """Primeiro campo de todas as notas do baralho (qualquer tipo), mais recentes primeiro."""
    from anki.utils import ids2str
    nids = col.find_notes(_deck_search(col, deck))
    if not nids:
        return []
    rows = col.db.list(f"select flds from notes where id in {ids2str(nids)} order by id desc")
    return [r.split("\x1f", 1)[0] for r in rows]


def to_html(text: str) -> str:
    return html.escape(str(text or ""), quote=False).replace("\r\n", "\n").replace("\n", "<br>")


def write_audio(col, data: bytes, stem: str) -> str:
    return col.media.write_data(f"autocards_{stem}.mp3", data)


def add_card(col, deck: str, card_format: str, card: dict, audio_file: str | None,
             audio_side: str, tags: list[str]) -> int:
    nt = col.models.get(ensure_notetype(col, card_format))
    note = col.new_note(nt)
    if card_format == "cloze":
        note["Text"] = to_html(card.get("text", ""))
        note["Back Extra"] = to_html(card.get("back_extra", ""))
    else:
        note["Front"] = to_html(card.get("front", ""))
        note["Back"] = to_html(card.get("back", ""))
    note["Context"] = to_html(card.get("context", ""))
    if audio_file:
        note["BackAudio" if audio_side == "back" else "FrontAudio"] = f"[sound:{audio_file}]"
    note.tags = list(tags)
    col.add_note(note, col.decks.id(deck))
    return note.id
