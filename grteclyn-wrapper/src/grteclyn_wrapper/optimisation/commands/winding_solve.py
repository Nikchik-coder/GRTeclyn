"""Solve rotating scalar clouds that carry part of a wormhole's spin.

Input: a saved massless member, potential parameters and cloud amplitudes.
Output: printed exoticity, cloud properties and spin/constraint checks.
At fixed J and R_e, Lambda = Z exp(i*(omega_z*t + k*phi)) with
Z = sin(theta)^k*zeta. The regular amplitude zeta is pinned at the throat;
omega_z is solved as an eigenvalue. A frozen-metric quadratic eigenproblem
seeds the first cloud. The total angular-momentum flux is checked independently
of Newton. These are stationary solutions, not stability certificates.

    python -m grteclyn_wrapper.optimisation.commands.winding_solve --help
"""

from __future__ import annotations
import argparse

from ..workflows import winding_solve as workflow


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--kink-m", type=float, default=0.3,
                    help="phantom kink mass (0 = pure V = 0 phantom)")
    ap.add_argument("--q", default="",
                    help="shape target q1,q2 (kink_q), walked in 0.3 steps")
    ap.add_argument("--m-z", type=float, default=1.0,
                    help="winding field mass (cal U_z = m_z^2 Z^2)")
    ap.add_argument("--k", type=int, default=1,
                    help="winding number k >= 1")
    ap.add_argument("--amp", default="0.05,0.1,0.2,0.3",
                    help="zeta amplitude ladder at the throat's equator "
                         "(the pin_zeta row; omega_z is the bordered "
                         "eigenvalue, continued rung to rung)")
    ap.add_argument("--omega-z-seed", type=float, default=0.9,
                    help="omega_z seed of the linear mode search, in "
                         "units of m_z")
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
