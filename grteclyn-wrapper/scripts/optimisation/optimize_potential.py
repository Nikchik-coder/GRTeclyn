#!/usr/bin/env python
"""Campaign M: the bare-field potential optimizer over (m, q1, q2, q3).

The step-3 scans showed the shape family is at least two-dimensional
(the q3 fan broke the far-well-mass collapse), so rays are not enough:
this walks all four knobs together with derivative-free Nelder-Mead,
at pinned J and R_e on one member, every evaluation a full Newton solve
with the step-1/2 gates.  cal V = lam psi^2 (psi - psi_minus)^2 Q(psi),
Q = 1 + q1 u + q2 u^2 + q3 u^3, u = psi/psi_minus, lam = m^2/psi_minus^2.

The objective is the bill X = |VIQ|/R_e, with penalties instead of
constraints: an inadmissible point (min Q <= 0 on the kink, or m outside
[--m-min, --m-max]) or a Newton failure scores worst-so-far + 1 without
solving twice; a solved point whose monitors sit between the 1e-8 gate
and the 1e-6 ceiling counts as frontier and pays +0.1 so the simplex
prefers clean ground but can cross a noisy ridge; above 1e-6 it pays
+1.  Every evaluation continues Newton from the NEAREST solved point
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
        --nx 150 --ny 30 --x0 0.3,2.4,2.4,0 --gpu 0
"""

from __future__ import annotations

import argparse
import dataclasses
import math
import pathlib
import sys
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import tail_ratio
from grteclyn_wrapper.optimisation.exoticity import exotic_x, throat
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
from grteclyn_wrapper.optimisation.solver.device import select_device
from grteclyn_wrapper.optimisation.solver.newton import newton

TOL = 1e-14
STALL_OK = 1e-11
C_GATE = 0.05
CLEAN_GATE = 1e-8
CEILING = 1e-6
#: knob scales for the nearest-seed metric and the initial simplex
SCALES = np.array([0.1, 0.3, 0.3, 0.3])


def min_q(q) -> float:
    u = np.linspace(0.0, 1.0, 1001)
    acc = np.ones_like(u)
    for k, qk in enumerate(q):
        acc = acc + qk * u ** (k + 1)
    return float(np.min(acc))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--x0", default="0.3,2.4,2.4,0",
                    help="start (m, q1, q2, q3); the step-3 best clean "
                         "shape of the member is the right seed")
    ap.add_argument("--m-min", type=float, default=0.15,
                    help="smallest kink mass the grid resolves (m = 0.1 "
                         "misses the gate below 240x48, step-2 record)")
    ap.add_argument("--m-max", type=float, default=1.2)
    ap.add_argument("--maxfev", type=int, default=200)
    ap.add_argument("--fatol", type=float, default=2e-5,
                    help="X tolerance of the simplex stop")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    select_device(args.gpu, args.jac_chunk)
    x0 = np.array([float(v) for v in args.x0.split(",")])
    assert x0.size == 4, "--x0 takes m,q1,q2,q3"

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    out = pathlib.Path(args.out or f"runs/optimisation/opt/"
                                   f"{stem}_opt4_{nx}x{ny}.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text(
            "member\tnx\tny\tmass\tq1\tq2\tq3\tnewton\titers\tX\tsigma\t"
            "psi_minus\tR_e\tE19\tE_c\ttails\tminQ\tverdict\n")

    # the member holding J on its own grid, and its measured throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("J", J0))
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
          f"J {J0:.6e}; optimize from ({', '.join(f'{v:g}' for v in x0)})",
          flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev0 = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
             "omega": sol.eta0 * omega1, "psim": psim1,
             "sigma": sol.eta0, "xi_t": xi1}
    state = {"solved": {}, "nfev": 0,
             "best_clean": None, "best_frontier": None}

    def solve_at(x, prev):
        """One pinned solve at knob vector x, continued from prev."""
        t0 = time.time()
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        pot = (None if m == 0.0
               else (lambda pm, m=m, q=q: PolynomialPotential.kink_q(
                   m, pm, q)))
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0), pin=("R_e", th["R_e"]), potential=pot)
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
        if not info["converged"] and info["res_scaled_inf"] > STALL_OK:
            return {"verdict": "FAILED",
                    "err": f"newton {info['res_scaled_inf']:.1e}",
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
        return row, nxt

    def record(x, row):
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        tag = f"m {m:.4f} q ({', '.join(f'{v:+.3f}' for v in q)})"
        qvals = "\t".join(f"{v:.6g}" for v in q)
        if row["verdict"] == "FAILED":
            print(f"  [{state['nfev']}] {tag}: NEWTON FAILED "
                  f"({row['err']})  [{row['secs']:.0f}s]", flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{m:.6g}\t{qvals}\tnan\tnan\tnan\t"
                    f"nan\tnan\tnan\tnan\tnan\tnan\t{min_q(q):.3f}\t"
                    f"FAILED\n")
        else:
            print(f"  [{state['nfev']}] {tag}: newton {row['newton']:.1e} "
                  f"({row['iters']} it)  X {row['X']:.8e}  "
                  f"sigma {row['sigma']:.8f}  E19 {row['e19']:.1e}  "
                  f"E_c {row['e_c']:.1e}  tails {row['tails']:.1e}  "
                  f"{row['verdict']}  [{row['secs']:.0f}s]", flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{m:.6g}\t{qvals}\t"
                    f"{row['newton']:.3e}\t{row['iters']}\t"
                    f"{row['X']:.10e}\t{row['sigma']:.10f}\t"
                    f"{row['psim']:.10f}\t{row['R_e']:.10f}\t"
                    f"{row['e19']:.3e}\t{row['e_c']:.3e}\t"
                    f"{row['tails']:.3e}\t{min_q(q):.3f}\t"
                    f"{row['verdict']}\n")
        with out.open("a") as fh:
            fh.write(line)

    worst = [0.0]

    def objective(x):
        state["nfev"] += 1
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        if not (args.m_min <= m <= args.m_max) or min_q(q) <= 0.0:
            print(f"  [{state['nfev']}] m {m:.4f} q "
                  f"({', '.join(f'{v:+.3f}' for v in q)}): inadmissible",
                  flush=True)
            return worst[0] + 1.0
        key = tuple(np.round(np.asarray(x, float), 10))
        if not state["solved"]:
            seed = prev0
        else:
            near = min(state["solved"],
                       key=lambda s: float(np.sum(np.abs(
                           (np.array(s) - np.array(key)) / SCALES))))
            seed = state["solved"][near]
        row, nxt = solve_at(x, seed)
        record(x, row)
        if nxt is None:
            return worst[0] + 1.0
        state["solved"][key] = nxt
        mon_pen = (0.0 if row["verdict"] == "PASS"
                   else 0.1 if row["verdict"] == "FRONTIER" else 1.0)
        val = row["X"] + mon_pen
        worst[0] = max(worst[0], val)
        for slot, ok in (("best_clean", row["verdict"] == "PASS"),
                         ("best_frontier", row["verdict"] != "ABOVE-GATE")):
            if ok and (state[slot] is None or row["X"] < state[slot][0]):
                state[slot] = (row["X"], key, dict(row))
        return val

    # the walk-in: m in thirds, then the shape in 0.3 steps
    prev = prev0
    m0 = float(x0[0])
    chain = [np.array([mk, 0, 0, 0]) for mk in
             (0.0, m0 / 3.0, 2 * m0 / 3.0, m0)]
    n_q = max(1, int(math.ceil(max(abs(v) for v in x0[1:]) / 0.3))
              if np.any(x0[1:]) else 1)
    chain += [np.concatenate([[m0], x0[1:] * k / n_q])
              for k in range(1, n_q + 1)]
    # a leg that stalls gets bisected toward the last solved point (the
    # stiff-spin straight line stalls marginally where the step-3 fan got
    # through on another route); capped so a true wall still stops the run
    xlast = chain[0] * 0.0
    for xk in chain:
        pending, splits = [xk], 0
        while pending:
            xt = pending[-1]
            row, nxt = solve_at(xt, prev)
            if nxt is None:
                splits += 1
                if splits > 6:
                    print(f"walk-in FAILED at "
                          f"({', '.join(f'{v:g}' for v in xt)}): "
                          f"{row['err']} (after {splits - 1} splits)",
                          flush=True)
                    return 1
                print(f"  walk-in stall at "
                      f"({', '.join(f'{v:g}' for v in xt)}): {row['err']}; "
                      f"bisecting", flush=True)
                pending.append((xlast + xt) / 2.0)
                continue
            prev, xlast = nxt, xt
            pending.pop()
    state["solved"][tuple(np.round(x0, 10))] = prev
    print(f"walk-in done: X {row['X']:.8e} at x0", flush=True)
    worst[0] = row["X"] + 1.0

    from scipy.optimize import minimize

    simplex = np.vstack([x0] + [x0 + SCALES[i] * np.eye(4)[i]
                                for i in range(4)])
    res = minimize(objective, x0, method="Nelder-Mead",
                   options={"maxfev": args.maxfev, "fatol": args.fatol,
                            "xatol": 1e-3, "initial_simplex": simplex,
                            "adaptive": True})
    print(f"\nsimplex stopped: {res.message} after {state['nfev']} "
          f"evaluations", flush=True)
    for slot, label in (("best_clean", "best clean (<= 1e-8)"),
                        ("best_frontier", "best frontier (<= 1e-6)")):
        if state[slot] is None:
            print(f"{label}: none", flush=True)
        else:
            xb, key, row = state[slot]
            print(f"{label}: X {xb:.8e} at m {key[0]:g} "
                  f"q ({', '.join(f'{v:g}' for v in key[1:])})  "
                  f"E19 {row['e19']:.1e}  E_c {row['e_c']:.1e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
