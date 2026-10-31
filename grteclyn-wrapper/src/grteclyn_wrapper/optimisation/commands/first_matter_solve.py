"""Continue a known wormhole from zero potential to a sequence of kink masses.

Input: a saved massless member and a list of scalar masses.
Output: printed solves, throat measurements, exoticity and constraint checks.
The search holds angular momentum J and equatorial radius R_e fixed.
The potential is cal V = m^2 psi^2 (psi - psi_minus)^2 / psi_minus^2;
its vacuum follows the bordered scalar endpoint psi_minus. Independent
constraints and the expected small-m quadratic limit test the solutions.

    python -m grteclyn_wrapper.optimisation.commands.first_matter_solve --help
"""

from __future__ import annotations
import argparse

from ..workflows import first_matter_solve as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--masses", default="0.1,0.2,0.3,0.5",
                    help="kink masses (physical units), continued in order")
    ap.add_argument("--nx", type=int, default=None,
                    help="re-solve on this grid from the interpolated member")
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD",
                    help="solve on this CUDA card (cards are shared: check "
                         "nvidia-smi first); default CPU")
    ap.add_argument("--jac-chunk", type=int, default=None,
                    help="Jacobian column block size (sets WH_JAC_CHUNK; "
                         "default: 1024 on gpu, unchunked on cpu)")
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
