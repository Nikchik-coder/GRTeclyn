"""Damped Newton for the collocation problem (SpinningSolver.md section 3).

The Jacobian is exact (jax.jacfwd of the jitted residual) and dense;
row equilibration then one scipy LU per Jacobian.  Steps are damped by
Armijo backtracking on the equilibrated 2-norm, and the factorization is
reused (chord steps) while the contraction ratio stays below
``chord_ratio``.  Convergence is the equilibrated max-norm -- each row of
the residual divided by its Jacobian row's max element, i.e. the residual
against that equation's operator norm -- at or below ``tol``.

Dense LU carries the planned sizes (<= ~10k unknowns, ~0.6 GB at 8.5k);
if P4 outgrows it, the documented follow-up is assembling the Kronecker
form (~2(N_x + N_y) nonzeros per row) for scipy.sparse.linalg.splu.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve

__all__ = ["newton"]


def newton(residual, jacobian, u0, *, tol: float = 1e-12,
           max_iter: int = 12, chord_ratio: float = 0.1,
           min_damping: float = 1.0 / 64.0, verbose: bool = False):
    """Solve residual(u) = 0 from u0.  Returns (u, info).

    info: converged, iters, res_scaled_inf, res_history, jacobian_evals,
    newton_steps (the per-step damping factors).
    """
    u = np.asarray(u0, dtype=np.float64).copy()
    r = np.asarray(residual(u))
    lu = piv = scale = None
    need_jac = True
    history, steps, jac_evals = [], [], 0

    def scaled_inf(res):
        return float(np.max(np.abs(res * scale))) if scale is not None else np.inf

    for it in range(max_iter):
        if need_jac:
            jac = np.asarray(jacobian(u))
            jac_evals += 1
            scale = 1.0 / np.maximum(np.max(np.abs(jac), axis=1), 1e-300)
            lu, piv = lu_factor(scale[:, None] * jac)
        history.append(scaled_inf(r))
        if history[-1] <= tol:
            if verbose:
                print(f"[newton] converged at iter {it}: "
                      f"|R|_inf,scaled = {history[-1]:.3e}")
            return u, {"converged": True, "iters": it,
                       "res_scaled_inf": history[-1],
                       "res_history": history, "jacobian_evals": jac_evals,
                       "newton_steps": steps}
        du = -lu_solve((lu, piv), scale * r)
        norm0 = float(np.linalg.norm(scale * r))
        t = 1.0
        while t >= min_damping:
            r_try = np.asarray(residual(u + t * du))
            if float(np.linalg.norm(scale * r_try)) <= (1.0 - 1e-4 * t) * norm0:
                break
            t *= 0.5
        else:
            return u, {"converged": False, "iters": it,
                       "res_scaled_inf": history[-1],
                       "res_history": history, "jacobian_evals": jac_evals,
                       "newton_steps": steps,
                       "reason": "line search stalled"}
        u = u + t * du
        contraction = float(np.linalg.norm(scale * r_try)) / max(norm0, 1e-300)
        need_jac = (t < 1.0) or (contraction > chord_ratio)
        r = r_try
        steps.append(t)
        if verbose:
            print(f"[newton] iter {it}: |R| {norm0:.3e} -> "
                  f"{float(np.linalg.norm(scale * r)):.3e} (t = {t:g})")

    final = scaled_inf(r)
    return u, {"converged": final <= tol, "iters": max_iter,
               "res_scaled_inf": final, "res_history": history + [final],
               "jacobian_evals": jac_evals, "newton_steps": steps,
               "reason": "max_iter"}
