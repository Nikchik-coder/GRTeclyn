"""Solve one background; step families in J (SpinningSolver.md P2-P3).

``solve_point`` is the unit step: seed from the O(J^2) member (or a given
Solution / unknown vector), Newton on (f, omega), the linear N solve, then
observables and identity gates attached.  Families are labelled by J, not
omega_{-inf}: omega_0 turns over along a family while J grows monotonically
to the extremal end, so prescribing J steps straight past that fold
(section 4); J's own monotonicity is checked by the driver, never assumed.
"""

from __future__ import annotations

import math

import numpy as np

from .backgrounds import slow_rotation_omega, slow_rotation_solution
from .equations import CollocationProblem
from .newton import newton
from .observables import identity_gates, observables
from .solution import Solution
from .spectral import ArctanMap, cheb_eval

__all__ = ["solve_point", "seed_from_slowspin"]


def seed_from_slowspin(problem: CollocationProblem, J: float,
                       n_cheb: int = 96):
    """The O(J^2) member as a Newton start: df = J^2 (A + B P2(y)) with
    P2 = (3y + 1)/4, dw = 0 (omega = J w1 IS omega_inf q by construction),
    omega_inf = J w1(-inf)."""
    sol = slow_rotation_solution(problem.eta0, problem.gamma, n_cheb)
    x = problem.map.xi_of_eta(
        np.concatenate([[math.inf], problem.eta_i[:, 0], [-math.inf]]))
    if problem.map.name == "arctan":
        x = problem.sx                   # exact, not just the map round trip
    A = cheb_eval(sol["s"], sol["A"], x)
    B = cheb_eval(sol["s"], sol["B"], x)
    p2 = (3.0 * problem.sy + 1.0) / 4.0
    df = J * J * (A[:, None] + np.outer(B, p2))
    dw = np.zeros_like(df)
    w1_inf = float(slow_rotation_omega(problem.eta0, problem.gamma,
                                       np.array([-0.5 * math.pi]))[0])
    return df, dw, J * w1_inf


def solve_point(*, eta0: float, gamma: float, J: float | None = None,
                omega_inf: float | None = None, nx: int = 64, ny: int = 16,
                radial_map=None, tol: float = 1e-12, u0=None,
                problem: CollocationProblem | None = None,
                with_observables: bool = True, verbose: bool = False):
    """One converged Solution (or a diagnosable failure).

    Exactly one of J (the bordered system) and omega_inf must be given.
    ``u0`` reuses a Newton start (continuation); default is the O(J^2) seed.
    Returns (solution, info); info carries the Newton record and, on
    success, the identity gates.
    """
    if (J is None) == (omega_inf is None):
        raise ValueError("prescribe exactly one of J and omega_inf")
    prescribe = ("J", J) if J is not None else ("omega_inf", omega_inf)
    if problem is None:
        problem = CollocationProblem(eta0=eta0, gamma=gamma,
                                     radial_map=radial_map, nx=nx, ny=ny,
                                     prescribe=prescribe)
    else:
        if (problem.mode, problem.value) != prescribe:
            raise ValueError("problem/prescribe mismatch")
    if u0 is None:
        w1_inf = float(slow_rotation_omega(eta0, gamma,
                                           np.array([-0.5 * math.pi]))[0])
        J_seed = J if J is not None else omega_inf / w1_inf
        df, dw, winf0 = seed_from_slowspin(problem, J_seed)
        u0 = problem.pack(df, dw, winf0 if J is not None else None)
    u, info = newton(problem.residual, problem.jacobian, u0, tol=tol,
                     verbose=verbose)
    if not info["converged"]:
        return None, info
    F, W = problem.fields(u)
    F, W = np.asarray(F), np.asarray(W)
    _, _, winf = problem.unpack(u)
    # N and D^2 from the constraint sector (eqs 13 + 19), NOT the printed
    # eq. 12: extremal Kerr satisfies 10, 11, 13, 19 exactly but violates
    # the published eq. 12 at 1e-2 (2026-10-12, derive_xy_equations.py
    # --stage kerr), and the elliptic eq.-12 N leaves a J^4-sized
    # constraint violation that no resolution removes.
    Nf, d2_solved, n_info = problem.solve_N_constrained(F, W)
    m = problem.map
    sol = Solution(
        eta0=eta0, gamma=gamma, omega_inf=float(winf),
        map_name=m.name,
        map_params={k: v for k, v in vars(m).items()
                    if k not in ("eta0", "name")},
        F=F, W=W, N=Nf,
        meta={"newton": {k: info[k] for k in
                         ("iters", "res_scaled_inf", "jacobian_evals")},
              "n_solve": n_info,
              "prescribed": {prescribe[0]: prescribe[1]},
              "nx": problem.nx, "ny": problem.ny},
    )
    if with_observables:
        sol.gates = identity_gates(sol)
        sol.observables = observables(sol)
    info = dict(info)
    info["u"] = u
    return sol, info
