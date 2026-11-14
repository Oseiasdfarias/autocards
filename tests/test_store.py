import csv
import os
import tempfile
import unittest

from addon.core.store import Store


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.store = Store(os.path.join(self.dir.name, "log.sqlite3"))
        self.addCleanup(self.store.close)

    def test_month_cost_ignores_tests_and_other_months(self):
        r1 = self.store.start_run("g", 1, False, when="2026-11-03T05:00:00")
        self.store.finish_run(r1, cost=0.5)
        r2 = self.store.start_run("g", 1, True, when="2026-11-04T05:00:00")
        self.store.finish_run(r2, cost=9.0)
        r3 = self.store.start_run("g", 1, False, when="2026-10-30T05:00:00")
        self.store.finish_run(r3, cost=3.0)
        self.assertAlmostEqual(self.store.month_cost(2026, 11), 0.5)

    def test_cards_and_csv(self):
        r = self.store.start_run("g", 1, False)
        self.store.finish_run(r, prompt="p", service="OpenAI", model="m", tokens_in=1, tokens_out=2,
                              inserted=1, requested=2, received=2, dropped_dupe=1)
        self.store.add_card(r, '{"front":"a"}', 123, True, "inserted")
        out = os.path.join(self.dir.name, "log.csv")
        self.store.export_csv(out)
        with open(out, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["note_id"], "123")
        self.assertEqual(rows[0]["generator_id"], "g")

    def test_unknown_finish_field_rejected(self):
        r = self.store.start_run("g", 1, False)
        with self.assertRaises(ValueError):
            self.store.finish_run(r, api_key="sk-secret")


if __name__ == "__main__":
    unittest.main()
