---
title: Privacy
---

# Privacy

- **API keys** are stored in plain text in the add-on's `user_files/autocards.json` on your computer, which is the usual practice for Anki add-ons. They are **never** written to exported generators, the log or the CSV.
- **Card text** is sent only to the services you configure. With Ollama or LM Studio, nothing leaves your computer.
- To avoid duplicates, AutoCards sends the AI a sample of the **fronts of the cards already in the target deck**. Keep that in mind for decks with private content, or turn off *Don't repeat*.
- **Edge audio** uses Microsoft's public read-aloud service; the card text goes to Microsoft.
- AutoCards has **no server, no analytics and no account**.
