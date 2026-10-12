#!/usr/bin/env python
"""Run one fixed-gamma family of fast-spin backgrounds (SpinningSolver.md P3).

Continuation in log(J/eta0^2) from the O(J^2) seed up to --ve-stop, every
converged Solution saved (.npz + .json) plus one TSV log, grids refined
automatically on the tail gate.  --anchor stops after omega_inf has
crossed --anchor-omega twice (both branches bracketed), for the CKK D
anchors at eta0 = 1, omega_inf = 0.5.

Run (repo root, CPU only; cap it -- CLAUDE.md "Environment"):

    (ulimit -v 67108864; grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/solve_family.py \
        --eta0 2 --mass 1 --j-start 0.25 --ve-stop 0.9 --out <dir> --name fam_a)
"""

from __future__ import annotations

import argparse
import math
import sys

from grteclyn_wrapper.analysis.spinning_wormhole.continuation import run_family
from grteclyn_wrapper.analysis.spinning_wormhole.conventions import (
    gamma_of_mass,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--eta0", type=float, required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--mass", type=float, help="static drainhole mass "
                   "(gamma = -2 pi m / eta0)")
    g.add_argument("--gamma", type=float, help="f(-inf) directly")
    ap.add_argument("--j-start", type=float, required=True)
    ap.add_argument("--ve-stop", type=float, default=0.9)
    ap.add_argument("--j-stop", type=float)
    ap.add_argument("--nx", type=int, default=48)
    ap.add_argument("--ny", type=int, default=12)
    ap.add_argument("--nx-max", type=int, default=192)
    ap.add_argument("--out", required=True, help="catalogue directory")
    ap.add_argument("--name", required=True)
    ap.add_argument("--anchor", action="store_true",
                    help="stop after omega_inf crosses --anchor-omega twice")
    ap.add_argument("--anchor-omega", type=float, default=0.5)
    args = ap.parse_args()
    gamma = args.gamma if args.gamma is not None else gamma_of_mass(
        args.mass, args.eta0)

    stop_fn = None
    if args.anchor:
        target = args.anchor_omega

        def stop_fn(rows):
            n = sum(1 for a, b in zip(rows, rows[1:])
                    if (a["omega_inf"] - target)
                    * (b["omega_inf"] - target) < 0)
            return n >= 2

    out = run_family(eta0=args.eta0, gamma=gamma, j_start=args.j_start,
                     nx=args.nx, ny=args.ny, nx_max=args.nx_max,
                     ve_stop=args.ve_stop, j_stop=args.j_stop,
                     out_dir=args.out, name=args.name, stop_fn=stop_fn)
    print(f"{args.name}: {out['reason']}, {len(out['rows'])} points, "
          f"final grid {out['nx']} x {out['ny']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
