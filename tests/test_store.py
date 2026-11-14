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
        self.assertEqual(rows[0]["generator"], "g")

    def test_unknown_finish_field_rejected(self):
        r = self.store.start_run("g", 1, False)
        with self.assertRaises(ValueError):
            self.store.finish_run(r, api_key="sk-secret")


if __name__ == "__main__":
    unittest.main()


class OutcomeTest(StoreTest):
    def test_set_outcome_updates_card_row(self):
        r = self.store.start_run("g", 1, False)
        self.store.add_card(r, "{}", 77, False, "pending")
        self.store.set_outcome(77, "edited", original='{"Back":"b"}', final='{"Back":"x"}')
        row = self.store._db.execute("select outcome, original, final from cards where note_id=77").fetchone()
        self.assertEqual(row, ("edited", '{"Back":"b"}', '{"Back":"x"}'))


class FriendlyCsvTest(StoreTest):
    def read(self, **kw):
        out = os.path.join(self.dir.name, "f.csv")
        self.store.export_csv(out, **kw)
        with open(out, encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_cost_once_per_run_and_generator_name(self):
        r = self.store.start_run("g1", 1, False, when="2026-11-14T05:00:00")
        self.store.finish_run(r, cost=0.002, status="ok", inserted=2)
        self.store.add_card(r, '{"front":"a"}', 1, False, "inserted")
        self.store.add_card(r, '{"front":"b"}', 2, False, "inserted")
        rows = self.read(generator_names={"g1": "Daily English"})
        self.assertEqual([x["generator"] for x in rows], ["Daily English", "Daily English"])
        self.assertEqual([x["run_cost_usd"] for x in rows], ["0.002000", ""])
        self.assertEqual(sum(float(x["run_cost_usd"] or 0) for x in rows), 0.002)

    def test_test_runs_excluded_by_default(self):
        t = self.store.start_run("g1", 1, True)
        self.store.finish_run(t, cost=1.0, status="ok")
        self.store.add_card(t, "{}", None, False, "test")
        r = self.store.start_run("g1", 1, False)
        self.store.finish_run(r, cost=0.5, status="blocked")
        rows = self.read()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "blocked")
        self.assertEqual(len(self.read(include_tests=True)), 2)

    def test_unknown_generator_falls_back_to_id(self):
        r = self.store.start_run("zz", 1, False)
        self.store.finish_run(r, status="ok")
        self.assertEqual(self.read()[0]["generator"], "zz")
