#!/usr/bin/env python
"""First solve with cal V != 0: the entry to campaign M step 3.

From a saved V = 0 member: solve holding its J on its own grid, measure
the throat, then continue in the kink mass m on the dimensionless grid
at pinned J and R_e, with cal V = lam psi^2 (psi - psi_minus)^2, lam =
m^2/psi_minus^2 -- the vacuum riding on the bordered psi_minus
(matter_equations.potential_at).  Each mass starts Newton from the
previous solution's fields.

psi_minus stays bordered by the E19-at-throat row, and the potential's
vacuum follows it.  Both detunings were measured before this form
settled (2026-10-27): a FROZEN vacuum with psi_minus bordered lets the
boundary value drift off the vacuum (0.14 at m = 0.05) onto a non-flat
end, E19/D^2 = O(1); psi_minus FIXED at the vacuum drops the border row,
the constraint system's one free constant survives, and E19/D^2 sits at
0.1-0.8, linear in m, however tight Newton converges.

Per mass it reports what step 3 will optimize over and what gates it:
  - Newton's residual and iterations (a failure is a verdict, not an
    error: print it and move on);
  - the field shifts from the m = 0 pinned solve -- dB is the
    potential's own signature, zero at V = 0 by construction;
  - sigma, the throat and the bill X = |VIQ|/R_e (scale-free, so the
    dimensionless fields give it directly);
  - the unimposed monitors E19/D^2 and E_c inside C >= 0.05, the same
    gate the V = 0 record sweep used (1e-8): the identities Newton never
    saw are the acceptance test for a genuinely new solution;
  - the spectral tail ratios of psi and B (the Trap-1 resolution check:
    a massive tail e^{-m eta} must still fit the arctan grid; --nx/--ny
    re-solve on a finer grid from the spectrally interpolated member).

The m -> 0 end must creep back to V = 0 quadratically: the first two
masses' shifts are checked for ~ m^2 scaling.  Run through capped_job.sh
(the five-field Jacobian; 40 GB is enough at 48x12):

    grteclyn-wrapper/scripts/ops/capped_job.sh start first-v \\
        --threads 4 --mem 40 --timeout 3600 -- \\
        grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/first_matter_solve.py \\
        results/spinningwormhole/solutions/fam_b/fam_b_0003.json
"""

from __future__ import annotations

import argparse
import dataclasses
import math
import sys
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.exoticity import (
    exotic_x,
    throat,
)
from grteclyn_wrapper.analysis.spinning_wormhole.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.analysis.spinning_wormhole.newton import newton
from grteclyn_wrapper.analysis.spinning_wormhole.potentials import (
    PolynomialPotential,
)
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import tail_ratio

TOL = 1e-14
C_GATE = 0.05
MONITOR_GATE = 1e-8


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--masses", default="0.1,0.2,0.3,0.5",
                    help="kink masses (physical units), continued in order")
    ap.add_argument("--nx", type=int, default=None,
                    help="re-solve on this grid from the interpolated member")
    ap.add_argument("--ny", type=int, default=None)
    args = ap.parse_args()
    masses = [float(m) for m in args.masses.split(",")]

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny

    # the member holding J on its own grid, and its measured throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("J", J0))
    F0 = sol.eval_grid("f", p1.sx, p1.sy)
    W0 = sol.eval_grid("w", p1.sx, p1.sy)
    N0 = sol.eval_grid("N", p1.sx, p1.sy)
    zero = np.zeros_like(F0)
    u1, i1 = newton(p1.residual, p1.jacobian,
                    p1.pack(F0 - p1.f_bg, W0 - sol.omega_inf * p1.q,
                            N0, zero, zero, omega_inf=sol.omega_inf,
                            psi_minus=psim0), tol=TOL)
    F1, W1, N1, B1, P1 = (np.asarray(a) for a in p1.fields(u1))
    omega1, psim1 = p1.unpack(u1)[-2:]
    th = throat(p1.eta0, p1.map, p1.sx, p1.sy, p1.Dx, F1, N1, B1)
    xi1 = float(p1.map.xi_of_eta(th["eta_throat"]))
    name = args.solution.rsplit("/", 1)[-1]
    print(f"{name} ({nx}x{ny}, {sol.map_name}, eta0 {sol.eta0:g}, "
          f"gamma {sol.gamma:g}): J-held solve {i1['res_scaled_inf']:.1e}; "
          f"R_e {th['R_e']:.10f}, J {J0:.6e}, psi_minus {psim1:.10f}",
          flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    base = None
    shifts = []
    # previous solution's fields, for continuation
    # (grid units: omega scales as 1/sigma, so W carries sigma = eta0)
    prev = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
            "omega": sol.eta0 * omega1, "psim": psim1,
            "sigma": sol.eta0, "xi_t": xi1}
    for m in [0.0] + masses:
        t0 = time.time()
        pot = (None if m == 0.0
               else (lambda pm, m=m: PolynomialPotential.kink(m, pm)))
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx,
            ny=ny, prescribe=("J", J0), pin=("R_e", th["R_e"]),
            potential=pot)
        u0 = p2.pack(prev["F"] - p2.f_bg, prev["W"] - prev["omega"] * p2.q,
                     prev["N"], prev["B"] - 1.0,
                     prev["PSI"] - prev["psim"] * p2.psi_prof,
                     omega_inf=prev["omega"], psi_minus=prev["psim"],
                     sigma=prev["sigma"], xi_t=prev["xi_t"])
        try:
            u, info = newton(p2.residual, p2.jacobian, u0, tol=TOL)
        except Exception as err:    # a verdict, not an error
            print(f"  m {m:.3f}: NEWTON FAILED ({err})", flush=True)
            continue
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        diag = p2.diagnostics(u)
        mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        x = exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx, F, Nf, B, PSI)
        tails = max(tail_ratio(PSI - psim * p2.psi_prof, axis=0),
                    tail_ratio(B - 1.0, axis=0))
        if m == 0.0:
            base = (F, Nf, B, PSI, x["X"])
            print(f"  m 0.000: newton {info['res_scaled_inf']:.1e} "
                  f"({info['iters']} it)  X {x['X']:.8e}  sigma "
                  f"{tt['sigma']:.10f}  E19 {e19:.1e}  E_c {e_c:.1e}  "
                  f"[{time.time() - t0:.0f}s]", flush=True)
        else:
            dfield = max(float(np.max(np.abs(F - base[0]))),
                         float(np.max(np.abs(Nf - base[1]))),
                         float(np.max(np.abs(PSI - base[3]))))
            db = float(np.max(np.abs(B - 1.0)))
            shifts.append((m, dfield, db))
            ok = max(e19, e_c) <= MONITOR_GATE
            print(f"  m {m:.3f}: newton {info['res_scaled_inf']:.1e} "
                  f"({info['iters']} it)  dfields {dfield:.3e}  "
                  f"max|B-1| {db:.3e}  psi- {psim:.6f} "
                  f"({psim - psim1:+.1e})  "
                  f"sigma {tt['sigma']:.10f}  R_e {tt['R_e']:.10f}  "
                  f"X {x['X']:.8e} (dX {x['X'] - base[4]:+.3e})  "
                  f"E19 {e19:.1e}  E_c {e_c:.1e}  tails {tails:.1e}  "
                  f"{'PASS' if ok else 'MONITORS ABOVE GATE'}  "
                  f"[{time.time() - t0:.0f}s]", flush=True)
        prev = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
                "omega": omega, "psim": psim,
                "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
    if len(shifts) >= 2 and shifts[0][1] > 0:
        m1, d1, _ = shifts[0]
        m2, d2_, _ = shifts[1]
        p = math.log(d2_ / d1) / math.log(m2 / m1)
        print(f"  shift scaling between m {m1:g} and {m2:g}: "
              f"d ~ m^{p:.2f} (2 = perturbative m^2)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
