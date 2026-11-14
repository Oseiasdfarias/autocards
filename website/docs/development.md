---
title: Development
---

# Development

AutoCards is open source under **AGPL-3.0**. Code: [github.com/Oseiasdfarias/autocards](https://github.com/Oseiasdfarias/autocards).

## Principles

- **Nothing to install for users.** Only the Python standard library and what Anki 26.09 bundles: `requests`, `jsonschema`, `PyQt6` (including `QtWebSockets`, used to talk to Edge TTS without `aiohttp`).
- **Never block Anki.** Network work never runs on the collection thread.
- **One broken generator never breaks the others**, nor Anki's startup.

## Layout

```text
addon/
  core/       pure Python: model, prompt, AI client, rules, dedupe, log, i18n, audio, exchange format
  ankiops/    collection operations and the generator run
  gui/        menu, dialogs, scheduler (only inside Anki)
tests/        unittest suite
scripts/      test.sh, dev-link.sh, build.sh
website/      this documentation (Docusaurus)
```

## A run in three phases

Anki has a single worker thread for the collection. AutoCards splits each run so that thread is never held while waiting for the network:

1. **prepare** (with the collection, fast): rules, quota, existing fronts, prompt.
2. **fetch** (without the collection): AI call, validation, duplicate filter, audio. This phase doesn't even receive the collection.
3. **commit** (with the collection, fast): write media and notes, log, mark the day.

`gui/phases.py` chains them: a `QueryOp`, then a `QueryOp(...).without_collection()`, then a `QueryOp`.

## Tests

Tests run on **Anki's own Python** with `unittest`. No pip needed.

```bash
scripts/test.sh                    # whole suite
AUTOCARDS_NET=1 scripts/test.sh    # also the live Edge TTS test
```

The suite covers:
- the pure core;
- collection operations, on a temporary collection;
- smoke tests of the dialogs, run offscreen.

## Try it in Anki without touching your profile

```bash
scripts/dev-link.sh                       # links addon/ into Anki's add-ons folder
anki -b /tmp/anki-dev -p AutoCards-dev    # separate data folder and profile
```

## Build the package

```bash
scripts/build.sh    # → dist/autocards.ankiaddon
```

The package never includes `user_files/` (your config and log).

## This website

```bash
cd website
npm install
npm start                    # English
npm start -- --locale pt-BR  # Portuguese
```

It deploys to GitHub Pages automatically on every push to `develop` that changes `website/`.
