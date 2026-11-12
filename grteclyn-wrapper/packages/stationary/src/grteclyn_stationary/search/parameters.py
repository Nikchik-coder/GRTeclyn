"""Optional search knobs for ``optimize_potential.py``.

Defaults stay the published four-knob walk: pin $R_e$, hold $J$, score
$X = |{\\rm VIQ}|/R_e$.  ``--pin area`` and ``--free-J`` are opt-in;
nothing here changes a call that omits them.
"""

from __future__ import annotations

import numpy as np

__all__ = ["bill_name", "knob_vector", "pin_held"]


def pin_held(kind: str, throat: dict) -> tuple[str, float]:
    """Newton pin from a measured throat: equatorial radius or area."""
    if kind == "R_e":
        return ("R_e", float(throat["R_e"]))
    if kind == "area":
        return ("area", float(throat["area_throat"]))
    raise ValueError(f"pin {kind!r}: 'R_e' or 'area'")


def bill_name(kind: str) -> str:
    """Score the bill per pinned radius: $X$ at $R_e$, $X_A$ at area."""
    if kind == "R_e":
        return "X"
    if kind == "area":
        return "X_A"
    raise ValueError(f"pin {kind!r}: 'R_e' or 'area'")


def knob_vector(x0, *, free_j: bool, j_start: float) -> np.ndarray:
    """$(m, q_1, q_2, q_3)$ or the same plus $J$ when spin is a knob."""
    x = np.asarray(x0, float).ravel()
    if x.size == 4:
        return np.append(x, j_start) if free_j else x
    if x.size == 5 and free_j:
        return x
    raise ValueError(
        "--x0 is m,q1,q2,q3"
        + (",J when --free-J" if free_j else ""))
