"""Verify that the matter equations reproduce the massless reference solver.

Input: saved spinning-wormhole members; output: comparisons and PASS/FAIL.
Both formulations are re-converged on the same grid. Checks cover Newton's
residual, metric/scalar fields, optional J pin, exoticity X = |VIQ|/R_e,
and unused Einstein constraints E19/D^2 and E_c. The decoupled option exploits
the triangular V = 0 system and still checks its full five-field residual.
This is an independent formulation check, not just a saved-file round trip.

    python -m grteclyn_wrapper.optimisation.checks.validate_matter_v0 --help
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
from grteclyn_wrapper.analysis.spinning_wormhole.observables import (
    exotic_matter,
)
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.optimisation.exoticity import exotic_x
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
    matter_residual_forms,
    row_matrix,
)
from grteclyn_wrapper.optimisation.solver.newton import newton

GATES = {"fields": 1e-10, "B": 1e-10, "psi_minus": 1e-9, "monitors": 1e-8,
         "newton": 1e-11}

# Both Newton solves stop here; the gate above is what they must reach.
TOL = 1e-14

# --prescribe-j: the start's rotation is off by this much (relative), and
# omega_inf must come back to GATES["omega_inf"].
OMEGA_KICK = 1e-3
GATES["omega_inf"] = 1e-10
GATES["bill"] = 1e-7

# The far-zone mask of observables._interior: E19's terms scale as
# h x (fields decaying as 1/h), so float noise in the tail nodes is
# amplified by h (~1e14 at the log-stretch ends) -- the same roundoff
# floor check_einstein.py documents.  Monitors are gated inside
# C^2 = eta0^2 / h >= C_GATE^2 and reported raw on the full grid.
C_GATE = 0.05


def reference(sol, nx, ny, F0, W0, prescribe, omega0):
    """The member re-converged by the V = 0 solver on this grid: (F, W)
    and omega_inf by Newton to TOL from (F0, W0, omega0), then N and D2
    from the constraints."""
    po = CollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=prescribe)
    u, info = newton(po.residual, po.jacobian,
                     po.pack(F0 - po.f_bg, W0 - omega0 * po.q,
                             omega_inf=omega0),
                     tol=TOL)
    F, W = (np.asarray(a) for a in po.fields(u))
    N, d2, _ = po.solve_N_constrained(F, W)
    return F, W, N, d2, po.unpack(u)[2], info["res_scaled_inf"]


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
                     psim * q, omega_inf=omega_inf, psi_minus=psim)


def validate(path: str, verbose: bool = False,
             decoupled_solve: bool = False, nx: int | None = None,
             ny: int | None = None, prescribe_j: bool = False) -> dict:
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

    if prescribe_j:
        prescribe = ("J", float(sol.meta["prescribed"]["J"]))
        omega0 = sol.omega_inf * (1.0 + OMEGA_KICK)
    else:
        prescribe = ("omega_inf", sol.omega_inf)
        omega0 = sol.omega_inf

    t0 = time.time()
    prob = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=prescribe)
    if regrid:
        # Resolution study: the saved member interpolated spectrally to
        # the new grid; the reference is re-converged there.
        F0 = sol.eval_grid("f", prob.sx, prob.sy)
        W0 = sol.eval_grid("w", prob.sx, prob.sy)
        N0 = sol.eval_grid("N", prob.sx, prob.sy)
    else:
        F0, W0, N0 = sol.F, sol.W, sol.N
    zero = np.zeros_like(F0)
    W_start = W0 * (omega0 / sol.omega_inf)
    u0 = prob.pack(F0 - prob.f_bg, W_start - omega0 * prob.q,
                   N0, zero, zero, omega_inf=omega0, psi_minus=psi_minus0)
    mask = (sol.eta0**2 / prob.h_i[:, 0]) >= C_GATE**2
    F_ref, W_ref, N_ref, d2_ref, omega_ref, ref_res = reference(
        sol, nx, ny, F0, W_start, prescribe, omega0)
    if decoupled_solve:
        # Raw five-field residual inside the mask (the E rows there carry
        # O(h <= eta0^2/C_GATE^2) operator scales), the bordering row and,
        # with --prescribe-j, the flux row.
        u = decoupled(prob, F_ref, W_ref, omega_ref)
        r = np.asarray(prob.residual(u))
        blocks = r[: 5 * prob.n].reshape(5, nx + 1, ny + 1)
        tail = np.abs(r[5 * prob.n:])
        if prob.mode == "J":
            tail[0] /= abs(prob.value)    # the flux row, in units of J
        res = max(float(np.max(np.abs(blocks[:, 1:-1][:, mask, :]))),
                  float(np.max(tail)))
        info = {"res_scaled_inf": res, "iters": 0}
    else:
        u, info = newton(prob.residual, prob.jacobian, u0, tol=TOL,
                         verbose=verbose)
    F, W, Nf, B, PSI = (np.asarray(a) for a in prob.fields(u))
    omega_inf, psi_minus = prob.unpack(u)[-2:]
    psi_minus_ref = -math.pi * math.sqrt(d2_ref) / sol.eta0
    diag = prob.diagnostics(u)
    x_new = exotic_x(prob.eta0, prob.map, prob.sx, prob.sy, prob.Dx, F, Nf,
                     B, PSI)["X"]
    x_pub = (abs(exotic_matter(sol, sol.observables["D"]))
             / sol.observables["R_eq"])
    out = {
        "newton": info["res_scaled_inf"],
        "ref_newton": ref_res,
        "iters": info["iters"],
        "dF": float(np.max(np.abs(F - F_ref))),
        "dW": float(np.max(np.abs(W - W_ref))),
        "dN": float(np.max(np.abs(Nf - N_ref))),
        "dB": float(np.max(np.abs(B - 1.0))),
        "dpsim": abs(psi_minus - psi_minus_ref) / abs(psi_minus_ref),
        "domega": abs(omega_inf - omega_ref) / abs(omega_ref),
        "saved_domega": abs(omega_inf - sol.omega_inf) / abs(sol.omega_inf),
        "X": x_new, "dX": abs(x_new - x_pub) / x_pub,
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
        and out["domega"] <= GATES["omega_inf"]
        and out["dX"] <= GATES["bill"]
        and max(out["E19"], out["E_c"]) <= GATES["monitors"]
    )
    return out


def main(argv: list[str] | None = None) -> int:
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
    ap.add_argument("--prescribe-j", action="store_true",
                    help="hold J, start omega_inf off by OMEGA_KICK, gate "
                    "the recovered omega_inf (the J pin)")
    args = ap.parse_args(argv)
    failed = []
    for path in args.solutions:
        r = validate(path, verbose=args.verbose,
                     decoupled_solve=args.decoupled,
                     nx=args.nx, ny=args.ny, prescribe_j=args.prescribe_j)
        name = path.rsplit("/", 1)[-1]
        solve = ("res" if args.decoupled else "newton")
        how = ("decoupled" if args.decoupled else f"{r['iters']} it")
        head = (f"{solve} {r['newton']:.1e} ({how}, "
                f"ref {r['ref_newton']:.1e})  dF {r['dF']:.1e}  "
                f"dW {r['dW']:.1e}  dN {r['dN']:.1e}  "
                f"dB {r['dB']:.1e}  dpsi- {r['dpsim']:.1e}  "
                + (f"domega {r['domega']:.1e}  " if args.prescribe_j else "")
                + f"[saved: dF {r['saved_dF']:.1e} dN {r['saved_dN']:.1e}"
                + (f" domega {r['saved_domega']:.1e}]" if args.prescribe_j
                   else "]"))
        print(f"{name}: {head}  "
              f"X {r['X']:.6e} (dX {r['dX']:.1e})  "
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
