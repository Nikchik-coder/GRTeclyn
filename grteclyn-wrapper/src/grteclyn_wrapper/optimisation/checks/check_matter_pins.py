"""Check that size and spin pins recover a known massless solution.

Input: saved spinning-wormhole members; output: pin errors and PASS/FAIL.
The reference is solved at its physical eta0, then on an eta0 = 1 grid with
a deliberately perturbed length scale sigma. Holding J and R_e (or area)
must recover the reference scale, rotation and fields to the existing 1e-10
gates. Physical angular velocities scale inversely with sigma.

    python -m grteclyn_wrapper.optimisation.checks.check_matter_pins --help
"""

from __future__ import annotations

import argparse
import dataclasses
import math
import sys
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.optimisation.exoticity import throat
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.optimisation.solver.newton import newton

SIGMA_KICK = 1e-3
TOL = 1e-14
GATE = 1e-10


def check(path: str) -> bool:
    t0 = time.time()
    sol = Solution.load(path)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    zero = np.zeros_like(sol.F)

    # 1. the member holding J on its own grid, and its measured throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=sol.nx, ny=sol.ny, prescribe=("J", J0))
    u1, i1 = newton(p1.residual, p1.jacobian,
                    p1.pack(sol.F - p1.f_bg, sol.W - sol.omega_inf * p1.q,
                            sol.N, zero, zero, omega_inf=sol.omega_inf,
                            psi_minus=psim0), tol=TOL)
    F1, W1, N1, B1, P1 = (np.asarray(a) for a in p1.fields(u1))
    omega1, psim1 = p1.unpack(u1)[-2:]
    th = throat(p1.eta0, p1.map, p1.sx, p1.sy, p1.Dx, F1, N1, B1)
    xi1 = float(p1.map.xi_of_eta(th["eta_throat"]))

    # 2. the same member on the dimensionless grid, sigma unknown
    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    name = path.rsplit("/", 1)[-1]
    ok = True
    print(f"{name} ({sol.nx}x{sol.ny}, {sol.map_name}, eta0 {sol.eta0:g}): "
          f"J-held solve {i1['res_scaled_inf']:.1e}; throat R_e "
          f"{th['R_e']:.12f} area {th['area_throat']:.10f}", flush=True)
    for kind, held in (("R_e", th["R_e"]), ("area", th["area_throat"])):
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=sol.nx,
            ny=sol.ny, prescribe=("J", J0), pin=(kind, held))
        s0 = sol.eta0 * (1.0 + SIGMA_KICK)
        u2, i2 = newton(p2.residual, p2.jacobian,
                        p2.pack(F1 - p2.f_bg, sol.eta0 * (W1 - omega1 * p2.q),
                                N1, B1 - 1.0, P1 - psim1 * p2.psi_prof,
                                omega_inf=sol.eta0 * omega1,
                                psi_minus=psim1, sigma=s0, xi_t=xi1),
                        tol=TOL)
        F2, W2, N2, B2, P2 = (np.asarray(a) for a in p2.fields(u2))
        omega2, psim2 = p2.unpack(u2)[-2:]
        th2 = p2.throat(u2)
        err = {
            "sigma": abs(th2["sigma"] / sol.eta0 - 1.0),
            "omega": abs(omega2 / th2["sigma"] - omega1) / abs(omega1),
            "R_e": abs(th2["R_e"] - th["R_e"]) / th["R_e"],
            "area": abs(th2["area"] - th["area_throat"]) / th["area_throat"],
            "eta_t": abs(th2["eta_t"] - th["eta_throat"]) / sol.eta0,
            "fields": max(float(np.max(np.abs(F2 - F1))),
                          float(np.max(np.abs(N2 - N1))),
                          float(np.max(np.abs(B2 - B1))),
                          abs(psim2 - psim1)),
        }
        good = (i2["res_scaled_inf"] <= 1e-11
                and max(err.values()) <= GATE)
        ok = ok and good
        print(f"   pin {kind:<4}: newton {i2['res_scaled_inf']:.1e} "
              f"({i2['iters']} it)  "
              + "  ".join(f"d{k} {v:.1e}" for k, v in err.items())
              + f"  {'PASS' if good else 'FAIL'}", flush=True)
    print(f"   [{time.time() - t0:.0f}s]", flush=True)
    return ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solutions", nargs="+", help=".npz / .json paths")
    args = ap.parse_args(argv)
    failed = [p.rsplit("/", 1)[-1] for p in args.solutions if not check(p)]
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
