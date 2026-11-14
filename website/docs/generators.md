---
title: Generators
---

# Generators

A generator is a recipe for cards. **Tools › AutoCards › Generators…** lists yours on the left. The buttons below the list are **+ New generator**, **Import…**, **Export…** and **Delete**. The selected generator has four tabs, plus **Test**, **Generate now**, **Cancel** and **Save** at the bottom.

## Basic

![Basic tab](/img/screens/en/generator-basic.png)

*Basic tab*


| Field | Meaning |
|---|---|
| Name | How the generator appears in notices and in the log. |
| What do you want to study? | One sentence. It fills `{topic}` in the prompt. |
| Level | Basic, intermediate or advanced. It fills `{level}`. |
| Cards per day | Used when the *Increase gradually* rule is off. |
| Target deck | An existing deck, or type a new name (`Parent::Child` works). It is created if missing. |
| Text service | Which AI connection to use. |
| AI model | Leave it empty to use the service's default model. |
| Your language / Language you study | Only on the Language template. They fill `{native_lang}` and `{target_lang}`. |

## Prompt

![Prompt tab: fields on the left, the selected field's text on the right, and the final prompt below](/img/screens/en/generator-prompt.png)

*Prompt tab: fields on the left, the selected field's text on the right, and the final prompt below*


The prompt is built from **fields**, each describing one aspect of the card:

`AI role` · `Topic` · `Level and audience` · `Card front` · `Card back` · `What to avoid` · `Examples of good cards`

- **Turn a field on or off** with its checkbox. The text is kept.
- **Reorder** by dragging.
- **+ Add custom field** for anything else, with any name.
- Placeholders `{topic}`, `{level}`, `{target_lang}` and `{native_lang}` are replaced with the values from the Basic tab.

![Naming a custom field](/img/screens/en/custom-field.png)

*Naming a custom field*


The **Final prompt** box shows exactly what is sent, live and read-only, with a **Copy** button. Below your fields, AutoCards always appends a fixed block (in English, for the model). It contains:
- how many cards to generate;
- the languages, when set;
- a sample of cards that already exist ("do not repeat these");
- the day's topics or reinforcement cards, when those rules are on;
- the exact JSON format of the answer.

## Format & audio

![Format & audio tab](/img/screens/en/generator-format.png)

*Format & audio tab*


| Option | Meaning |
|---|---|
| Card format | **Front and back**, **Front and back + reversed card**, or **Cloze** (fill in the blank). |
| Extra "Context" field | One short sentence about when the phrase or fact is used, shown on the back. |
| Audio | On or off. |
| Audio text comes from | The front or the back. For cloze, the front audio hides the answer and the back audio says it. |
| Audio service / Voice | Pick from the list for Edge and OpenAI. For ElevenLabs, paste the **voice ID** from your ElevenLabs account. |
| Listen to sample | Plays the chosen voice. |

### Note types

AutoCards creates its own note types, so it does not depend on the field names of your Anki language:

| Note type | Fields |
|---|---|
| AutoCards Basic | Front, Back, Context, FrontAudio, BackAudio |
| AutoCards Reversed | same as Basic, with two cards per note |
| AutoCards Cloze | Text, Back Extra, Context, FrontAudio, BackAudio |

Every generated note gets the tag `autocards`.

## Rules

See [Rules](rules.md).

## When generators run

- **When the profile opens**, and **every hour** while Anki stays open (for when the day changes overnight).
- **Once a day** per generator. "Day" follows your computer's clock. Missed days don't pile up: after three days away you get one day's cards.
- Generators run one after another. If one fails, the others still run.
- If one fails, it tries again on the next hourly check, **up to 3 attempts a day**. Without internet it tries again after **2 minutes**, which helps right after the computer wakes up.
- **Generate now** ignores "once a day" but still respects the protection rules.
