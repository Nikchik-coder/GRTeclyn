"""Search constants and the explicit state shared by workflow functions."""
from __future__ import annotations
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np

TOL = 1e-14
STALL_OK = 1e-11
C_GATE = 0.05
CLEAN_GATE = 1e-8
CEILING = 1e-6
# 2026-10-29: X+1 ranked cheaper ABOVE-GATE over each other and walked
# q3 to 17 on drainholes (3 accepted in 400).  Any accepted X (~1-5)
# beats this floor; log10(residual/CEILING) ranks the rejected toward
# the 1e-6 ceiling.
DEATH = 1e3
#: knob scales for the nearest-seed metric and the initial simplex
SCALES = np.array([0.1, 0.3, 0.3, 0.3])
FIELDS = ("F", "W", "N", "B", "PSI")
SAVE_CONVENTIONS = (
    "F, W, N, B, PSI on the collocation nodes of the pinned problem (sx "
    "radial xi, sy = cos 2 theta) in grid units (eta0 = 1): ds^2 = -e^F "
    "dt^2 + B^2 e^-F [e^nu (deta^2 + h dtheta^2) + h sin^2 theta (dphi - "
    "W dt)^2], nu = N sin^2 theta, h = eta^2 + 1, eta = radial_map(sx).  "
    "Physical lengths are sigma times the grid's; W and omega scale as "
    "1/sigma.  psi = sqrt(4 pi) phi, cal V = 8 pi V, potential_coeffs "
    "ascending in psi for the physical cal V (the rows use sigma^2 cal "
    "V); psim = psi(-inf).")


@dataclass
class SearchContext:
    """One search; caches and incumbent records belong only to this instance."""
    J0: float
    J_max: float | None
    J_min: float
    args: Namespace
    checks_root: Path
    d2: float
    grid: Any
    grids: list[tuple[int, int]]
    name: str
    nx: int
    ny: int
    out: Path
    pin_row: tuple[str, float]
    prev0: dict
    scales: np.ndarray
    score_key: str
    sol: Any
    state: dict
    sx_all: np.ndarray
    th: dict
    wide: bool
    x_v0: float | None = None
