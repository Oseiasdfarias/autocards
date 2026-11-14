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
