"""Pinned Newton solves and independent checks of search incumbents.

Fields use eta0 = 1 and the physical scale sigma. The unused Einstein
constraints gate acceptance independently of the Newton residual. A screen
interpolates; only successful refinement labels a saved result validated.
"""
from __future__ import annotations

from .state import SearchContext
import gc
import math
import time
import numpy as np
from ..matter_equations import MatterCollocationProblem
from ..potentials import PolynomialPotential
from ..exoticity import exotic_x
from ..resolution import check_candidate, save_checked
from ..solver.newton import newton
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import tail_ratio
from .state import TOL, C_GATE, CLEAN_GATE, CEILING, SAVE_CONVENTIONS


def solve_at(ctx: SearchContext, x, prev, jval=None):
    """One pinned solve at knob vector x, continued from prev, at
    the member's J (or ``jval`` -- the stability twin's branch, which
    takes the twin's stall cut).  When --free-J and jval is omitted,
    the fifth knob is the prescribed J."""
    t0 = time.time()
    stall_ok = ctx.args.stall_ok if jval is None else ctx.args.twin_stall_ok
    m, q = float(x[0]), tuple(float(v) for v in x[1:4])
    j_run = (float(jval) if jval is not None
             else (float(x[4]) if len(x) > 4 else ctx.J0))
    pot = (None if m == 0.0
           else (lambda pm, m=m, q=q: PolynomialPotential.kink_q(
               m, pm, q)))
    p2 = MatterCollocationProblem(
        eta0=1.0, gamma=ctx.sol.gamma, radial_map=ctx.grid, nx=ctx.nx, ny=ctx.ny,
        prescribe=("J", j_run), pin=ctx.pin_row, potential=pot)
    u0 = p2.pack(prev["F"] - p2.f_bg, prev["W"] - prev["omega"] * p2.q,
                 prev["N"], prev["B"] - 1.0,
                 prev["PSI"] - prev["psim"] * p2.psi_prof,
                 omega_inf=prev["omega"], psi_minus=prev["psim"],
                 sigma=prev["sigma"], xi_t=prev["xi_t"])
    try:
        u, info = newton(p2.residual, p2.jacobian, u0, tol=TOL)
    except Exception as err:
        return {"verdict": "FAILED", "err": str(err),
                "secs": time.time() - t0, "J": j_run}, None
    if (not np.isfinite(info["res_scaled_inf"])
            or (not info["converged"] and info["res_scaled_inf"] > stall_ok)):
        return {"verdict": "FAILED",
                "err": f"newton {info['res_scaled_inf']:.1e}, "
                       f"{info.get('reason', '?')}",
                "secs": time.time() - t0, "J": j_run}, None
    F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
    omega, psim = p2.unpack(u)[-2:]
    tt = p2.throat(u)
    diag = p2.diagnostics(u)
    mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
    e19 = float(np.max(np.abs(diag["E19"][mask]))) / ctx.d2
    e_c = float(np.max(np.abs(diag["E_c"][mask])))
    xv = exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx, F, Nf, B, PSI)
    tails = max(tail_ratio(PSI - psim * p2.psi_prof, axis=0),
                tail_ratio(B - 1.0, axis=0))
    if not all(np.isfinite(a).all() for a in
               (F, W, Nf, B, PSI, e19, e_c, xv["X"], xv["X_A"])):
        return {"verdict": "FAILED", "err": "nonfinite fields or diagnostics",
                "secs": time.time() - t0, "J": j_run}, None
    mon = max(e19, e_c)
    row = {"newton": info["res_scaled_inf"], "iters": info["iters"],
           "X": xv["X"], "X_A": xv["X_A"], "sigma": tt["sigma"],
           "psim": psim, "R_e": tt["sigma"] * xv["R_e"],
           "R_A": tt["sigma"] * xv["R_A"],
           "R_pol": tt["sigma"] * xv["R_pol"], "J": j_run,
           "e19": e19, "e_c": e_c, "tails": tails,
           "verdict": ("PASS" if mon <= CLEAN_GATE else
                       "FRONTIER" if mon <= CEILING else "ABOVE-GATE"),
           "secs": time.time() - t0}
    nxt = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
           "omega": omega, "psim": psim,
           "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
    ctx.state.setdefault("nodes", (np.asarray(p2.sx), np.asarray(p2.sy)))
    return row, nxt


def check_best(ctx: SearchContext, key, row, method):
    # Release old JAX executables before changing grid sizes. Only CPU
    # field arrays survive in the continuation cache.
    import jax
    gc.collect()
    jax.clear_caches()
    spin = dict(ctx.state["solved"][key], sx=ctx.state["nodes"][0],
                sy=ctx.state["nodes"][1], gamma=ctx.sol.gamma, map=ctx.grid)
    config = dict(m=float(key[0]), q=list(map(float, key[1:4])),
                  gamma=ctx.sol.gamma, J=float(row["J"]))
    check_d2 = (float(spin["psim"])*float(spin["sigma"])/math.pi)**2
    result, checked = check_candidate(
        spin, config, ctx.grids, ctx.pin_row, check_d2,
        ctx.checks_root/f"e{row['nfev']:04d}_{method}", method=method,
        score_key=ctx.score_key)
    if not result["passed"]:
        return None
    final = dict(row, **result["records"][-1])
    final.update(e19=final["E19"], e_c=final["E_c"])
    slot = "best_clean" if method == "refine" else "best_screened"
    # Rank checked candidates by the checked bill, not the coarse bill.
    if ctx.state[slot] is None or final[ctx.score_key] < ctx.state[slot][0]:
        if not ctx.args.no_save:
            save_checked(ctx.out.with_name(f"{ctx.out.stem}_{slot}.npz"),
                         checked, config,
                         dict(member=ctx.name, member_eta0=ctx.sol.eta0, pin=ctx.args.pin,
                              nfev=row["nfev"], X_v0=ctx.x_v0,
                              conventions=SAVE_CONVENTIONS), result)
        ctx.state[slot] = (final[ctx.score_key], key, final)
    return final
