#!/usr/bin/env python
"""Full-Einstein check of a fast-spin Solution, independent of the solver.

check_slowspin_einstein.py generalized (SpinningSolver.md P2): the Ricci
tensor of the Kleihaus-Kunz ansatz is built symbolically once
(ricci_lambdas, imported from the slow-spin script), then

    E_ab = R_ab + 2 d_a psi d_b psi

is evaluated on a SAVED Solution with exact spectral jets -- the solver
imposed E_f, E_w, E_N, so this tests the whole formulation, discretization
and converged fields at once.  Weights are the slow-spin check's (h^2 for
tt and ee, h for thth, ee against its 2 D^2 / h^2 source), so the far zone
counts.  The gate is max |E_ab| <= 1e-8, or the round-off floor measured
on the static member at the same grid if that is higher (--floor prints
it); the O(J^2) generator sits at ~1e-2 at J = 1 for comparison.

Run (repo root, CPU, ~30 s of sympy at first call):

    (ulimit -v 16777216; grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/check_einstein.py \
        <solution .npz/.json path> [...]
        [--floor NX,NY   static-member floor at that grid]
        [--c-gate 0.05   also print the max away from the ends])
"""

from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_slowspin_einstein import COMPONENTS, ORDERS, ricci_lambdas  # noqa: E402

from grteclyn_wrapper.analysis.spinning_wormhole import conventions as cv  # noqa: E402
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution  # noqa: E402


def jets_from_solution(sol: Solution) -> dict[str, np.ndarray]:
    """(eta, theta) jets of f, nu = N sin^2 theta, omega on the interior
    nodes, from the exact spectral (xi, y) jets."""
    ix = iy = slice(1, -1)
    m = sol.radial_map
    xi = sol.sx[ix]
    ep = m.deta(xi)[:, None]
    epp = m.d2eta(xi)[:, None]
    y = sol.sy[iy][None, :]
    th = 0.5 * np.arccos(np.clip(y, -1.0, 1.0))
    s2t, c2t = np.sin(2.0 * th), y
    s2 = np.sin(th) ** 2
    raw = {}
    for tag in ("f", "w", "N"):
        g = {"00": sol.jet(tag)[ix, iy],
             "x": sol.jet(tag, 1, 0)[ix, iy],
             "xx": sol.jet(tag, 2, 0)[ix, iy],
             "y": sol.jet(tag, 0, 1)[ix, iy],
             "yy": sol.jet(tag, 0, 2)[ix, iy],
             "xy": sol.jet(tag, 1, 1)[ix, iy]}
        raw[tag] = {
            "00": g["00"],
            "10": g["x"] / ep,
            "20": g["xx"] / ep**2 - g["x"] * epp / ep**3,
            "01": -2.0 * s2t * g["y"],
            "02": -4.0 * c2t * g["y"] + 4.0 * s2t**2 * g["yy"],
            "11": -2.0 * s2t * g["xy"] / ep,
        }
    n = raw["N"]
    jets = {}
    for ij in ("00", "10", "20", "01", "02", "11"):
        jets[f"f_{ij}"] = raw["f"][ij]
        jets[f"w_{ij}"] = raw["w"][ij]
    jets["nu_00"] = n["00"] * s2
    jets["nu_10"] = n["10"] * s2
    jets["nu_20"] = n["20"] * s2
    jets["nu_01"] = n["01"] * s2 + n["00"] * s2t
    jets["nu_02"] = n["02"] * s2 + 2.0 * n["01"] * s2t + 2.0 * n["00"] * c2t
    jets["nu_11"] = n["11"] * s2 + n["10"] * s2t
    return jets


def einstein_residuals(ricci, names, sol: Solution, d2: float,
                       c_gate: float = 0.05) -> dict:
    """Weighted max |E_ab| per component, full grid and away from the ends."""
    jets = jets_from_solution(sol)
    ix = iy = slice(1, -1)
    m = sol.radial_map
    eta = m.eta(sol.sx[ix])[:, None]
    y = sol.sy[iy][None, :]
    th = 0.5 * np.arccos(np.clip(y, -1.0, 1.0))
    h = eta**2 + sol.eta0**2
    ETA = np.broadcast_to(eta, jets["f_00"].shape)
    TH = np.broadcast_to(th, jets["f_00"].shape)
    args = [ETA, TH, sol.eta0] + [jets[nm] for nm in names]
    mask = (sol.eta0**2 / h >= c_gate**2) * np.ones_like(TH, bool)
    out = {}
    for (b, c), fn in ricci.items():
        E = np.asarray(fn(*args)) * np.ones_like(h)
        if (b, c) == (1, 1):
            E = (E + 2.0 * d2 / h**2) * h**2 / (2.0 * d2)
        elif (b, c) == (0, 0):
            E = E * h**2 / sol.eta0**2
        elif (b, c) == (2, 2):
            E = E * h / sol.eta0**2
        out[COMPONENTS[(b, c)]] = (float(np.max(np.abs(E))),
                                   float(np.max(np.abs(E[mask]))))
    return out


def static_solution(eta0: float, gamma: float, nx: int, ny: int) -> Solution:
    from grteclyn_wrapper.analysis.spinning_wormhole import spectral

    sx, _ = spectral.lobatto(nx)
    f = cv.static_f_of_x(sx, gamma)[:, None] * np.ones((1, ny + 1))
    z = np.zeros_like(f)
    return Solution(eta0=eta0, gamma=gamma, omega_inf=0.0,
                    map_name="arctan", map_params={}, F=f, W=z.copy(),
                    N=z.copy())


def report(ricci, names, sol: Solution, label: str, d2: float,
           c_gate: float) -> float:
    res = einstein_residuals(ricci, names, sol, d2, c_gate)
    full = max(v[0] for v in res.values())
    masked = max(v[1] for v in res.values())
    parts = "  ".join(f"{k} {v[0]:.2e}" for k, v in res.items())
    print(f"{label}: {parts}")
    print(f"{label}: max {full:.3e} (full grid), {masked:.3e} "
          f"(C >= {c_gate})", flush=True)
    return full


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solutions", nargs="*", help=".npz (or .json) paths")
    ap.add_argument("--floor", metavar="NX,NY",
                    help="print the static member's round-off floor at this "
                    "grid (eta0 2, gamma -pi)")
    ap.add_argument("--c-gate", type=float, default=0.05)
    args = ap.parse_args()
    ricci, names = ricci_lambdas()
    if args.floor:
        nx, ny = (int(v) for v in args.floor.split(","))
        sol = static_solution(2.0, -math.pi, nx, ny)
        d2 = 4.0 + cv.mass_of_gamma(-math.pi, 2.0) ** 2
        report(ricci, names, sol, f"static floor {nx}x{ny}", d2, args.c_gate)
    for path in args.solutions:
        sol = Solution.load(path)
        d2 = sol.gates.get("D2_median")
        if d2 is None:
            from grteclyn_wrapper.analysis.spinning_wormhole.observables import (
                identity_gates,
            )
            d2 = identity_gates(sol)["D2_median"]
        report(ricci, names, sol, os.path.basename(path), float(d2),
               args.c_gate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
