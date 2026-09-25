from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np


def _extract_areal_radius_min(
    ds,
    center: Sequence[float] = (0.0, 0.0, 0.0),
    chi_floor: float = 1.0e-8,
    min_radius: float = 0.0,
    full_metric: bool = False,
) -> Tuple[float, float]:
    """Extract the minimum areal radius along the x-axis.

    Default: R_areal = r / sqrt(chi), the flat-conformal-metric estimate every
    areal_radius.dat of the campaign carries.  It is exact at t = 0 (h_ij =
    delta_ij) and wrong once the Gamma-driver shift has moved the grid: h_ij
    goes anisotropic (det h = 1, so h22 = h33 > 1 where h11 < 1) and
    r / sqrt(chi) under-reads the sphere.  At the F1b arm's neck at t = 90 it
    read 10.08 for a true 12.17 (h22 = 1.45) and hid 40 % of the growth rate;
    the t500 arm's record (single_pureq_q1e2_L128_ml4_scalar_t500) carries the
    same bias at late times.

    ``full_metric`` (the consumer's ``--areal-full-metric``, opt-in since
    2026-09-25): R_areal = r (h22 h33)^(1/4) / sqrt(chi).  The coordinate
    sphere through (r, 0, 0) has the transverse metric gamma_yy = h22/chi,
    gamma_zz = h33/chi, so its area is 4 pi r^2 sqrt(gamma_yy gamma_zz).  Needs
    h22 and h33 in the plotfile and raises if either is missing -- never a
    silent fall-back to the flat estimate (the launch preflight refuses that
    combination before anything starts).

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

    # The radius must be the true |x - center|, not the x-offset alone.  When the
    # run center falls on a cell corner -- which it does for any centred box whose
    # center is L/2 with an even cell count -- the ray runs along a cell edge and
    # every cell it picks up is offset in y and z by half a cell.  Ignoring that
    # offset understates r by 70% at the innermost sample (0.25 instead of 0.433
    # at dx = 0.5), which is exactly where the throat is.
    dx_arr = np.asarray(ray[("index", "x")], dtype=float) - c[0]
    dy_arr = np.asarray(ray[("index", "y")], dtype=float) - c[1]
    dz_arr = np.asarray(ray[("index", "z")], dtype=float) - c[2]
    r_arr = np.sqrt(dx_arr**2 + dy_arr**2 + dz_arr**2)
    chi_arr = np.asarray(ray[("boxlib", "chi")], dtype=float)
    if full_metric:
        lacking = [f for f in ("h22", "h33") if ("boxlib", f) not in ds.field_list]
        if lacking:
            raise KeyError(f"--areal-full-metric needs {', '.join(lacking)} in the plotfile "
                           "(amr.plot_vars); no flat-metric fall-back")
        hT = np.sqrt(np.asarray(ray[("boxlib", "h22")], dtype=float)
                     * np.asarray(ray[("boxlib", "h33")], dtype=float))
    else:
        hT = np.ones_like(chi_arr)

    order = np.argsort(r_arr)
    r_arr = r_arr[order]
    chi_arr = chi_arr[order]
    hT = np.maximum(hT[order], 1.0e-12)

    chi_arr = np.maximum(chi_arr, chi_floor)
    R_areal = r_arr * np.sqrt(hT / chi_arr)

    skip = r_arr > max(1.0e-12, float(min_radius))
    if not np.any(skip):
        return (0.0, 0.0)
    R_areal_valid = R_areal[skip]
    r_valid = r_arr[skip]
    i_min = np.argmin(R_areal_valid)
    return (float(R_areal_valid[i_min]), float(r_valid[i_min]))
