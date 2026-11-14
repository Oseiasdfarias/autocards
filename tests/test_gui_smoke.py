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
        from addon.gui import paths, services_dialog
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "autocards.json")
        config_store.save(self.path, AppConfig(services=[
            Service(id="t", name="OpenAI", kind="text", base_url="https://api.openai.com/v1")]))
        self.mods = [paths, services_dialog]
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


if __name__ == "__main__":
    unittest.main()
