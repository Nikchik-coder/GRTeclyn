from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np


def _extract_areal_radius_min(
    ds,
    center: Sequence[float] = (0.0, 0.0, 0.0),
    chi_floor: float = 1.0e-8,
    min_radius: float = 0.0,
) -> Tuple[float, float]:
    """Extract the minimum areal radius R_areal = r / sqrt(chi) along the x-axis.

    Returns (R_areal_min, r_at_min).

    ``min_radius`` excludes an inner ball from the search, and for wormhole
    initial data it is not optional.  An Ellis-Bronnikov throat is compactified
    at r = 0: chi vanishes there like r^4 because r = 0 is the *other*
    universe's spatial infinity squeezed to a point, so analytically R = r /
    sqrt(chi) ~ 1/r *diverges* as r -> 0 and the throat is the interior minimum
    at r = b/2.  Numerically the innermost cells cannot resolve chi ~ r^4, chi
    fills in orders of magnitude above its analytic value, and the argmin jumps
    off the throat and onto the innermost sample -- which then reports a
    steadily shrinking "throat" and reads as a collapse that is not happening.
    Measured on a b = 0.5 throat at t = 1.2: this returns 0.152 at r = 0.0156
    with min_radius = 0, and 0.498 at r = 0.297 -- the real throat, holding at
    its initial value -- once the inner ball is excluded.  Default 0.0 keeps
    the previous behaviour for callers that are not looking at a throat.
    """
    right = float(ds.domain_right_edge[0])
    c = np.asarray(center, dtype=float)
    ray = ds.ray(c, [right, c[1], c[2]])

    r_arr = np.asarray(ray[("index", "x")], dtype=float) - c[0]
    chi_arr = np.asarray(ray[("boxlib", "chi")], dtype=float)

    order = np.argsort(r_arr)
    r_arr = r_arr[order]
    chi_arr = chi_arr[order]

    chi_arr = np.maximum(chi_arr, chi_floor)
    R_areal = r_arr / np.sqrt(chi_arr)

    skip = r_arr > max(1.0e-12, float(min_radius))
    if not np.any(skip):
        return (0.0, 0.0)
    R_areal_valid = R_areal[skip]
    r_valid = r_arr[skip]
    i_min = np.argmin(R_areal_valid)
    return (float(R_areal_valid[i_min]), float(r_valid[i_min]))
