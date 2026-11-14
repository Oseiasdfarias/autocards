---
sidebar_position: 3
title: Getting started
---

# Getting started

## 1. Connect an AI service

Open **Tools › AutoCards › Generators…**. The first time, the **setup assistant** opens:

1. **Choose a service.** OpenAI is the simplest; OpenRouter and Groq have free options; Ollama runs on your own computer (install it first).
2. **Paste your API key.** An API key is a password-like code that lets the add-on use your account. The assistant links to the page where you create it. Click **Test connection** to check it on the spot.
3. **Finish.** The service is saved, together with free Edge audio.

![Setup assistant: choose a service, then paste and test your key](/img/screens/en/wizard-1.png)
![Setup assistant: choose a service, then paste and test your key](/img/screens/en/wizard-2.png)

*Setup assistant: choose a service, then paste and test your key*


You can change services later in **Tools › AutoCards › Services…**.

![The last page of the assistant](/img/screens/en/wizard-3.png)

*The last page of the assistant*


## 2. Create a generator

Click **+ New generator** and pick a starter template:

![Choosing the starter template](/img/screens/en/template-picker.png)

*Choosing the starter template*


| Template | Good for | Defaults |
|---|---|---|
| **Language** | Phrases in the language you study, translated into yours | Context field and audio on |
| **Technical interview** | Interview questions with short, objective answers | No audio |
| **Concepts** | One concept per card, definition plus example | No audio |
| **Blank** | Writing your own prompt from scratch | All fields empty |

Then, on the **Basic** tab, fill in what you want to study, the level, the cards per day and the target deck. See [Generators](generators.md) for every option.

![The Basic tab of a Language generator](/img/screens/en/generator-basic.png)

*The Basic tab of a Language generator*


## 3. Test before saving

Click **Test: generate 1 sample card**. AutoCards shows a card made with your current settings, plays the audio if there is any, and **does not add it to Anki**. It is also the quickest way to check that your key works.

![A sample card: nothing is added to Anki](/img/screens/en/test-result.png)

*A sample card: nothing is added to Anki*


## 4. Save and let it run

Click **Save**. From now on, each time your profile opens:

- each generator that has not run today creates its quota in the background;
- you keep studying while it works;
- a notice shows the result, for example `Daily English: 6 new · Interview: 3 new · 2 waiting for review`.

To run it right away, use **Generate now** (in the dialog or in the menu).

![The notice at the end of a run](/img/screens/en/notice.png)

*The notice at the end of a run*


:::tip Start small
The **Increase gradually** rule is on by default: a new generator starts with 2 cards a day and reaches 10 after 4 weeks. Change it on the [Rules](rules.md) tab.
:::
