"""Measure exotic matter across potential shapes and end-mass asymmetries.

Input: a saved massless member and a shape grid, gamma list or ray directions.
Output: TSV evaluations and printed diagnostics at fixed J and R_e.
X = |VIQ|/R_e is dimensionless. The potential uses u = psi/psi_minus and
Q = 1 + q1*u + q2*u^2. Points with nonpositive Q are skipped. Ray walks stop
on Newton failure, repeated constraint violations or repeated increases in X.
Rows are search-grid measurements, not independently refined solutions.

    python -m grteclyn_wrapper.optimisation.commands.scan_potential --help
"""

from __future__ import annotations
import argparse

from ..workflows import scan_potential as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--mass", type=float, default=0.3,
                    help="kink mass of the scan (0.3 passes the monitor "
                         "gate at 150x30 at all three spins, 2026-10-28)")
    ap.add_argument("--q1", default="-0.6,-0.3,0,0.3,0.6",
                    help="shape-scan values of q1")
    ap.add_argument("--q2", default="-0.6,-0.3,0,0.3,0.6",
                    help="shape-scan values of q2")
    ap.add_argument("--gammas", default=None,
                    help="gamma-scan values, walked in order from the "
                         "member's gamma (switches the scan axis)")
    ap.add_argument("--rays", default=None,
                    help="semicolon-separated (dq1,dq2[,dq3,...]) directions "
                         "for the open-ended ray walk (switches the scan "
                         "axis; kink_q takes any shape order)")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD",
                    help="solve on this CUDA card (cards are shared: check "
                         "nvidia-smi first); default CPU")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None,
                    help="TSV path (default runs/optimisation/scans/"
                         "<member>_<mode>_<grid>.tsv)")
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
