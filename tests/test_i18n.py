import unittest

from addon.core import i18n


class I18nTest(unittest.TestCase):
    def tearDown(self):
        i18n.set_lang("en")

    def test_pt_translation(self):
        i18n.set_lang("pt_BR")
        self.assertEqual(i18n.tr("summary.new", name="X", n=3), "X: 3 novos")

    def test_english_default(self):
        i18n.set_lang("en")
        self.assertEqual(i18n.tr("summary.new", name="X", n=3), "X: 3 new")

    def test_falls_back_to_english(self):
        i18n.set_lang("de")
        self.assertEqual(i18n.tr("summary.new", name="X", n=1), "X: 1 new")

    def test_unknown_key_returns_key(self):
        self.assertEqual(i18n.tr("no.such.key"), "no.such.key")

    def test_all_pt_keys_exist_in_en(self):
        self.assertLessEqual(set(i18n.STRINGS["pt"]), set(i18n.STRINGS["en"]))


if __name__ == "__main__":
    unittest.main()


class SummaryTest(unittest.TestCase):
    def test_summary_mentions_pending_and_topics(self):
        from addon.ankiops.runner import RunResult
        from addon.gui.scheduler import summarize
        text, err = summarize([RunResult("Interview", "ok", 3, "3 new; topic list finished")], pending=3)
        self.assertIn("Interview: 3 new", text)
        self.assertIn("3 waiting for review", text)
        self.assertIn("topic list finished", text)
        self.assertFalse(err)


class CompletenessTest(unittest.TestCase):
    def test_pt_complete(self):
        missing = set(i18n.STRINGS["en"]) - set(i18n.STRINGS["pt"]) - {"menu.title", "common.ok"}
        self.assertEqual(missing, set())


class NetworkFailureTest(unittest.TestCase):
    def setUp(self):
        from addon.ankiops.runner import RunResult
        self.net = RunResult("Entrevista", "error", 0, "LLMError: network error: HTTPSConnectionPool(...) "
                             "Failed to resolve 'api.openai.com'")
        self.other = RunResult("Inglês", "error", 0, "LLMError: HTTP 401: invalid key")

    def test_network_failure_reason_and_retry_shown(self):
        from addon.gui.scheduler import summarize
        text, err = summarize([self.net])
        self.assertTrue(err)
        self.assertIn("no internet", text)
        self.assertIn("2 min", text)

    def test_other_failure_shows_short_reason(self):
        from addon.gui.scheduler import summarize
        text, _ = summarize([self.other])
        self.assertIn("HTTP 401", text)

    def test_retry_soon_only_for_network(self):
        from addon.gui.scheduler import should_retry_soon
        self.assertTrue(should_retry_soon([self.net]))
        self.assertFalse(should_retry_soon([self.other]))


class ScreenTextTest(unittest.TestCase):
    def tearDown(self):
        i18n.set_lang("en")

    def test_prompt_field_titles_follow_language(self):
        from datetime import date
        from addon.core import templates
        i18n.set_lang("pt_BR")
        g = templates.new_generator("blank", "N", "D", "s", date(2026, 11, 14))
        self.assertEqual(g.prompt_fields[0].title, "Papel da IA")
        i18n.set_lang("en")
        g = templates.new_generator("blank", "N", "D", "s", date(2026, 11, 14))
        self.assertEqual(g.prompt_fields[0].title, "AI role")

    def test_import_summary_is_translated(self):
        from addon.gui.import_dialog import describe
        i18n.set_lang("pt_BR")
        text = describe({"name": "X", "template": "interview", "format": "reversed", "fields": 7, "audio": False,
                         "cards_per_day": 5, "spend_cap_usd": 2.0, "rules": ["ramp", "approval", "topics"]})
        self.assertIn("Frente e verso, com cartão invertido", text)
        self.assertIn("Aumentar aos poucos", text)
        self.assertIn("Aprovar antes de entrar", text)
        self.assertNotIn("approval", text)
        self.assertNotIn("(cards esperam", text)
