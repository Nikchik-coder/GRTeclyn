#!/usr/bin/env python
"""Campaign M: the bare-field potential optimizer over (m, q1, q2, q3).

The step-3 scans showed the shape family is at least two-dimensional
(the q3 fan broke the far-well-mass collapse), so rays are not enough:
this walks all four knobs together with a derivative-free engine, at
pinned J and R_e on one member, every evaluation a full Newton solve
with the step-1/2 gates.  cal V = lam psi^2 (psi - psi_minus)^2 Q(psi),
Q = 1 + q1 u + q2 u^2 + q3 u^3, u = psi/psi_minus, lam = m^2/psi_minus^2.

Engines (--engine): nm is scipy Nelder-Mead (the 2026-10-28 first pass;
a simplex collapses into one basin and stops improving past ~150
evals), cma is CMA-ES (the cma package): population-based, adapts the
step covariance, tolerates the FAILED/FRONTIER penalty cliffs, and can
leave a basin, so it is the engine for fresh starts and bigger budgets.
Both share the same objective, penalties, nearest-solved-seed
continuation cache and TSV.  The gradient path (implicit
differentiation of the bill through the solved state, the step-6
convergence item) is not wired yet: nothing here uses dX/dknobs.

The objective is the bill X = |VIQ|/R_e, with penalties instead of
constraints: an inadmissible point (min Q <= 0 on the kink, m outside
[--m-min, --m-max], or any q outside [--q-min, --q-max]) or a Newton
failure scores DEATH + 10 (DEATH = 1e3) without solving twice; a
solved point whose unused-constraint residual (E19, E_c) sits between
the 1e-8 gate and the 1e-6 ceiling counts as frontier and pays +0.1
so the search prefers clean ground but can cross a noisy ridge;
above 1e-6 is infeasible (DEATH + log10(residual/1e-6)), so CMA
cannot rank cheaper rejected points over each other and walk q3 off
the box (2026-10-29: X+1 did that on the drainholes).  Every
evaluation continues Newton from the NEAREST solved point
(L1 in scaled knob units), the cache growing as the simplex moves; rows
append to the scan-format TSV (--out; default under
runs/optimisation/opt/).  The walk-in to --x0 runs the ladder's anchor
chain (m in thirds, then the shape in 0.3 steps along the straight
line).  Reported at the end: best clean, best frontier, evaluation
counts.  A Newton failure anywhere is a verdict, not an error.

Run through capped_job.sh; solver jobs take a card by default
(2026-10-28), so pass --gpu N after nvidia-smi:

    grteclyn-wrapper/scripts/ops/capped_job.sh start opt4-0003-150 \\
        --threads 4 --mem 220 --timeout 10800 -- \\
        grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/optimisation/optimize_potential.py \\
        results/spinningwormhole/solutions/fam_b/fam_b_0003.json \\
        --nx 150 --ny 30 --x0 0.3,0,0,0 --gpu 0
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import pathlib
import sys
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
    lobatto,
    tail_ratio,
)
from grteclyn_wrapper.optimisation.exoticity import exotic_x, throat
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
from grteclyn_wrapper.optimisation.solver.device import select_device
from grteclyn_wrapper.optimisation.solver.newton import newton
from grteclyn_wrapper.optimisation.stability_radial import (
    growth_rate,
    static_background,
)

TOL = 1e-14
STALL_OK = 1e-11
C_GATE = 0.05
CLEAN_GATE = 1e-8
CEILING = 1e-6
# 2026-10-29: X+1 ranked cheaper ABOVE-GATE over each other and walked
# q3 to 17 on drainholes (3 accepted in 400).  Any accepted X (~1-5)
# beats this floor; log10(residual/CEILING) ranks the rejected toward
# the 1e-6 ceiling.
DEATH = 1e3
#: knob scales for the nearest-seed metric and the initial simplex
SCALES = np.array([0.1, 0.3, 0.3, 0.3])
FIELDS = ("F", "W", "N", "B", "PSI")
SAVE_CONVENTIONS = (
    "F, W, N, B, PSI on the collocation nodes of the pinned problem (sx "
    "radial xi, sy = cos 2 theta) in grid units (eta0 = 1): ds^2 = -e^F "
    "dt^2 + B^2 e^-F [e^nu (deta^2 + h dtheta^2) + h sin^2 theta (dphi - "
    "W dt)^2], nu = N sin^2 theta, h = eta^2 + 1, eta = radial_map(sx).  "
    "Physical lengths are sigma times the grid's; W and omega scale as "
    "1/sigma.  psi = sqrt(4 pi) phi, cal V = 8 pi V, potential_coeffs "
    "ascending in psi for the physical cal V (the rows use sigma^2 cal "
    "V); psim = psi(-inf).")


def min_q(q) -> float:
    u = np.linspace(0.0, 1.0, 1001)
    acc = np.ones_like(u)
    for k, qk in enumerate(q):
        acc = acc + qk * u ** (k + 1)
    return float(np.min(acc))


def death(extra: float = 0.0) -> float:
    return DEATH + extra


def monitor_overflow(row: dict) -> float:
    try:
        mon = max(float(row["e19"]), float(row["e_c"]))
    except (KeyError, TypeError, ValueError):
        return 10.0
    return math.log10(max(mon / CEILING, 1.0))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--x0", default="0.3,0,0,0",
                    help="start (m, q1, q2, q3); the pure kink at the "
                         "mass this grid resolves (2026-10-29: not the "
                         "shape-scan best point)")
    ap.add_argument("--m-min", type=float, default=0.15,
                    help="smallest kink mass the grid resolves (m = 0.1 "
                         "misses the gate below 240x48, step-2 record)")
    ap.add_argument("--m-max", type=float, default=1.2)
    ap.add_argument("--q-min", type=float, default=-2.0,
                    help="lower bound on each of q1, q2, q3 (the step-3 "
                         "shape box, with room for a mild negative q3)")
    ap.add_argument("--q-max", type=float, default=8.0,
                    help="upper bound on each of q1, q2, q3 (the step-3 "
                         "shape box; D51's rejected basin sat at q3 ~ 17)")
    ap.add_argument("--m-step", type=float, default=SCALES[0],
                    help="the mass knob's scale (CMA step, simplex edge, "
                         "seed metric); m is physical, its stiffness is "
                         "m R_e, so a member with a larger throat takes "
                         "m, its bounds and this step scaled by 1/R_e")
    ap.add_argument("--engine", choices=["nm", "cma"], default="nm",
                    help="nm: scipy Nelder-Mead (one basin, the first "
                         "pass); cma: CMA-ES (population-based, escapes "
                         "a collapsed simplex, the better engine for "
                         "fresh starts)")
    ap.add_argument("--sigma0", type=float, default=1.0,
                    help="cma: global step multiplier on the per-knob "
                         "SCALES")
    ap.add_argument("--popsize", type=int, default=None,
                    help="cma population (default 4 + 3 ln n = 8)")
    ap.add_argument("--seed", type=int, default=7,
                    help="cma RNG seed (D21 used 7; a new member needs a "
                         "fresh seed or it replays D21's knob sequence)")
    ap.add_argument("--stability", action="store_true",
                    help="score stability too: every evaluation also "
                         "solves the knobs at J = 0 (from its own "
                         "continuation cache, else by spinning the "
                         "evaluation's solve down in J), runs the gated "
                         "radial screen on the twin and pays stab-weight * "
                         "lam*eta0 (decided 2026-10-28: one score in "
                         "the loop, two axes on the frontier)")
    ap.add_argument("--stab-weight", type=float, default=1.0,
                    help="price of the growth rate (classical lam*eta0 "
                         "is 1.18 against X ~ 2-3)")
    ap.add_argument("--stab-nx", type=int, default=150,
                    help="screen grid inside the loop (its internal "
                         "0.7-coarse match grid comes free)")
    ap.add_argument("--stall-ok", type=float, default=STALL_OK,
                    help="the bill solve's Newton stall cut (default: the "
                         "step-1 gate); the drainhole (gamma = -pi) floors "
                         "at 1e-11 to 2e-10 on stiff shapes, a line-search "
                         "stall bisection does not lift, and the identity "
                         "monitors gate every accepted solve regardless")
    ap.add_argument("--twin-stall-ok", type=float, default=1e-10,
                    help="the twin branch's Newton stall cut (the bill "
                         "solve keeps the step-1 gate 1e-11): stiff J = 0 "
                         "shapes stall at 1e-11 to 1e-10 at 150x30, and "
                         "the twin only feeds the radial screen, whose "
                         "two-grid match tolerates far larger background "
                         "errors")
    ap.add_argument("--stab-fail-pen", type=float, default=0.25,
                    help="penalty when the J = 0 twin solves by neither "
                         "route: stability uncertifiable, not "
                         "disqualifying")
    ap.add_argument("--maxfev", type=int, default=200)
    ap.add_argument("--fatol", type=float, default=2e-5,
                    help="X tolerance of the simplex stop")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--J", type=float, default=None, dest="J_pin",
                    help="optimize at this J instead of the member's "
                         "(0 is the static drainhole of the same family)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-save", action="store_true",
                    help="skip the .npz of each best slot's solved fields "
                         "(written next to the TSV by default)")
    ap.add_argument("--save-accepted", action="store_true", default=True,
                    help="also write a .npz for every PASS and FRONTIER "
                         "evaluation (the family a later grid-check reads; "
                         "on by default)")
    ap.add_argument("--no-save-accepted", action="store_false",
                    dest="save_accepted")
    args = ap.parse_args()
    select_device(args.gpu, args.jac_chunk)
    x0 = np.array([float(v) for v in args.x0.split(",")])
    scales = np.array([args.m_step, *SCALES[1:]])
    assert x0.size == 4, "--x0 takes m,q1,q2,q3"
    assert args.q_min < args.q_max, "--q-min must be < --q-max"
    if not (args.m_min <= x0[0] <= args.m_max) or np.any(
            (x0[1:] < args.q_min) | (x0[1:] > args.q_max)):
        ap.error("--x0 sits outside the m or q bounds")

    sol = Solution.load(args.solution)
    J_member = float(sol.meta["prescribed"]["J"])
    J0 = J_member if args.J_pin is None else float(args.J_pin)
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    out = pathlib.Path(args.out or f"runs/optimisation/opt/{stem}_opt4"
                                   f"{'s' if args.stability else ''}_"
                                   f"{nx}x{ny}.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text(
            "member\tnx\tny\tmass\tq1\tq2\tq3\tnewton\titers\tX\tsigma\t"
            "psi_minus\tR_e\tE19\tE_c\ttails\tminQ\tverdict"
            + ("\tlam_eta0\n" if args.stability else "\n"))

    # the member holding J on its own grid, and its measured throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("J", J_member))
    F0 = sol.eval_grid("f", p1.sx, p1.sy)
    W0 = sol.eval_grid("w", p1.sx, p1.sy)
    N0 = sol.eval_grid("N", p1.sx, p1.sy)
    zero = np.zeros_like(F0)
    u1, i1 = newton(p1.residual, p1.jacobian,
                    p1.pack(F0 - p1.f_bg, W0 - sol.omega_inf * p1.q,
                            N0, zero, zero, omega_inf=sol.omega_inf,
                            psi_minus=psim0), tol=TOL)
    F1, W1, N1, B1, P1 = (np.asarray(a) for a in p1.fields(u1))
    omega1, psim1 = p1.unpack(u1)[-2:]
    th = throat(p1.eta0, p1.map, p1.sx, p1.sy, p1.Dx, F1, N1, B1)
    xi1 = float(p1.map.xi_of_eta(th["eta_throat"]))
    print(f"{name} ({nx}x{ny}, eta0 {sol.eta0:g}, gamma {sol.gamma:g}): "
          f"J-held {i1['res_scaled_inf']:.1e}; R_e {th['R_e']:.10f}, "
          f"J {J_member:.6e}; optimize from ({', '.join(f'{v:g}' for v in x0)})",
          flush=True)
    if J0 != J_member:
        print(f"optimize at J {J0:g} (member holds {J_member:g})",
              flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev0 = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
             "omega": sol.eta0 * omega1, "psim": psim1,
             "sigma": sol.eta0, "xi_t": xi1}
    state = {"solved": {}, "nfev": 0,
             "best_clean": None, "best_frontier": None}

    def solve_at(x, prev, jval=None):
        """One pinned solve at knob vector x, continued from prev, at
        the member's J (or ``jval`` -- the stability twin's branch, which
        takes the twin's stall cut)."""
        t0 = time.time()
        stall_ok = args.stall_ok if jval is None else args.twin_stall_ok
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        pot = (None if m == 0.0
               else (lambda pm, m=m, q=q: PolynomialPotential.kink_q(
                   m, pm, q)))
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0 if jval is None else jval),
            pin=("R_e", th["R_e"]), potential=pot)
        u0 = p2.pack(prev["F"] - p2.f_bg, prev["W"] - prev["omega"] * p2.q,
                     prev["N"], prev["B"] - 1.0,
                     prev["PSI"] - prev["psim"] * p2.psi_prof,
                     omega_inf=prev["omega"], psi_minus=prev["psim"],
                     sigma=prev["sigma"], xi_t=prev["xi_t"])
        try:
            u, info = newton(p2.residual, p2.jacobian, u0, tol=TOL)
        except Exception as err:
            return {"verdict": "FAILED", "err": str(err),
                    "secs": time.time() - t0}, None
        if not info["converged"] and info["res_scaled_inf"] > stall_ok:
            return {"verdict": "FAILED",
                    "err": f"newton {info['res_scaled_inf']:.1e}, "
                           f"{info.get('reason', '?')}",
                    "secs": time.time() - t0}, None
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        diag = p2.diagnostics(u)
        mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        xv = exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx, F, Nf, B, PSI)
        tails = max(tail_ratio(PSI - psim * p2.psi_prof, axis=0),
                    tail_ratio(B - 1.0, axis=0))
        mon = max(e19, e_c)
        row = {"newton": info["res_scaled_inf"], "iters": info["iters"],
               "X": xv["X"], "sigma": tt["sigma"], "psim": psim,
               "R_e": tt["R_e"], "e19": e19, "e_c": e_c, "tails": tails,
               "verdict": ("PASS" if mon <= CLEAN_GATE else
                           "FRONTIER" if mon <= CEILING else "ABOVE-GATE"),
               "secs": time.time() - t0}
        nxt = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
               "omega": omega, "psim": psim,
               "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
        state.setdefault("nodes", (np.asarray(p2.sx), np.asarray(p2.sy)))
        return row, nxt

    def record(x, row):
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        tag = f"m {m:.4f} q ({', '.join(f'{v:+.3f}' for v in q)})"
        qvals = "\t".join(f"{v:.6g}" for v in q)
        stab_col = ""
        stab_tag = ""
        if args.stability:
            lam = row.get("lam")
            stab_col = (f"\t{lam:.8f}" if lam is not None else "\tnan")
            stab_tag = (f"  lam {lam:.4f}" if lam is not None
                        else f"  J0-FAIL ({row['j0_fail']})"
                        if row.get("j0_fail") else "")
        if row["verdict"] == "FAILED":
            print(f"  [{state['nfev']}] {tag}: NEWTON FAILED "
                  f"({row['err']})  [{row['secs']:.0f}s]", flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{m:.6g}\t{qvals}\tnan\tnan\tnan\t"
                    f"nan\tnan\tnan\tnan\tnan\tnan\t{min_q(q):.3f}\t"
                    f"FAILED{stab_col}\n")
        else:
            print(f"  [{state['nfev']}] {tag}: newton {row['newton']:.1e} "
                  f"({row['iters']} it)  X {row['X']:.8e}  "
                  f"sigma {row['sigma']:.8f}  E19 {row['e19']:.1e}  "
                  f"E_c {row['e_c']:.1e}  tails {row['tails']:.1e}  "
                  f"{row['verdict']}{stab_tag}  [{row['secs']:.0f}s]",
                  flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{m:.6g}\t{qvals}\t"
                    f"{row['newton']:.3e}\t{row['iters']}\t"
                    f"{row['X']:.10e}\t{row['sigma']:.10f}\t"
                    f"{row['psim']:.10f}\t{row['R_e']:.10f}\t"
                    f"{row['e19']:.3e}\t{row['e_c']:.3e}\t"
                    f"{row['tails']:.3e}\t{min_q(q):.3f}\t"
                    f"{row['verdict']}{stab_col}\n")
        with out.open("a") as fh:
            fh.write(line)

    state["solved_j0"] = {}
    state["best_stable"] = None
    state["twins"] = {"direct": 0, "spun down": 0, "failed": 0}
    sx_all, _ = lobatto(nx)

    def static_seed():
        """The J = 0, V = 0 root from the problem's own background (f_bg,
        psi_prof: the exact static member at gamma on the arctan map,
        B = 1, nu = omega = 0), scaled to the R_e pin."""
        p0 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", 0.0), pin=("R_e", th["R_e"]))
        F = np.asarray(p0.f_bg) * np.ones((1, ny + 1))
        zero, one = np.zeros_like(F), np.ones_like(F)
        psim_s = -math.pi * math.hypot(1.0, sol.gamma / (2.0 * math.pi))
        ts = throat(1.0, p0.map, p0.sx, p0.sy, p0.Dx, F, zero, one)
        return {"F": F, "W": zero, "N": zero, "B": one,
                "PSI": psim_s * np.asarray(p0.psi_prof), "omega": 0.0,
                "psim": psim_s, "sigma": th["R_e"] / ts["R_e"],
                "xi_t": float(p0.map.xi_of_eta(ts["eta_throat"]))}

    if J0 == 0.0:
        prev0 = static_seed()
        print("J = 0: start from the static drainhole seed", flush=True)

    def spin_down(x, spin, cap=3):
        """The J = 0 twin by continuation in J at fixed knobs, from the
        spinning solve at x (J in thirds, a stalled leg bisected toward
        the last solved J, cap splits per leg): the route that does not
        depend on how far the nearest J = 0 seed sits in knob space."""
        prev, jlast = spin, J0
        for Jk in (2 * J0 / 3, J0 / 3, 0.0):
            pending, splits = [Jk], 0
            while pending:
                jt = pending[-1]
                row, nxt = solve_at(x, prev, jval=jt)
                if nxt is None:
                    splits += 1
                    if splits > cap:
                        return None, f"spun down to J {jt:.3g}: {row['err']}"
                    pending.append((jlast + jt) / 2.0)
                    continue
                prev, jlast = nxt, jt
                pending.pop()
        return prev, None

    def stab_at(x, key, spin):
        """The J = 0 twin's growth rate: a continued solve from the
        nearest J = 0 cache entry, else spin_down from the spinning solve
        at x; flatten, screen.  Returns (lam, None), or (None, why) when
        both routes failed."""
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        near = min(state["solved_j0"],
                   key=lambda s: float(np.sum(np.abs(
                       (np.array(s) - np.array(key)) / scales))))
        _, jnxt = solve_at(x, state["solved_j0"][near], jval=0.0)
        route = "direct"
        if jnxt is None:
            (jnxt, why), route = spin_down(x, spin), "spun down"
            if jnxt is None:
                state["twins"]["failed"] += 1
                return None, why
        state["twins"][route] += 1
        state["solved_j0"][key] = jnxt
        pot = (None if m == 0.0 else
               PolynomialPotential.kink_q(m, float(jnxt["psim"]), q))
        bg = static_background(
            sx=sx_all, radial_map=grid,
            F0=jnxt["F"].mean(axis=1), P0=jnxt["B"].mean(axis=1),
            psi0=jnxt["PSI"].mean(axis=1), potential=pot)
        o = growth_rate(eta0=1.0, nx=args.stab_nx, background=bg,
                        radial_map=grid)
        return (0.0 if o.get("stable") else float(o["lam"])), None

    def dump_npz(path, key, row, slot=None):
        """Solved fields and what rebuilds them: collocation nodes, the
        map, sigma, the potential coefficients, and the J = 0 twin."""
        spin = state["solved"][key]
        twin = state["solved_j0"].get(key)
        m, q = float(key[0]), [float(v) for v in key[1:]]
        pot = PolynomialPotential.kink_q(m, float(spin["psim"]), tuple(q))
        arrays = {k: np.asarray(spin[k]) for k in FIELDS}
        if twin is not None:
            arrays.update({f"j0_{k}": np.asarray(twin[k]) for k in FIELDS})
        scal = ("omega", "psim", "sigma", "xi_t")
        meta = {
            "member": name, "slot": slot, "nx": nx, "ny": ny,
            "nfev": state["nfev"], "member_eta0": sol.eta0,
            "gamma": sol.gamma,
            "radial_map": {"class": type(grid).__name__,
                           **dataclasses.asdict(grid)},
            "J": J0, "R_e": th["R_e"], "m": m, "q": q,
            "potential_coeffs": [float(c) for c in pot.coeffs],
            **{k: float(spin[k]) for k in scal},
            "X": row["X"], "X_v0": x_v0, "E19": row["e19"],
            "E_c": row["e_c"],
            "verdict": row["verdict"], "lam_eta0": row.get("lam"),
            "j0": (None if twin is None
                   else {k: float(twin[k]) for k in scal}),
            "conventions": SAVE_CONVENTIONS,
        }
        np.savez(path, sx=state["nodes"][0], sy=state["nodes"][1],
                 meta=json.dumps(meta, default=float), **arrays)
        return path

    def save_solution(slot):
        _, key, row = state[slot]
        path = out.with_name(f"{out.stem}_{slot}.npz")
        return dump_npz(path, key, row, slot=slot)

    def objective(x):
        state["nfev"] += 1
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        if (not (args.m_min <= m <= args.m_max)
                or any(not (args.q_min <= qk <= args.q_max) for qk in q)
                or min_q(q) <= 0.0):
            print(f"  [{state['nfev']}] m {m:.4f} q "
                  f"({', '.join(f'{v:+.3f}' for v in q)}): inadmissible",
                  flush=True)
            return death(10.0)
        key = tuple(np.round(np.asarray(x, float), 10))
        if not state["solved"]:
            seed = prev0
        else:
            near = min(state["solved"],
                       key=lambda s: float(np.sum(np.abs(
                           (np.array(s) - np.array(key)) / scales))))
            seed = state["solved"][near]
        row, nxt = solve_at(x, seed)
        lam = None
        if nxt is not None and args.stability:
            lam, row["j0_fail"] = stab_at(x, key, nxt)
            row["lam"] = lam
        record(x, row)
        if nxt is None:
            return death(10.0)
        state["solved"][key] = nxt
        if (args.save_accepted and not args.no_save
                and row["verdict"] in ("PASS", "FRONTIER")
                and "nodes" in state):
            dump_npz(out.with_name(f"{out.stem}_e{state['nfev']:04d}.npz"),
                     key, row, slot=f"e{state['nfev']:04d}")
        if row["verdict"] == "ABOVE-GATE":
            return death(monitor_overflow(row))
        mon_pen = 0.0 if row["verdict"] == "PASS" else 0.1
        val = row["X"] + mon_pen
        if args.stability:
            val += (args.stab_fail_pen if lam is None
                    else args.stab_weight * lam)
        for slot, ok in (("best_clean", row["verdict"] == "PASS"),
                         ("best_frontier", row["verdict"] != "ABOVE-GATE"),
                         ("best_stable", args.stability and lam == 0.0
                          and row["verdict"] == "PASS")):
            if ok and (state[slot] is None or row["X"] < state[slot][0]):
                state[slot] = (row["X"], key, dict(row))
        return val

    # the walk-in: m in thirds, then the shape in 0.3 steps.  A leg that
    # stalls gets bisected toward the last solved point (the stiff-spin
    # straight line stalls marginally where the step-3 fan got through
    # on another route); capped so a true wall still stops the run
    m0 = float(x0[0])
    chain = [np.array([mk, 0, 0, 0]) for mk in
             (0.0, m0 / 3.0, 2 * m0 / 3.0, m0)]
    n_q = max(1, int(math.ceil(max(abs(v) for v in x0[1:]) / 0.3))
              if np.any(x0[1:]) else 1)
    chain += [np.concatenate([[m0], x0[1:] * k / n_q])
              for k in range(1, n_q + 1)]

    def walk(chain, prev, jval=None, what="walk-in"):
        xlast, row = chain[0] * 0.0, None
        for xk in chain:
            pending, splits = [xk], 0
            while pending:
                xt = pending[-1]
                row, nxt = solve_at(xt, prev, jval=jval)
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

    row_v0, _ = solve_at(np.zeros(4), prev0)
    x_v0 = row_v0.get("X")
    if x_v0 is None:
        print(f"classical (V = 0) FAILED: {row_v0['err']}", flush=True)
        return 1
    print(f"classical (V = 0): X {x_v0:.8e}  E19 {row_v0['e19']:.1e}  "
          f"E_c {row_v0['e_c']:.1e}", flush=True)

    prev, row = walk(chain, prev0)
    if prev is None:
        return 1
    state["solved"][tuple(np.round(x0, 10))] = prev
    print(f"walk-in done: X {row['X']:.8e} at x0", flush=True)

    if args.stability:
        # the J = 0 branch: J down in thirds at V = 0, then the same
        # knob chain -- its cache seeds every twin solve in the loop
        jprev, why = spin_down(np.zeros(4), prev0, cap=6)
        if jprev is None:
            print(f"J walk failed ({why}); J = 0 from the static member",
                  flush=True)
            _, jprev = solve_at(np.zeros(4), static_seed(), jval=0.0)
            if jprev is None:
                print("J = 0 static seed FAILED", flush=True)
                return 1
        print(f"J = 0 base: sigma {jprev['sigma']:.8f}", flush=True)
        jprev, _ = walk(chain, jprev, jval=0.0, what="J0 walk-in")
        if jprev is None:
            return 1
        state["solved_j0"][tuple(np.round(x0, 10))] = jprev
        lam0, _ = stab_at(x0, tuple(np.round(x0, 10)), prev)
        print(f"J0 walk-in done: lam*eta0 at x0 "
              f"{lam0 if lam0 is not None else float('nan'):.6f}",
              flush=True)

    if args.engine == "cma":
        import cma

        es = cma.CMAEvolutionStrategy(
            list(x0), args.sigma0,
            {"CMA_stds": list(scales),
             "bounds": [[args.m_min, args.q_min, args.q_min, args.q_min],
                        [args.m_max, args.q_max, args.q_max, args.q_max]],
             "popsize": args.popsize, "maxfevals": args.maxfev,
             "tolfun": args.fatol, "verbose": -9, "seed": args.seed})
        while not es.stop() and state["nfev"] < args.maxfev:
            xs = es.ask()
            es.tell(xs, [objective(np.asarray(xv)) for xv in xs])
        print(f"\ncma stopped: {dict(es.stop()) or 'maxfev'} after "
              f"{state['nfev']} evaluations", flush=True)
    else:
        from scipy.optimize import minimize

        simplex = np.vstack([x0] + [x0 + scales[i] * np.eye(4)[i]
                                    for i in range(4)])
        res = minimize(objective, x0, method="Nelder-Mead",
                       options={"maxfev": args.maxfev, "fatol": args.fatol,
                                "xatol": 1e-3, "initial_simplex": simplex,
                                "adaptive": True})
        print(f"\nsimplex stopped: {res.message} after {state['nfev']} "
              f"evaluations", flush=True)
    slots = [("best_clean", "best clean (<= 1e-8)"),
             ("best_frontier", "best frontier (<= 1e-6)")]
    if args.stability:
        slots.append(("best_stable", "best stable clean (lam = 0)"))
    for slot, label in slots:
        if state[slot] is None:
            print(f"{label}: none", flush=True)
        else:
            xb, key, row = state[slot]
            stab = (f"  lam {row['lam']:.4f}"
                    if row.get("lam") is not None else "")
            print(f"{label}: X {xb:.8e} ({100 * (xb / x_v0 - 1):+.1f} % "
                  f"vs V = 0) at m {key[0]:g} "
                  f"q ({', '.join(f'{v:g}' for v in key[1:])})  "
                  f"E19 {row['e19']:.1e}  E_c {row['e_c']:.1e}{stab}",
                  flush=True)
    if args.stability:
        tw = state["twins"]
        print(f"J = 0 twins: {tw['direct']} direct, {tw['spun down']} "
              f"spun down, {tw['failed']} failed", flush=True)
    if not args.no_save:
        for slot, _ in slots:
            if state[slot] is not None:
                print(f"saved {slot}: {save_solution(slot)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
