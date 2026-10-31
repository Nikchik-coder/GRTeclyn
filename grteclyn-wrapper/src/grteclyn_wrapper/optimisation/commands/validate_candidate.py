"""Independently refine a saved candidate before an evolution handoff.

Input: a candidate NPZ, increasing grids and an optional physical radius.
Output: manifests, per-grid diagnostic fields and, only on clearance,
handoff.npz. The last two grids must PASS with finite positive X = |VIQ|/R_e
and relative drift at most 1e-6. Radius rescaling changes lengths by s,
J by s^2 and the potential by 1/s^2. Stability remains unassessed.

    python -m grteclyn_wrapper.optimisation.commands.validate_candidate --help
"""

from __future__ import annotations
import argparse
from pathlib import Path

from ..workflows import validate_candidate as workflow


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("seed")
    ap.add_argument("--grids", default="150x30,180x36,210x42")
    ap.add_argument("--radius", type=float, help="rescale to this physical R_e before refinement")
    ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
