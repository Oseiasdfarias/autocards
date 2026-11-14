# AutoCards

**An Anki add-on that writes new flashcards for you every day, with AI, on its own.**

You set up *generators*: a topic, how the cards should be written, the card format, optional audio and a few rules. When you open Anki, each generator creates its daily quota in the background and tells you when it is done. Nothing to click, nothing to install besides the add-on.

> Status: version 1.1, in real-world validation by the author. Interface in English and Portuguese.
>
> 📖 **Documentation:** https://oseiasdfarias.github.io/autocards/ (English · Português)

## Why

AI add-ons for Anki generate cards *when you ask*. AutoCards is built for a habit instead:

- **Generates by itself, once a day** per generator, when the profile opens (and checks every hour if Anki stays open overnight). Missed days do not pile up.
- **Protects you from avalanches:** it pauses when your overdue reviews pile up, can ramp the daily amount up slowly, and has a monthly spending cap.
- **Prompts you can actually edit:** the prompt is split into fields (AI role, topic, level, front, back, what to avoid, examples). Toggle, reorder or add your own, with a live preview of the final prompt.
- **Audio with the service you choose:** free Microsoft Edge voices, OpenAI or ElevenLabs.
- **Quality you can measure:** every run and every card is logged (prompt, model, tokens, estimated cost, what you accepted, edited or discarded). Export it as CSV.

## Features

- Starter templates: **Language**, **Technical interview**, **Concepts**, **Blank**.
- Card formats: front/back, front/back + reversed, cloze. Optional "Context" field.
- Rules: increase gradually · only on some weekdays · pause when reviews pile up · don't repeat existing cards · spending cap · **approve before adding** (review queue) · **reinforce what you get wrong** · **follow a topic list**.
- Text services: anything that speaks the OpenAI chat format — OpenAI, OpenRouter, Groq, Ollama (local), LM Studio (local).
- Export/import generators as `.autocards.json` files (keys, services and decks are never exported).
- Setup assistant that explains API keys and tests yours on the spot.

## Install

1. In Anki (26.09 or newer): *Tools › Add-ons › Install from file…* and pick `autocards.ankiaddon`.
2. Restart Anki and open *Tools › AutoCards › Generators…*. The setup assistant opens the first time.

No Python packages, no command line: it runs only on what ships with Anki.

## Costs

You use your own AI account. With `gpt-4o-mini`, ten cards a day cost a few US cents **per month**; Edge audio is free. Local models (Ollama, LM Studio) cost nothing. Prices in the add-on are estimates you can edit; the spending cap uses them.

## Privacy

- Your API keys stay in the add-on's `user_files` folder on your computer. They never go into exported generators, the log or the CSV.
- Card text is sent only to the services you configure.
- Edge audio uses Microsoft's public read-aloud service (unofficial). If it changes, switch audio to OpenAI or ElevenLabs.

## For sensitive topics

For medicine, law or anything where a wrong fact matters, turn on **Approve before adding**: generated cards wait in *Tools › AutoCards › Review generated cards…* until you accept, edit or discard them.

## Development

Everything runs on the Python bundled with Anki — no pip.

| Command | What |
|---|---|
| `scripts/test.sh` | Test suite (`unittest`) on Anki's Python |
| `AUTOCARDS_NET=1 scripts/test.sh` | Also runs the live Edge TTS test |
| `scripts/dev-link.sh` | Links `addon/` into Anki's add-ons folder |
| `scripts/build.sh` | Builds `dist/autocards.ankiaddon` |

Layout: `addon/core/` (pure Python: model, prompt, AI client, rules, log, audio), `addon/ankiops/` (collection operations and the three-phase run: read → network → write, so Anki never waits on the network), `addon/gui/` (menu, dialogs, scheduling).

Design and plans (Portuguese): [`docs/LEIAME.md`](docs/LEIAME.md).

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE). Includes the Edge token routine adapted from [edge-tts](https://github.com/rany2/edge-tts) (LGPL-3.0).
