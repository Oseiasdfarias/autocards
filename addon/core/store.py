"""Registro em SQLite (spec §10): execuções e cards. Nunca guarda chaves."""
from __future__ import annotations

import csv
import os
import sqlite3
import threading
from datetime import datetime

RUN_FIELDS = (
    "prompt", "service", "model", "tokens_in", "tokens_out", "cost", "duration_s",
    "requested", "received", "dropped_invalid", "dropped_dupe", "inserted",
    "blocked_reason", "error", "status",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, started TEXT NOT NULL, generator_id TEXT NOT NULL,
  config_version INTEGER, is_test INTEGER NOT NULL DEFAULT 0,
  prompt TEXT, service TEXT, model TEXT, tokens_in INTEGER, tokens_out INTEGER,
  cost REAL DEFAULT 0, duration_s REAL, requested INTEGER, received INTEGER,
  dropped_invalid INTEGER, dropped_dupe INTEGER, inserted INTEGER,
  blocked_reason TEXT, error TEXT, status TEXT
);
CREATE TABLE IF NOT EXISTS cards (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES runs(id),
  content TEXT, note_id INTEGER, has_audio INTEGER, outcome TEXT,
  original TEXT, final TEXT, error TEXT
);
"""


class Store:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def start_run(self, generator_id: str, config_version: int, is_test: bool,
                  when: str | None = None) -> int:
        when = when or datetime.now().isoformat(timespec="seconds")
        with self._lock, self._db:
            cur = self._db.execute(
                "INSERT INTO runs(started, generator_id, config_version, is_test) VALUES (?,?,?,?)",
                (when, generator_id, config_version, int(is_test)))
            return cur.lastrowid

    def finish_run(self, run_id: int, **fields) -> None:
        unknown = set(fields) - set(RUN_FIELDS)
        if unknown:
            raise ValueError(f"unknown run fields: {sorted(unknown)}")
        if not fields:
            return
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._lock, self._db:
            self._db.execute(f"UPDATE runs SET {cols} WHERE id=?", (*fields.values(), run_id))

    def add_card(self, run_id: int, content: str, note_id: int | None, has_audio: bool,
                 outcome: str, error: str | None = None) -> None:
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO cards(run_id, content, note_id, has_audio, outcome, error) VALUES (?,?,?,?,?,?)",
                (run_id, content, note_id, int(has_audio), outcome, error))

    def month_cost(self, year: int, month: int) -> float:
        prefix = f"{year:04d}-{month:02d}"
        with self._lock:
            row = self._db.execute(
                "SELECT COALESCE(SUM(cost),0) FROM runs WHERE is_test=0 AND substr(started,1,7)=?",
                (prefix,)).fetchone()
        return float(row[0])

    def export_csv(self, path: str) -> None:
        q = """SELECT r.id AS run_id, r.started, r.generator_id, r.is_test, r.status, r.service, r.model,
                      r.tokens_in, r.tokens_out, r.cost, r.duration_s, r.requested, r.received,
                      r.dropped_invalid, r.dropped_dupe, r.inserted, r.blocked_reason, r.error,
                      c.content, c.note_id, c.has_audio, c.outcome, c.error AS card_error, r.prompt
               FROM runs r LEFT JOIN cards c ON c.run_id = r.id ORDER BY r.id, c.id"""
        with self._lock:
            cur = self._db.execute(q)
            names = [d[0] for d in cur.description]
            rows = cur.fetchall()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(names)
            w.writerows(rows)
