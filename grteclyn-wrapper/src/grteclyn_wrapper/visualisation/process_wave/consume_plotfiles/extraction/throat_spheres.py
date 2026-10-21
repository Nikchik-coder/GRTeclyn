"""The throat's areal radius per plotfile, from coordinate spheres about the centre.

Why (2026-10-17): the evolution's throat_geometry.dat takes the minimum circumference along
two rays from r = 0.6.  On the fast-recipe holds the min_chi 1e-4 floor makes the circumference
fall towards the centre inside a core that reaches r = 0.6 (the 0.99c from t = 0, the 0.9c from
t ~ 45), so that minimum is the core, not the throat; the spectral MOTS finder in turn loses the
throat once it deforms past lmax 6 or stops being marginally trapped.  This measure needs
neither: for each coordinate sphere r it integrates the area A(r) of the full 3-metric
gamma_ij = h_ij / chi, and the throat is the OUTERMOST local minimum of R(r) = sqrt(A / 4 pi),
i.e. the one outside the floored core.  Checked by hand the same day on the live 0.7c
(6.86-6.89 at t = 127 against the MOTS 6.873 at t = 0) and 0.99c (182.4 against 181.8).

One row per plotfile to throat_spheres.dat.  The spheres are sampled from the inner level's
covering grid while they fit in it, from the outer level's beyond (the throat drifts outwards in
coordinates on the fast holds); only point values are interpolated, no derivatives.
"""

from __future__ import annotations

import numpy as np

THROAT_SPHERES_HEADER = (
    "# time  r_throat  R_throat  n_minima  R(r=1)  R(r=2)  R(r=4)  R(r=8)  R(r=12)  dx_inner  dx_outer\n"
    "# R(r) = sqrt(A/4 pi), A the area of the coordinate sphere r about the centre in the full metric "
    "h_ij/chi; the throat is the outermost local minimum of R(r) (outside the min_chi-floored core); "
    "n_minima > 1 flags more structure; nan: no minimum inside the sampled radii"
)
_NAMES = ("chi", "h11", "h12", "h13", "h22", "h23", "h33")


def _grid(ds, lev: int, centre: np.ndarray, half: float):
    """The level's covering grid of the metric on +-half about the centre, half cut to the level's cover."""
    lev = int(min(lev, ds.index.max_level))
    grids = [g for g in ds.index.grids if g.Level == lev]
    lo = np.min([g.LeftEdge.d for g in grids], axis=0)
    hi = np.max([g.RightEdge.d for g in grids], axis=0)
    dx = float(grids[0].dds.d[0])
    half = float(min(half, np.min(centre - lo), np.min(hi - centre)) - dx)
    n = int(np.floor(2 * half / dx))
    half = 0.5 * n * dx
    cg = ds.covering_grid(lev, left_edge=centre - half, dims=[n] * 3)
    return {k: np.asarray(cg[("boxlib", k)], dtype=np.float64) for k in _NAMES}, dx, half


def _sphere_R(F: dict, dx: float, half: float, centre: np.ndarray, r: float, TH, PH, w) -> float:
    from scipy.ndimage import map_coordinates

    n = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
    idx = ((r * n).reshape(3, -1) + half) / dx - 0.5            # grid index of each point
    val = {k: map_coordinates(F[k], idx, order=1, mode="nearest") for k in _NAMES}
    g = {k: val[k] / val["chi"] for k in _NAMES[1:]}
    G = np.array([[g["h11"], g["h12"], g["h13"]], [g["h12"], g["h22"], g["h23"]], [g["h13"], g["h23"], g["h33"]]])
    et = (r * np.stack([np.cos(TH) * np.cos(PH), np.cos(TH) * np.sin(PH), -np.sin(TH)])).reshape(3, -1)
    ep = (r * np.stack([-np.sin(TH) * np.sin(PH), np.sin(TH) * np.cos(PH), np.zeros_like(TH)])).reshape(3, -1)
    qtt = np.einsum("im,ijm,jm->m", et, G, et)
    qpp = np.einsum("im,ijm,jm->m", ep, G, ep)
    qtp = np.einsum("im,ijm,jm->m", et, G, ep)
    dA = np.sqrt(np.maximum(qtt * qpp - qtp ** 2, 0.0)).reshape(TH.shape) / np.sin(TH)
    A = float(np.sum(dA * w[:, None]) * (2 * np.pi / TH.shape[1]))
    return float(np.sqrt(A / (4 * np.pi)))


def throat_spheres_row(ds, t: float, *, center, rmin: float = 0.3, level_inner: int = 2,
                       half_inner: float = 9.0, level_outer: int = 1, half_outer: float = 16.0) -> str:
    centre = np.asarray(center, dtype=float)
    Fi, dxi, hi = _grid(ds, level_inner, centre, half_inner)
    Fo, dxo, ho = _grid(ds, level_outer, centre, half_outer)
    x, w = np.polynomial.legendre.leggauss(32)
    TH, PH = np.meshgrid(np.arccos(-x), np.linspace(0, 2 * np.pi, 64, endpoint=False), indexing="ij")
    r_in = np.arange(rmin, hi - 2 * dxi, 0.5 * dxi)
    r_out = np.arange(r_in[-1] + 0.5 * dxo, ho - 2 * dxo, 0.5 * dxo) if ho - 2 * dxo > r_in[-1] else np.array([])
    rs = np.concatenate([r_in, r_out])
    R = np.array([_sphere_R(Fi, dxi, hi, centre, r, TH, PH, w) for r in r_in]
                 + [_sphere_R(Fo, dxo, ho, centre, r, TH, PH, w) for r in r_out])
    k_min = [k for k in range(1, len(R) - 1) if R[k] < R[k - 1] and R[k] <= R[k + 1]]
    r_th, R_th = (float(rs[k_min[-1]]), float(R[k_min[-1]])) if k_min else (float("nan"), float("nan"))
    at = [float(np.interp(v, rs, R)) if rs[0] <= v <= rs[-1] else float("nan") for v in (1.0, 2.0, 4.0, 8.0, 12.0)]
    return (f"{t:.16e}  {r_th:.6f}  {R_th:.10e}  {len(k_min)}  " + "  ".join(f"{v:.8e}" for v in at)
            + f"  {dxi:.6g}  {dxo:.6g}")
