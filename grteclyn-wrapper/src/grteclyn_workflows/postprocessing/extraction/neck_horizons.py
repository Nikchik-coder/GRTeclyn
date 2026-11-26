"""The throat's neck and the two trapping horizons around it, per plotfile.

Along the +x ray from ``--center``: the areal radius with the full conformal
metric, R = r (h22 h33)^(1/4) / sqrt(chi) (as ``areal.py --areal-full-metric``),
its proper radial derivative dR/dl = (dR/dx) / sqrt(h11/chi), the tangential
extrinsic curvature K_q = K - K^x_x with K^x_x = (A11 + h11 K/3)/h11, and the
null expansions of the spheres

    theta_l = 2 (dR/dl)/R - K_q,    theta_k = -2 (dR/dl)/R - K_q,

and the Misner-Sharp mass M = (R/2) (1 - (dR/dl)^2 + (R K_q / 2)^2).

The NECK is the minimum of R on the slice, TRACKED from the previous plotfile
(``x_prev``): the interior local minimum nearest it.  At t = 0 it is the
global minimum beyond ``X_IN``.  A fixed cut misses the early neck (x = 1.59
on the L = 512 throat at t = 0), and a global minimum falls into the
compactified other end once its chi plateau forms (R = r/sqrt(chi) -> 0 as
r -> 0 there).  Inside an inflating throat both expansions are positive at
the neck; the theta_l = 0 sphere nearest the neck on the inner side (the other
universe's horizon, "hl") and the theta_k = 0 sphere nearest it on the outer
side (ours, "hk") bound that anti-trapped region -- the cosmological horizons
of Shinkai & Hayward's inflating throat.  Each search reaches one sample past
the neck, so a horizon within a cell of it is found; a static throat (K = 0)
reports both AT the neck, its degenerate double trapping horizon.  NaN while
an expansion does not change sign on the ray.  Replaces the hand-started sidecar
``watch.py`` of 2026-09-25 (same formulae), so the record starts and stops
with the run and sees every plotfile before it is deleted.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from ..fields import _field_type_for

NECK_HORIZONS_HEADER = (
    "# time  x_neck  R_neck  R_neck_flat  h22_neck  alpha_neck  rate_neck  M_MS_neck  phi_neck  "
    "x_hl  R_hl  alpha_hl  M_hl  x_hk  R_hk  alpha_hk  M_hk"
)
#: Inside this the ray is the compactified other end's fiction at any time.
X_IN = 0.3
#: The outer-horizon search stops here.
X_OUT = 200.0
_FIELDS = ("chi", "K", "lapse", "h11", "h22", "h33", "A11", "phi")


def _find_neck(x: np.ndarray, R: np.ndarray, x_prev: float | None) -> int:
    idx = np.flatnonzero(x > X_IN)
    if x_prev is None or not np.isfinite(x_prev) or x_prev <= 0:
        return int(idx[np.argmin(R[idx])])
    i = idx[1:-1]
    lm = i[(R[i] <= R[i - 1]) & (R[i] < R[i + 1])]
    if lm.size == 0:
        return int(idx[np.argmin(R[idx])])
    near = lm[(x[lm] > x_prev / 1.5) & (x[lm] < x_prev * 1.5)]
    if near.size:
        return int(near[np.argmin(R[near])])
    return int(lm[np.argmin(np.abs(np.log(x[lm] / x_prev)))])


def _crossing(x, f, lo, hi, x0, cols):
    """Zero of f in (lo, hi) nearest x0: (x, *cols interpolated) or NaNs."""
    m = np.flatnonzero((x > lo) & (x < hi) & np.isfinite(f))
    best = None
    for a, b in zip(m[:-1], m[1:]):
        if b == a + 1 and np.sign(f[a]) != np.sign(f[b]):
            w = f[a] / (f[a] - f[b])
            xc = x[a] + w * (x[b] - x[a])
            if best is None or abs(xc - x0) < abs(best[0] - x0):
                best = (xc, a, b, w)
    if best is None:
        return (np.nan,) * (1 + len(cols))
    xc, a, b, w = best
    return (xc, *[c[a] + w * (c[b] - c[a]) for c in cols])


def neck_horizons_row(ds, center: Sequence[float], x_prev: float | None) -> tuple[tuple, float]:
    """(row matching NECK_HORIZONS_HEADER, x_neck) for one plotfile."""
    ftype = _field_type_for(ds, "chi")
    lacking = [f for f in _FIELDS if (ftype, f) not in ds.field_list]
    if lacking:
        raise KeyError(f"--neck-horizons needs {', '.join(lacking)} in the plotfile (amr.plot_vars)")
    c = np.asarray(center, dtype=float)
    ray = ds.ray(c, [float(ds.domain_right_edge[0]), c[1], c[2]])
    dxs = np.asarray(ray[("index", "x")], dtype=float) - c[0]
    dys = np.asarray(ray[("index", "y")], dtype=float) - c[1]
    dzs = np.asarray(ray[("index", "z")], dtype=float) - c[2]
    o = np.argsort(dxs)
    x = dxs[o]
    # the true distance of each sampled cell centre, as areal.py uses it
    r = np.sqrt(dxs**2 + dys**2 + dzs**2)[o]
    f = {k: np.asarray(ray[(ftype, k)], dtype=float)[o] for k in _FIELDS}
    chi = np.maximum(f["chi"], 1.0e-12)
    R = r * np.sqrt(np.sqrt(f["h22"] * f["h33"]) / chi)
    Rflat = r / np.sqrt(chi)
    dRdl = np.gradient(R, x) / np.sqrt(f["h11"] / chi)
    Kq = f["K"] - (f["A11"] + f["h11"] * f["K"] / 3.0) / f["h11"]
    th_l = 2.0 * dRdl / R - Kq
    th_k = -2.0 * dRdl / R - Kq
    M = 0.5 * R * (1.0 - dRdl**2 + (0.5 * R * Kq) ** 2)

    j = _find_neck(x, R, x_prev)
    band = np.flatnonzero((x > x[j] / 1.5) & (x < x[j] * 1.5))
    jf = int(band[np.argmin(Rflat[band])]) if band.size else j
    inner = np.flatnonzero((x > X_IN) & (x < x[j]))
    x_in = float(x[inner[np.argmax(R[inner])]]) if inner.size else X_IN
    cols = (R, f["lapse"], M)
    # Each search reaches one sample past the neck: a horizon within a cell of
    # it (the thin early region; a static throat's degenerate double horizon,
    # which IS the neck) lies between the neck sample and a neighbour.
    eps = 1.0e-9 * max(1.0, abs(float(x[j])))
    hl = _crossing(x, th_l, x_in, x[min(j + 1, len(x) - 1)] + eps, x[j], cols)
    hk = _crossing(x, th_k, x[max(j - 1, 0)] - eps, X_OUT, x[j], cols)
    row = (float(ds.current_time), x[j], R[j], Rflat[jf], f["h22"][j], f["lapse"][j],
           -0.5 * Kq[j], M[j], f["phi"][j], *hl, *hk)
    return row, float(x[j])


def neck_horizons_line(row: tuple) -> str:
    return "  ".join(f"{float(v):.10e}" for v in row)
