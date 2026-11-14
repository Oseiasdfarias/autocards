#!/usr/bin/env bash
# Gera dist/autocards.ankiaddon (zip de addon/ sem dados do usuário nem cache).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
OUT="dist/autocards.ankiaddon"
rm -f "$OUT"
PY="${ANKI_PY:-$HOME/.local/share/AnkiProgramFiles/.venv/bin/python}"
"$PY" - "$OUT" <<'PY'
import os, sys, zipfile
out = sys.argv[1]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk("addon"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, "addon")
            if f.endswith(".pyc") or f == "meta.json":
                continue
            if rel.startswith("user_files" + os.sep) and f != "README.txt":
                continue
            z.write(path, rel)
print(out, os.path.getsize(out), "bytes")
PY
