"""Custo estimado a partir do preço informado em cada serviço."""
from __future__ import annotations

from .model import Service


def text_cost(svc: Service | None, tokens_in: int, tokens_out: int) -> float:
    if svc is None:
        return 0.0
    return tokens_in / 1e6 * svc.price_in_per_m + tokens_out / 1e6 * svc.price_out_per_m


def tts_cost(svc: Service | None, chars: int) -> float:
    if svc is None:
        return 0.0
    return chars / 1000 * svc.price_per_k_chars
