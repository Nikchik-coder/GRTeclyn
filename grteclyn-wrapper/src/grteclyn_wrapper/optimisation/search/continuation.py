"""Construct seeds and bisect failed continuation steps.

Potential knobs walk from the massless solution; spin continuation supplies
static twins for diagnostic radial work. Splits are bounded, so a failed
solve returns a failure instead of an unbounded retry loop.
"""
from __future__ import annotations

from .state import SearchContext
import math
import numpy as np
from ..matter_equations import MatterCollocationProblem
from ..exoticity import throat
from ..potentials import PolynomialPotential
from ..stability_radial import static_background, growth_rate
from . import evaluation


def nearest_seed(solved, key, scales, fallback):
    """Return the nearest solved fields in scaled L1 distance, or the fallback."""
    if not solved:
        return fallback
    near = min(solved, key=lambda previous:
               float(np.sum(np.abs((np.asarray(previous) - np.asarray(key)) / scales))))
    return solved[near]


def static_seed(ctx: SearchContext):
    """The J = 0, V = 0 root from the problem's own background (f_bg,
    psi_prof: the exact static member at gamma on the arctan map,
    B = 1, nu = omega = 0), scaled to the active size pin."""
    p0 = MatterCollocationProblem(
        eta0=1.0, gamma=ctx.sol.gamma, radial_map=ctx.grid, nx=ctx.nx, ny=ctx.ny,
        prescribe=("J", 0.0), pin=ctx.pin_row)
    F = np.asarray(p0.f_bg) * np.ones((1, ctx.ny + 1))
    zero, one = np.zeros_like(F), np.ones_like(F)
    psim_s = -math.pi * math.hypot(1.0, ctx.sol.gamma / (2.0 * math.pi))
    ts = throat(1.0, p0.map, p0.sx, p0.sy, p0.Dx, F, zero, one)
    if ctx.args.pin == "area":
        sigma0 = math.sqrt(ctx.th["area_throat"] / ts["area_throat"])
    else:
        sigma0 = ctx.th["R_e"] / ts["R_e"]
    return {"F": F, "W": zero, "N": zero, "B": one,
            "PSI": psim_s * np.asarray(p0.psi_prof), "omega": 0.0,
            "psim": psim_s, "sigma": sigma0,
            "xi_t": float(p0.map.xi_of_eta(ts["eta_throat"]))}


def spin_down(ctx: SearchContext, x, spin, cap=3):
    """The J = 0 twin by continuation in J at fixed knobs, from the
    spinning solve at x (J in thirds, a stalled leg bisected toward
    the last solved J, cap splits per leg): the route that does not
    depend on how far the nearest J = 0 seed sits in knob space."""
    j_spin = float(x[4]) if len(x) > 4 else ctx.J0
    prev, jlast = spin, j_spin
    for Jk in (2 * j_spin / 3, j_spin / 3, 0.0):
        pending, splits = [Jk], 0
        while pending:
            jt = pending[-1]
            row, nxt = evaluation.solve_at(ctx, x, prev, jval=jt)
            if nxt is None:
                splits += 1
                if splits > cap:
                    return None, f"spun down to J {jt:.3g}: {row['err']}"
                pending.append((jlast + jt) / 2.0)
                continue
            prev, jlast = nxt, jt
            pending.pop()
    return prev, None


def stab_at(ctx: SearchContext, x, key, spin):
    """The J = 0 twin's growth rate: a continued solve from the
    nearest J = 0 cache entry, else spin_down from the spinning solve
    at x; flatten, screen.  Returns (lam, None), or (None, why) when
    both routes failed."""
    m, q = float(x[0]), tuple(float(v) for v in x[1:4])
    near = min(ctx.state["solved_j0"],
               key=lambda s: float(np.sum(np.abs(
                   (np.array(s)[:4] - np.array(key)[:4])
                   / ctx.scales[:4]))))
    _, jnxt = evaluation.solve_at(ctx, x, ctx.state["solved_j0"][near], jval=0.0)
    route = "direct"
    if jnxt is None:
        (jnxt, why), route = spin_down(ctx, x, spin), "spun down"
        if jnxt is None:
            ctx.state["twins"]["failed"] += 1
            return None, why
    ctx.state["twins"][route] += 1
    ctx.state["solved_j0"][key] = jnxt
    pot = (None if m == 0.0 else
           PolynomialPotential.kink_q(m, float(jnxt["psim"]), q))
    bg = static_background(
        sx=ctx.sx_all, radial_map=ctx.grid,
        F0=jnxt["F"].mean(axis=1), P0=jnxt["B"].mean(axis=1),
        psi0=jnxt["PSI"].mean(axis=1), potential=pot)
    o = growth_rate(eta0=1.0, nx=ctx.args.stab_nx, background=bg,
                    radial_map=ctx.grid)
    return (0.0 if o.get("stable") else float(o["lam"])), None


def walk(ctx: SearchContext, chain, prev, jval=None, what="walk-in"):
    xlast, row = chain[0] * 0.0, None
    for xk in chain:
        pending, splits = [xk], 0
        while pending:
            xt = pending[-1]
            row, nxt = evaluation.solve_at(ctx, xt, prev, jval=jval)
            if nxt is None:
                splits += 1
                if splits > 6:
                    print(f"{what} FAILED at "
                          f"({', '.join(f'{v:g}' for v in xt)}): "
                          f"{row['err']} (after {splits - 1} splits)",
                          flush=True)
                    return None, None
                print(f"  {what} stall at "
                      f"({', '.join(f'{v:g}' for v in xt)}): "
                      f"{row['err']}; bisecting", flush=True)
                pending.append((xlast + xt) / 2.0)
                continue
            prev, xlast = nxt, xt
            pending.pop()
    return prev, row
