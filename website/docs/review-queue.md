---
title: Review queue
---

# Review queue

Turn on **Approve before adding** (Rules tab) for topics where a wrong fact matters, such as medicine, law or interview answers.

With the rule on, new cards are added **suspended** and tagged `autocards::pending`, so they never show up in study before you approve them.

Open **Tools › AutoCards › Review generated cards…**. It shows one card at a time with editable fields:

| Button | What happens |
|---|---|
| **Accept (with your edits)** | Saves any edits, removes the tag and unsuspends the card. Logged as `accepted`, or `edited` with the original and final text. |
| **Discard** | Deletes the note. Logged as `discarded`. The same card won't be generated again. |
| **Skip** | Moves it to the end of the queue. |
| **Play audio** | Plays the card's audio, if any. |
| **Close** | Leaves the rest for later. |

When the queue is empty, the window closes and shows a notice. If you unsuspend a pending card by hand, it stays in the queue until you accept or discard it. Pending notes deleted in the Browser simply leave the queue.

:::tip
Acceptance, edits and discards are the best quality signal you have. Export the log to see how a generator is doing ([Log and quality](log-and-quality.md)).
:::
