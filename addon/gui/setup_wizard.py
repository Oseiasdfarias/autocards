"""Configuração guiada do primeiro serviço (spec §7.6, fase 2): escolher, colar a chave, testar."""
from __future__ import annotations

import uuid

from aqt import mw
from aqt.qt import (QButtonGroup, QLabel, QLineEdit, QPushButton, QRadioButton, QVBoxLayout, QWizard,
                    QWizardPage)

from ..core.i18n import tr
from ..core.model import AppConfig, Service
from ..core.presets import TEXT_PRESETS, TTS_PRESETS

WIZARD_PRESETS = ["OpenAI", "OpenRouter", "Groq", "Ollama (local)"]
KEY_LINKS = {
    "OpenAI": "https://platform.openai.com/api-keys",
    "OpenRouter": "https://openrouter.ai/keys",
    "Groq": "https://console.groq.com/keys",
}


def needs_setup(cfg: AppConfig) -> bool:
    return not any(s.kind == "text" for s in cfg.services)


def _service(preset: str, kind: str, key: str = "") -> Service:
    p = (TEXT_PRESETS if kind == "text" else TTS_PRESETS)[preset]
    return Service(id=uuid.uuid4().hex[:12], name=preset, kind=kind, provider=p.get("provider", "openai"),
                   base_url=p["base_url"], api_key=key, default_model=p.get("default_model", ""),
                   price_in_per_m=p.get("price_in_per_m", 0.0), price_out_per_m=p.get("price_out_per_m", 0.0),
                   price_per_k_chars=p.get("price_per_k_chars", 0.0))


def apply_setup(cfg: AppConfig, preset: str, key: str) -> Service:
    svc = _service(preset, "text", key.strip())
    cfg.services.append(svc)
    if not any(s.kind == "tts" for s in cfg.services):
        cfg.services.append(_service("Edge (free)", "tts"))
    return svc


class SetupWizard(QWizard):
    def __init__(self, parent, cfg: AppConfig):
        super().__init__(parent or mw)
        self.cfg = cfg
        self.setWindowTitle(tr("wizard.title"))
        self.preset = WIZARD_PRESETS[0]

        p1 = QWizardPage()
        p1.setTitle(tr("wizard.p1.title"))
        v1 = QVBoxLayout(p1)
        intro = QLabel(tr("wizard.p1.intro"))
        intro.setWordWrap(True)
        v1.addWidget(intro)
        self.group = QButtonGroup(p1)
        for i, name in enumerate(WIZARD_PRESETS):
            rb = QRadioButton(tr(f"wizard.preset.{i}"))
            rb.setChecked(i == 0)
            self.group.addButton(rb, i)
            v1.addWidget(rb)

        p2 = QWizardPage()
        p2.setTitle(tr("wizard.p2.title"))
        v2 = QVBoxLayout(p2)
        self.key_help = QLabel()
        self.key_help.setWordWrap(True)
        self.key_help.setOpenExternalLinks(True)
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.test_btn = QPushButton(tr("svc.test"))
        self.test_btn.clicked.connect(self._test)
        self.test_result = QLabel()
        for w in (self.key_help, self.key, self.test_btn, self.test_result):
            v2.addWidget(w)

        p3 = QWizardPage()
        p3.setTitle(tr("wizard.p3.title"))
        v3 = QVBoxLayout(p3)
        done = QLabel(tr("wizard.p3.text"))
        done.setWordWrap(True)
        v3.addWidget(done)

        for p in (p1, p2, p3):
            self.addPage(p)
        self.currentIdChanged.connect(self._on_page)

    def _on_page(self, _id: int) -> None:
        self.preset = WIZARD_PRESETS[max(0, self.group.checkedId())]
        link = KEY_LINKS.get(self.preset)
        if link:
            self.key_help.setText(tr("wizard.p2.key", name=self.preset, link=link))
            self.key.setEnabled(True)
        else:
            self.key_help.setText(tr("wizard.p2.local"))
            self.key.setEnabled(False)

    def _test(self) -> None:
        from .services_dialog import test_service
        svc = _service(self.preset, "text", self.key.text().strip())
        self.test_btn.setEnabled(False)
        self.test_result.setText("…")

        def done(fut) -> None:
            self.test_btn.setEnabled(True)
            try:
                fut.result()
                self.test_result.setText("✓ " + tr("svc.test_ok"))
            except Exception as e:
                self.test_result.setText("✗ " + tr("svc.test_fail", err=str(e)[:200]))

        mw.taskman.run_in_background(lambda: test_service(svc), done)

    def key_page_ok(self) -> bool:
        return not self.key.isEnabled() or bool(self.key.text().strip())

    def validateCurrentPage(self) -> bool:
        if self.currentId() == 1 and not self.key_page_ok():
            self.test_result.setText("✗ " + tr("wizard.key_required"))
            return False
        return super().validateCurrentPage()

    def accept(self) -> None:
        apply_setup(self.cfg, self.preset, self.key.text() if self.key.isEnabled() else "")
        super().accept()
