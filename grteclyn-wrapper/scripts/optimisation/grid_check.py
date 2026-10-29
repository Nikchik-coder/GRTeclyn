#!/usr/bin/env python
"""Campaign M: grid convergence of solved potentials at the member's J.

Decides whether a point the 150x30 search rated above the identity gate is
under-resolved (E19 falls with the grid, X converging) or sits on the dense
solve's round-off floor (E19 stalls while X holds).  Each point walks in once
on the first grid (m in thirds, then the shape in 0.3 steps, a stalled leg
bisected toward the last solved point, capped), then every finer grid starts
from the previous grid's solution, spectrally interpolated onto its nodes, so
a finer grid costs one Newton solve.  ``--from-npz`` skips that continuation
and starts from a search dump on the first grid, which is the check of the
point the optimizer actually stored.  Every grid pins the same R_e, the one
the member holds on the first grid -- the optimizer's pin when the first grid
is its own -- so the first row reproduces the search's X and the rows differ
by resolution alone.

    grteclyn-wrapper/scripts/ops/capped_job.sh start grid-d51 \\
        --threads 4 --mem 220 --gpu --timeout 7200 -- \\
        grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/optimisation/grid_check.py \\
        results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0012.json \\
        --points "w1=0.477,2.636,3.340,0.248" \\
        --grids 150x30,180x36,210x42 --stall-ok 1e-9 --gpu 0
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import pathlib
import sys

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval
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
FIELDS = ("F", "W", "N", "B", "PSI")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--points", required=True,
                    help="label=m,q1,q2,q3 list, ';'-separated")
    ap.add_argument("--grids", default="150x30,180x36,210x42",
                    help="nx x ny list, coarse to fine; the first is the "
                         "walk-in grid and the R_e pin's")
    ap.add_argument("--stall-ok", type=float, default=STALL_OK,
                    help="accept a Newton stall at or below this scaled "
                         "residual (default: the step-1 gate; the "
                         "drainhole floors at 1e-11 to 2e-10)")
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-dir", default=None,
                    help="save each solved nonzero point as an evolution "
                         "handoff NPZ in this directory")
    ap.add_argument("--from-npz", default=None,
                    help="search dump to start from (one --points entry); "
                         "skips continuation from V = 0")
    args = ap.parse_args()
    select_device(args.gpu, args.jac_chunk)

    points = []
    for part in args.points.split(";"):
        label, _, knobs = part.strip().partition("=")
        x = np.array([float(v) for v in knobs.split(",")])
        assert x.size == 4, f"point {label}: m,q1,q2,q3"
        points.append((label, x))
    grids = [tuple(int(v) for v in g.split("x"))
             for g in args.grids.split(",")]

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    out = pathlib.Path(args.out or f"runs/optimisation/grid/{stem}_grid.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text("member\tlabel\tmass\tq1\tq2\tq3\tnx\tny\tnewton\t"
                       "iters\tX\tsigma\tE19\tE_c\tverdict\n")

    # the member holding J on the first grid: the R_e pin and the seed
    nx0, ny0 = grids[0]
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx0, ny=ny0, prescribe=("J", J0))
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
    print(f"{name} (eta0 {sol.eta0:g}, gamma {sol.gamma:g}): J-held "
          f"{i1['res_scaled_inf']:.1e} on {nx0}x{ny0}; R_e "
          f"{th['R_e']:.10f}, J {J0:.6e}; grids {args.grids}", flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev0 = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
             "omega": sol.eta0 * omega1, "psim": psim1,
             "sigma": sol.eta0, "xi_t": xi1}

    def solve_at(x, prev, nx, ny):
        """One pinned solve at knob vector x on an nx x ny grid."""
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
            return None, f"newton raised: {err}"
        if not info["converged"] and info["res_scaled_inf"] > args.stall_ok:
            return None, (f"newton {info['res_scaled_inf']:.1e}, "
                          f"{info.get('reason', '?')}")
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        diag = p2.diagnostics(u)
        mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        mon = max(e19, e_c)
        return {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
                "omega": omega, "psim": psim,
                "sigma": tt["sigma"], "xi_t": tt["xi_t"],
                "sx": np.asarray(p2.sx), "sy": np.asarray(p2.sy),
                "newton": info["res_scaled_inf"], "iters": info["iters"],
                "X": exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx,
                              F, Nf, B, PSI)["X"],
                "e19": e19, "e_c": e_c,
                "verdict": ("PASS" if mon <= CLEAN_GATE else
                            "FRONTIER" if mon <= CEILING
                            else "ABOVE-GATE")}, None

    def walk(chain, prev, nx, ny):
        """Continuation along chain from prev (solved at V = 0), each
        stalled leg bisected toward the last solved point, capped."""
        xlast = np.zeros(4)
        for xk in chain:
            pending, splits = [xk], 0
            while pending:
                xt = pending[-1]
                nxt, err = solve_at(xt, prev, nx, ny)
                if nxt is None:
                    splits += 1
                    if splits > 6:
                        where = ", ".join(f"{v:g}" for v in xt)
                        return None, f"walk-in FAILED at ({where}): {err}"
                    pending.append((xlast + xt) / 2.0)
                    continue
                prev, xlast = nxt, xt
                pending.pop()
        return prev, None

    def prolong(prev, nx, ny):
        """prev's fields spectrally interpolated onto the nx x ny nodes."""
        p = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0), pin=("R_e", th["R_e"]))
        seed = dict(prev)
        for k in FIELDS:
            rows = cheb_eval(prev["sx"], np.asarray(prev[k]), p.sx)
            seed[k] = cheb_eval(prev["sy"], rows.T, p.sy).T
        return seed

    def report(label, x, nx, ny, row, x_prev):
        dx = (f"  dX {row['X'] - x_prev:+.2e}" if x_prev is not None
              else "")
        print(f"  [{label}] {nx}x{ny}: newton {row['newton']:.1e} "
              f"({row['iters']} it)  X {row['X']:.10e}{dx}  sigma "
              f"{row['sigma']:.10f}  E19 {row['e19']:.1e}  E_c "
              f"{row['e_c']:.1e}  {row['verdict']}", flush=True)
        q = "\t".join(f"{v:.6g}" for v in x[1:])
        with out.open("a") as fh:
            fh.write(f"{name}\t{label}\t{x[0]:.6g}\t{q}\t{nx}\t{ny}\t"
                     f"{row['newton']:.3e}\t{row['iters']}\t"
                     f"{row['X']:.12e}\t{row['sigma']:.12f}\t"
                     f"{row['e19']:.3e}\t{row['e_c']:.3e}\t"
                     f"{row['verdict']}\n")
        if args.save_dir and x[0] != 0.0:
            save_dir = pathlib.Path(args.save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
            pot = PolynomialPotential.kink_q(
                float(x[0]), float(row["psim"]),
                tuple(float(v) for v in x[1:]))
            meta = {
                "member": name, "slot": f"{label}_{nx}x{ny}",
                "nx": nx, "ny": ny, "member_eta0": sol.eta0,
                "gamma": sol.gamma,
                "radial_map": {"class": type(grid).__name__,
                               **dataclasses.asdict(grid)},
                "J": J0, "R_e": th["R_e"], "m": float(x[0]),
                "q": [float(v) for v in x[1:]],
                "potential_coeffs": [float(c) for c in pot.coeffs],
                **{k: float(row[k])
                   for k in ("omega", "psim", "sigma", "xi_t")},
                "X": row["X"], "X_v0": None, "E19": row["e19"],
                "E_c": row["e_c"], "verdict": row["verdict"],
                "lam_eta0": 0.0,
            }
            path = save_dir / f"{stem}_{label}_{nx}x{ny}.npz"
            np.savez(path, sx=row["sx"], sy=row["sy"],
                     meta=json.dumps(meta, default=float),
                     **{k: np.asarray(row[k]) for k in FIELDS})
            print(f"    saved {path}", flush=True)

    def load_npz(path):
        z = np.load(path, allow_pickle=True)
        meta = json.loads(str(z["meta"]))
        row = {k: np.asarray(z[k]) for k in FIELDS}
        row.update({k: float(meta[k])
                    for k in ("omega", "psim", "sigma", "xi_t")})
        row["sx"] = np.asarray(z["sx"])
        row["sy"] = np.asarray(z["sy"])
        x = np.array([float(meta["m"]), *[float(v) for v in meta["q"]]])
        return x, row

    v0, err = solve_at(np.zeros(4), prev0, nx0, ny0)
    if v0 is None:
        print(f"classical (V = 0) FAILED: {err}", flush=True)
        return 1
    report("v0", np.zeros(4), nx0, ny0, v0, None)

    if args.from_npz:
        if len(points) != 1:
            print("--from-npz takes one --points entry", flush=True)
            return 1
        label, _ = points[0]
        x, seed = load_npz(args.from_npz)
        print(f"  from {args.from_npz}: m {x[0]:.6g} q "
              f"({x[1]:.6g}, {x[2]:.6g}, {x[3]:.6g})", flush=True)
        row, err = solve_at(x, seed, nx0, ny0)
        if row is None:
            print(f"  [{label}] {nx0}x{ny0}: {err}", flush=True)
            return 1
        report(label, x, nx0, ny0, row, None)
        for nx, ny in grids[1:]:
            nxt, err = solve_at(x, prolong(row, nx, ny), nx, ny)
            if nxt is None:
                print(f"  [{label}] {nx}x{ny}: {err}", flush=True)
                return 1
            report(label, x, nx, ny, nxt, row["X"])
            row = nxt
        return 0

    for label, x in points:
        m0 = float(x[0])
        chain = [np.array([mk, 0, 0, 0]) for mk in
                 (m0 / 3.0, 2 * m0 / 3.0, m0)]
        n_q = (max(1, int(math.ceil(max(abs(v) for v in x[1:]) / 0.3)))
               if np.any(x[1:]) else 0)
        chain += [np.concatenate([[m0], x[1:] * k / n_q])
                  for k in range(1, n_q + 1)]
        row, err = walk(chain, v0, nx0, ny0)
        if row is None:
            print(f"  [{label}] {nx0}x{ny0}: {err}", flush=True)
            continue
        report(label, x, nx0, ny0, row, None)
        for nx, ny in grids[1:]:
            nxt, err = solve_at(x, prolong(row, nx, ny), nx, ny)
            if nxt is None:
                print(f"  [{label}] {nx}x{ny}: {err}", flush=True)
                break
            report(label, x, nx, ny, nxt, row["X"])
            row = nxt
    return 0


if __name__ == "__main__":
    sys.exit(main())
