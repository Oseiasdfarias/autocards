"""Uma execução de gerador (spec §6.3), em três fases para não prender a coleção do Anki:

1. `prepare` (com a coleção, rápida): regras, cota, frentes existentes, prompt.
2. `fetch` (SEM a coleção): IA, filtro, áudio. Pode demorar; roda fora da thread da coleção.
3. `commit` (com a coleção, rápida): grava mídia e notas, registra, marca o dia.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import date

from ..core import costs, dedupe, prompt, rules
from ..core.llm import chat_cards
from ..core.model import AppConfig, Generator, Service
from ..core.store import Store
from ..core.tts import make_tts
from .collection import add_card, existing_fronts, overdue_count, write_audio

_CLOZE = re.compile(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}")


@dataclass
class RunResult:
    generator_name: str
    status: str  # ok | blocked | error | skipped | aborted
    inserted: int
    message: str


@dataclass
class Prepared:
    cfg: AppConfig
    gen: Generator
    svc: Service
    run_id: int
    today: date
    is_test: bool
    count: int
    existing_all: list[str]
    messages: list[dict]
    schema: dict
    model: str
    started: float
    # preenchidos por fetch
    cards: list[dict] = field(default_factory=list)
    audio: list[tuple[bytes | None, str | None]] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    received: int = 0
    dropped_invalid: int = 0
    dropped_dupe: int = 0
    cost: float = 0.0
    error: str | None = None
    aborted: bool = False


def _audio_text(gen: Generator, card: dict) -> str:
    if gen.card_format == "cloze":
        repl = r"\1" if gen.audio_side == "back" else "..."
        return _CLOZE.sub(repl, card.get("text", ""))
    return card.get("back" if gen.audio_side == "back" else "front", "")


def _fail(gen: Generator, today: date, store: Store, run_id: int | None, msg: str, **fields) -> RunResult:
    key = today.isoformat()
    gen.attempts_today = {key: gen.attempts_today.get(key, 0) + 1}
    if run_id is not None:
        store.finish_run(run_id, error=msg[:2000], status="error", **fields)
    return RunResult(gen.name, "error", 0, msg)


def _aborted(gen: Generator, store: Store, run_id: int | None) -> RunResult:
    if run_id is not None:
        store.finish_run(run_id, status="aborted")
    return RunResult(gen.name, "aborted", 0, "aborted (profile closed)")


def prepare(col, cfg: AppConfig, gen: Generator, store: Store, today: date, force: bool = False,
            is_test: bool = False, should_abort=lambda: False) -> Prepared | RunResult:
    if should_abort():
        return _aborted(gen, store, None)
    if not rules.should_run(gen, today, force or is_test):
        return RunResult(gen.name, "skipped", 0, "already done today or too many attempts")
    svc = cfg.service(gen.text_service_id)
    if svc is None:
        return _fail(gen, today, store, None, "text service not configured")
    started = time.time()
    run_id = store.start_run(gen.id, cfg.schema_version, is_test)
    if not is_test:
        block = rules.check_blocks(gen, today, overdue_count(col, gen.deck),
                                   store.month_cost(today.year, today.month))
        if block:
            store.finish_run(run_id, blocked_reason=f"{block.reason}: {block.detail}", status="blocked")
            gen.last_success = today.isoformat()  # o dia foi tratado; não repete a cada hora
            return RunResult(gen.name, "blocked", 0, block.detail)
    count = 1 if is_test else rules.daily_quota(gen.rules, gen.cards_per_day,
                                                date.fromisoformat(gen.created or today.isoformat()), today)
    existing_all = existing_fronts(col, gen.deck) if gen.rules.no_repeat else []
    sample = [dedupe.normalize(x) for x in dedupe.sample_existing(existing_all)]
    messages = prompt.build_messages(gen, count, [x for x in sample if x], [])
    return Prepared(cfg=cfg, gen=gen, svc=svc, run_id=run_id, today=today, is_test=is_test, count=count,
                    existing_all=existing_all, messages=messages,
                    schema=prompt.response_schema(gen.card_format, gen.context_field),
                    model=gen.text_model or svc.default_model, started=started)


def fetch(prep: Prepared, chat=chat_cards, tts_factory=make_tts, should_abort=lambda: False) -> Prepared:
    """Fase de rede. Não recebe a coleção de propósito."""
    gen = prep.gen
    if should_abort():
        prep.aborted = True
        return prep
    try:
        result = chat(prep.svc.base_url, prep.svc.api_key, prep.model, prep.messages, prep.schema)
    except Exception as e:  # rede, HTTP, JSON: falha só este gerador
        prep.error = f"{type(e).__name__}: {e}"
        return prep
    prep.tokens_in, prep.tokens_out = result.tokens_in, result.tokens_out
    prep.received = len(result.cards) + result.dropped_invalid
    prep.dropped_invalid = result.dropped_invalid
    prep.cost = costs.text_cost(prep.svc, result.tokens_in, result.tokens_out)
    if not result.cards:
        prep.error = f"no valid cards in the AI reply ({result.dropped_invalid} invalid)"
        return prep
    key = "text" if gen.card_format == "cloze" else "front"
    cards, prep.dropped_dupe = dedupe.filter_cards(result.cards, key, prep.existing_all)
    prep.cards = cards[:prep.count]

    tts_svc = prep.cfg.service(gen.audio_service_id) if gen.audio_enabled else None
    tts = None
    if tts_svc is not None:
        try:
            tts = tts_factory(tts_svc)
        except Exception:
            tts = None
    for card in prep.cards:
        if should_abort():
            prep.aborted = True
            return prep
        if not gen.audio_enabled:
            prep.audio.append((None, None))
            continue
        if tts is None:
            prep.audio.append((None, "audio service not configured"))
            continue
        text = _audio_text(gen, card)
        try:
            prep.audio.append((tts.synthesize(text, gen.voice), None))
            prep.cost += costs.tts_cost(tts_svc, len(text))
        except Exception as e:
            prep.audio.append((None, f"audio: {e}"))
    return prep


def _finish_fields(prep: Prepared, inserted: int) -> dict:
    return dict(prompt=json.dumps(prep.messages, ensure_ascii=False), service=prep.svc.name, model=prep.model,
                tokens_in=prep.tokens_in, tokens_out=prep.tokens_out, cost=prep.cost,
                duration_s=round(time.time() - prep.started, 2), requested=prep.count, received=prep.received,
                dropped_invalid=prep.dropped_invalid, dropped_dupe=prep.dropped_dupe, inserted=inserted)


def commit(col, prep: Prepared, store: Store, should_abort=lambda: False) -> RunResult:
    gen = prep.gen
    if prep.error:
        return _fail(gen, prep.today, store, prep.run_id, prep.error, **_finish_fields(prep, 0))
    if prep.aborted or should_abort():
        return _aborted(gen, store, prep.run_id)
    if prep.is_test:
        card = prep.cards[0] if prep.cards else None
        data, err = prep.audio[0] if prep.audio else (None, None)
        payload = {"card": card, "audio_path": None, "audio_error": err}
        if data:
            fd, path = tempfile.mkstemp(prefix="autocards_test_", suffix=".mp3")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            payload["audio_path"] = path
        if card:
            store.add_card(prep.run_id, json.dumps(card, ensure_ascii=False), None, bool(data), "test", err)
        store.finish_run(prep.run_id, status="ok", **_finish_fields(prep, 0))
        return RunResult(gen.name, "ok", 0, json.dumps(payload, ensure_ascii=False))
    inserted = 0
    for card, (data, err) in zip(prep.cards, prep.audio):
        if should_abort():
            store.finish_run(prep.run_id, status="aborted", **_finish_fields(prep, inserted))
            return RunResult(gen.name, "aborted", inserted, "aborted (profile closed)")
        audio_file = write_audio(col, data, uuid.uuid4().hex[:16]) if data else None
        nid = add_card(col, gen.deck, gen.card_format, card, audio_file, gen.audio_side, ["autocards"])
        store.add_card(prep.run_id, json.dumps(card, ensure_ascii=False), nid, bool(audio_file), "inserted", err)
        inserted += 1
    store.finish_run(prep.run_id, status="ok", **_finish_fields(prep, inserted))
    gen.last_success = prep.today.isoformat()
    return RunResult(gen.name, "ok", inserted, f"{inserted} new")


def run_generator(col, cfg: AppConfig, gen: Generator, store: Store, today: date, force: bool = False,
                  is_test: bool = False, chat=chat_cards, tts_factory=make_tts,
                  should_abort=lambda: False) -> RunResult:
    """As três fases em sequência (testes e uso síncrono)."""
    prep = prepare(col, cfg, gen, store, today, force, is_test, should_abort)
    if isinstance(prep, RunResult):
        return prep
    fetch(prep, chat, tts_factory, should_abort)
    return commit(col, prep, store, should_abort)


def _guard(gen: Generator, today: date, store: Store, fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as e:  # nunca deixa um gerador derrubar os outros
        return _fail(gen, today, store, None, f"{type(e).__name__}: {e}")


def prepare_all(col, cfg: AppConfig, store: Store, today: date, force: bool = False, only: str | None = None,
                is_test: bool = False, should_abort=lambda: False) -> list[Prepared | RunResult]:
    gens = [g for g in cfg.generators if not only or g.id == only]
    return [_guard(g, today, store, prepare, col, cfg, g, store, today, force, is_test, should_abort)
            for g in gens]


def fetch_all(items: list[Prepared | RunResult], chat=chat_cards, tts_factory=make_tts,
              should_abort=lambda: False) -> list[Prepared | RunResult]:
    out = []
    for it in items:
        if isinstance(it, Prepared):
            try:
                fetch(it, chat, tts_factory, should_abort)
            except Exception as e:
                it.error = f"{type(e).__name__}: {e}"
        out.append(it)
    return out


def commit_all(col, items: list[Prepared | RunResult], store: Store,
               should_abort=lambda: False) -> list[RunResult]:
    return [_guard(it.gen, it.today, store, commit, col, it, store, should_abort)
            if isinstance(it, Prepared) else it for it in items]


def run_all(col, cfg: AppConfig, store: Store, today: date, force: bool = False, only: str | None = None,
            chat=chat_cards, tts_factory=make_tts, should_abort=lambda: False) -> list[RunResult]:
    items = prepare_all(col, cfg, store, today, force, only, should_abort=should_abort)
    fetch_all(items, chat, tts_factory, should_abort)
    return commit_all(col, items, store, should_abort)
