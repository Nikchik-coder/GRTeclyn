"""Damped Newton for dense collocation problems.

Grown from the spinning solver's Newton (research/spinningwormhole/
SpinningSolver.md section 3), whose published, CPU-only copy stays in
analysis/spinning_wormhole/newton.py.  The Jacobian is exact (jacobian.py:
jax.jacfwd of the jitted residual, or chunked_jacfwd in column blocks)
and dense; row equilibration then one LU per Jacobian.  Steps are damped
by Armijo backtracking on the equilibrated 2-norm, and the factorization
is reused (chord steps) while the contraction ratio stays below
``chord_ratio``.  Convergence is the
equilibrated max-norm -- each row of the residual divided by its Jacobian
row's max element, i.e. the residual against that equation's operator
norm -- at or below ``tol``.

Backends: a Jacobian that arrives as a CUDA-resident jax array keeps the
whole solve on the card (jax.scipy.linalg LU, cusolver getrf in float64);
anything else goes the numpy + scipy route exactly as before.  The
returned solution is a numpy array either way.

Dense LU carries the planned sizes (<= ~10k unknowns, ~0.6 GB at 8.5k);
if P4 outgrows it, the documented follow-up is assembling the Kronecker
form (~2(N_x + N_y) nonzeros per row) for scipy.sparse.linalg.splu.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve

__all__ = ["newton"]


def _cuda_backend(jac):
    """(xp, lu_factor, lu_solve) when ``jac`` lives on a CUDA device."""
    if not type(jac).__module__.startswith(("jax", "jaxlib")):
        return None
    try:
        devs = jac.devices() if callable(getattr(jac, "devices", None)) \
            else {jac.device}
        if any(getattr(d, "platform", "") == "gpu" for d in devs):
            import jax.numpy as jnp
            import jax.scipy.linalg as jsl
            return jnp, jsl.lu_factor, jsl.lu_solve
    except Exception:
        return None
    return None


def newton(residual, jacobian, u0, *, tol: float = 1e-12,
           max_iter: int = 12, chord_ratio: float = 0.1,
           min_damping: float = 1.0 / 64.0, verbose: bool = False,
           min_updates: int = 0):
    """Solve residual(u) = 0 from u0.  Returns (u, info).

    info: converged, iters, res_scaled_inf, res_history, jacobian_evals,
    newton_steps (the per-step damping factors). min_updates can require
    recovery from a perturbed seed even when row equilibration makes its
    initial residual smaller than tol.
    """
    if not 0 <= min_updates < max_iter:
        raise ValueError('min_updates must lie in [0, max_iter)')
    u = np.asarray(u0, dtype=np.float64).copy()
    xp, factor, solve = np, lu_factor, lu_solve
    gpu = False
    r = np.asarray(residual(u))
    lu = piv = scale = None
    need_jac = True
    history, steps, jac_evals = [], [], 0

    def scaled_inf(res):
        return float(xp.max(xp.abs(res * scale))) if scale is not None else np.inf

    def done(u, info):
        return (np.asarray(u) if gpu else u), info

    for it in range(max_iter):
        fresh = need_jac
        if need_jac:
            jac = jacobian(u)
            jac_evals += 1
            if jac_evals == 1:
                cuda = _cuda_backend(jac)
                if cuda is not None:
                    xp, factor, solve = cuda
                    gpu = True
            if not gpu:
                jac = np.asarray(jac)
            scale = 1.0 / xp.maximum(xp.max(xp.abs(jac), axis=1), 1e-300)
            lu, piv = factor(scale[:, None] * jac)
        history.append(scaled_inf(r))
        if history[-1] <= tol and len(steps) >= min_updates:
            if verbose:
                print(f"[newton] converged at iter {it}: "
                      f"|R|_inf,scaled = {history[-1]:.3e}")
            return done(u, {"converged": True, "iters": it,
                            "res_scaled_inf": history[-1],
                            "res_history": history,
                            "jacobian_evals": jac_evals,
                            "newton_steps": steps})
        du = -solve((lu, piv), scale * r)
        norm0 = float(xp.linalg.norm(scale * r))
        t = 1.0
        while t >= min_damping:
            r_try = residual(u + t * du)
            if not gpu:
                r_try = np.asarray(r_try)
            if float(xp.linalg.norm(scale * r_try)) <= (1.0 - 1e-4 * t) * norm0:
                break
            t *= 0.5
        else:
            if not fresh:
                # a chord step on a reused Jacobian: refresh before stalling
                need_jac = True
                continue
            return done(u, {"converged": False, "iters": it,
                            "res_scaled_inf": history[-1],
                            "res_history": history,
                            "jacobian_evals": jac_evals,
                            "newton_steps": steps,
                            "reason": "line search stalled"})
        u = u + t * du
        contraction = float(xp.linalg.norm(scale * r_try)) / max(norm0, 1e-300)
        need_jac = (t < 1.0) or (contraction > chord_ratio)
        r = r_try
        steps.append(t)
        if verbose:
            print(f"[newton] iter {it}: |R| {norm0:.3e} -> "
                  f"{float(xp.linalg.norm(scale * r)):.3e} (t = {t:g})")

    final = scaled_inf(r)
    return done(u, {"converged": final <= tol and len(steps)>=min_updates, "iters": max_iter,
                    "res_scaled_inf": final, "res_history": history + [final],
                    "jacobian_evals": jac_evals, "newton_steps": steps,
                    "reason": "max_iter"})
