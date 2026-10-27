#!/usr/bin/env python
"""Step-1 gate of campaign M: the matter solver at V = 0 reproduces the
saved Kleihaus-Kunz family.

For each saved solution, build a MatterCollocationProblem (the
five-field system f, omega, N, B, psi bordered by psi_minus) at the same
(eta0, gamma, map, grid), prescribe the solution's omega_inf, start
Newton from the saved fields with B = 1 and the closed-form scalar, and
gate on
  - Newton converged (equilibrated |R|_inf <= 1e-11),
  - max |F - F_saved|, |W - W_saved|, |N - N_saved| <= 1e-10,
  - max |B - 1| <= 1e-10,
  - the recovered psi_minus against -pi sqrt(D2_median) / eta0 (1e-9 rel),
  - the unimposed monitors: max |E19| / eta0^2 and max |E_c| <= 1e-8.

The saved (f, omega) solved E_f, E_w with N from the constraint sector;
here all five elliptic rows are imposed and the constraints stay free,
so agreement is a genuine cross-check of the new formulation, not a
round trip.

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

from grteclyn_wrapper.analysis.spinning_wormhole.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.analysis.spinning_wormhole.newton import newton
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution

GATES = {"fields": 1e-10, "B": 1e-10, "psi_minus": 1e-9, "monitors": 1e-8,
         "newton": 1e-11}


def validate(path: str, verbose: bool = False) -> dict:
    sol = Solution.load(path)
    nx, ny = sol.F.shape[0] - 1, sol.F.shape[1] - 1
    d2 = sol.gates.get("D2_median") if sol.gates else None
    if d2 is None:
        from grteclyn_wrapper.analysis.spinning_wormhole.observables import (
            identity_gates,
        )
        d2 = identity_gates(sol)["D2_median"]
    psi_minus0 = -math.pi * math.sqrt(float(d2)) / sol.eta0

    t0 = time.time()
    prob = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("omega_inf", sol.omega_inf))
    zero = np.zeros_like(sol.F)
    u0 = prob.pack(sol.F - prob.f_bg, sol.W - sol.omega_inf * prob.q,
                   sol.N, zero, zero, psi_minus=psi_minus0)
    u, info = newton(prob.residual, prob.jacobian, u0, tol=1e-12,
                     verbose=verbose)
    F, W, Nf, B, PSI = (np.asarray(a) for a in prob.fields(u))
    _, _, _, _, _, _, psi_minus = prob.unpack(u)
    diag = prob.diagnostics(u)
    out = {
        "newton": info["res_scaled_inf"],
        "iters": info["iters"],
        "converged": info["converged"],
        "dF": float(np.max(np.abs(F - sol.F))),
        "dW": float(np.max(np.abs(W - sol.W))),
        "dN": float(np.max(np.abs(Nf - sol.N))),
        "dB": float(np.max(np.abs(B - 1.0))),
        "dpsim": abs(psi_minus - psi_minus0) / abs(psi_minus0),
        "E19": float(np.max(np.abs(diag["E19"]))) / sol.eta0**2,
        "E_c": float(np.max(np.abs(diag["E_c"]))),
        "seconds": time.time() - t0,
    }
    out["pass"] = (
        out["converged"] and out["newton"] <= GATES["newton"]
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
    args = ap.parse_args()
    failed = []
    for path in args.solutions:
        r = validate(path, verbose=args.verbose)
        name = path.rsplit("/", 1)[-1]
        print(f"{name}: newton {r['newton']:.1e} ({r['iters']} it)  "
              f"dF {r['dF']:.1e}  dW {r['dW']:.1e}  dN {r['dN']:.1e}  "
              f"dB {r['dB']:.1e}  dpsi- {r['dpsim']:.1e}  "
              f"E19 {r['E19']:.1e}  E_c {r['E_c']:.1e}  "
              f"[{r['seconds']:.0f}s]  "
              f"{'PASS' if r['pass'] else 'FAIL'}", flush=True)
        if not r["pass"]:
            failed.append(name)
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
