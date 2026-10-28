#!/usr/bin/env python
"""Where the V = 0 validation's unimposed E19 comes from, member by member.

Solves the matter system as validate_matter_v0.py does (optionally on
another grid), then re-evaluates the masked monitors with fields reset
to their exact V = 0 values -- B = 1, psi = psi_minus pr(eta) with the
solved psi_minus -- and with the starting N, and prints where the
largest |E19| sits.  It also re-solves the member the old way on the
same grid (Newton on f, omega; then N and D^2 by least squares on the
constraints, equations.CollocationProblem.solve_N_constrained) and
compares the two discrete N.

Reading it: a floor that vanishes once B (or psi) is reset is grid-scale
noise in that field, amplified by the h-weighted second derivatives in
E19 (h (1 - y^2) B_yy, h A2 B_xx); a defect that survives the reset and
shrinks with the grid is truncation of the elliptic N row.

    grteclyn-wrapper/scripts/ops/capped_job.sh start diag-v0 \
        --threads 4 --mem 40 --timeout 3600 -- \
        grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/optimisation/diagnose_matter_v0.py \
        results/spinningwormhole/solutions/<leg>/<member>.json [--nx 96 --ny 24]
"""

from __future__ import annotations

import argparse
import math
import sys
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
    CollocationProblem,
)
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
    matter_residual_forms,
)
from grteclyn_wrapper.optimisation.solver.newton import newton

C_GATE = 0.05


def monitors(prob, mask, d2, F, W, Nf, B, PSI) -> dict:
    """Masked max |E19| / D2, |E_c|, |E_N|, and where |E19| peaks."""
    F, W, Nf, B, PSI = (np.asarray(a) for a in (F, W, Nf, B, PSI))
    jets = prob._jets({"f": F, "w": W, "N": Nf, "B": B, "psi": PSI})
    inner = {k: np.asarray(v)[1:-1] for k, v in jets.items()}
    E = matter_residual_forms(
        np.exp, eta0=prob.eta0, y=prob.sy[None, :], eta=prob.eta_i,
        deta=prob.deta_i, d2eta=prob.d2eta_i, jets=inner,
        V=prob.pot.V(inner["psi"]), dV=prob.pot.dV(inner["psi"]))
    e19 = np.abs(np.asarray(E["E19"]))[mask] / d2
    i, j = np.unravel_index(int(np.argmax(e19)), e19.shape)
    k = int(np.flatnonzero(mask)[i])                 # interior x index
    eta = float(prob.eta_i[k, 0])
    return {
        "E19": float(e19[i, j]),
        "E_c": float(np.max(np.abs(np.asarray(E["E_c"]))[mask])),
        "E_N": float(np.max(np.abs(np.asarray(E["E_N"]))[mask])),
        "xi": float(prob.sx[k + 1]), "y": float(prob.sy[j]),
        "eta": eta / prob.eta0,
        "C": prob.eta0 / math.hypot(eta, prob.eta0),
    }


def diagnose(path: str, nx: int | None = None, ny: int | None = None,
             old: bool = True) -> None:
    sol = Solution.load(path)
    regrid = nx is not None or ny is not None
    nx = nx if nx is not None else sol.nx
    ny = ny if ny is not None else sol.ny
    d2 = float(sol.gates["D2_median"])
    psim0 = -math.pi * math.sqrt(d2) / sol.eta0

    prob = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("omega_inf", sol.omega_inf))
    if regrid:
        F0, W0, N0 = (sol.eval_grid(t, prob.sx, prob.sy)
                      for t in ("f", "w", "N"))
    else:
        F0, W0, N0 = sol.F, sol.W, sol.N
    zero = np.zeros_like(F0)
    u0 = prob.pack(F0 - prob.f_bg, W0 - sol.omega_inf * prob.q, N0,
                   zero, zero, psi_minus=psim0)
    t0 = time.time()
    u, info = newton(prob.residual, prob.jacobian, u0, tol=1e-12)
    F, W, Nf, B, PSI = (np.asarray(a) for a in prob.fields(u))
    psim = float(prob.unpack(u)[-1])
    ones = np.ones_like(F)
    psi_exact = psim * prob.psi_prof
    mask = (sol.eta0**2 / prob.h_i[:, 0]) >= C_GATE**2

    name = path.rsplit("/", 1)[-1]
    print(f"== {name} at {nx}x{ny}: newton {info['res_scaled_inf']:.1e} "
          f"({info['iters']} it, {time.time() - t0:.0f}s)")
    print(f"   max|B - 1| {np.max(np.abs(B - 1.0)):.1e}  "
          f"max|psi - exact| {np.max(np.abs(PSI - psi_exact)):.1e}  "
          f"max|N - N0| {np.max(np.abs(Nf - N0)):.1e}  "
          f"max|Dxx 1| {np.max(np.abs(prob.Dxx @ ones)):.1e}  "
          f"max|Dyy 1| {np.max(np.abs(ones @ prob.Dyy.T)):.1e}", flush=True)

    rows = [
        ("solved", (F, W, Nf, B, PSI)),
        ("B = 1", (F, W, Nf, ones, PSI)),
        ("psi exact", (F, W, Nf, B, psi_exact)),
        ("B = 1, psi exact", (F, W, Nf, ones, psi_exact)),
        ("B = 1, psi exact, start N", (F, W, N0, ones, psi_exact)),
        ("start (saved fields)", (F0, W0, N0, ones, psim0 * prob.psi_prof)),
    ]
    if old:
        po = CollocationProblem(
            eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
            nx=nx, ny=ny, prescribe=("omega_inf", sol.omega_inf))
        uo, io = newton(po.residual, po.jacobian,
                        po.pack(F0 - po.f_bg, W0 - sol.omega_inf * po.q),
                        tol=1e-12)
        Fo, Wo = (np.asarray(a) for a in po.fields(uo))
        No, d2o, _ = po.solve_N_constrained(Fo, Wo)
        print(f"   old solver here: newton {io['res_scaled_inf']:.1e} "
              f"({io['iters']} it)  max|F_old - F| {np.max(np.abs(Fo - F)):.1e}  "
              f"max|W_old - W| {np.max(np.abs(Wo - W)):.1e}  "
              f"max|N_old - N| {np.max(np.abs(No - Nf)):.1e}  "
              f"D2 rel {abs(d2o - d2) / d2:.1e}", flush=True)
        rows.append(("old solver (N by LS)",
                     (Fo, Wo, No, ones,
                      -math.pi * math.sqrt(d2o) / sol.eta0 * prob.psi_prof)))

    for label, flds in rows:
        m = monitors(prob, mask, d2, *flds)
        print(f"   {label:<27} E19 {m['E19']:.1e}  E_c {m['E_c']:.1e}  "
              f"E_N {m['E_N']:.1e}   E19 peak: xi {m['xi']:+.3f} "
              f"y {m['y']:+.3f} eta/eta0 {m['eta']:+.2f} C {m['C']:.3f}",
              flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solutions", nargs="+", help=".npz / .json paths")
    ap.add_argument("--nx", type=int)
    ap.add_argument("--ny", type=int)
    ap.add_argument("--no-old", action="store_true",
                    help="skip the old-solver re-solve on the same grid")
    args = ap.parse_args()
    for path in args.solutions:
        diagnose(path, nx=args.nx, ny=args.ny, old=not args.no_old)
    return 0


if __name__ == "__main__":
    sys.exit(main())
