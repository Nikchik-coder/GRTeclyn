"""Re-solve potential candidates at increasing spatial resolution.

Input: a massless member plus potential points, or a saved optimiser NPZ.
Output: a TSV with exoticity and independent constraints at each grid.
Every grid holds the same J and physical R_e. The first grid uses continuation;
later grids start from spectral interpolation of the previous solved fields.
This distinguishes under-resolution from a numerical residual floor.
X = |VIQ|/R_e is dimensionless; no physical stability claim follows.

    python -m grteclyn_wrapper.optimisation.commands.grid_check --help
"""

from __future__ import annotations
import argparse

from ..workflows import grid_check as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--points", required=True,
                    help="label=m,q1,q2,q3 list, ';'-separated")
    ap.add_argument("--grids", default="150x30,180x36,210x42",
                    help="nx x ny list, coarse to fine; the first is the "
                         "walk-in grid and the R_e pin's")
    ap.add_argument("--stall-ok", type=float, default=workflow.STALL_OK,
                    help="accept a Newton stall at or below this scaled "
                         "residual (default: the step-1 gate; the "
                         "drainhole floors at 1e-11 to 2e-10)")
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-dir", default=None,
                    help="save each solved nonzero point as an evolution "
                         "handoff NPZ in this directory")
    ap.add_argument("--from-npz", default=None,
                    help="search dump to start from (one --points entry); "
                         "skips continuation from V = 0")
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
