#!/usr/bin/env bash
# Roda a suíte com o Python do próprio Anki (sem pytest, sem pip).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${ANKI_PY:-$HOME/.local/share/AnkiProgramFiles/.venv/bin/python}"
QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}" exec "$PY" -m unittest discover -s tests -t . "$@"
