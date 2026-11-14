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

    def test_v11_rules_saved(self):
        d = self.make()
        d.new_from_template("interview")
        d.approval.setChecked(True)
        d.reinforce.setChecked(True)
        d.reinforce_lapses.setValue(4)
        d.reinforce_per_day.setValue(1)
        d.topics.setChecked(True)
        d.topics_text.setPlainText("RAG\n\n  Fine-tuning  \nEvaluation")
        d.topics_per_day.setValue(2)
        d.save()
        r = config_store.load(self.path).generators[0].rules
        self.assertTrue(r.approval_enabled and r.reinforce_enabled and r.topics_enabled)
        self.assertEqual((r.reinforce_min_lapses, r.reinforce_per_day, r.topics_per_day), (4, 1, 2))
        self.assertEqual(r.topics, ["RAG", "Fine-tuning", "Evaluation"])
        self.assertIn("0", d.topics_status.text())

    def test_switching_audio_service_resets_incompatible_voice(self):
        cfg = config_store.load(self.path)
        cfg.services += [Service(id="oa", name="OA", kind="tts", provider="openai"),
                         Service(id="el", name="EL", kind="tts", provider="elevenlabs")]
        config_store.save(self.path, cfg)
        d = self.make()
        d.new_from_template("language")
        d.audio_service.setCurrentIndex(d.audio_service.findData("oa"))
        self.assertIn(d.voice.currentText(), ["alloy", "ash", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"])
        d.audio_service.setCurrentIndex(d.audio_service.findData("el"))
        self.assertEqual(d.voice.currentText(), "")

    def test_new_language_generator_with_elevenlabs_has_no_openai_voice(self):
        cfg = config_store.load(self.path)
        cfg.services += [Service(id="el", name="EL", kind="tts", provider="elevenlabs")]
        config_store.save(self.path, cfg)
        d = self.make()
        d.new_from_template("language")
        d.save()
        self.assertEqual(config_store.load(self.path).generators[0].voice, "")

    def test_export_then_import(self):
        import json as _json
        from addon.gui.import_dialog import ImportDialog
        d = self.make()
        d.new_from_template("interview")
        d.topic.setText("RAG systems")
        out = os.path.join(self.tmp.name, "gen.autocards.json")
        d.export_current(out)
        with open(out, encoding="utf-8") as f:
            data = _json.load(f)
        self.assertNotIn("text_service_id", data["generator"])
        imp = ImportDialog(d, d.cfg, data)
        imp.deck.setEditText("Imported::Deck")
        d.add_generator(imp.build())
        d.save()
        gens = config_store.load(self.path).generators
        self.assertEqual(len(gens), 2)
        self.assertEqual((gens[1].deck, gens[1].topic, gens[1].text_service_id), ("Imported::Deck", "RAG systems", "t"))
        self.assertNotEqual(gens[0].id, gens[1].id)

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


class ReviewDialogSmoke(unittest.TestCase):
    def test_accept_edit_and_discard(self):
        from anki.collection import Collection
        from addon.ankiops import collection as ops
        from addon.core.store import Store
        from addon.gui import paths
        from addon.gui.review_dialog import ReviewDialog
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        col = Collection(os.path.join(tmp.name, "c.anki2"))
        self.addCleanup(col.close)
        log = os.path.join(tmp.name, "log.sqlite3")
        orig = paths.LOG_PATH
        paths.LOG_PATH = log
        self.addCleanup(setattr, paths, "LOG_PATH", orig)
        store = Store(log)
        run = store.start_run("g", 1, False)
        a = ops.add_card(col, "Q", "basic", {"front": "a", "back": "b"}, None, "front", [], pending=True)
        b = ops.add_card(col, "Q", "basic", {"front": "c", "back": "d"}, None, "front", [], pending=True)
        store.add_card(run, "{}", a, False, "pending")
        store.add_card(run, "{}", b, False, "pending")
        store.close()
        d = ReviewDialog(None, col=col)
        d.editors["Back"].setPlainText("b2")
        d.accept_current()
        d.discard_current()
        self.assertEqual(ops.pending_notes(col), [])
        self.assertEqual(col.get_note(a)["Back"], "b2")
        s2 = Store(log)
        self.addCleanup(s2.close)
        rows = dict(s2._db.execute("select note_id, outcome from cards").fetchall())
        self.assertEqual(rows, {a: "edited", b: "discarded"})
