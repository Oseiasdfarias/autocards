"""Roda as três fases (ler → rede → gravar) sem prender a coleção do Anki durante a rede."""
from __future__ import annotations

from datetime import date
from typing import Callable

from aqt import mw
from aqt.operations import QueryOp

from ..ankiops.runner import RunResult, commit_all, fetch_all, prepare_all
from ..core.model import AppConfig
from ..core.store import Store
from .paths import LOG_PATH


def _with_store(fn):
    store = Store(LOG_PATH)
    try:
        return fn(store)
    finally:
        store.close()


def run_phases(parent, cfg: AppConfig, today: date, *, force: bool = False, only: str | None = None,
               is_test: bool = False, should_abort: Callable[[], bool] = lambda: False,
               on_done: Callable[[list[RunResult]], None], on_fail: Callable[[Exception], None]) -> None:
    def read(col):
        return _with_store(lambda s: prepare_all(col, cfg, s, today, force, only, is_test, should_abort))

    def net(_col_unused, items):
        return fetch_all(items, should_abort=should_abort)

    def write(col, items):
        return _with_store(lambda s: commit_all(col, items, s, should_abort))

    def after_read(items):
        QueryOp(parent=parent, op=lambda c: net(c, items), success=after_net) \
            .without_collection().failure(on_fail).run_in_background()

    def after_net(items):
        QueryOp(parent=parent, op=lambda c: write(c, items), success=on_done) \
            .failure(on_fail).run_in_background()

    QueryOp(parent=parent, op=read, success=after_read).failure(on_fail).run_in_background()
