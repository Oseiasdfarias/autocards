"""Lê e grava a config (`user_files/autocards.json`) de forma atômica."""
from __future__ import annotations

import json
import os
import tempfile

from .model import AppConfig, app_config_from_dict, to_dict


def load(path: str) -> AppConfig:
    try:
        with open(path, encoding="utf-8") as f:
            return app_config_from_dict(json.load(f))
    except FileNotFoundError:
        return AppConfig()


def save(path: str, cfg: AppConfig) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(to_dict(cfg), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def update_run_state(path: str, generators) -> None:
    """Grava só o estado de execução (last_success, attempts_today) na config atual do disco,
    sem apagar o que o usuário editou enquanto a geração rodava."""
    cfg = load(path)
    by_id = {g.id: g for g in generators}
    for g in cfg.generators:
        ran = by_id.get(g.id)
        if ran is not None:
            g.last_success = ran.last_success
            g.attempts_today = dict(ran.attempts_today)
    save(path, cfg)
