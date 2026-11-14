---
title: Rules
---

# Rules

Each rule can be turned on or off on the **Rules** tab of a generator. The defaults below are for a new generator.

![Rules tab, with the review queue and a topic list turned on](/img/screens/en/generator-rules-topics.png)

*Rules tab, with the review queue and a topic list turned on*


| Rule | Default | Settings | What it does |
|---|---|---|---|
| **Increase gradually** | on | start with A, reach B in N weeks (2 → 10 in 4) | The daily amount rises in a straight line from A to B, counted from the day the generator was created. When off, *Cards per day* is used. |
| **Only on some days** | off | weekdays | No cards on the days you uncheck. |
| **Pause when reviews pile up** | on | limit (30) | If the target deck has more overdue review cards than the limit, nothing is generated today and the notice says why. |
| **Don't repeat** | on | — | See below. |
| **Spending cap** | on | US$ per month (2.00) | Adds up the estimated cost of **all** generators this month. Above the cap, no generator runs until the month changes or you raise it. |
| **Approve before adding** | off | — | Cards wait in the [review queue](review-queue.md) instead of going straight to study. |
| **Reinforce what you get wrong** | off | from E lapses (3), up to R per day (2) | Finds up to R notes in the deck you failed E or more times and asks for new cards that explain the same thing differently. They count toward the day's quota and get the tag `autocards::reinforcement`. Each source note is used once (tagged `autocards::reinforced`). |
| **Follow a topic list** | off | one topic per line, T per day (1) | Each day takes the next T topics, in order, instead of letting the AI choose. Topics count as used only when at least one card was added. When the list ends you get a notice, and the generator goes back to the theme. Editing or replacing the list never skips or repeats topics, because used ones are remembered by their text. |

:::info A blocked day counts as done
When *Only on some days*, *Pause when reviews pile up* or *Spending cap* stops a generator, the day is considered handled and it does not retry every hour. Use **Generate now** if you want cards anyway.
:::

## Don't repeat

Before calling the AI, AutoCards collects the front of **every** note in the target deck, of any note type, including cards you made before installing it. It also includes the cards you **discarded** in the review queue.

- The prompt receives the 150 most recent ones as "do not repeat these".
- After the answer, a card is dropped if its front is equal or too similar (88% similarity or more) to an existing one or to another card in the same batch.
- If the filter drops cards, AutoCards does **not** call the AI again to fill the quota. The log records how many were dropped.

## Other protections

- Cards with an empty field, and cloze cards without a `{{c1::…}}` deletion, are dropped.
- If the AI replies with no valid card at all, the run counts as a failure and is retried later.
- If you close your profile while it is generating, it stops before writing anything and does not count the day.
