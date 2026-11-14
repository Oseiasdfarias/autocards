"""Filtro de repetidos (spec §8): normaliza o texto e compara com difflib."""
from __future__ import annotations

import html
import re
from difflib import SequenceMatcher

THRESHOLD = 0.88
_TAGS = re.compile(r"<[^>]+>")
_CLOZE = re.compile(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}")
_SOUND = re.compile(r"\[sound:[^\]]*\]")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    t = _CLOZE.sub(r"\1", text or "")
    t = _SOUND.sub(" ", t)
    t = _TAGS.sub(" ", t)
    t = html.unescape(t).replace("\xa0", " ")
    t = _PUNCT.sub("", t.lower())
    return _SPACES.sub(" ", t).strip()


def _similar(a: str, b: str, threshold: float) -> bool:
    if a == b:
        return True
    # corte barato antes do SequenceMatcher
    if min(len(a), len(b)) / max(len(a), len(b), 1) < threshold:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def filter_cards(cards: list[dict], key: str, existing: list[str],
                 threshold: float = THRESHOLD) -> tuple[list[dict], int]:
    seen = [n for n in (normalize(e) for e in existing) if n]
    seen_exact = set(seen)
    kept: list[dict] = []
    for card in cards:
        n = normalize(str(card.get(key, "")))
        if not n or n in seen_exact or any(_similar(n, s, threshold) for s in seen):
            continue
        kept.append(card)
        seen.append(n)
        seen_exact.add(n)
    return kept, len(cards) - len(kept)


def sample_existing(fronts_newest_first: list[str], limit: int = 150) -> list[str]:
    return fronts_newest_first[:limit]
