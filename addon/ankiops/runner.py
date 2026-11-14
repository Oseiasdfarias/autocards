"""Uma execução de gerador (spec §6.3): regras → cota → prompt → IA → filtro → áudio → inserir → registrar."""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import date

from ..core import costs, dedupe, prompt, rules
from ..core.llm import chat_cards
from ..core.model import AppConfig, Generator
from ..core.store import Store
from ..core.tts import make_tts
from .collection import add_card, existing_fronts, overdue_count, write_audio

_CLOZE = re.compile(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}")


@dataclass
class RunResult:
    generator_name: str
    status: str  # ok | blocked | error | skipped
    inserted: int
    message: str


def _audio_text(gen: Generator, card: dict) -> str:
    if gen.card_format == "cloze":
        return _CLOZE.sub(r"\1", card.get("text", "")) if gen.audio_side == "back" else \
            _CLOZE.sub("...", card.get("text", ""))
    return card.get("back" if gen.audio_side == "back" else "front", "")


def _fail(gen: Generator, today: date, store: Store, run_id: int | None, msg: str) -> RunResult:
    key = today.isoformat()
    gen.attempts_today = {key: gen.attempts_today.get(key, 0) + 1}
    if run_id is not None:
        store.finish_run(run_id, error=msg[:2000], status="error")
    return RunResult(gen.name, "error", 0, msg)


def run_generator(col, cfg: AppConfig, gen: Generator, store: Store, today: date, force: bool = False,
                  is_test: bool = False, chat=chat_cards, tts_factory=make_tts,
                  should_abort=lambda: False) -> RunResult:
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
    existing = dedupe.sample_existing(existing_fronts(col, gen.deck)) if gen.rules.no_repeat else []
    messages = prompt.build_messages(gen, count, existing, [])
    schema = prompt.response_schema(gen.card_format, gen.context_field)
    model = gen.text_model or svc.default_model
    try:
        result = chat(svc.base_url, svc.api_key, model, messages, schema)
    except Exception as e:  # rede, HTTP, JSON: falha só este gerador
        store.finish_run(run_id, prompt=json.dumps(messages, ensure_ascii=False), service=svc.name, model=model,
                         requested=count)
        return _fail(gen, today, store, run_id, f"{type(e).__name__}: {e}")

    key = "text" if gen.card_format == "cloze" else "front"
    cards, dropped = dedupe.filter_cards(result.cards, key, existing if gen.rules.no_repeat else [])
    cards = cards[:count]
    cost = costs.text_cost(svc, result.tokens_in, result.tokens_out)
    tts_svc = cfg.service(gen.audio_service_id) if gen.audio_enabled else None
    tts = None
    if tts_svc is not None:
        try:
            tts = tts_factory(tts_svc)
        except Exception:
            tts = None

    def synth(card: dict) -> tuple[bytes | None, str | None]:
        if tts is None:
            return None, ("audio service not configured" if gen.audio_enabled else None)
        text = _audio_text(gen, card)
        try:
            data = tts.synthesize(text, gen.voice)
        except Exception as e:
            return None, f"audio: {e}"
        nonlocal cost
        cost += costs.tts_cost(tts_svc, len(text))
        return data, None

    inserted = 0
    message = ""
    if is_test:
        payload = {"card": cards[0] if cards else None, "audio_path": None}
        if cards:
            data, err = synth(cards[0])
            if data:
                fd, path = tempfile.mkstemp(prefix="autocards_test_", suffix=".mp3")
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                payload["audio_path"] = path
            payload["audio_error"] = err
            store.add_card(run_id, json.dumps(cards[0], ensure_ascii=False), None, bool(data), "test", err)
        message = json.dumps(payload, ensure_ascii=False)
    else:
        for card in cards:
            if should_abort():
                break
            data, err = synth(card)
            audio_file = write_audio(col, data, uuid.uuid4().hex[:16]) if data else None
            if should_abort():
                break
            nid = add_card(col, gen.deck, gen.card_format, card, audio_file, gen.audio_side, ["autocards"])
            store.add_card(run_id, json.dumps(card, ensure_ascii=False), nid, bool(audio_file), "inserted", err)
            inserted += 1
        message = f"{inserted} new"

    store.finish_run(run_id, prompt=json.dumps(messages, ensure_ascii=False), service=svc.name, model=model,
                     tokens_in=result.tokens_in, tokens_out=result.tokens_out, cost=cost,
                     duration_s=round(time.time() - started, 2), requested=count,
                     received=len(result.cards) + result.dropped_invalid,
                     dropped_invalid=result.dropped_invalid, dropped_dupe=dropped, inserted=inserted,
                     status="ok")
    if not is_test:
        gen.last_success = today.isoformat()
    return RunResult(gen.name, "ok", inserted, message)


def run_all(col, cfg: AppConfig, store: Store, today: date, force: bool = False, only: str | None = None,
            **kw) -> list[RunResult]:
    results = []
    for gen in cfg.generators:
        if only and gen.id != only:
            continue
        try:
            results.append(run_generator(col, cfg, gen, store, today, force=force, **kw))
        except Exception as e:  # nunca deixa um gerador derrubar os outros
            results.append(_fail(gen, today, store, None, f"{type(e).__name__}: {e}"))
    return results
