---
title: Log and quality
---

# Log and quality

AutoCards keeps a log of every run and every card, so you can measure what the AI produces.

**Each run records:**
- date and generator;
- the final prompt sent;
- service and model;
- input and output tokens, estimated cost and duration;
- cards requested, received, rejected as invalid, dropped as duplicates and added;
- the reason when a run was blocked or failed.

**Each card records:**
- the generated text and the note ID;
- whether it got audio;
- its outcome: `inserted`, `pending`, `accepted`, `edited` (with the original and final text), `discarded` or `test`.

## Export

**Tools › AutoCards › Export log (CSV)…** saves everything as a spreadsheet: one row per card, with the generator name. Each run's cost appears only on its first row, so adding up the `run_cost_usd` column gives your real spend. Test runs are left out. API keys are never written to the log.

## Ideas for analysis

- **Acceptance rate per generator:** `accepted` and `edited` versus `discarded`, with the review queue on.
- **Cost per month:** the sum of `cost`, excluding test runs.
- **Duplicate rate:** if `dropped_dupe` is high, add examples or a "what to avoid" field to the prompt.
- **Cards you keep failing:** compare with Anki's own statistics, or turn on *Reinforce what you get wrong*.

The log is a SQLite file at `addons21/autocards/user_files/log.sqlite3` inside your Anki folder.
