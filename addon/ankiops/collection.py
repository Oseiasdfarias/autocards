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


PENDING_TAG = "autocards::pending"
REINFORCED_TAG = "autocards::reinforced"  # nota de origem já usada para reforço
REINFORCEMENT_TAG = "autocards::reinforcement"  # card novo criado como reforço


def struggling_fronts(col, deck: str, min_lapses: int, limit: int) -> list[tuple[int, str]]:
    """Notas do baralho com algum cartão errado `min_lapses`+ vezes, ainda não usadas para reforço."""
    from anki.utils import ids2str
    nids = col.find_notes(_deck_search(col, deck, f"prop:lapses>={int(min_lapses)}", f"-tag:{REINFORCED_TAG}"))
    if not nids or limit <= 0:
        return []
    rows = col.db.all(
        f"select n.id, n.flds, max(c.lapses) as l from notes n join cards c on c.nid = n.id "
        f"where n.id in {ids2str(nids)} group by n.id order by l desc, n.id limit {int(limit)}")
    return [(nid, flds.split("\x1f", 1)[0]) for nid, flds, _l in rows]


def add_card(col, deck: str, card_format: str, card: dict, audio_file: str | None,
             audio_side: str, tags: list[str], pending: bool = False) -> int:
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
    note.tags = list(tags) + ([PENDING_TAG] if pending else [])
    col.add_note(note, col.decks.id(deck))
    if pending:  # fora do estudo até ser aceito (spec §7.5)
        col.sched.suspend_cards(note.card_ids())
    return note.id


def pending_notes(col) -> list[int]:
    return sorted(col.find_notes(f"tag:{PENDING_TAG}"))


def accept_note(col, nid: int, fields: dict | None) -> tuple[dict, dict]:
    note = col.get_note(nid)
    original = dict(note.items())
    for k, v in (fields or {}).items():
        note[k] = v
    note.remove_tag(PENDING_TAG)
    col.update_note(note)
    col.sched.unsuspend_cards(note.card_ids())
    return original, dict(note.items())


def discard_note(col, nid: int) -> None:
    col.remove_notes([nid])
