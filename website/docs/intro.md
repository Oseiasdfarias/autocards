---
sidebar_position: 1
slug: /intro
title: What is AutoCards
---

# What is AutoCards

**AutoCards is an Anki add-on that writes new flashcards for you every day, with AI, on its own.**

You set up one or more **generators**. Each generator is a recipe: what you want to study, how the cards should be written, the card format, optional audio and a few rules. When you open Anki, every generator creates its quota for the day in the background and shows a short notice when it is done.

## Why it exists

Most AI add-ons for Anki generate cards **when you ask**. AutoCards is built for a daily habit instead:

| | |
|---|---|
| **Runs by itself** | Once a day per generator, when your profile opens. If Anki stays open overnight, it checks again every hour. Missed days don't pile up. |
| **Protects your reviews** | Pauses when overdue reviews pile up, can ramp the daily amount up slowly, and has a monthly spending cap. |
| **Prompts you can edit** | The prompt is split into fields (AI role, topic, level, front, back, what to avoid, examples) that you can turn on and off, reorder and extend, with a live preview. |
| **Audio you choose** | Free Microsoft Edge voices, OpenAI or ElevenLabs. |
| **Quality you can measure** | Every run and card is logged: prompt, model, tokens, estimated cost and what you accepted, edited or discarded. |

## What you need

- **Anki 26.09 or newer** on Windows, macOS or Linux.
- **An AI service.** Any service that speaks the OpenAI chat format works: OpenAI, OpenRouter, Groq, or a model on your own computer with Ollama or LM Studio.

Nothing else: AutoCards uses only what ships with Anki. There are no Python packages and no command line.

:::note
Generation happens on the computer. Cards made there sync to AnkiDroid and AnkiMobile as usual.
:::

## Next steps

1. [Install the add-on](install.md).
2. [Create your first generator](getting-started.md).
