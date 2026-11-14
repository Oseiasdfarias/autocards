import unittest
from datetime import date

from addon.core import templates
from addon.core.model import Generator

TODAY = date(2026, 11, 13)


class TemplatesTest(unittest.TestCase):
    def test_all_templates_build(self):
        for key in ("language", "interview", "concepts", "blank"):
            g = templates.new_generator(key, "N", "Deck", "svc", TODAY)
            self.assertIsInstance(g, Generator)
            self.assertEqual((g.template, g.deck, g.text_service_id, g.created), (key, "Deck", "svc", "2026-11-13"))
            self.assertTrue(g.id)
            self.assertEqual([f.key for f in g.prompt_fields],
                             ["role", "topic", "level", "front", "back", "avoid", "examples"])

    def test_language_has_audio_and_context(self):
        g = templates.new_generator("language", "N", "D", "s", TODAY)
        self.assertTrue(g.audio_enabled)
        self.assertTrue(g.context_field)
        self.assertEqual(g.audio_side, "front")
        self.assertIn("native speaker", g.prompt_fields[0].text)

    def test_interview_no_audio(self):
        g = templates.new_generator("interview", "N", "D", "s", TODAY)
        self.assertFalse(g.audio_enabled)

    def test_blank_has_empty_enabled_fields(self):
        g = templates.new_generator("blank", "N", "D", "s", TODAY)
        self.assertEqual(len(g.prompt_fields), 7)
        self.assertTrue(all(f.text == "" and f.enabled for f in g.prompt_fields))

    def test_ids_unique(self):
        a = templates.new_generator("blank", "A", "D", "s", TODAY)
        b = templates.new_generator("blank", "B", "D", "s", TODAY)
        self.assertNotEqual(a.id, b.id)

    def test_topic_field_follows_generator_topic_placeholder(self):
        g = templates.new_generator("concepts", "N", "D", "s", TODAY)
        self.assertIn("{topic}", g.prompt_fields[1].text)


if __name__ == "__main__":
    unittest.main()
