import unittest

from addon.core import dedupe


def c(front):
    return {"front": front, "back": "x"}


class DedupeTest(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(dedupe.normalize("<b>Hello,</b>  World!"), "hello world")
        self.assertEqual(dedupe.normalize("Olá&nbsp;mundo"), "olá mundo")

    def test_exact_duplicate_of_existing_dropped(self):
        kept, dropped = dedupe.filter_cards([c("Hello world!")], "front", ["hello world"])
        self.assertEqual((kept, dropped), ([], 1))

    def test_near_duplicate_dropped(self):  # ratio 0.952
        kept, dropped = dedupe.filter_cards([c("Hello word")], "front", ["Hello world"])
        self.assertEqual(dropped, 1)

    def test_rephrasing_below_threshold_kept(self):  # ratio 0.828
        kept, dropped = dedupe.filter_cards([c("I'd rather go")], "front", ["I would rather go"])
        self.assertEqual((len(kept), dropped), (1, 0))

    def test_duplicate_within_batch_dropped(self):
        kept, dropped = dedupe.filter_cards([c("Same"), c("same!")], "front", [])
        self.assertEqual(([k["front"] for k in kept], dropped), (["Same"], 1))

    def test_empty_front_dropped(self):
        kept, dropped = dedupe.filter_cards([c("  "), c("<br>")], "front", [])
        self.assertEqual((kept, dropped), ([], 2))

    def test_cloze_key_strips_cloze_markup(self):
        kept, dropped = dedupe.filter_cards(
            [{"text": "The {{c1::cat}} sat"}], "text", ["The cat sat"])
        self.assertEqual(dropped, 1)

    def test_sample_existing_limit(self):
        fronts = [f"f{i}" for i in range(200)]
        self.assertEqual(dedupe.sample_existing(fronts, 150), fronts[:150])


if __name__ == "__main__":
    unittest.main()
