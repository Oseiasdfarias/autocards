"""Importar gerador (spec §9): mostra o resumo e pede baralho e serviços."""
from __future__ import annotations

from datetime import date

from aqt import mw
from aqt.qt import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel

from ..core import exchange
from ..core.i18n import tr
from ..core.model import AppConfig, Generator


class ImportDialog(QDialog):
    def __init__(self, parent, cfg: AppConfig, data: dict):
        super().__init__(parent)
        self.cfg, self.data = cfg, data
        info = exchange.summary(data)  # levanta ExchangeError se o arquivo não serve
        self.setWindowTitle(tr("import.title"))
        form = QFormLayout(self)
        form.addRow(QLabel(tr("import.summary", name=info["name"], fields=info["fields"],
                              format=info["format"], audio=tr("common.yes") if info["audio"] else tr("common.no"),
                              rules=", ".join(info["rules"]) or "—")))
        self.deck = QComboBox()
        self.deck.setEditable(True)
        if mw is not None and mw.col is not None:
            self.deck.addItems(sorted(d.name for d in mw.col.decks.all_names_and_ids()))
        self.deck.setEditText(f"AutoCards::{info['name']}")
        self.text_service = QComboBox()
        for s in cfg.services:
            if s.kind == "text":
                self.text_service.addItem(s.name, s.id)
        self.audio_service = QComboBox()
        self.audio_service.addItem("—", "")
        for s in cfg.services:
            if s.kind == "tts":
                self.audio_service.addItem(s.name, s.id)
        if info["audio"] and self.audio_service.count() > 1:
            self.audio_service.setCurrentIndex(1)
        form.addRow(tr("gen.deck"), self.deck)
        form.addRow(tr("gen.text_service"), self.text_service)
        form.addRow(tr("gen.audio_service"), self.audio_service)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def build(self) -> Generator:
        return exchange.import_generator(self.data, self.deck.currentText().strip() or "AutoCards",
                                         self.text_service.currentData() or "",
                                         self.audio_service.currentData() or "", date.today())
