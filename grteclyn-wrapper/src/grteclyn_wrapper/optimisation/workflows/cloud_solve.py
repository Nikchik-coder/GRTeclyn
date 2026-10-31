"""Solve ordinary scalar clouds around a rotating wormhole.

Input: a saved massless member, a phantom potential and cloud amplitudes.
Output: printed Newton, cloud, throat and independent-constraint diagnostics.
Comparisons hold J and R_e fixed and report X = |VIQ|/R_e relative to the
same potential without a cloud. A one-dimensional boson-star solution seeds
chi = X exp(i*omega_chi*t); here X denotes the cloud amplitude, while the
reported exoticity X is a separate dimensionless observable. A vanished
cloud is identified as the trivial branch, not a successful matter cloud.

    python -m grteclyn_wrapper.optimisation.commands.cloud_solve --help
"""

from __future__ import annotations

import dataclasses
import math
import time

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import tail_ratio
from grteclyn_wrapper.grtresna.profiles.boson_star_ode import (
    QBallCouplings,
    solve_selfgrav_boson_star,
)
from grteclyn_wrapper.optimisation.exoticity import exotic_x, throat
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
from grteclyn_wrapper.optimisation.solver.device import select_device
from grteclyn_wrapper.optimisation.solver.newton import newton

TOL = 1e-14
STALL_OK = 1e-11          # the step-1 Newton gate: a stall there is a solve
C_GATE = 0.05
MONITOR_GATE = 1e-8
S4PI = math.sqrt(4.0 * math.pi)


def solve(p, u0):
    u, info = newton(p.residual, p.jacobian, u0, tol=TOL)
    if not (info["converged"] or info["res_scaled_inf"] <= STALL_OK):
        raise RuntimeError(f"newton at {info['res_scaled_inf']:.1e} "
                           f"after {info['iters']} it")
    return u, info


def star_seed(m_chi, phi_c, sigma, eta, h):
    """The 1D self-gravitating mini star at central amplitude phi_c
    (omega is its gravitational eigenvalue), and the X seed: its profile
    read at the isotropic radius r = sigma (|eta| + sqrt(h))/2 (exact at
    nu = 0), zero past the star's grid and on the Dirichlet rows."""
    star = solve_selfgrav_boson_star(
        QBallCouplings(mass=m_chi, lam=0.0, mu=0.0,
                       omega=0.9 * m_chi, phi_core=0.0),
        phi_c=phi_c)
    r = sigma * 0.5 * (np.abs(eta) + np.sqrt(h))
    rq = np.clip(r, float(star.r[0]), float(star.r[-1]))
    x0 = np.where(r <= float(star.r[-1]),
                  S4PI * np.asarray(star.spline_phi0(rq)), 0.0)
    x0[0, :] = 0.0
    x0[-1, :] = 0.0
    return x0, float(star.omega), float(star.adm_mass)


def run(args, *, error):
    """Execute parsed options; report invalid requests through ``error``."""
    select_device(args.gpu, args.jac_chunk)
    phi_cs = [float(v) for v in args.phi_c.split(",")]
    q_tgt = tuple(float(v) for v in args.q.split(",")) if args.q else ()

    sol = Solution.load(args.solution)
    J0 = float(sol.meta["prescribed"]["J"])
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny

    # stage A: the member holding J on its own grid, and its throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("J", J0))
    F0 = sol.eval_grid("f", p1.sx, p1.sy)
    W0 = sol.eval_grid("w", p1.sx, p1.sy)
    N0 = sol.eval_grid("N", p1.sx, p1.sy)
    zero = np.zeros_like(F0)
    u1, i1 = solve(p1, p1.pack(F0 - p1.f_bg, W0 - sol.omega_inf * p1.q,
                               N0, zero, zero, omega_inf=sol.omega_inf,
                               psi_minus=psim0))
    F1, W1, N1, B1, P1 = (np.asarray(a) for a in p1.fields(u1))
    omega1, psim1 = p1.unpack(u1)[-2:]
    th = throat(p1.eta0, p1.map, p1.sx, p1.sy, p1.Dx, F1, N1, B1)
    xi1 = float(p1.map.xi_of_eta(th["eta_throat"]))
    name = args.solution.rsplit("/", 1)[-1]
    print(f"{name} ({nx}x{ny}, eta0 {sol.eta0:g}, gamma {sol.gamma:g}): "
          f"J-held {i1['res_scaled_inf']:.1e}; R_e {th['R_e']:.10f}, "
          f"J {J0:.6e}", flush=True)

    # stage B: pinned, the phantom potential walked to (kink-m, q)
    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
            "omega": sol.eta0 * omega1, "psim": psim1,
            "sigma": sol.eta0, "xi_t": xi1}

    def pinned(pot, chi=None):
        return MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0), pin=("R_e", th["R_e"]),
            potential=pot, chi=chi)

    def pack_prev(p, dchi=None):
        kw = {} if dchi is None else {"dchi": dchi}
        return p.pack(prev["F"] - p.f_bg, prev["W"] - prev["omega"] * p.q,
                      prev["N"], prev["B"] - 1.0,
                      prev["PSI"] - prev["psim"] * p.psi_prof,
                      omega_inf=prev["omega"], psi_minus=prev["psim"],
                      sigma=prev["sigma"], xi_t=prev["xi_t"], **kw)

    m = args.kink_m
    steps = [(0.0, ())]
    if m > 0.0:
        steps += [(m / 3.0, ()), (2.0 * m / 3.0, ()), (m, ())]
        if q_tgt:
            n_q = max(1, int(math.ceil(max(abs(v) for v in q_tgt) / 0.3)))
            steps += [(m, tuple(v * k / n_q for v in q_tgt))
                      for k in range(1, n_q + 1)]
    x_v0 = x_base = None
    for mk, qk in steps:
        pot = (None if mk == 0.0 else
               (lambda pm, mk=mk, qk=qk:
                PolynomialPotential.kink_q(mk, pm, qk)))
        p2 = pinned(pot)
        u, info = solve(p2, pack_prev(p2))
        F, W, Nf, B, PSI = (np.asarray(a) for a in p2.fields(u))
        omega, psim = p2.unpack(u)[-2:]
        tt = p2.throat(u)
        x = exotic_x(1.0, p2.map, p2.sx, p2.sy, p2.Dx, F, Nf, B, PSI)
        if mk == 0.0:
            x_v0 = x["X"]
        x_base = x["X"]
        prev = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
                "omega": omega, "psim": psim,
                "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
        print(f"  no cloud m {mk:.3f} q ({', '.join(f'{v:g}' for v in qk)}): "
              f"newton {info['res_scaled_inf']:.1e} ({info['iters']} it)  "
              f"X {x['X']:.8e}  sigma {tt['sigma']:.8f}", flush=True)
    pot_base = (None if m == 0.0 else
                (lambda pm: PolynomialPotential.kink_q(m, pm, q_tgt)))

    # stage C: the cloud ladder at the stage-B potential, star-seeded
    u_cloud = PolynomialPotential.mass(args.m_chi)
    for phi_c in phi_cs:
        t0 = time.time()
        try:
            # the 1D star first: its eigen-omega defines the problem
            eta_nodes = grid.eta(p1.sx)
            eta_nodes[0], eta_nodes[-1] = np.inf, -np.inf
            h = eta_nodes[:, None] ** 2 + 1.0
            eta_g = np.where(np.isfinite(eta_nodes), eta_nodes,
                             0.0)[:, None] * np.ones(ny + 1)
            x0, omega_chi, m_star = star_seed(
                args.m_chi, phi_c, prev["sigma"], eta_g, h)
            x0[~np.isfinite(eta_nodes), :] = 0.0
        except Exception as err:
            print(f"  phi_c {phi_c:g}: 1D STAR FAILED ({err})", flush=True)
            continue
        print(f"  seed phi_c {phi_c:g}: 1D star omega {omega_chi:.6f}, "
              f"ADM {m_star:.4e}", flush=True)
        p3 = pinned(pot_base, chi=(u_cloud, omega_chi))
        try:
            u, info = solve(p3, pack_prev(p3, dchi=x0))
        except Exception as err:
            print(f"  phi_c {phi_c:g}: NEWTON FAILED ({err})", flush=True)
            continue
        F, W, Nf, B, PSI, X = (np.asarray(a) for a in p3.fields(u))
        omega, psim = p3.unpack(u)[-2:]
        tt = p3.throat(u)
        diag = p3.diagnostics(u)
        mask = (1.0 / p3.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        x = exotic_x(1.0, p3.map, p3.sx, p3.sy, p3.Dx, F, Nf, B, PSI)
        x_max = float(np.max(np.abs(X)))
        if x_max < 0.1 * S4PI * phi_c:
            print(f"  phi_c {phi_c:g}: cloud evaporated "
                  f"(max|X| {x_max:.1e}, the X = 0 branch)", flush=True)
            continue
        tails = tail_ratio(X, axis=0)
        ok = max(e19, e_c) <= MONITOR_GATE
        print(f"  phi_c {phi_c:g} (omega_chi {omega_chi:.6f}): newton "
              f"{info['res_scaled_inf']:.1e} ({info['iters']} it)  "
              f"X_throat {X[nx // 2, -1]:.5e}  max|X| {x_max:.5e}  "
              f"sigma {tt['sigma']:.8f}  R_e {tt['R_e']:.8f}  "
              f"psi- {psim:.6f}  X {x['X']:.8e} "
              f"(vs base {100 * (x['X'] / x_base - 1):+.2f} %, "
              f"vs V=0 {100 * (x['X'] / x_v0 - 1):+.2f} %)  "
              f"E19 {e19:.1e}  E_c {e_c:.1e}  tails {tails:.1e}  "
              f"{'PASS' if ok else 'MONITORS ABOVE GATE'}  "
              f"[{time.time() - t0:.0f}s]", flush=True)
        prev = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
                "omega": omega, "psim": psim,
                "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
    return 0
