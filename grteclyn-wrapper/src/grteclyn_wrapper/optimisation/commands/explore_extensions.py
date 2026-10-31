"""Compare richer potentials, ordinary matter, shape and asymmetry.

Input: a saved optimiser NPZ and a bounded selection of trial stages.
Output: diagnostic JSONL records and NPZ fields, including failed trials.
Physical radii are reconstructed from fields and sigma. Trials retain J and
R_e; shape and asymmetry trials retain J and area instead. Every stage refines
its best trial and a matched reference. These are stationary comparisons;
no stability penalty or evolution-cleared export is produced.

    python -m grteclyn_wrapper.optimisation.commands.explore_extensions --help
"""

from __future__ import annotations
import argparse

from ..workflows import explore_extensions as workflow


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("seed")
    ap.add_argument("--stages", default="potential,cloud,winding,shape,asymmetry")
    ap.add_argument("--grid", default="150x30")
    ap.add_argument("--fine-grid", default="180x36")
    ap.add_argument("--degree", type=int, default=6)
    ap.add_argument("--indices", default="1,2,3,4,5,6")
    ap.add_argument("--shape-step", type=float, default=.25,
                    help="multiplicative control perturbation exp(+/- step)")
    ap.add_argument("--amplitudes", default="0.005,0.02")
    ap.add_argument("--matter-mass", type=float, default=1.)
    ap.add_argument("--quartic", type=float, default=0.)
    ap.add_argument("--gamma-offsets", default="-0.1,0.1")
    ap.add_argument("--gpu", type=int)
    ap.add_argument("--jac-chunk", type=int, default=512)
    ap.add_argument("--out", required=True, help="new output directory; refuses overwrite")
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
