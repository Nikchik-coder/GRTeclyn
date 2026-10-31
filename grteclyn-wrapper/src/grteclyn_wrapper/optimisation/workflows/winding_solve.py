"""Solve rotating scalar clouds that carry part of a wormhole's spin.

Input: a saved massless member, potential parameters and cloud amplitudes.
Output: printed exoticity, cloud properties and spin/constraint checks.
At fixed J and R_e, Lambda = Z exp(i*(omega_z*t + k*phi)) with
Z = sin(theta)^k*zeta. The regular amplitude zeta is pinned at the throat;
omega_z is solved as an eigenvalue. A frozen-metric quadratic eigenproblem
seeds the first cloud. The total angular-momentum flux is checked independently
of Newton. These are stationary solutions, not stability certificates.

    python -m grteclyn_wrapper.optimisation.commands.winding_solve --help
"""

from __future__ import annotations

import dataclasses
import math
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
STALL_OK = 1e-11          # the step-1 Newton gate: a stall there is a solve
C_GATE = 0.05
MONITOR_GATE = 1e-8


def solve(p, u0):
    u, info = newton(p.residual, p.jacobian, u0, tol=TOL)
    if not (info["converged"] or info["res_scaled_inf"] <= STALL_OK):
        raise RuntimeError(f"newton at {info['res_scaled_inf']:.1e} "
                           f"after {info['iters']} it")
    return u, info


def linear_mode(make_problem, make_u0, sigma, oz_seed, oz_max):
    """The winding field's bound mode on the frozen metric: at zeta = 0
    the Jacobian's z block decouples into the linear operator
    L(oz) = L0 + oz L1 + oz^2 L2 (oz = sigma omega_z, grid units),
    Dirichlet rows included.  L0, L1, L2 come from three problems at
    oz = 0, +1, -1 (each jitted afresh: omega_z is baked into the
    trace); the quadratic eigenproblem is companion-linearized and
    solved dense.  Returns (oz, zeta) for a real eigenvalue in
    (0, oz_max) with a localized eigenvector, nearest the seed."""
    import scipy.linalg as sla

    Ls, p = [], None
    for v in (0.0, 1.0, -1.0):
        p = make_problem(v / sigma)
        iz = p.tags.index("z")
        sl = slice(iz * p.n, (iz + 1) * p.n)
        Ls.append(np.asarray(p.jacobian(make_u0(p)))[sl, sl])
    n, nxy = p.n, (p.nx + 1, p.ny + 1)
    L0 = Ls[0]
    L1 = (Ls[1] - Ls[2]) / 2.0
    L2 = (Ls[1] + Ls[2]) / 2.0 - Ls[0]
    eye, zr = np.eye(n), np.zeros((n, n))
    vals, vecs = sla.eig(np.block([[-L1, -L0], [eye, zr]]),
                         np.block([[L2, zr], [zr, eye]]))
    good = np.isfinite(vals) & (np.abs(vals.imag) < 1e-8)
    sx_out = np.abs(p.sx) > 0.8
    bound, loose = [], []
    for i in np.where(good)[0]:
        oz = float(vals[i].real)
        if not 0.02 <= oz < oz_max:
            continue
        zeta = vecs[n:, i].real.reshape(nxy)
        loc = (np.abs(zeta[sx_out]).max()
               / max(np.abs(zeta).max(), 1e-300))
        (bound if loc < 0.05 else loose).append((loc, oz, zeta))
    if bound:
        _, oz, zeta = min(bound, key=lambda t: abs(t[1] - oz_seed))
    elif loose:
        _, oz, zeta = min(loose, key=lambda t: t[0])
    else:
        raise RuntimeError("no bound winding mode in (0, oz_max)")
    return oz, zeta


def run(args, *, error):
    """Execute parsed options; report invalid requests through ``error``."""
    select_device(args.gpu, args.jac_chunk)
    amps = [float(v) for v in args.amp.split(",")]
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
    print(f"{name} ({nx}x{ny}, eta0 {sol.eta0:g}, gamma {sol.gamma:g}, "
          f"k {args.k}): J-held {i1['res_scaled_inf']:.1e}; "
          f"R_e {th['R_e']:.10f}, J {J0:.6e}", flush=True)

    # stage B: pinned, the phantom potential walked to (kink-m, q)
    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
            "omega": sol.eta0 * omega1, "psim": psim1,
            "sigma": sol.eta0, "xi_t": xi1}

    def pinned(pot, winding=None, pin_zeta=None):
        return MatterCollocationProblem(
            eta0=1.0, gamma=sol.gamma, radial_map=grid, nx=nx, ny=ny,
            prescribe=("J", J0), pin=("R_e", th["R_e"]),
            potential=pot, winding=winding, pin_zeta=pin_zeta)

    def pack_prev(p, dzeta=None, omega_z=None):
        kw = {}
        if dzeta is not None:
            kw["dzeta"] = dzeta
        if omega_z is not None:
            kw["omega_z"] = omega_z
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

    # stage C: the amplitude ladder, omega_z the bordered eigenvalue,
    # continued rung to rung; the first rung is seeded by the
    # frozen-metric linear mode
    u_z = PolynomialPotential.mass(args.m_z)
    zeta_prev = amp_prev = None
    omega_seed = args.omega_z_seed * args.m_z
    for amp in amps:
        t0 = time.time()
        if zeta_prev is None:
            zeros = np.zeros((nx + 1, ny + 1))
            oz0, zmode = linear_mode(
                lambda wz: pinned(pot_base, winding=(u_z, wz, args.k)),
                lambda p: pack_prev(p, dzeta=zeros),
                prev["sigma"], omega_seed * prev["sigma"],
                args.m_z * prev["sigma"])
            omega_seed = oz0 / prev["sigma"]
            pin_val = zmode[nx // 2, -1]
            if abs(pin_val) < 0.05 * np.abs(zmode).max():
                print(f"  linear mode: WEAK at the pin point "
                      f"({pin_val:.2e} vs max "
                      f"{np.abs(zmode).max():.2e})", flush=True)
            z0 = amp * zmode / pin_val
            print(f"  linear mode: omega_z {omega_seed:.6f} "
                  f"(oz {oz0:.6f}, max|zeta|/pin "
                  f"{np.abs(z0).max() / amp:.2f})", flush=True)
        else:
            z0 = zeta_prev * (amp / amp_prev)
        p3 = pinned(pot_base, winding=(u_z, omega_seed, args.k),
                    pin_zeta=amp)
        try:
            u, info = solve(p3, pack_prev(p3, dzeta=z0,
                                          omega_z=omega_seed))
        except Exception as err:
            print(f"  amp {amp:g}: NEWTON FAILED ({err})", flush=True)
            zeta_prev = amp_prev = None
            continue
        F, W, Nf, B, PSI, ZETA = (np.asarray(a) for a in p3.fields(u))
        omega, psim = p3.unpack(u)[-2:]
        omega_z = p3.omega_z_of(u)
        tt = p3.throat(u)
        diag = p3.diagnostics(u)
        mask = (1.0 / p3.h_i[:, 0]) >= C_GATE**2
        e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
        e_c = float(np.max(np.abs(diag["E_c"][mask])))
        x = exotic_x(1.0, p3.map, p3.sx, p3.sy, p3.Dx, F, Nf, B, PSI)
        z_max = float(np.max(np.abs(ZETA)))
        # the J bookkeeping: flux + matter tail must be flat in x, and
        # together they are the prescribed J
        j_tot = diag["j_of_x"] + diag["j_matter_tail"]
        j_grid = J0 / tt["sigma"] ** 2
        j_flat = float(np.max(np.abs(j_tot - j_grid))) / abs(j_grid)
        j_mat = float(diag["j_matter_tail"][p3.mid - 1]) / j_grid
        tails = tail_ratio(ZETA, axis=0)
        ok = max(e19, e_c) <= MONITOR_GATE
        print(f"  amp {amp:g} (omega_z {omega_z:.6f}): newton "
              f"{info['res_scaled_inf']:.1e} ({info['iters']} it)  "
              f"max|zeta| {z_max:.5e}  sigma {tt['sigma']:.8f}  "
              f"R_e {tt['R_e']:.8f}  psi- {psim:.6f}  "
              f"J_mat/J {j_mat:+.4f}  j-flat {j_flat:.1e}  "
              f"X {x['X']:.8e} "
              f"(vs base {100 * (x['X'] / x_base - 1):+.2f} %, "
              f"vs V=0 {100 * (x['X'] / x_v0 - 1):+.2f} %)  "
              f"E19 {e19:.1e}  E_c {e_c:.1e}  tails {tails:.1e}  "
              f"{'PASS' if ok else 'MONITORS ABOVE GATE'}  "
              f"[{time.time() - t0:.0f}s]", flush=True)
        prev = {"F": F, "W": W, "N": Nf, "B": B, "PSI": PSI,
                "omega": omega, "psim": psim,
                "sigma": tt["sigma"], "xi_t": tt["xi_t"]}
        zeta_prev, amp_prev, omega_seed = ZETA, amp, omega_z
    return 0
