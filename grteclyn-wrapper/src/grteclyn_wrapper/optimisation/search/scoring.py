"""Potential positivity checks and finite rejection penalties.

The minimum of Q is sampled at the established 1001 points on [0, 1].
Independent-constraint overflow is measured relative to the 1e-6 ceiling.
Non-finite or missing monitors receive the fixed rejection penalty.
"""
from __future__ import annotations
import math
import numpy as np
from .state import DEATH, CEILING


def min_q(q) -> float:
    u = np.linspace(0.0, 1.0, 1001)
    acc = np.ones_like(u)
    for k, qk in enumerate(q):
        acc = acc + qk * u ** (k + 1)
    return float(np.min(acc))


def death(extra: float = 0.0) -> float:
    return DEATH + extra


def monitor_overflow(row: dict) -> float:
    try:
        values = [float(row["e19"]), float(row["e_c"])]
    except (KeyError, TypeError, ValueError):
        return 10.0
    if not all(math.isfinite(v) for v in values):
        return 10.0
    return math.log10(max(max(values) / CEILING, 1.0))
