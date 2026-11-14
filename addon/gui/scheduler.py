"""Geração automática: ao abrir o perfil e a cada hora (spec §6.1), aviso ao terminar (§6.2)."""
from __future__ import annotations

import shlex
import subprocess
from datetime import date

from aqt import gui_hooks, mw
from aqt.utils import tooltip

from ..ankiops.runner import RunResult
from ..core import config_store, i18n
from ..core.config_store import ConfigError
from ..core.i18n import tr
from .paths import CONFIG_PATH
from .phases import run_phases

HOUR_MS = 3600 * 1000
_state = {"running": False, "abort": False, "timer": None}


def setup() -> None:
    gui_hooks.profile_did_open.append(_on_profile_open)
    gui_hooks.profile_will_close.append(_on_profile_close)


def _on_profile_open() -> None:
    # Nunca deixa exceção sair do hook: o Anki removeria o hook e pularia a sincronização ao abrir.
    try:
        _profile_open()
    except Exception as e:
        print(f"AutoCards: {e!r}")
        tooltip(f"AutoCards: {e}", period=10000)


def _profile_open() -> None:
    try:
        from anki.lang import current_lang
        i18n.set_lang(current_lang)
    except Exception:
        pass
    _state["abort"] = False
    if _state["timer"] is None:
        _state["timer"] = mw.progress.timer(HOUR_MS, _safe_run_due, True, parent=mw)
    run_due()


def _safe_run_due() -> None:
    try:
        run_due()
    except Exception as e:
        print(f"AutoCards: {e!r}")


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
    try:
        cfg = config_store.load(CONFIG_PATH)
    except ConfigError as e:
        tooltip(tr("config.invalid", err=str(e)[:200]), period=10000)
        return
    if not cfg.generators:
        if not quiet_if_nothing:
            tooltip(tr("summary.nothing"))
        return
    _state["running"] = True
    today = date.today()

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
    run_phases(mw, cfg, today, force=force, only=only, should_abort=lambda: _state["abort"],
               on_done=done, on_fail=failed)
