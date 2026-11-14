"""Fumaça das telas: monta os diálogos em modo offscreen com uma config temporária."""
import os
import tempfile
import unittest

from aqt.qt import QApplication

from addon.core import config_store
from addon.core.model import AppConfig, Service

_app = QApplication.instance() or QApplication([])


class GuiSmokeBase(unittest.TestCase):
    def setUp(self):
        from addon.gui import generator_dialog, paths, services_dialog
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "autocards.json")
        config_store.save(self.path, AppConfig(services=[
            Service(id="t", name="OpenAI", kind="text", base_url="https://api.openai.com/v1")]))
        self.mods = [paths, services_dialog, generator_dialog]
        self.orig = [m.CONFIG_PATH for m in self.mods]
        for m in self.mods:
            m.CONFIG_PATH = self.path

    def tearDown(self):
        for m, o in zip(self.mods, self.orig):
            m.CONFIG_PATH = o


class ServicesDialogSmoke(GuiSmokeBase):
    def test_new_tts_with_preset_and_save(self):
        from addon.gui.services_dialog import ServicesDialog
        d = ServicesDialog(None)
        d._new("tts")
        d.preset.setCurrentIndex(1)  # Edge (free)
        d._apply_preset(1)
        d.api_key.setText("")
        d._save()
        cfg = config_store.load(self.path)
        self.assertEqual([s.kind for s in cfg.services], ["text", "tts"])
        self.assertEqual(cfg.services[1].provider, "edge")
        self.assertEqual(cfg.services[1].name, "Edge (free)")

    def test_edit_text_service_key(self):
        from addon.gui.services_dialog import ServicesDialog
        d = ServicesDialog(None)
        d.api_key.setText("sk-new")
        d._save()
        self.assertEqual(config_store.load(self.path).services[0].api_key, "sk-new")


class GeneratorsDialogSmoke(GuiSmokeBase):
    def make(self):
        from addon.gui.generator_dialog import GeneratorsDialog
        return GeneratorsDialog(None)

    def test_create_edit_save(self):
        d = self.make()
        d.new_from_template("language")
        d.name.setText("Daily English")
        d.topic.setText("remote work")
        d.native_lang.setText("Portuguese")
        d.target_lang.setText("English")
        d.per_day.setValue(4)
        d.deck.setEditText("English::Daily")
        d.brake_limit.setValue(12)
        d.weekday_boxes[6].setChecked(False)
        d.save()
        g = config_store.load(self.path).generators[0]
        self.assertEqual((g.name, g.topic, g.cards_per_day, g.deck), ("Daily English", "remote work", 4, "English::Daily"))
        self.assertEqual((g.template, g.text_service_id, g.rules.brake_limit), ("language", "t", 12))
        self.assertNotIn(6, g.rules.weekdays)
        self.assertTrue(g.audio_enabled)

    def test_preview_renders_topic_and_fixed_block(self):
        d = self.make()
        d.new_from_template("concepts")
        d.topic.setText("linear algebra")
        d.refresh_preview()
        text = d.preview.toPlainText()
        self.assertIn("linear algebra", text)
        self.assertIn("Generate exactly", text)

    def test_field_toggle_reorder_and_custom(self):
        d = self.make()
        d.new_from_template("blank")
        ed = d.fields_editor
        ed.add_field("My rule", "Always cite a source.")
        ed.set_enabled("avoid", False)
        ed.move("examples", 0)
        d.save()
        fields = config_store.load(self.path).generators[0].prompt_fields
        self.assertEqual(fields[0].key, "examples")
        self.assertEqual(fields[-1].title, "My rule")
        self.assertEqual(fields[-1].text, "Always cite a source.")
        self.assertFalse(next(f for f in fields if f.key == "avoid").enabled)

    def test_save_keeps_run_state_from_disk(self):
        d = self.make()
        d.new_from_template("blank")
        d.save()
        cfg = config_store.load(self.path)
        cfg.generators[0].last_success = "2026-11-13"
        config_store.save(self.path, cfg)
        d2 = self.make()
        d2.topic.setText("x")
        d2.save()
        self.assertEqual(config_store.load(self.path).generators[0].last_success, "2026-11-13")


if __name__ == "__main__":
    unittest.main()
