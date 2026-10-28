#!/usr/bin/env python
"""Campaign M step 5: the first winding-field solves on a spinning member.

From a saved V = 0 member: hold its J on its own grid, measure the
throat, move to the dimensionless grid at pinned J and R_e, walk the
phantom potential to the chosen kink (and shape, --q, in 0.3 steps),
then switch the winding field on: Lambda = Z e^{i(omega_z t + k phi)}
with cal U_z = m_z^2 Z^2 and Z = sin^k theta zeta (the solver's unknown
is the regular zeta).  Unlike the step-4 cloud there is no 1D seeding
star -- a rotating cloud is intrinsically 2D -- so the ladder walks the
cloud AMPLITUDE at the throat's equator (the pin_zeta border row) and
omega_z is the bordered eigenvalue, the boson-star way around the
fixed-frequency Newton whose trivial zeta = 0 branch swallows seeds
(2026-10-28: four gaussian-seeded fixed-omega_z rungs all fell to it,
and a gaussian-seeded bordered rung overshoots -- the Jacobian checked
exact, the full step just leaves the basin).  The first rung is seeded
EXACTLY: at zeta = 0 the Jacobian's z block decouples and is the
frozen-metric linear operator L(oz) = L0 + oz L1 + oz^2 L2, so the
bound mode and its frequency come from that quadratic eigenproblem
(companion linearization, dense eig), and the full Newton starts from
the mode shape at the asked amplitude with corrections only O(amp^2).
Later rungs continue from the previous cloud, rescaled.

Per rung it reports the step-5 question -- does matter-carried spin
lower the phantom bill at matched R_e and J? -- and what gates it:
  - Newton's residual and iterations (a failure is a verdict);
  - the cloud: Z on the throat's equator, max |zeta|, its spectral tail;
  - sigma, R_e (the pin check), psi_minus, and the matter's share of J
    (j_matter over J): the winding phase carries angular momentum, so
    the frame dragging no longer has to;
  - the J bookkeeping: j_of_x + j_matter_tail must be flat in x (the
    twist source against the flux, an identity Newton never saw);
  - the bill X = |VIQ|/R_e and dX against the SAME potential with no
    cloud, plus dX against V = 0;
  - the unimposed monitors E19/D^2 and E_c inside C >= 0.05, gate 1e-8.

CPU shakedown through capped_job.sh (seven-field Jacobian):

    grteclyn-wrapper/scripts/ops/capped_job.sh start winding-first \\
        --threads 4 --mem 40 --timeout 3600 -- \\
        grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/optimisation/winding_solve.py \\
        results/spinningwormhole/solutions/fam_b/fam_b_0003.json \\
        --nx 48 --ny 12
"""

from __future__ import annotations

import argparse
import dataclasses
import math
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--kink-m", type=float, default=0.3,
                    help="phantom kink mass (0 = pure V = 0 phantom)")
    ap.add_argument("--q", default="",
                    help="shape target q1,q2 (kink_q), walked in 0.3 steps")
    ap.add_argument("--m-z", type=float, default=1.0,
                    help="winding field mass (cal U_z = m_z^2 Z^2)")
    ap.add_argument("--k", type=int, default=1,
                    help="winding number k >= 1")
    ap.add_argument("--amp", default="0.05,0.1,0.2,0.3",
                    help="zeta amplitude ladder at the throat's equator "
                         "(the pin_zeta row; omega_z is the bordered "
                         "eigenvalue, continued rung to rung)")
    ap.add_argument("--omega-z-seed", type=float, default=0.9,
                    help="omega_z seed of the linear mode search, in "
                         "units of m_z")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD",
                    help="solve on this CUDA card (cards are shared: check "
                         "nvidia-smi first); default CPU")
    ap.add_argument("--jac-chunk", type=int, default=None)
    args = ap.parse_args()
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


if __name__ == "__main__":
    sys.exit(main())
