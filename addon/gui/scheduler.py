"""Geração automática: ao abrir o perfil e a cada hora (spec §6.1), aviso ao terminar (§6.2)."""
from __future__ import annotations

import shlex
import subprocess
from datetime import date

from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.utils import tooltip

from ..ankiops.runner import RunResult, run_all
from ..core import config_store, i18n
from ..core.i18n import tr
from ..core.store import Store
from .paths import CONFIG_PATH, LOG_PATH

HOUR_MS = 3600 * 1000
_state = {"running": False, "abort": False, "timer": None}


def setup() -> None:
    gui_hooks.profile_did_open.append(_on_profile_open)
    gui_hooks.profile_will_close.append(_on_profile_close)


def _on_profile_open() -> None:
    try:
        from anki.lang import current_lang
        i18n.set_lang(current_lang)
    except Exception:
        pass
    _state["abort"] = False
    if _state["timer"] is None:
        _state["timer"] = mw.progress.timer(HOUR_MS, run_due, True, parent=mw)
    run_due()


def _on_profile_close() -> None:
    _state["abort"] = True


def summarize(results: list[RunResult]) -> tuple[str, bool]:
    """Texto do aviso e se houve erro. Geradores pulados (já feitos hoje) não aparecem."""
    parts, had_error = [], False
    for r in results:
        if r.status == "ok":
            parts.append(tr("summary.new", name=r.generator_name, n=r.inserted))
        elif r.status == "blocked":
            parts.append(tr("summary.blocked", name=r.generator_name, reason=r.message))
        elif r.status == "error":
            had_error = True
            parts.append(tr("summary.failed", name=r.generator_name))
    return " · ".join(parts), had_error


def _post_run(cmd: str, ok: bool, msg: str) -> None:
    if not cmd.strip():
        return
    try:
        subprocess.Popen([*shlex.split(cmd), "success" if ok else "error", msg],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:  # comando do usuário nunca derruba o add-on
        print(f"AutoCards: post-run command failed: {e}")


def run_due(force: bool = False, only: str | None = None, quiet_if_nothing: bool = True) -> None:
    if _state["running"] or mw.col is None:
        return
    cfg = config_store.load(CONFIG_PATH)
    if not cfg.generators:
        if not quiet_if_nothing:
            tooltip(tr("summary.nothing"))
        return
    _state["running"] = True
    today = date.today()

    def op(col):
        store = Store(LOG_PATH)
        try:
            return run_all(col, cfg, store, today, force=force, only=only,
                           should_abort=lambda: _state["abort"])
        finally:
            store.close()

    def done(results: list[RunResult]) -> None:
        _state["running"] = False
        config_store.update_run_state(CONFIG_PATH, cfg.generators)
        text, had_error = summarize(results)
        if not text:
            if not quiet_if_nothing:
                tooltip(tr("summary.nothing"))
            return
        tooltip(text, period=10000)
        if any(r.inserted for r in results):
            mw.reset()
        _post_run(cfg.post_run_command, not had_error, text)

    def failed(exc: Exception) -> None:
        _state["running"] = False
        tooltip(f"AutoCards: {exc}", period=10000)
        _post_run(cfg.post_run_command, False, str(exc))

    if not quiet_if_nothing:
        tooltip(tr("summary.running"))
    QueryOp(parent=mw, op=op, success=done).failure(failed).run_in_background()
