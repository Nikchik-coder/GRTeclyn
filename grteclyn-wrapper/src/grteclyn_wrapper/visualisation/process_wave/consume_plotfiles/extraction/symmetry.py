"""Reflection symmetry for symmetry-reduced runs (the params' lo_boundary = 2).

A run whose lower domain faces are reflective simulates one octant (or
quadrant, or half) of a box that is mirror-symmetric about planes through the
physics centre (``--center``, on those faces).  Every extraction that samples
points around the centre must fold the points that fall outside the simulated
domain back across those planes.  For an even-parity field -- a scalar (chi,
lapse, K, phi, Pi) or a diagonal metric component -- the folded value IS the
value there.  Odd-parity fields (a shift component along a reflected axis, an
off-diagonal metric component, Psi4 in general) change sign across the plane
and must not be folded; the consumer switches off the extractions that sample
them (``--reflect`` in driver.py).
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

AXIS_INDEX = {"x": 0, "y": 1, "z": 2}

#: Fields that change sign across some reflection plane: never fold these.
ODD_PARITY_FIELDS = frozenset({
    "shift1", "shift2", "shift3", "B1", "B2", "B3", "Gamma1", "Gamma2", "Gamma3",
    "h12", "h13", "h23", "A12", "A13", "A23", "Weyl4_Re", "Weyl4_Im",
})


def reflect_axes(reflect: Sequence[str] | None) -> tuple[int, ...]:
    """Axis indices of the reflective planes, e.g. ("x", "z") -> (0, 2)."""
    return tuple(sorted({AXIS_INDEX[a] for a in (reflect or ())}))


def fold_points(sx, sy, sz, center: Sequence[float], reflect: Sequence[str] | None):
    """Sample points mapped into the simulated domain across the reflective
    planes through ``center``: s -> c + |s - c| on each reflected axis."""
    pts = [np.asarray(sx, dtype=float), np.asarray(sy, dtype=float), np.asarray(sz, dtype=float)]
    c = np.asarray(center, dtype=float)
    for i in reflect_axes(reflect):
        pts[i] = c[i] + np.abs(pts[i] - c[i])
    return pts[0], pts[1], pts[2]
