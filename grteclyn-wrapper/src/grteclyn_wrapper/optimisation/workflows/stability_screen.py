"""Run diagnostic radial-stability calculations on static candidate twins.

Input: a saved member and potential targets; output: a radial-rate TSV.
Each target is re-solved at J = 0 with the member's size pin. Rates use
lambda*eta0 and lambda*R_e; grid coordinates have eta0 = 1.
The radial screen is under repair. Its output is diagnostic and must not be
used to certify physical stability or to score the production optimiser.

    python -m grteclyn_wrapper.optimisation.commands.stability_screen --help
"""

from __future__ import annotations

import math
import pathlib
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
    ArctanMap,
    lobatto,
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


def run(args, *, error):
    """Execute parsed options; report invalid requests through ``error``."""
    select_device(args.gpu, args.jac_chunk)

    targets = []
    for part in args.targets.split(";"):
        label, _, knobs = part.strip().partition("=")
        x = [float(v) for v in knobs.split(",")]
        assert len(x) == 4, f"target {label}: m,q1,q2,q3"
        targets.append((label, np.array(x)))

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    out = pathlib.Path(args.out or f"runs/optimisation/stability/"
                                   f"{stem}_radial_{nx}x{ny}.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text(
            "member\tlabel\tmass\tq1\tq2\tq3\tsigma\tR_e\tX_J0\tE19\tE_c\t"
            "flat1d\tlam_eta0\tlam_Re\tdrift\ttt\tteta\tverdict\n")

    # the member holding J on its own grid, for the R_e pin
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
          f"J {J0:.6e}", flush=True)

    grid = ArctanMap(eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
            "omega": sol.eta0 * omega1, "psim": psim1,
            "sigma": sol.eta0, "xi_t": xi1}

    def solve_at(x, Jk, prev):
        """One pinned solve at knob vector x and prescribed J."""
        m, q = float(x[0]), tuple(float(v) for v in x[1:])
        potf = (None if m == 0.0
                else (lambda pm, m=m, q=q: PolynomialPotential.kink_q(
                    m, pm, q)))
        p2 = MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", Jk), pin=("R_e", th["R_e"]), potential=potf)
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
            return None, (f"newton {info['res_scaled_inf']:.1e} "
                          f"({info.get('reason', '?')})")
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        diag = p2.diagnostics(u)
        mask = (1.0 / p2.h_i[:, 0]) >= C_GATE**2
        nxt = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
               "omega": omega, "psim": psim,
               "sigma": tt["sigma"], "xi_t": tt["xi_t"], "p2": p2,
               "newton": info["res_scaled_inf"],
               "e19": float(np.max(np.abs(diag["E19"][mask]))) / d2,
               "e_c": float(np.max(np.abs(diag["E_c"][mask]))),
               "X": exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx,
                             F, Nf, B, PSI)["X"],
               "R_e": tt["R_e"],
               "pot": (None if m == 0.0
                       else PolynomialPotential.kink_q(m, float(psim), q))}
        return nxt, None

    def chain_to(points, prev, what, xstart):
        """Continuation along points (5-vectors m,q1,q2,q3,J) from prev,
        solved at xstart, bisecting a stalled leg toward the last solved
        point (the first leg toward xstart)."""
        xlast = np.asarray(xstart, float)
        for xk in points:
            pending, splits = [xk], 0
            while pending:
                xt = pending[-1]
                nxt, err = solve_at(xt[:4], float(xt[4]), prev)
                if nxt is None:
                    splits += 1
                    if splits > 6:
                        print(f"  {what} FAILED at "
                              f"({', '.join(f'{v:g}' for v in xt)}): {err}",
                              flush=True)
                        return None
                    pending.append((xlast + xt) / 2.0)
                    continue
                prev, xlast = nxt, xt
                pending.pop()
        return prev

    # J walks to 0 at V = 0 (the knob vector carries J as its 5th slot)
    jchain = [np.array([0.0, 0, 0, 0, Jk])
              for Jk in (J0, 2 * J0 / 3, J0 / 3, 0.0)]
    base = chain_to(jchain, prev, "J walk", jchain[0])
    if base is None:
        return 1
    print(f"J = 0 base: sigma {base['sigma']:.8f}  R_e {base['R_e']:.8f}  "
          f"X {base['X']:.8e}  E19 {base['e19']:.1e}", flush=True)

    screen_nx = [int(v) for v in args.screen_nx.split(",")]
    sx_all, _ = lobatto(nx)

    for label, x in targets:
        t0 = time.time()
        qstr = ", ".join(f"{v:+.3f}" for v in x[1:])
        print(f"\n[{label}] m {x[0]:g} q ({qstr})", flush=True)
        m0 = float(x[0])
        kchain = [np.array([mk, 0, 0, 0, 0.0]) for mk in
                  (m0 / 3.0, 2 * m0 / 3.0, m0)] if m0 else []
        n_q = (max(1, int(math.ceil(max(abs(v) for v in x[1:]) / 0.3)))
               if np.any(x[1:]) else 0)
        kchain += [np.concatenate([[m0], x[1:] * k / n_q, [0.0]])
                   for k in range(1, n_q + 1)]
        tgt = (chain_to(kchain, base, f"{label} walk-in", np.zeros(5))
               if kchain else base)
        if tgt is None:
            continue

        # flatten to 1D: the J = 0 solution must be spherical
        F, Nf, B, PSI, W = (tgt[k] for k in ("F", "N", "B", "PSI", "W"))
        flat = max(float(np.max(np.abs(a - a.mean(axis=1, keepdims=True))))
                   for a in (F, B, PSI))
        flat = max(flat, float(np.max(np.abs(Nf))),
                   float(np.max(np.abs(W))), abs(float(tgt["omega"])))
        F0d, B0d, PSI0d = (a.mean(axis=1) for a in (F, B, PSI))
        background = static_background(sx=sx_all, radial_map=grid,
                                       F0=F0d, P0=B0d, psi0=PSI0d,
                                       potential=tgt["pot"])

        lam = drift = ttr = ter = None
        for snx in screen_nx:
            o = growth_rate(eta0=1.0, nx=snx, background=background,
                            radial_map=grid)
            if o.get("stable"):
                print(f"  screen nx {snx}: no matched unstable mode "
                      f"(unmatched lam2 "
                      f"{', '.join(f'{v:.4f}' for v in o['lam2_unmatched'])})",
                      flush=True)
                lam = 0.0
                continue
            lam, drift = o["lam"], o["match_drift"]
            ttr, ter = o["tt_res"], o["teta_res"]
            print(f"  screen nx {snx}: lam*eta0 {lam:.6f}  "
                  f"lam*R_e {lam * tgt['R_e'] / tgt['sigma']:.6f}  "
                  f"2-grid {drift:.1e}  tt {ttr:.1e}  teta {ter:.1e}",
                  flush=True)
        verdict = ("STABLE?" if lam == 0.0
                   else "UNSTABLE")
        print(f"[{label}] lam*eta0 {lam:.6f}  lam*R_e "
              f"{(lam or 0.0) * tgt['R_e'] / tgt['sigma']:.6f}  X_J0 "
              f"{tgt['X']:.8e}  newton {tgt['newton']:.1e}  "
              f"E19 {tgt['e19']:.1e}  flat1d {flat:.1e}  "
              f"{verdict}  [{time.time() - t0:.0f}s]", flush=True)
        qv = "\t".join(f"{v:.6g}" for v in x[1:])
        with out.open("a") as fh:
            fh.write(f"{stem}\t{label}\t{x[0]:.6g}\t{qv}\t"
                     f"{tgt['sigma']:.10f}\t{tgt['R_e']:.10f}\t"
                     f"{tgt['X']:.10e}\t{tgt['e19']:.3e}\t{tgt['e_c']:.3e}\t"
                     f"{flat:.3e}\t{lam:.8f}\t"
                     f"{(lam or 0.0) * tgt['R_e'] / tgt['sigma']:.8f}\t"
                     f"{drift if drift is not None else float('nan'):.3e}\t"
                     f"{ttr if ttr is not None else float('nan'):.3e}\t"
                     f"{ter if ter is not None else float('nan'):.3e}\t"
                     f"{verdict}\n")
    return 0
