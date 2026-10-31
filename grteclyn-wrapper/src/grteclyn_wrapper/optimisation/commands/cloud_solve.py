"""Solve ordinary scalar clouds around a rotating wormhole.

Input: a saved massless member, a phantom potential and cloud amplitudes.
Output: printed Newton, cloud, throat and independent-constraint diagnostics.
Comparisons hold J and R_e fixed and report X = |VIQ|/R_e relative to the
same potential without a cloud. A one-dimensional boson-star solution seeds
chi = X exp(i*omega_chi*t); here X denotes the cloud amplitude, while the
reported exoticity X is a separate dimensionless observable. A vanished
cloud is identified as the trivial branch, not a successful matter cloud.

    python -m grteclyn_wrapper.optimisation.commands.cloud_solve --help
"""

from __future__ import annotations
import argparse

from ..workflows import cloud_solve as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--kink-m", type=float, default=0.3,
                    help="phantom kink mass (0 = pure V = 0 phantom)")
    ap.add_argument("--q", default="",
                    help="shape target q1,q2 (kink_q), walked in 0.3 steps")
    ap.add_argument("--m-chi", type=float, default=1.0,
                    help="cloud mass (cal U = m_chi^2 X^2)")
    ap.add_argument("--phi-c", default="0.01,0.02,0.05,0.1",
                    help="central-amplitude ladder of the seeding 1D mini "
                         "star; its eigen-omega is the prescribed omega_chi")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD",
                    help="solve on this CUDA card (cards are shared: check "
                         "nvidia-smi first); default CPU")
    ap.add_argument("--jac-chunk", type=int, default=None)
    args = ap.parse_args(argv)
    return workflow.run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
