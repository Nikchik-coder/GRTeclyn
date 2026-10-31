"""Find the first saved candidate that clears independent refinement.

Input: an NPZ glob, optional excluded slots and a candidate-count limit.
Output: an ordered manifest, attempt logs and selected.json on success.
Candidates are ordered by finite X = |VIQ|/R_e, with filename breaking ties.
Each validator runs in a fresh process to release GPU allocations. Selection
requires both a successful exit and handoff.npz; unexpected failures stop the
batch. Numerical clearance is not a physical stability certificate.

    python -m grteclyn_wrapper.optimisation.commands.select_validated_candidate --help
"""

from __future__ import annotations
import argparse
from pathlib import Path

from ..workflows import select_validated_candidate as workflow


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pattern", help="glob of saved candidate NPZ files")
    ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--radius", type=float)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--skip", nargs="*", default=[], help="already checked slot names")
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
