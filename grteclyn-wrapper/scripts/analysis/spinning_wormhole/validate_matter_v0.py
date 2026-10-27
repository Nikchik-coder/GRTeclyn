#!/usr/bin/env python
"""Step-1 gate of campaign M: the matter solver at V = 0 reproduces the
saved Kleihaus-Kunz family.

For each saved solution, build a MatterCollocationProblem (the
five-field system f, omega, N, B, psi bordered by psi_minus) at the same
(eta0, gamma, map, grid), prescribe the solution's omega_inf, start
Newton from the saved fields with B = 1 and the closed-form scalar, and
gate on
  - Newton converged (equilibrated |R|_inf <= 1e-11),
  - max |F - F_ref|, |W - W_ref|, |N - N_ref| <= 1e-10,
  - max |B - 1| <= 1e-10,
  - psi_minus against -pi sqrt(D2_ref) / eta0 (1e-9 rel),
  - the unimposed monitors: max |E19| / D2 and max |E_c| <= 1e-8.

The reference (F_ref, W_ref, N_ref, D2_ref) is the member re-converged
by the V = 0 solver (equations.CollocationProblem) on the same grid,
both Newton solves taken to 1e-14.  The saved files stopped at 1e-12,
which leaves their F off by up to 1.5e-9 and their monitors up to 1e-7
on the leg ends (2026-10-27); against the files, a tighter solve fails
for being more converged.  Their differences are printed alongside.

The V = 0 solver solved E_f, E_w with N and D2 from the constraint
sector; here all five elliptic rows are imposed and the constraints stay
free, so agreement is a genuine cross-check of the new formulation, not
a round trip.

--decoupled serves the two largest grids (144 x 30, 162 x 42), whose
five-field Jacobian does not fit: at cal V = 0, B = 1 the system is
triangular -- E_f, E_w hold no N, B or psi (they are the V = 0 solver's
rows, derive_matter_equations.py v0forms), B = 1 solves E_B, E_psi is
linear in psi, the bordering row holds no N (eta = 0, y = -1 at its node)
and E_Nr is linear in N -- so (F, W) from the reference, psi from one
solve, psi_minus from the bordering row and N from one solve, both
solves with matter_equations.row_matrix, are the five-field solution.
Its full five-field residual is gated (raw, masked), not assumed.

Run on the cluster node (the workstation venv has no JAX), capped:

    grteclyn-wrapper/scripts/ops/capped_job.sh start validate-v0 \
        --threads 4 --mem 16 --timeout 3600 -- \
        grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/validate_matter_v0.py \
        results/spinningwormhole/solutions/<dir>/<file>.json [...]
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
from grteclyn_wrapper.analysis.spinning_wormhole.matter_equations import (
    MatterCollocationProblem,
    matter_residual_forms,
    row_matrix,
)
from grteclyn_wrapper.analysis.spinning_wormhole.newton import newton
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution

GATES = {"fields": 1e-10, "B": 1e-10, "psi_minus": 1e-9, "monitors": 1e-8,
         "newton": 1e-11}

# Both Newton solves stop here; the gate above is what they must reach.
TOL = 1e-14

# The far-zone mask of observables._interior: E19's terms scale as
# h x (fields decaying as 1/h), so float noise in the tail nodes is
# amplified by h (~1e14 at the log-stretch ends) -- the same roundoff
# floor check_einstein.py documents.  Monitors are gated inside
# C^2 = eta0^2 / h >= C_GATE^2 and reported raw on the full grid.
C_GATE = 0.05


def reference(sol, nx, ny, F0, W0):
    """The member re-converged by the V = 0 solver on this grid: (F, W)
    by Newton to TOL from (F0, W0), then N and D2 from the constraints."""
    po = CollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("omega_inf", sol.omega_inf))
    u, info = newton(po.residual, po.jacobian,
                     po.pack(F0 - po.f_bg, W0 - sol.omega_inf * po.q),
                     tol=TOL)
    F, W = (np.asarray(a) for a in po.fields(u))
    N, d2, _ = po.solve_N_constrained(F, W)
    return F, W, N, d2, info["res_scaled_inf"]


def decoupled(prob, F, W, omega_inf):
    """The V = 0 five-field unknown vector assembled block by block from
    (F, W) (module docstring).  psi = psi_minus (pr + q): q cancels the
    discrete E_psi residual of the closed-form profile pr (zero on the
    arctan map, where pr is linear in xi); then psi_minus from the
    bordering row, affine in psi_minus^2; then N from the E_Nr rows."""
    one, zero = np.ones_like(F), np.zeros_like(F)
    geo = {"eta0": prob.eta0, "y": prob.sy, "eta": prob.eta_i,
           "deta": prob.deta_i, "d2eta": prob.d2eta_i, "Dx": prob.Dx,
           "Dy": prob.Dy}

    def forms(N, PSI):
        jets = prob._jets({"f": F, "w": W, "N": N, "B": one, "psi": PSI})
        inner = {k: np.asarray(v)[1:-1] for k, v in jets.items()}
        z = np.zeros_like(inner["psi"])
        return matter_residual_forms(
            np.exp, eta0=prob.eta0, y=prob.sy[None, :], eta=prob.eta_i,
            deta=prob.deta_i, d2eta=prob.d2eta_i, jets=inner, V=z, dV=z)

    def solve(key, field, interior_rows):
        rhs = np.zeros_like(F)
        rhs[1:-1] = -interior_rows
        return np.linalg.solve(row_matrix(key, field, **geo),
                               rhs.ravel()).reshape(F.shape)

    q = solve("E_psi", "psi", forms(zero, prob.psi_prof)["E_psi"])
    prof = prob.psi_prof + q
    node = (prob.mid - 1, -1)
    e0 = forms(zero, zero)["E19"][node]
    e1 = forms(zero, prof)["E19"][node]
    psim = -math.sqrt(-e0 / (e1 - e0))
    N = solve("E_Nr", "N", forms(zero, psim * prof)["E_Nr"])
    return prob.pack(F - prob.f_bg, W - omega_inf * prob.q, N, zero,
                     psim * q, psi_minus=psim)


def validate(path: str, verbose: bool = False,
             decoupled_solve: bool = False, nx: int | None = None,
             ny: int | None = None) -> dict:
    sol = Solution.load(path)
    regrid = nx is not None or ny is not None
    nx = nx if nx is not None else sol.F.shape[0] - 1
    ny = ny if ny is not None else sol.F.shape[1] - 1
    d2 = sol.gates.get("D2_median") if sol.gates else None
    if d2 is None:
        from grteclyn_wrapper.analysis.spinning_wormhole.observables import (
            identity_gates,
        )
        d2 = identity_gates(sol)["D2_median"]
    d2 = float(d2)
    psi_minus0 = -math.pi * math.sqrt(d2) / sol.eta0

    t0 = time.time()
    prob = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("omega_inf", sol.omega_inf))
    if regrid:
        # Resolution study: the saved member interpolated spectrally to
        # the new grid; the reference is re-converged there.
        F0 = sol.eval_grid("f", prob.sx, prob.sy)
        W0 = sol.eval_grid("w", prob.sx, prob.sy)
        N0 = sol.eval_grid("N", prob.sx, prob.sy)
    else:
        F0, W0, N0 = sol.F, sol.W, sol.N
    zero = np.zeros_like(F0)
    u0 = prob.pack(F0 - prob.f_bg, W0 - sol.omega_inf * prob.q,
                   N0, zero, zero, psi_minus=psi_minus0)
    mask = (sol.eta0**2 / prob.h_i[:, 0]) >= C_GATE**2
    F_ref, W_ref, N_ref, d2_ref, ref_res = reference(sol, nx, ny, F0, W0)
    if decoupled_solve:
        # Raw five-field residual inside the mask (the E rows there carry
        # O(h <= eta0^2/C_GATE^2) operator scales) and the bordering row.
        u = decoupled(prob, F_ref, W_ref, sol.omega_inf)
        r = np.asarray(prob.residual(u))
        blocks = r[: 5 * prob.n].reshape(5, nx + 1, ny + 1)
        res = max(float(np.max(np.abs(blocks[:, 1:-1][:, mask, :]))),
                  float(abs(r[-1])))
        info = {"res_scaled_inf": res, "iters": 0}
    else:
        u, info = newton(prob.residual, prob.jacobian, u0, tol=TOL,
                         verbose=verbose)
    F, W, Nf, B, PSI = (np.asarray(a) for a in prob.fields(u))
    psi_minus = prob.unpack(u)[-1]
    psi_minus_ref = -math.pi * math.sqrt(d2_ref) / sol.eta0
    diag = prob.diagnostics(u)
    out = {
        "newton": info["res_scaled_inf"],
        "ref_newton": ref_res,
        "iters": info["iters"],
        "dF": float(np.max(np.abs(F - F_ref))),
        "dW": float(np.max(np.abs(W - W_ref))),
        "dN": float(np.max(np.abs(Nf - N_ref))),
        "dB": float(np.max(np.abs(B - 1.0))),
        "dpsim": abs(psi_minus - psi_minus_ref) / abs(psi_minus_ref),
        "saved_dF": float(np.max(np.abs(F - F0))),
        "saved_dN": float(np.max(np.abs(Nf - N0))),
        "E19": float(np.max(np.abs(diag["E19"][mask]))) / d2_ref,
        "E19_full": float(np.max(np.abs(diag["E19"]))) / d2_ref,
        "E_c": float(np.max(np.abs(diag["E_c"][mask]))),
        "E_c_full": float(np.max(np.abs(diag["E_c"]))),
        "seconds": time.time() - t0,
    }
    gate_res = GATES["monitors"] if decoupled_solve else GATES["newton"]
    out["pass"] = (
        out["newton"] <= gate_res and out["ref_newton"] <= GATES["newton"]
        and max(out["dF"], out["dW"], out["dN"]) <= GATES["fields"]
        and out["dB"] <= GATES["B"]
        and out["dpsim"] <= GATES["psi_minus"]
        and max(out["E19"], out["E_c"]) <= GATES["monitors"]
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solutions", nargs="+", help=".npz / .json paths")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--decoupled", action="store_true",
                    help="no five-field Jacobian: the V = 0 system solved "
                    "block by block, its raw masked residual gated (the "
                    "two largest grids)")
    ap.add_argument("--nx", type=int, help="resolution study: re-solve at "
                    "this grid from the spectrally interpolated member")
    ap.add_argument("--ny", type=int)
    args = ap.parse_args()
    failed = []
    for path in args.solutions:
        r = validate(path, verbose=args.verbose,
                     decoupled_solve=args.decoupled,
                     nx=args.nx, ny=args.ny)
        name = path.rsplit("/", 1)[-1]
        solve = ("res" if args.decoupled else "newton")
        how = ("decoupled" if args.decoupled else f"{r['iters']} it")
        head = (f"{solve} {r['newton']:.1e} ({how}, "
                f"ref {r['ref_newton']:.1e})  dF {r['dF']:.1e}  "
                f"dW {r['dW']:.1e}  dN {r['dN']:.1e}  "
                f"dB {r['dB']:.1e}  dpsi- {r['dpsim']:.1e}  "
                f"[saved: dF {r['saved_dF']:.1e} dN {r['saved_dN']:.1e}]")
        print(f"{name}: {head}  "
              f"E19 {r['E19']:.1e} (full {r['E19_full']:.1e})  "
              f"E_c {r['E_c']:.1e} (full {r['E_c_full']:.1e})  "
              f"[{r['seconds']:.0f}s]  "
              f"{'PASS' if r['pass'] else 'FAIL'}", flush=True)
        if not r["pass"]:
            failed.append(name)
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
