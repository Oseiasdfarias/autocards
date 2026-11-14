"""Tela Serviços (spec §7.6): conexões de texto e áudio, guardadas uma vez só."""
from __future__ import annotations

import uuid

import requests
from aqt import mw
from aqt.qt import (QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QHBoxLayout,
                    QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget)
from aqt.utils import showInfo, showWarning

from ..core import config_store
from ..core.i18n import tr
from ..core.model import Service
from ..core.presets import TEXT_PRESETS, TTS_PRESETS
from ..core.tts import EDGE_VOICES, make_tts
from .paths import CONFIG_PATH


def test_service(svc: Service) -> None:
    """Levanta exceção se o serviço não responde. Roda em segundo plano."""
    if svc.kind == "text":
        headers = {"Authorization": f"Bearer {svc.api_key}"} if svc.api_key else {}
        r = requests.get(svc.base_url.rstrip("/") + "/models", headers=headers, timeout=20)
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    else:
        voice = EDGE_VOICES["en-US"][0] if svc.provider == "edge" else "alloy"
        make_tts(svc).synthesize("Hello", voice)


class ServicesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle(tr("svc.title"))
        self.resize(760, 440)
        self.cfg = config_store.load(CONFIG_PATH)
        self.current: Service | None = None

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._select)
        new_text = QPushButton(tr("svc.new_text"))
        new_text.clicked.connect(lambda: self._new("text"))
        new_tts = QPushButton(tr("svc.new_tts"))
        new_tts.clicked.connect(lambda: self._new("tts"))
        delete = QPushButton(tr("common.delete"))
        delete.clicked.connect(self._delete)
        left = QVBoxLayout()
        left.addWidget(self.list)
        for b in (new_text, new_tts, delete):
            left.addWidget(b)

        self.form_box = QWidget()
        form = QFormLayout(self.form_box)
        self.preset = QComboBox()
        self.preset.activated.connect(self._apply_preset)
        self.name = QLineEdit()
        self.base_url = QLineEdit()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.model = QLineEdit()
        self.price_in = self._price()
        self.price_out = self._price()
        self.price_chars = self._price()
        self.test_btn = QPushButton(tr("svc.test"))
        self.test_btn.clicked.connect(self._test)
        form.addRow(tr("svc.preset"), self.preset)
        form.addRow(tr("common.name"), self.name)
        form.addRow(tr("svc.base_url"), self.base_url)
        form.addRow(tr("svc.api_key"), self.api_key)
        form.addRow(tr("svc.model"), self.model)
        self.row_in = (QLabel(tr("svc.price_in")), self.price_in)
        self.row_out = (QLabel(tr("svc.price_out")), self.price_out)
        self.row_chars = (QLabel(tr("svc.price_chars")), self.price_chars)
        for lbl, w in (self.row_in, self.row_out, self.row_chars):
            form.addRow(lbl, w)
        form.addRow(QLabel(tr("svc.price_note")))
        form.addRow(self.test_btn)

        top = QHBoxLayout()
        top.addLayout(left, 1)
        top.addWidget(self.form_box, 2)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(buttons)
        self._refresh_list()
        self.form_box.setEnabled(bool(self.cfg.services))
        if self.cfg.services:
            self.list.setCurrentRow(0)

    @staticmethod
    def _price() -> QDoubleSpinBox:
        s = QDoubleSpinBox()
        s.setDecimals(4)
        s.setMaximum(1000)
        return s

    def _refresh_list(self) -> None:
        self.list.blockSignals(True)
        self.list.clear()
        for s in self.cfg.services:
            self.list.addItem(f"[{'T' if s.kind == 'text' else '♪'}] {s.name}")
        self.list.blockSignals(False)

    def _store_form(self) -> None:
        s = self.current
        if s is None:
            return
        s.name = self.name.text().strip() or s.name
        s.base_url = self.base_url.text().strip()
        s.api_key = self.api_key.text().strip()
        s.default_model = self.model.text().strip()
        s.price_in_per_m = self.price_in.value()
        s.price_out_per_m = self.price_out.value()
        s.price_per_k_chars = self.price_chars.value()

    def _select(self, row: int) -> None:
        self._store_form()
        if row < 0 or row >= len(self.cfg.services):
            self.current = None
            self.form_box.setEnabled(False)
            return
        self.current = self.cfg.services[row]
        self.form_box.setEnabled(True)
        self._load_form()

    def _load_form(self) -> None:
        s = self.current
        presets = TEXT_PRESETS if s.kind == "text" else TTS_PRESETS
        self.preset.clear()
        self.preset.addItems(["—", *presets])
        self.name.setText(s.name)
        self.base_url.setText(s.base_url)
        self.api_key.setText(s.api_key)
        self.model.setText(s.default_model)
        self.price_in.setValue(s.price_in_per_m)
        self.price_out.setValue(s.price_out_per_m)
        self.price_chars.setValue(s.price_per_k_chars)
        for lbl, w in (self.row_in, self.row_out):
            lbl.setVisible(s.kind == "text")
            w.setVisible(s.kind == "text")
        self.row_chars[0].setVisible(s.kind == "tts")
        self.row_chars[1].setVisible(s.kind == "tts")

    def _apply_preset(self, idx: int) -> None:
        if self.current is None or idx <= 0:
            return
        self._store_form()
        name = self.preset.itemText(idx)
        p = (TEXT_PRESETS if self.current.kind == "text" else TTS_PRESETS)[name]
        for k, v in p.items():
            setattr(self.current, k, v)
        if self.current.name.startswith("New "):
            self.current.name = name
        row = self.cfg.services.index(self.current)
        self._refresh_list()
        self.list.blockSignals(True)
        self.list.setCurrentRow(row)
        self.list.blockSignals(False)
        self._load_form()
        self.preset.setCurrentIndex(idx)

    def _new(self, kind: str) -> None:
        self._store_form()
        s = Service(id=uuid.uuid4().hex[:12], name=f"New {kind} service", kind=kind,
                    provider="openai" if kind == "text" else "edge")
        self.cfg.services.append(s)
        self._refresh_list()
        self.list.setCurrentRow(len(self.cfg.services) - 1)

    def _delete(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        self.current = None
        del self.cfg.services[row]
        self._refresh_list()
        self.list.setCurrentRow(min(row, len(self.cfg.services) - 1))

    def _test(self) -> None:
        self._store_form()
        svc = self.current
        if svc is None:
            return
        self.test_btn.setEnabled(False)

        def done(fut) -> None:
            self.test_btn.setEnabled(True)
            try:
                fut.result()
                showInfo(tr("svc.test_ok"), parent=self)
            except Exception as e:
                showWarning(tr("svc.test_fail", err=str(e)[:300]), parent=self)

        mw.taskman.run_in_background(lambda: test_service(svc), done)

    def _save(self) -> None:
        self._store_form()
        disk = config_store.load(CONFIG_PATH)
        disk.services = self.cfg.services
        config_store.save(CONFIG_PATH, disk)
        self.accept()
