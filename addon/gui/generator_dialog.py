"""Tela de geradores (spec §7): lista à esquerda, 4 abas à direita, Testar/Gerar agora/Cancelar/Salvar."""
from __future__ import annotations

import copy
import json
import os
import tempfile
from datetime import date

from aqt import mw
from aqt.qt import (QApplication, QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout,
                    QInputDialog, QLabel, QLineEdit, QListWidget, QMessageBox, QPlainTextEdit, QPushButton,
                    QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from ..core import config_store, prompt, rules as rules_mod, templates
from ..core.i18n import tr
from ..core.model import Generator, Rules
from ..core.tts import EDGE_VOICES, OPENAI_VOICES, make_tts
from .paths import CONFIG_PATH
from .widgets import PromptFieldsEditor

LEVELS = ["basic", "intermediate", "advanced"]
FORMATS = ["basic", "reversed", "cloze"]
SIDES = ["front", "back"]
TEMPLATE_KEYS = ["language", "interview", "concepts", "blank"]


def _spin(lo: int, hi: int) -> QSpinBox:
    s = QSpinBox()
    s.setRange(lo, hi)
    return s


class GeneratorsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle(tr("gen.title"))
        self.resize(980, 640)
        self.cfg = config_store.load(CONFIG_PATH)
        self.current: Generator | None = None
        self._loading = False

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._select)
        new_btn = QPushButton(tr("gen.new"))
        new_btn.clicked.connect(self._ask_new)
        del_btn = QPushButton(tr("common.delete"))
        del_btn.clicked.connect(self._delete)
        left = QVBoxLayout()
        left.addWidget(self.list)
        left.addWidget(new_btn)
        left.addWidget(del_btn)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._basic_tab(), tr("gen.tab.basic"))
        self.tabs.addTab(self._prompt_tab(), tr("gen.tab.prompt"))
        self.tabs.addTab(self._format_tab(), tr("gen.tab.format"))
        self.tabs.addTab(self._rules_tab(), tr("gen.tab.rules"))

        top = QHBoxLayout()
        top.addLayout(left, 1)
        top.addWidget(self.tabs, 3)
        self.test_btn = QPushButton(tr("gen.test"))
        self.test_btn.clicked.connect(self._test)
        gen_btn = QPushButton(tr("gen.generate_now"))
        gen_btn.clicked.connect(self._generate_now)
        cancel = QPushButton(tr("common.cancel"))
        cancel.clicked.connect(self.reject)
        save = QPushButton(tr("common.save"))
        save.setDefault(True)
        save.clicked.connect(lambda: (self.save(), self.accept()))
        bottom = QHBoxLayout()
        for b in (self.test_btn, gen_btn):
            bottom.addWidget(b)
        bottom.addStretch(1)
        bottom.addWidget(cancel)
        bottom.addWidget(save)
        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addLayout(bottom)

        self._fill_service_combos()
        self._refresh_list()
        self.tabs.setEnabled(bool(self.cfg.generators))
        if self.cfg.generators:
            self.list.setCurrentRow(0)

    # ----- abas -----
    def _basic_tab(self) -> QWidget:
        w = QWidget()
        f = QFormLayout(w)
        self.name = QLineEdit()
        self.topic = QLineEdit()
        self.level = QComboBox()
        self.level.addItems([tr(f"gen.level.{x}") for x in LEVELS])
        self.per_day = _spin(1, 200)
        self.deck = QComboBox()
        self.deck.setEditable(True)
        if mw is not None and mw.col is not None:
            self.deck.addItems(sorted(d.name for d in mw.col.decks.all_names_and_ids()))
        self.text_service = QComboBox()
        self.model = QLineEdit()
        self.native_lang = QLineEdit()
        self.target_lang = QLineEdit()
        self.lang_labels = (QLabel(tr("gen.native_lang")), QLabel(tr("gen.target_lang")))
        f.addRow(tr("common.name"), self.name)
        f.addRow(tr("gen.topic"), self.topic)
        f.addRow(tr("gen.level"), self.level)
        f.addRow(tr("gen.per_day"), self.per_day)
        f.addRow(tr("gen.deck"), self.deck)
        f.addRow(tr("gen.text_service"), self.text_service)
        f.addRow(tr("gen.model"), self.model)
        f.addRow(self.lang_labels[0], self.native_lang)
        f.addRow(self.lang_labels[1], self.target_lang)
        for wid in (self.topic, self.native_lang, self.target_lang):
            wid.textChanged.connect(self._changed)
        self.level.currentIndexChanged.connect(self._changed)
        return w

    def _prompt_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.fields_editor = PromptFieldsEditor()
        self.fields_editor.changed.connect(self._changed)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        copy_btn = QPushButton(tr("gen.copy"))
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.preview.toPlainText()))
        head = QHBoxLayout()
        head.addWidget(QLabel(tr("gen.preview")))
        head.addStretch(1)
        head.addWidget(copy_btn)
        v.addWidget(self.fields_editor, 3)
        v.addLayout(head)
        v.addWidget(self.preview, 2)
        return w

    def _format_tab(self) -> QWidget:
        w = QWidget()
        f = QFormLayout(w)
        self.card_format = QComboBox()
        self.card_format.addItems([tr(f"gen.format.{x}") for x in FORMATS])
        self.card_format.currentIndexChanged.connect(self._changed)
        self.context = QCheckBox(tr("gen.context"))
        self.context.toggled.connect(self._changed)
        self.audio = QCheckBox(tr("gen.audio"))
        self.audio_side = QComboBox()
        self.audio_side.addItems([tr(f"gen.side.{x}") for x in SIDES])
        self.audio_service = QComboBox()
        self.audio_service.currentIndexChanged.connect(self._fill_voices)
        self.voice = QComboBox()
        self.voice.setEditable(True)
        self.listen_btn = QPushButton(tr("gen.listen"))
        self.listen_btn.clicked.connect(self._listen)
        f.addRow(tr("gen.format"), self.card_format)
        f.addRow(self.context)
        f.addRow(self.audio)
        f.addRow(tr("gen.audio_side"), self.audio_side)
        f.addRow(tr("gen.audio_service"), self.audio_service)
        f.addRow(tr("gen.voice"), self.voice)
        f.addRow(self.listen_btn)
        return w

    def _rules_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.ramp = QCheckBox(tr("rule.ramp"))
        self.ramp_start, self.ramp_end, self.ramp_weeks = _spin(1, 200), _spin(1, 200), _spin(1, 52)
        row = QHBoxLayout()
        for lbl, s in ((tr("rule.start"), self.ramp_start), (tr("rule.reach"), self.ramp_end),
                       (tr("rule.weeks"), self.ramp_weeks)):
            row.addWidget(QLabel(lbl))
            row.addWidget(s)
        row.addStretch(1)
        self.weekdays = QCheckBox(tr("rule.weekdays"))
        self.weekday_boxes = [QCheckBox(tr(f"day.{i}")) for i in range(7)]
        days = QHBoxLayout()
        for b in self.weekday_boxes:
            days.addWidget(b)
        days.addStretch(1)
        self.brake = QCheckBox(tr("rule.brake"))
        self.brake_limit = _spin(0, 10000)
        brow = QHBoxLayout()
        brow.addWidget(QLabel(tr("rule.brake_detail")))
        brow.addWidget(self.brake_limit)
        brow.addStretch(1)
        self.no_repeat = QCheckBox(tr("rule.no_repeat"))
        self.spend_cap = QCheckBox(tr("rule.spend_cap"))
        self.spend_cap_usd = QDoubleSpinBox()
        self.spend_cap_usd.setRange(0, 1000)
        self.spend_cap_usd.setDecimals(2)
        srow = QHBoxLayout()
        srow.addWidget(QLabel(tr("rule.spend_cap_detail")))
        srow.addWidget(self.spend_cap_usd)
        srow.addStretch(1)
        self.post_cmd = QLineEdit(self.cfg.post_run_command)
        for item in (self.ramp, row, self.weekdays, days, self.brake, brow, self.no_repeat, self.spend_cap, srow):
            (v.addLayout if isinstance(item, QHBoxLayout) else v.addWidget)(item)
        v.addSpacing(16)
        v.addWidget(QLabel(tr("settings.post_cmd")))
        v.addWidget(self.post_cmd)
        v.addStretch(1)
        for s in (self.ramp_start, self.ramp_end, self.ramp_weeks):
            s.valueChanged.connect(self._changed)
        self.ramp.toggled.connect(self._changed)
        self.per_day.valueChanged.connect(self._changed)
        return w

    # ----- dados -----
    def _services(self, kind: str):
        return [s for s in self.cfg.services if s.kind == kind]

    def _fill_service_combos(self) -> None:
        self.text_service.clear()
        for s in self._services("text"):
            self.text_service.addItem(s.name, s.id)
        self.audio_service.clear()
        self.audio_service.addItem("—", "")
        for s in self._services("tts"):
            self.audio_service.addItem(s.name, s.id)

    def _fill_voices(self) -> None:
        current = self.voice.currentText()
        svc = self.cfg.service(self.audio_service.currentData() or "")
        self.voice.clear()
        if svc is not None and svc.provider == "edge":
            for voices in EDGE_VOICES.values():
                self.voice.addItems(voices)
        elif svc is not None:
            self.voice.addItems(OPENAI_VOICES)
        self.voice.setEditText(current)

    def _refresh_list(self) -> None:
        self.list.blockSignals(True)
        self.list.clear()
        self.list.addItems([g.name for g in self.cfg.generators])
        self.list.blockSignals(False)

    @staticmethod
    def _set_combo_data(combo: QComboBox, value: str) -> None:
        idx = combo.findData(value)
        combo.setCurrentIndex(max(idx, 0))

    def _load_form(self) -> None:
        g = self.current
        self._loading = True
        self.name.setText(g.name)
        self.topic.setText(g.topic)
        self.level.setCurrentIndex(LEVELS.index(g.level) if g.level in LEVELS else 1)
        self.per_day.setValue(g.cards_per_day)
        self.deck.setEditText(g.deck)
        self._set_combo_data(self.text_service, g.text_service_id)
        self.model.setText(g.text_model)
        svc = self.cfg.service(g.text_service_id)
        self.model.setPlaceholderText(svc.default_model if svc else "")
        self.native_lang.setText(g.native_lang)
        self.target_lang.setText(g.target_lang)
        is_lang = g.template == "language"
        for wdg in (self.native_lang, self.target_lang, *self.lang_labels):
            wdg.setVisible(is_lang)
        self.fields_editor.set_fields(g.prompt_fields)
        self.card_format.setCurrentIndex(FORMATS.index(g.card_format) if g.card_format in FORMATS else 0)
        self.context.setChecked(g.context_field)
        self.audio.setChecked(g.audio_enabled)
        self.audio_side.setCurrentIndex(SIDES.index(g.audio_side) if g.audio_side in SIDES else 0)
        self._set_combo_data(self.audio_service, g.audio_service_id)
        self._fill_voices()
        self.voice.setEditText(g.voice)
        r = g.rules
        self.ramp.setChecked(r.ramp_enabled)
        self.ramp_start.setValue(r.ramp_start)
        self.ramp_end.setValue(r.ramp_end)
        self.ramp_weeks.setValue(r.ramp_weeks)
        self.weekdays.setChecked(r.weekdays_enabled)
        for i, b in enumerate(self.weekday_boxes):
            b.setChecked(i in r.weekdays)
        self.brake.setChecked(r.brake_enabled)
        self.brake_limit.setValue(r.brake_limit)
        self.no_repeat.setChecked(r.no_repeat)
        self.spend_cap.setChecked(r.spend_cap_enabled)
        self.spend_cap_usd.setValue(r.spend_cap_usd)
        self._loading = False
        self.refresh_preview()

    def _store_form(self) -> None:
        g = self.current
        if g is None:
            return
        g.name = self.name.text().strip() or g.name
        g.topic = self.topic.text().strip()
        g.level = LEVELS[self.level.currentIndex()]
        g.cards_per_day = self.per_day.value()
        g.deck = self.deck.currentText().strip() or g.deck
        g.text_service_id = self.text_service.currentData() or ""
        g.text_model = self.model.text().strip()
        g.native_lang = self.native_lang.text().strip()
        g.target_lang = self.target_lang.text().strip()
        g.prompt_fields = self.fields_editor.fields()
        g.card_format = FORMATS[self.card_format.currentIndex()]
        g.context_field = self.context.isChecked()
        g.audio_enabled = self.audio.isChecked()
        g.audio_side = SIDES[self.audio_side.currentIndex()]
        g.audio_service_id = self.audio_service.currentData() or ""
        g.voice = self.voice.currentText().strip()
        extra = g.rules.extra
        g.rules = Rules(
            ramp_enabled=self.ramp.isChecked(), ramp_start=self.ramp_start.value(),
            ramp_end=self.ramp_end.value(), ramp_weeks=self.ramp_weeks.value(),
            weekdays_enabled=self.weekdays.isChecked(),
            weekdays=[i for i, b in enumerate(self.weekday_boxes) if b.isChecked()],
            brake_enabled=self.brake.isChecked(), brake_limit=self.brake_limit.value(),
            no_repeat=self.no_repeat.isChecked(), spend_cap_enabled=self.spend_cap.isChecked(),
            spend_cap_usd=self.spend_cap_usd.value(), extra=extra)
        self.cfg.post_run_command = self.post_cmd.text().strip()

    def _changed(self, *_a) -> None:
        if not self._loading:
            self.refresh_preview()

    def refresh_preview(self) -> None:
        if self.current is None or self._loading:
            return
        g = copy.deepcopy(self.current)
        saved, self.current = self.current, g
        self._store_form()
        self.current = saved
        today = date.today()
        count = rules_mod.daily_quota(g.rules, g.cards_per_day, date.fromisoformat(g.created or today.isoformat()),
                                      today)
        msgs = prompt.build_messages(g, count, ["…"] if g.rules.no_repeat else [], [])
        self.preview.setPlainText(msgs[0]["content"] + "\n\n―――――\n\n" + msgs[1]["content"])

    def _select(self, row: int) -> None:
        self._store_form()
        if row < 0 or row >= len(self.cfg.generators):
            self.current = None
            self.tabs.setEnabled(False)
            return
        self.current = self.cfg.generators[row]
        self.tabs.setEnabled(True)
        self._load_form()

    # ----- ações -----
    def new_from_template(self, key: str) -> None:
        self._store_form()
        texts = self._services("text")
        name = tr(f"gen.tpl.{key}")
        g = templates.new_generator(key, name, f"AutoCards::{name}", texts[0].id if texts else "", date.today())
        tts = self._services("tts")
        if g.audio_enabled and tts:
            g.audio_service_id = tts[0].id
            g.voice = EDGE_VOICES["en-US"][0] if tts[0].provider == "edge" else "alloy"
        self.cfg.generators.append(g)
        self._refresh_list()
        self.tabs.setEnabled(True)
        self.list.setCurrentRow(len(self.cfg.generators) - 1)

    def _ask_new(self) -> None:
        if not self._services("text"):
            QMessageBox.information(self, tr("gen.title"), tr("gen.no_services"))
            return
        labels = [tr(f"gen.tpl.{k}") for k in TEMPLATE_KEYS]
        label, ok = QInputDialog.getItem(self, tr("gen.new"), tr("gen.pick_template"), labels, 0, False)
        if ok:
            self.new_from_template(TEMPLATE_KEYS[labels.index(label)])

    def _delete(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        self.current = None
        del self.cfg.generators[row]
        self._refresh_list()
        self.list.setCurrentRow(min(row, len(self.cfg.generators) - 1))

    def save(self) -> None:
        self._store_form()
        disk = config_store.load(CONFIG_PATH)
        state = {g.id: g for g in disk.generators}
        for g in self.cfg.generators:  # estado de execução vem do disco (o agendador pode ter rodado)
            d = state.get(g.id)
            if d is not None:
                g.last_success, g.attempts_today = d.last_success, dict(d.attempts_today)
        disk.generators = self.cfg.generators
        disk.post_run_command = self.cfg.post_run_command
        config_store.save(CONFIG_PATH, disk)

    def _generate_now(self) -> None:
        if self.current is None:
            return
        self.save()
        from .scheduler import run_due
        run_due(force=True, only=self.current.id, quiet_if_nothing=False)

    def _test(self) -> None:
        if self.current is None or mw is None or mw.col is None:
            return
        self._store_form()
        from aqt.operations import QueryOp
        from ..ankiops.runner import run_generator
        from ..core.store import Store
        from .paths import LOG_PATH
        cfg, gen = copy.deepcopy(self.cfg), copy.deepcopy(self.current)
        self.test_btn.setEnabled(False)

        def op(col):
            store = Store(LOG_PATH)
            try:
                return run_generator(col, cfg, gen, store, date.today(), is_test=True)
            finally:
                store.close()

        def done(result) -> None:
            self.test_btn.setEnabled(True)
            if result.status != "ok":
                QMessageBox.warning(self, tr("gen.test"), result.message)
                return
            payload = json.loads(result.message)
            card = payload.get("card") or {}
            text = "\n\n".join(f"{k}: {v}" for k, v in card.items())
            if payload.get("audio_error"):
                text += f"\n\n⚠ {payload['audio_error']}"
            if payload.get("audio_path"):
                from aqt.sound import av_player
                av_player.play_file(payload["audio_path"])
            QMessageBox.information(self, tr("gen.test_result"), text or "—")

        def failed(exc) -> None:
            self.test_btn.setEnabled(True)
            QMessageBox.warning(self, tr("gen.test"), str(exc))

        QueryOp(parent=self, op=op, success=done).failure(failed).run_in_background()

    def _listen(self) -> None:
        self._store_form()
        g = self.current
        svc = self.cfg.service(g.audio_service_id) if g else None
        if svc is None or mw is None:
            return
        voice = g.voice
        sample = {"pt": "Olá! Este é um exemplo de voz.", "es": "¡Hola! Este es un ejemplo de voz."}.get(
            voice[:2].lower(), "Hello! This is a voice sample.")
        self.listen_btn.setEnabled(False)

        def work() -> str:
            data = make_tts(svc).synthesize(sample, voice)
            fd, path = tempfile.mkstemp(prefix="autocards_voice_", suffix=".mp3")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            return path

        def done(fut) -> None:
            self.listen_btn.setEnabled(True)
            try:
                from aqt.sound import av_player
                av_player.play_file(fut.result())
            except Exception as e:
                QMessageBox.warning(self, tr("gen.listen"), str(e)[:300])

        mw.taskman.run_in_background(work, done)
