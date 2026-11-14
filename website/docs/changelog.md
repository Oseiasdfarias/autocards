---
title: Changelog
---

# Changelog

## 1.1.0

**New**
- **Approve before adding:** a review queue to accept, edit or discard generated cards before they reach your study.
- **Reinforce what you get wrong:** new cards that re-explain the notes you keep failing.
- **Follow a topic list:** generate from your own list, in order.
- ElevenLabs audio.
- Export and import generators (`.autocards.json`). Keys, services, deck and model are never exported.
- Setup assistant for the first AI service.
- Portuguese interface.

**Fixes**
- Network calls no longer hold Anki's collection thread, so startup sync and reviews never wait for the AI.
- Closing the profile mid-run no longer spends API calls or marks the day as done.
- Without internet, the notice says so and the run retries after 2 minutes.
- The review window closes when the queue is empty.

## 1.0.0

First version:
- generators with four tabs and four starter templates;
- rules: increase gradually, only on some days, pause when reviews pile up, don't repeat, spending cap;
- any OpenAI-compatible text service;
- Edge and OpenAI audio;
- automatic daily run with a notice and an optional command at the end;
- log with CSV export.
