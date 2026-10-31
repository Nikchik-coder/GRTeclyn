"""Run diagnostic radial-stability calculations on static candidate twins.

Input: a saved member and potential targets; output: a radial-rate TSV.
Each target is re-solved at J = 0 with the member's size pin. Rates use
lambda*eta0 and lambda*R_e; grid coordinates have eta0 = 1.
The radial screen is under repair. Its output is diagnostic and must not be
used to certify physical stability or to score the production optimiser.

    python -m grteclyn_wrapper.optimisation.commands.stability_screen --help
"""

from __future__ import annotations
import argparse

from ..workflows import stability_screen as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of the member "
                                     "whose R_e pin scales the targets")
    ap.add_argument("--targets", default="v0=0,0,0,0;kink03=0.3,0,0,0",
                    help="label=m,q1,q2,q3 list, ';'-separated")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--screen-nx", default="100,150,200")
    ap.add_argument("--stall-ok", type=float, default=workflow.STALL_OK,
                    help="accept a Newton stall at or below this scaled "
                         "residual (default: the step-1 gate); the twin "
                         "only feeds the radial screen, whose two-grid "
                         "match tolerates far larger background errors")
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
