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
        cap = info["spend_cap_usd"]
        form.addRow(QLabel(tr("import.summary", name=info["name"], fields=info["fields"],
                              format=info["format"], audio=tr("common.yes") if info["audio"] else tr("common.no"),
                              rules=", ".join(info["rules"]) or "—", per_day=info["cards_per_day"],
                              cap=f"US$ {cap:.2f}" if cap is not None else tr("import.no_cap"))))
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
        from .generator_dialog import default_voice, voices_for
        g = exchange.import_generator(self.data, self.deck.currentText().strip() or "AutoCards",
                                      self.text_service.currentData() or "",
                                      self.audio_service.currentData() or "", date.today())
        svc = self.cfg.service(g.audio_service_id)
        options = voices_for(svc.provider) if svc else []
        if svc and ((options and g.voice not in options) or (not options and svc.provider != "elevenlabs")):
            g.voice = default_voice(svc.provider)  # voz do arquivo é de outro serviço
        elif svc and svc.provider == "elevenlabs" and g.voice in voices_for("edge") + voices_for("openai"):
            g.voice = ""
        return g
