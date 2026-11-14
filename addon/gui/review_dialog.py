"""Tela "Revisar cards gerados" (spec §7.5): aceitar (com ou sem edição) ou descartar cada card da fila."""
from __future__ import annotations

import json
import os

from aqt import mw
from aqt.qt import (QDialog, QFormLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout,
                    QWidget)
from aqt.utils import tooltip

from ..ankiops.collection import accept_note, discard_note, pending_notes
from ..core.i18n import tr
from ..core.store import Store
from . import paths

AUDIO_FIELDS = ("FrontAudio", "BackAudio")


class ReviewDialog(QDialog):
    def __init__(self, parent=None, col=None):
        super().__init__(parent or mw)
        self.col = col or mw.col
        self.setWindowTitle(tr("review.title"))
        self.resize(640, 520)
        self.queue = pending_notes(self.col)
        self.nid: int | None = None
        self.editors: dict[str, QPlainTextEdit] = {}
        self.header = QLabel()
        self.form_host = QWidget()
        self.form = QFormLayout(self.form_host)
        self.play_btn = QPushButton(tr("review.play"))
        self.play_btn.clicked.connect(self._play)
        self.accept_btn = QPushButton(tr("review.accept"))
        self.accept_btn.clicked.connect(self.accept_current)
        self.discard_btn = QPushButton(tr("review.discard"))
        self.discard_btn.clicked.connect(self.discard_current)
        skip = QPushButton(tr("review.skip"))
        skip.clicked.connect(self._next)
        row = QHBoxLayout()
        row.addWidget(self.play_btn)
        row.addStretch(1)
        for b in (skip, self.discard_btn, self.accept_btn):
            row.addWidget(b)
        root = QVBoxLayout(self)
        root.addWidget(self.header)
        root.addWidget(self.form_host, 1)
        root.addLayout(row)
        self._show_next()

    def _show_next(self) -> None:
        while self.form.rowCount():
            self.form.removeRow(0)
        self.editors = {}
        self.queue = [n for n in self.queue if self.col.find_notes(f"nid:{n}")]  # apagadas por fora saem
        if not self.queue:
            self.nid = None
            self.header.setText(tr("review.empty"))
            for b in (self.accept_btn, self.discard_btn, self.play_btn):
                b.setEnabled(False)
            return
        self.nid = self.queue[0]
        note = self.col.get_note(self.nid)
        deck = self.col.decks.name(note.cards()[0].did)
        self.header.setText(tr("review.header", n=len(self.queue), deck=deck))
        for name, value in note.items():
            if name in AUDIO_FIELDS:
                continue
            ed = QPlainTextEdit(value)
            ed.setMaximumHeight(90)
            self.editors[name] = ed
            self.form.addRow(name, ed)
        self.audio = next((v for k, v in note.items() if k in AUDIO_FIELDS and v), "")
        self.play_btn.setEnabled(bool(self.audio))

    def _next(self) -> None:
        if self.queue:
            self.queue.append(self.queue.pop(0))
        self._show_next()

    def _log(self, outcome: str, original=None, final=None) -> None:
        store = Store(paths.LOG_PATH)
        try:
            store.set_outcome(self.nid, outcome,
                              json.dumps(original, ensure_ascii=False) if original else None,
                              json.dumps(final, ensure_ascii=False) if final else None)
        finally:
            store.close()

    def accept_current(self) -> None:
        if self.nid is None:
            return
        note = self.col.get_note(self.nid)
        changed = {k: ed.toPlainText() for k, ed in self.editors.items() if ed.toPlainText() != note[k]}
        original, final = accept_note(self.col, self.nid, changed or None)
        if changed:
            self._log("edited", original, final)
        else:
            self._log("accepted")
        self.queue.pop(0)
        self._show_next()

    def discard_current(self) -> None:
        if self.nid is None:
            return
        self._log("discarded")
        discard_note(self.col, self.nid)
        self.queue.pop(0)
        self._show_next()

    def _play(self) -> None:
        name = self.audio.removeprefix("[sound:").removesuffix("]")
        from aqt.sound import av_player
        av_player.play_file(os.path.join(self.col.media.dir(), name))

    def done(self, r: int) -> None:
        if mw is not None and mw.col is not None:
            mw.reset()
        super().done(r)
