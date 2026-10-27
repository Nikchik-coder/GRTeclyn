"""Energy density of the phantom scalar for stationary observers.

The families' only matter is the phantom field psi(eta) with
psi_eta = D / h (conventions of the spinning solver), so

    T_ab = -(1 / 4 pi) [ d_a psi d_b psi - (1/2) g_ab (d psi)^2 ],
    (d psi)^2 = e^{f - nu} D^2 / h^2  > 0,

and an observer u sees

    rho(u) = -(1 / 4 pi) [ (u^eta psi_eta)^2 + (1/2) (d psi)^2 ].

Every observer everywhere sees rho < 0 (WEC fails pointwise), and every
STATIONARY observer (u^eta = 0: static, ZAMO, any rigid rotation) sees the
same

    rho = -(1 / 8 pi) e^{f - nu} D^2 / h^2,

which is also the least negative over all observers; a radial boost only
deepens it.  The stationary class is therefore the rigorous v1: its F is a
lower bound on any worst-case F, so F > 1 on it is already a no-go.  A
radially transiting observer needs the transit-limited sampling window
(the plan's flagged hurdle) and enters as a second observer class later,
not by unbounding the boost here.
"""

from __future__ import annotations

import math

import numpy as np

from ..spinning_wormhole.solution import Solution

__all__ = ["d_charge_sq", "rho_stationary"]


def d_charge_sq(sol: Solution) -> float:
    """D^2: the constraint-fitted median when saved, else observables' D."""
    d2 = sol.gates.get("D2_median")
    if d2 is None:
        d = sol.observables.get("D")
        if d is None:
            raise ValueError("Solution carries neither D2_median nor D")
        d2 = float(d) ** 2
    return float(d2)


def rho_stationary(work: dict, d2: float) -> np.ndarray:
    """rho on a curvature.kk_jets() grid: -(1/8 pi) e^{f-nu} D^2 / h^2."""
    f00 = work["jets"]["f_00"]
    nu00 = work["jets"]["nu_00"]
    return -np.exp(f00 - nu00) * d2 / (8.0 * math.pi * work["h"] ** 2)
