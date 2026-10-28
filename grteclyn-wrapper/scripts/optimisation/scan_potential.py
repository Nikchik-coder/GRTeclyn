#!/usr/bin/env python
"""Campaign M step 3: the bill across the potential's shape and gamma.

From a saved V = 0 member: hold its J on its own grid, measure the
throat, then at pinned J and R_e walk one of two axes and measure the
bill X = |VIQ|/R_e per point, the step-1/2 gates printed on every row:

  - the shape scan (default): cal V = lam psi^2 (psi - psi_minus)^2
    Q(psi) with Q = 1 + q1 u + q2 u^2 in u = psi/psi_minus
    (potentials.kink_q), over the declared (q1, q2) grid at fixed kink
    mass.  A point whose Q touches <= 0 on the kink is inadmissible
    (the psi_minus end stops being a vacuum) and is skipped.  Each
    point continues Newton from the nearest solved neighbour.
  - the gamma scan (--gammas): the end-mass asymmetry, continued in
    the given order from the member's own gamma, at the pure kink.
  - the ray walk (--rays "dq1,dq2;..."): open-ended continuation
    outward from the kink along each (dq1, dq2) direction, one step
    per rung, with NO preset box (decided 2026-10-28): a ray stops
    only when the solutions themselves say stop -- Newton fails, the
    unimposed monitors exceed 1e-6 on two consecutive rungs (well past
    the grid's floor scatter: the resolution limit), or X rises on
    three consecutive rungs (the minimum is behind us).

The anchor chain is the ladder's (first_matter_solve.py): the m = 0
pinned solve, then the pure kink continued in thirds of the scan mass.
Per row: Newton's verdict, X and its shift against the pure-kink
anchor, sigma, psi_minus, the unimposed monitors E19/D^2 and E_c
inside C >= 0.05 (gate 1e-8), the spectral tails, min Q.  Rows also
append to a TSV (--out; default under runs/optimisation/scans/).  A
Newton failure is a verdict, not an error: the row prints and the walk
continues from the solved set.

Run through capped_job.sh / pipeline.py; a card needs the standing go.
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
C_GATE = 0.05
MONITOR_GATE = 1e-8

TSV_HEADER = ("member\tnx\tny\tmode\tmass\tgamma\tq1\tq2\tnewton\titers\t"
              "X\tdX_kink\tsigma\tpsi_minus\tR_e\tE19\tE_c\ttails\tminQ\t"
              "verdict\n")


def min_q(q1: float, q2: float) -> float:
    u = np.linspace(0.0, 1.0, 1001)
    return float(np.min(1.0 + q1 * u + q2 * u * u))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--mass", type=float, default=0.3,
                    help="kink mass of the scan (0.3 passes the monitor "
                         "gate at 150x30 at all three spins, 2026-10-28)")
    ap.add_argument("--q1", default="-0.6,-0.3,0,0.3,0.6",
                    help="shape-scan values of q1")
    ap.add_argument("--q2", default="-0.6,-0.3,0,0.3,0.6",
                    help="shape-scan values of q2")
    ap.add_argument("--gammas", default=None,
                    help="gamma-scan values, walked in order from the "
                         "member's gamma (switches the scan axis)")
    ap.add_argument("--rays", default=None,
                    help="semicolon-separated (dq1,dq2) directions for the "
                         "open-ended ray walk (switches the scan axis)")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD",
                    help="solve on this CUDA card (cards are shared: check "
                         "nvidia-smi first); default CPU")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None,
                    help="TSV path (default runs/optimisation/scans/"
                         "<member>_<mode>_<grid>.tsv)")
    args = ap.parse_args()
    select_device(args.gpu, args.jac_chunk)

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny
    mode = "gamma" if args.gammas else ("rays" if args.rays else "shape")
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    out = pathlib.Path(args.out or f"runs/optimisation/scans/"
                                   f"{stem}_{mode}_{nx}x{ny}.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text(TSV_HEADER)

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
    print(f"{name} ({nx}x{ny}, {sol.map_name}, eta0 {sol.eta0:g}, "
          f"gamma {sol.gamma:g}): J-held solve {i1['res_scaled_inf']:.1e}; "
          f"R_e {th['R_e']:.10f}, J {J0:.6e}, psi_minus {psim1:.10f}; "
          f"{mode} scan at kink mass {args.mass:g}", flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev0 = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
             "omega": sol.eta0 * omega1, "psim": psim1,
             "sigma": sol.eta0, "xi_t": xi1}

    def solve(prev, gamma, m, q):
        """One pinned solve continued from ``prev``; returns (row, prev)."""
        t0 = time.time()
        pot = (None if m == 0.0
               else (lambda pm, m=m, q=q: PolynomialPotential.kink_q(
                   m, pm, q)))
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0), pin=("R_e", th["R_e"]), potential=pot)
        u0 = p2.pack(prev["F"] - p2.f_bg, prev["W"] - prev["omega"] * p2.q,
                     prev["N"], prev["B"] - 1.0,
                     prev["PSI"] - prev["psim"] * p2.psi_prof,
                     omega_inf=prev["omega"], psi_minus=prev["psim"],
                     sigma=prev["sigma"], xi_t=prev["xi_t"])
        try:
            u, info = newton(p2.residual, p2.jacobian, u0, tol=TOL)
        except Exception as err:        # a verdict, not an error
            return {"verdict": "FAILED", "err": str(err),
                    "secs": time.time() - t0}, None
        # a line search stalled at the round-off floor is a solve (the
        # step-1 Newton gate is 1e-11); only a genuinely large residual
        # is a failure
        if not info["converged"] and info["res_scaled_inf"] > 1e-11:
            return {"verdict": "FAILED",
                    "err": f"newton {info['res_scaled_inf']:.1e} "
                           f"({info.get('reason', 'max_iter')})",
                    "secs": time.time() - t0}, None
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        diag = p2.diagnostics(u)
        mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        x = exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx, F, Nf, B, PSI)
        tails = max(tail_ratio(PSI - psim * p2.psi_prof, axis=0),
                    tail_ratio(B - 1.0, axis=0))
        row = {"newton": info["res_scaled_inf"], "iters": info["iters"],
               "X": x["X"], "sigma": tt["sigma"], "psim": psim,
               "R_e": tt["R_e"], "e19": e19, "e_c": e_c, "tails": tails,
               "verdict": ("PASS" if max(e19, e_c) <= MONITOR_GATE
                           else "ABOVE-GATE"),
               "secs": time.time() - t0}
        nxt = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
               "omega": omega, "psim": psim,
               "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
        return row, nxt

    def record(gamma, q, row, x_ref):
        tag = (f"gamma {gamma:+.4f}" if mode == "gamma"
               else f"q1 {q[0]:+.2f} q2 {q[1]:+.2f}")
        if row["verdict"] == "FAILED":
            print(f"  {tag}: NEWTON FAILED ({row['err']})  "
                  f"[{row['secs']:.0f}s]", flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{mode}\t{args.mass:g}\t{gamma:g}\t"
                    f"{q[0]:g}\t{q[1]:g}\tnan\tnan\tnan\tnan\tnan\tnan\tnan\t"
                    f"nan\tnan\tnan\t{min_q(*q):.3f}\tFAILED\n")
        else:
            dxk = "" if x_ref is None else f" (dXk {row['X'] - x_ref:+.3e})"
            print(f"  {tag}: newton {row['newton']:.1e} "
                  f"({row['iters']} it)  X {row['X']:.8e}{dxk}  "
                  f"sigma {row['sigma']:.10f}  psi- {row['psim']:.6f}  "
                  f"E19 {row['e19']:.1e}  E_c {row['e_c']:.1e}  "
                  f"tails {row['tails']:.1e}  minQ {min_q(*q):.2f}  "
                  f"{row['verdict']}  [{row['secs']:.0f}s]", flush=True)
            line = (f"{name}\t{nx}\t{ny}\t{mode}\t{args.mass:g}\t{gamma:g}\t"
                    f"{q[0]:g}\t{q[1]:g}\t{row['newton']:.3e}\t"
                    f"{row['iters']}\t{row['X']:.10e}\t"
                    f"{'nan' if x_ref is None else f'{row['X'] - x_ref:.3e}'}"
                    f"\t{row['sigma']:.10f}\t{row['psim']:.10f}\t"
                    f"{row['R_e']:.10f}\t{row['e19']:.3e}\t{row['e_c']:.3e}\t"
                    f"{row['tails']:.3e}\t{min_q(*q):.3f}\t"
                    f"{row['verdict']}\n")
        with out.open("a") as fh:
            fh.write(line)

    # anchor chain: m = 0, then the pure kink in thirds of the scan mass
    row, prev = solve(prev0, sol.gamma, 0.0, ())
    if prev is None:
        print(f"  m 0 anchor: NEWTON FAILED ({row['err']})", flush=True)
        return 1
    print(f"  m 0.000: newton {row['newton']:.1e} ({row['iters']} it)  "
          f"X {row['X']:.8e}  sigma {row['sigma']:.10f}  "
          f"E19 {row['e19']:.1e}  E_c {row['e_c']:.1e}", flush=True)
    for mstep in (args.mass / 3.0, 2.0 * args.mass / 3.0, args.mass):
        row, nxt = solve(prev, sol.gamma, mstep, ())
        if nxt is None:
            print(f"  kink anchor m {mstep:.3f}: NEWTON FAILED "
                  f"({row['err']})", flush=True)
            return 1
        prev = nxt
    x_kink = row["X"]
    record(sol.gamma, (0.0, 0.0), row, None)

    if mode == "gamma":
        for g in [float(v) for v in args.gammas.split(",")]:
            row, nxt = solve(prev, g, args.mass, ())
            record(g, (0.0, 0.0), row, x_kink)
            if nxt is not None:
                prev = nxt
        return 0

    if mode == "rays":
        for ray in args.rays.split(";"):
            # dq names: d2 is the monitors' D^2 normalizer in solve()
            dq1, dq2 = (float(v) for v in ray.split(","))
            prev_r, last_x = prev, x_kink
            above = rising = 0
            k = 0
            while True:
                k += 1
                q = (round(k * dq1, 10), round(k * dq2, 10))
                if min_q(*q) <= 0.0:
                    why = "min Q <= 0: inadmissible"
                    break
                row, nxt = solve(prev_r, sol.gamma, args.mass, q)
                record(sol.gamma, q, row, x_kink)
                if nxt is None:
                    why = "Newton"
                    break
                prev_r = nxt
                above = above + 1 if max(row["e19"], row["e_c"]) > 1e-6 else 0
                rising = rising + 1 if row["X"] > last_x else 0
                last_x = row["X"]
                if above >= 2:
                    why = "monitors > 1e-6 twice: the grid's limit"
                    break
                if rising >= 3:
                    why = "X rising: the minimum is behind us"
                    break
            print(f"  ray ({dq1:g},{dq2:g}) stopped at rung {k}: {why}",
                  flush=True)
        return 0

    q1s = [float(v) for v in args.q1.split(",")]
    q2s = [float(v) for v in args.q2.split(",")]
    points = sorted({(a, b) for a in q1s for b in q2s} - {(0.0, 0.0)},
                    key=lambda p: (abs(p[0]) + abs(p[1]), p))
    solved = {(0.0, 0.0): prev}
    for q in points:
        if min_q(*q) <= 0.0:
            print(f"  q1 {q[0]:+.2f} q2 {q[1]:+.2f}: SKIP "
                  f"(min Q {min_q(*q):.2f} <= 0: the psi_minus end is "
                  f"not a vacuum)", flush=True)
            continue
        seed = min(solved, key=lambda s: abs(s[0] - q[0]) + abs(s[1] - q[1]))
        row, nxt = solve(solved[seed], sol.gamma, args.mass, q)
        record(sol.gamma, q, row, x_kink)
        if nxt is not None:
            solved[q] = nxt
    return 0


if __name__ == "__main__":
    sys.exit(main())
