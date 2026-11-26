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

Frames are different: a mirrored frame can carry the sign, so they use
``field_parity`` -- the parity the code itself gives each variable for its
reflective ghost cells -- and mirror odd fields with a sign flip instead of
dropping them (frames/mirror.py).
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

_X, _Y, _Z = (-1, 1, 1), (1, -1, 1), (1, 1, -1)
_XY, _XZ, _YZ, _XYZ = (-1, -1, 1), (-1, 1, -1), (1, -1, -1), (-1, -1, -1)

#: Sign of each field under reflection across the x = c, y = c and z = c planes
#: (+1 even, -1 odd).  Copied from the code's own ghost-cell parities, so a
#: mirrored frame is what the run itself assumes across the plane:
#: Source/CCZ4/CCZ4StateVariables.hpp (``parities``) and
#: Source/ParticleInterpolator/WeylExtraction.hpp ({even, odd_xyz} for
#: Weyl4 Re/Im).  Fields not named here are scalars or diagonal components:
#: even.  Derived frame fields (fields.py) take the parity of their formula.
FIELD_PARITY: dict[str, tuple[int, int, int]] = {
    "h12": _XY, "h13": _XZ, "h23": _YZ,
    "A12": _XY, "A13": _XZ, "A23": _YZ,
    "Gamma1": _X, "Gamma2": _Y, "Gamma3": _Z,
    "shift1": _X, "shift2": _Y, "shift3": _Z,
    "B1": _X, "B2": _Y, "B3": _Z,
    "Weyl4_Im": _XYZ,
    # Weyl4_Re is even: WeylExtraction.hpp.  Derived: GW_Cross = 2 A12.
    "GW_Cross": _XY,
}


def field_parity(field: str) -> tuple[int, int, int]:
    """(sx, sy, sz): the field's sign under reflection across each axis plane."""
    return FIELD_PARITY.get(field, (1, 1, 1))


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
