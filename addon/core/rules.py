"""Regras do gerador (spec §7.4): cota do dia, bloqueios e 'uma vez por dia'."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .model import Generator, Rules

MAX_ATTEMPTS_PER_DAY = 3


@dataclass
class Block:
    reason: str  # weekday | brake | spend_cap
    detail: str


def daily_quota(rules: Rules, cards_per_day: int, created: date, today: date) -> int:
    if not rules.ramp_enabled:
        return max(0, cards_per_day)
    weeks = max(1, rules.ramp_weeks)
    frac = min(1.0, max(0, (today - created).days) / (7 * weeks))
    return max(0, round(rules.ramp_start + (rules.ramp_end - rules.ramp_start) * frac))


def check_blocks(gen: Generator, today: date, overdue: int, month_cost: float) -> Block | None:
    r = gen.rules
    if r.weekdays_enabled and today.weekday() not in r.weekdays:
        return Block("weekday", "not a generation day")
    if r.brake_enabled and overdue > r.brake_limit:
        return Block("brake", f"{overdue} overdue cards (limit {r.brake_limit})")
    if r.spend_cap_enabled and month_cost >= r.spend_cap_usd:
        return Block("spend_cap", f"US$ {month_cost:.2f} spent this month (cap {r.spend_cap_usd:.2f})")
    return None


def should_run(gen: Generator, today: date, force: bool) -> bool:
    if force:
        return True
    key = today.isoformat()
    return gen.last_success != key and gen.attempts_today.get(key, 0) < MAX_ATTEMPTS_PER_DAY
