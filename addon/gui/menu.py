"""Menu Ferramentas › AutoCards."""
from __future__ import annotations

import os
from datetime import datetime

from aqt import mw
from aqt.qt import QAction, QFileDialog, QMenu
from aqt.utils import tooltip

from ..core.i18n import tr
from ..core.store import Store
from .paths import LOG_PATH


def setup() -> None:
    menu = QMenu(tr("menu.title"), mw)
    mw.form.menuTools.addMenu(menu)

    def add(label: str, fn) -> None:
        act = QAction(label, mw)
        act.triggered.connect(fn)
        menu.addAction(act)

    add(tr("menu.generators"), open_generators)
    add(tr("menu.services"), open_services)
    add(tr("menu.generate_now"), generate_now)
    add(tr("menu.export_log"), export_log)


def open_generators() -> None:
    from .generator_dialog import GeneratorsDialog
    GeneratorsDialog(mw).exec()


def open_services() -> None:
    from .services_dialog import ServicesDialog
    ServicesDialog(mw).exec()


def generate_now() -> None:
    from .scheduler import run_due
    run_due(force=True, quiet_if_nothing=False)


def export_log() -> None:
    default = os.path.join(os.path.expanduser("~"), f"autocards-log-{datetime.now():%Y%m%d}.csv")
    path, _ = QFileDialog.getSaveFileName(mw, tr("menu.export_log"), default, "CSV (*.csv)")
    if not path:
        return
    store = Store(LOG_PATH)
    try:
        store.export_csv(path)
    finally:
        store.close()
    tooltip(tr("log.exported", path=path))
