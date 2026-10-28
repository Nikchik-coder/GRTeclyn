#!/usr/bin/env python
"""Campaign M step 4: the J = 0 dressed-star cross-check.

The published 1D object (the Bondi paper's canonical sector,
grtresna/profiles/boson_star_ode.py) is a self-gravitating sextic
boson star at fixed omega, solved by amplitude shooting in isotropic
gauge.  The matter solver must contain it: at gamma = 0, omega_inf = 0,
a wormhole with a tiny throat eta0 threading the star is the same
spacetime up to O(eta0^2) (the phantom charge D = eta0 is part of that
budget), so the two-field solve seeded with the 1D star must land on it
and converge toward it as eta0^2.

The conventions map exactly (derive_matter_equations.py fixes ours):

    X = sqrt(4 pi) phi0,   omega_chi = omega,   cal U = 8 pi U_evo
    (from_evolution of U = m^2 phi^2/2 - lam phi^4/4 + mu phi^6/6),
    e^{f/2} = alpha,   B = psi_c^2 alpha   (nu = 0: isotropic),

their Phi = phi0 e^{-i omega t} carrying the two half-normalized real
components (ComplexScalarField), i.e. R_ab = 8 pi [sum_k d phi_k d
phi_k + U g_ab] = our 2[X_a X_b + omega^2 X^2 dt dt] + cal U g_ab.

Per eta0 it prints Newton, the monitors, max|N| (the spherical limit),
and the profile errors against the 1D star on 0.5 <= r <= 6; the gate
is the eta0^2 convergence between the two runs (factor >= 2.5) plus
Newton <= 1e-11.  CPU, through capped_job.sh (~6.5k unknowns):

    grteclyn-wrapper/scripts/ops/capped_job.sh start chi-star \\
        --threads 4 --mem 60 --timeout 3600 -- \\
        grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/optimisation/check_chi_star.py
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap
from grteclyn_wrapper.grtresna.profiles.boson_star_ode import (
    cached_selfgrav_at_omega,
)
from grteclyn_wrapper.optimisation.matter_equations import (
    MatterCollocationProblem,
)
from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
from grteclyn_wrapper.optimisation.solver.device import select_device
from grteclyn_wrapper.optimisation.solver.newton import newton

# The published ultraweak rung (bondi_dipole/star_family_scan.py), the
# canonical member of the equal-|ADM| pair.
MASS, LAM, MU = 1.0, 10240.0, 21845333.0
OMEGA = 0.550
S4PI = math.sqrt(4.0 * math.pi)
TOL = 1e-14
C_GATE = 0.05


def star_eval(star, spline, r):
    rq = np.clip(np.abs(r), float(star.r[0]), float(star.r[-1]))
    return spline(rq)


def solve_at(star, eta0, nx, ny):
    u_x = PolynomialPotential.from_evolution(
        (0.0, 0.0, MASS * MASS / 2.0, 0.0, -LAM / 4.0, 0.0, MU / 6.0))
    p = MatterCollocationProblem(
        eta0=eta0, gamma=0.0, radial_map=ArctanMap(eta0=2.0),
        nx=nx, ny=ny, prescribe=("omega_inf", 0.0),
        chi=(u_x, star.omega))
    eta = p.map.eta(p.sx)
    eta[0], eta[-1] = np.inf, -np.inf
    r = np.abs(eta)[:, None] * np.ones(ny + 1)
    alpha = star_eval(star, star.spline_alpha, r)
    psi_c = star_eval(star, star.spline_psi, r)
    phi0 = star_eval(star, star.spline_phi0, r)
    F0 = 2.0 * np.log(alpha)
    B0 = psi_c**2 * alpha
    X0 = S4PI * phi0
    zero = np.zeros_like(F0)
    u0 = p.pack(F0, zero, zero, B0 - 1.0, zero, psi_minus=-math.pi,
                dchi=X0)
    u, info = newton(p.residual, p.jacobian, u0, tol=TOL)
    F, W, Nf, B, PSI, X = (np.asarray(a) for a in p.fields(u))
    # our eta chart vs the star's isotropic chart, exactly:
    # d eta^2 + h dOmega^2 = (h/r^2)(dr^2 + r^2 dOmega^2) with
    # r = (eta + sqrt(h))/2, so the star is read at r(eta) and the
    # conformal factor picks up sqrt(h)/r
    psim = p.unpack(u)[-1]
    d2 = (psim * eta0 / math.pi) ** 2
    diag = p.diagnostics(u)
    mask = (1.0 / p.h_i[:, 0]) >= C_GATE**2
    e19 = float(np.max(np.abs(diag["E19"][mask]))) / d2
    e_c = float(np.max(np.abs(diag["E_c"][mask])))
    # the spherical limit: N -> 0 and X theta-independent
    n_max = float(np.max(np.abs(Nf)))
    x_aniso = float(np.max(np.abs(X - X[:, :1])))
    # profile errors against the 1D star on the sample radii, relative
    # to the star's own scales
    rs = np.linspace(0.5, 6.0, 23)
    ks = [int(np.argmin(np.abs(eta - rv))) for rv in rs]
    errs = {"phi0": 0.0, "alpha": 0.0, "psi_c": 0.0}
    for k in ks:
        ev = abs(eta[k])
        hv = ev * ev + eta0 * eta0
        rv = (ev + math.sqrt(hv)) / 2.0
        errs["phi0"] = max(errs["phi0"], abs(
            X[k, 0] / S4PI - float(star.eval_phi0(rv))) / star.phi_c)
        errs["alpha"] = max(errs["alpha"], abs(
            math.exp(F[k, 0] / 2.0)
            - float(star_eval(star, star.spline_alpha, rv))))
        errs["psi_c"] = max(errs["psi_c"], abs(
            B[k, 0] * math.exp(-F[k, 0] / 2.0) * math.sqrt(hv) / rv
            - float(star_eval(star, star.spline_psi, rv)) ** 2))
    print(f"  eta0 {eta0:g} ({nx}x{ny}): newton {info['res_scaled_inf']:.1e}"
          f" ({info['iters']} it)  X_throat {X[nx // 2, 0]:.6e}  "
          f"max|N| {n_max:.1e}  X aniso {x_aniso:.1e}  "
          f"E19/D2 {e19:.1e}  E_c {e_c:.1e}  "
          f"dphi0 {errs['phi0']:.2e}  dalpha {errs['alpha']:.2e}  "
          f"dpsi_c^2 {errs['psi_c']:.2e}", flush=True)
    return info, errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nx", type=int, default=120)
    ap.add_argument("--ny", type=int, default=8)
    ap.add_argument("--eta0", default="0.2,0.1")
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    args = ap.parse_args()
    select_device(args.gpu, args.jac_chunk)

    star = cached_selfgrav_at_omega(MASS, LAM, MU, OMEGA, 1.0)
    print(f"1D star: omega {star.omega:.9f}  phi_c {star.phi_c:.6e}  "
          f"ADM {star.adm_mass:.6e}", flush=True)
    etas = [float(v) for v in args.eta0.split(",")]
    results = []
    for eta0 in etas:
        info, errs = solve_at(star, eta0, args.nx, args.ny)
        if not (info["converged"] or info["res_scaled_inf"] <= 1e-11):
            print("FAIL: Newton did not converge")
            return 1
        results.append(errs)
    ok = True
    if len(results) == 2:
        for key in results[0]:
            num, den = results[0][key], max(results[1][key], 1e-300)
            ratio = num / den
            good = ratio >= 2.5
            ok = ok and good
            print(f"convergence[{key}]: {num:.2e} -> {den:.2e} "
                  f"(x{ratio:.1f}, gate >= 2.5) "
                  f"{'PASS' if good else 'FAIL'}", flush=True)
    print("ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
