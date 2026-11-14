#!/usr/bin/env bash
# Liga a pasta addon/ do repositório à pasta de add-ons do Anki (desenvolvimento).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ANKI_ADDONS:-$HOME/.local/share/Anki2/addons21}/autocards"
if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then echo "$DEST existe e não é link; abortando" >&2; exit 1; fi
ln -sfn "$REPO/addon" "$DEST"
echo "ok: $DEST -> $REPO/addon"
