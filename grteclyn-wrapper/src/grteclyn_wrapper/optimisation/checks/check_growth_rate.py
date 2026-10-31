"""Compare the diagnostic radial solver with a static drainhole benchmark.

Input: grid sizes and a rate tolerance; output: rates and a PASS/FAIL result.
The reference rate is |omega_I|*eta0 = 0.390. The exact background uses
F0 = gamma*(1-x)/2, P0 = 1, psi0_prime = D/h, and
D^2 = eta0^2 + (gamma*eta0/pi)^2/4.
This is a calibration tool for the radial screen, which remains under repair;
it does not certify the stability of a rotating candidate.

    python -m grteclyn_wrapper.optimisation.checks.check_growth_rate --help
"""

from __future__ import annotations

import argparse
import math
import sys
import time

import numpy as np

from grteclyn_wrapper.optimisation.stability_radial import growth_rate

AZAD = 0.390  # |omega_I| eta0 of the C = 1 family at J = 0


def drainhole_background(eta0: float, gamma: float):
    """The massless static drainhole's jets and potential values."""
    gam_s = gamma * eta0 / math.pi
    D = math.sqrt(eta0**2 + gam_s**2 / 4.0)

    def bg(eta):
        h = eta**2 + eta0**2
        z = np.zeros_like(eta)
        return {
            "F0_0": gamma * (1.0 - (2.0 / math.pi)
                             * np.arctan(eta / eta0)) / 2.0,
            "F0_1": -gam_s / h,
            "F0_2": 2.0 * gam_s * eta / h**2,
            "P0_0": np.ones_like(eta), "P0_1": z, "P0_2": z,
            "psi0_1": D / h, "psi0_2": -2.0 * D * eta / h**2,
            "V0": z, "V1": z, "V2": z,
        }
    return bg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--eta0", type=float, default=2.0)
    ap.add_argument("--gamma", type=float, default=-math.pi,
                    help="the drainhole family's gamma")
    ap.add_argument("--nx", default="100,150,200")
    ap.add_argument("--tol", type=float, default=0.03)
    args = ap.parse_args(argv)
    bg = drainhole_background(args.eta0, args.gamma)
    lam_last = None
    ok = True
    for nx in (int(v) for v in args.nx.split(",")):
        t0 = time.time()
        out = growth_rate(eta0=args.eta0, nx=nx, background=bg)
        if out.get("stable"):
            print(f"nx {nx}: NO unstable localized mode found  FAIL",
                  flush=True)
            ok = False
            continue
        lam = out["lam"]
        drift = ("" if lam_last is None
                 else f"  d(lam) {lam - lam_last:+.2e}")
        print(f"nx {nx}: lam {lam:.8f}  lam*eta0 {lam * args.eta0:.6f}  "
              f"2-grid {out['match_drift']:.1e}  "
              f"imposed {out['imposed_res']:.1e}  tt {out['tt_res']:.1e}  "
              f"teta {out['teta_res']:.1e}  "
              f"matched lam2 {', '.join(f'{v:.5f}' for v in out['lam2_top'])}"
              f"{drift}  [{time.time() - t0:.0f}s]", flush=True)
        lam_last = lam
    rel = abs(lam_last * args.eta0 - AZAD) / AZAD
    print(f"gate: lam*eta0 {lam_last * args.eta0:.6f} vs {AZAD} "
          f"(arXiv:2301.05243 C=1, J=0): rel {rel:.3f} "
          f"{'PASS' if rel <= args.tol and ok else 'FAIL'}", flush=True)
    return 0 if rel <= args.tol and ok else 1


if __name__ == "__main__":
    sys.exit(main())
