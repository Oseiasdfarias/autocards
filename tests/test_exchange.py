import json
import unittest
from datetime import date

from addon.core import exchange, templates
from addon.core.model import Rules

TODAY = date(2026, 11, 13)


def source():
    g = templates.new_generator("language", "Daily English", "English::Daily", "svc-text", TODAY)
    g.audio_service_id = "svc-tts"
    g.voice = "en-US-AriaNeural"
    g.topic = "remote work"
    g.last_success = "2026-11-12"
    g.attempts_today = {"2026-11-13": 1}
    g.rules = Rules(brake_limit=12, topics_enabled=True, topics=["a", "b"], topics_done=["a"])
    return g


class ExchangeTest(unittest.TestCase):
    def test_export_strips_private_and_state(self):
        data = exchange.export_generator(source())
        self.assertEqual((data["format"], data["format_version"]), ("autocards-generator", 1))
        g = data["generator"]
        for k in ("id", "deck", "text_service_id", "audio_service_id", "last_success", "attempts_today", "created"):
            self.assertNotIn(k, g)
        self.assertNotIn("topics_done", g["rules"])
        self.assertNotIn("svc-text", json.dumps(data))

    def test_roundtrip(self):
        src = source()
        g = exchange.import_generator(exchange.export_generator(src), "Mine", "t2", "a2", TODAY)
        self.assertEqual((g.deck, g.text_service_id, g.audio_service_id, g.created), ("Mine", "t2", "a2", "2026-11-13"))
        self.assertEqual(g.prompt_fields, src.prompt_fields)
        self.assertEqual((g.topic, g.voice, g.card_format, g.rules.brake_limit, g.rules.topics),
                         ("remote work", "en-US-AriaNeural", src.card_format, 12, ["a", "b"]))
        self.assertEqual((g.last_success, g.attempts_today, g.rules.topics_done), (None, {}, []))
        self.assertNotEqual(g.id, src.id)

    def test_newer_version_rejected(self):
        data = exchange.export_generator(source())
        data["format_version"] = 2
        with self.assertRaises(exchange.ExchangeError):
            exchange.import_generator(data, "D", "t", "", TODAY)

    def test_not_a_generator_rejected(self):
        for bad in ({"hello": 1}, [], "x", {"format": "autocards-generator", "format_version": 1}):
            with self.assertRaises(exchange.ExchangeError):
                exchange.import_generator(bad, "D", "t", "", TODAY)

    def test_import_twice_gives_new_ids(self):
        data = exchange.export_generator(source())
        a = exchange.import_generator(data, "D", "t", "", TODAY)
        b = exchange.import_generator(data, "D", "t", "", TODAY)
        self.assertNotEqual(a.id, b.id)

    def test_summary(self):
        s = exchange.summary(exchange.export_generator(source()))
        self.assertEqual(s["name"], "Daily English")
        self.assertTrue(s["audio"])
        self.assertIn("topics", s["rules"])


if __name__ == "__main__":
    unittest.main()
