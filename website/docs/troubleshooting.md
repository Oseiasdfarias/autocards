---
title: Troubleshooting
---

# Troubleshooting

The notice at the end of a run tells you what happened to each generator.

![A generator that ran without internet](/img/screens/en/notice-offline.png)

*A generator that ran without internet*


| Notice | Cause | What to do |
|---|---|---|
| `failed, no internet — trying again in 2 min` | The computer had no network or DNS yet, which is common right after waking up. | Nothing: it retries in 2 minutes, up to 3 attempts a day. |
| `failed (HTTP 401 …)` | Wrong or expired API key. | Fix the key in **Services…** and use **Test connection**. |
| `failed (HTTP 429 …)` | Rate limit or no credit left with the provider. | Check your provider account. |
| `failed (no valid cards in the AI reply …)` | The model answered in the wrong format. Common with very small local models. | Try a bigger model, or simplify the prompt. It retries on the next hourly check. |
| `not today (35 overdue cards, limit 30)` | *Pause when reviews pile up* stopped it. | Do your reviews, raise the limit, or use **Generate now**. |
| `not today (US$ 2.00 spent this month, cap 2.00)` | The spending cap was reached. | Raise the cap on the Rules tab, or wait for next month. |
| `not today (not a generation day)` | *Only on some days*. | — |
| `topic list finished` | Your topic list ran out. | Add topics, or keep generating from the theme. |

## Cards were created but I don't see them

Is **Approve before adding** on? Then they wait in **Tools › AutoCards › Review generated cards…**, suspended. See [Review queue](review-queue.md).

## A card has no audio

The audio service failed for that card, for example because Edge was unavailable or the ElevenLabs voice ID was wrong. The card is still added, and the reason is in the log. Use **Listen to sample** on the *Format & audio* tab to test the voice.

## "The settings file is invalid"

The add-on's `user_files/autocards.json` was edited by hand and has an error. AutoCards does not overwrite it. Fix the file, or delete it to start over (you lose your generators and services).

![The settings file has an error](/img/screens/en/config-invalid.png)

*The settings file has an error*


## Nothing happens when I open Anki

- Each generator runs **once a day**. Did it already run today? Use **Generate now** to run it again.
- Check that the generator has a text service selected and that **Test** works.

## Reporting a bug

Open an issue on [GitHub](https://github.com/Oseiasdfarias/autocards/issues) with:
- your Anki version and operating system;
- the notice text;
- if you can, the relevant lines of the exported log, **without your API key**.
