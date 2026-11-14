---
title: Import and export
---

# Import and export generators

Share a generator with a friend, or install a ready-made pack.

## Export

Select a generator and click **Export…**. You get a `.autocards.json` file with the prompt fields, format, audio settings and rules.

**Never exported:**
- API keys and services;
- the target deck;
- the AI model;
- run history: last run, attempts, used topics.

## Import

Click **Import…** and pick the file. AutoCards checks it and shows a summary before adding anything:

- name, number of prompt fields, card format, audio;
- **cards per day and the spending cap**, so you know what the file will cost you;
- which rules are on.

Then choose the **target deck**, the **text service** and the **audio service**. The imported generator:

![Import: the summary shows volume and spending before anything is added](/img/screens/en/import.png)

*Import: the summary shows volume and spending before anything is added*


- uses your service's default model;
- switches the voice to one that exists in the audio service you chose;
- starts fresh, as if you had just created it.

Importing the same file twice creates two separate generators.

AutoCards refuses, with a clear message:
- files that aren't generator files;
- files from a newer, unsupported format version;
- files with wrong field types.

![A file that isn't a generator](/img/screens/en/import-invalid.png)

*A file that isn't a generator*


Numbers are limited to the same ranges the settings screen allows.

If you have no text service yet, **Import…** opens the setup assistant first.
