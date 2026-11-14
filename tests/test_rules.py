import unittest
from datetime import date

from addon.core import costs, rules
from addon.core.model import Generator, Rules, Service

D0 = date(2026, 11, 2)  # segunda-feira


def g(**rk) -> Generator:
    return Generator(id="g", name="N", cards_per_day=7, created=D0.isoformat(), rules=Rules(**rk))


class QuotaTest(unittest.TestCase):
    def test_ramp(self):
        r = Rules(ramp_start=2, ramp_end=10, ramp_weeks=4)
        q = lambda days: rules.daily_quota(r, 7, D0, date.fromordinal(D0.toordinal() + days))
        self.assertEqual([q(0), q(14), q(28), q(60)], [2, 6, 10, 10])

    def test_ramp_disabled_uses_cards_per_day(self):
        self.assertEqual(rules.daily_quota(Rules(ramp_enabled=False), 7, D0, D0), 7)


class BlockTest(unittest.TestCase):
    def test_weekday_blocks(self):
        b = rules.check_blocks(g(weekdays_enabled=True, weekdays=[1, 2]), D0, 0, 0.0)
        self.assertEqual(b.reason, "weekday")

    def test_weekday_allowed(self):
        self.assertIsNone(rules.check_blocks(g(weekdays_enabled=True, weekdays=[0]), D0, 0, 0.0))

    def test_brake_over_limit(self):
        self.assertEqual(rules.check_blocks(g(brake_limit=30), D0, 31, 0.0).reason, "brake")

    def test_brake_at_limit_passes(self):
        self.assertIsNone(rules.check_blocks(g(brake_limit=30), D0, 30, 0.0))

    def test_brake_disabled(self):
        self.assertIsNone(rules.check_blocks(g(brake_enabled=False), D0, 999, 0.0))

    def test_spend_cap(self):
        self.assertEqual(rules.check_blocks(g(spend_cap_usd=2.0), D0, 0, 2.0).reason, "spend_cap")
        self.assertIsNone(rules.check_blocks(g(spend_cap_usd=2.0), D0, 0, 1.99))


class ShouldRunTest(unittest.TestCase):
    def test_runs_once_per_day(self):
        gen = g()
        self.assertTrue(rules.should_run(gen, D0, False))
        gen.last_success = D0.isoformat()
        self.assertFalse(rules.should_run(gen, D0, False))
        self.assertTrue(rules.should_run(gen, D0, True))

    def test_three_attempts_max(self):
        gen = g()
        gen.attempts_today = {D0.isoformat(): 3}
        self.assertFalse(rules.should_run(gen, D0, False))
        gen.attempts_today = {D0.isoformat(): 2}
        self.assertTrue(rules.should_run(gen, D0, False))


class CostTest(unittest.TestCase):
    def test_costs(self):
        s = Service(id="s", name="s", price_in_per_m=0.15, price_out_per_m=0.6, price_per_k_chars=0.015)
        self.assertAlmostEqual(costs.text_cost(s, 1_000_000, 500_000), 0.45)
        self.assertAlmostEqual(costs.tts_cost(s, 2000), 0.03)
        self.assertEqual(costs.text_cost(None, 10, 10), 0.0)


if __name__ == "__main__":
    unittest.main()
