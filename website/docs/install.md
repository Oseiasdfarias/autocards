---
sidebar_position: 2
title: Install
---

# Install

1. Download `autocards.ankiaddon` from the [GitHub Releases page](https://github.com/Oseiasdfarias/autocards/releases), or [build it from source](development.md#build-the-package).
2. In Anki, open **Tools › Add-ons › Install from file…** and pick the file.
3. Restart Anki.

You will find a new menu: **Tools › AutoCards**.

| Menu item | What it does |
|---|---|
| Generators… | Create and edit generators. |
| Services… | Your AI and audio connections. |
| Setup assistant… | Guided setup of your first AI service. |
| Review generated cards… | The approval queue (see [Review queue](review-queue.md)). |
| Generate now | Runs every generator now, even if it already ran today. |
| Export log (CSV)… | Saves the full log as a spreadsheet. |

## Updating

Install the new file the same way. Your generators, services and log live in the add-on's `user_files` folder, which Anki keeps across updates.

## Uninstalling

**Tools › Add-ons**, select AutoCards, **Delete**. Cards that were already created stay in your collection.
