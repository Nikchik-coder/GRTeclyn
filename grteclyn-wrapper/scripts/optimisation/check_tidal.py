#!/usr/bin/env python
"""The tidal observable of campaign M step 2, gated on closed forms.

Three parts, hardest gate first:

1. Static Ellis (f = omega = nu = 0, B = 1): Morris and Thorne's lateral
   tidal (AJP 56, 395, box 2 with b = eta0^2/r) at the throat and off it,
   E_rad = 0 and E_theta = E_phi = -gamma_L^2 v^2 eta0^2 / h^2 for a
   radial transit at speed v: the throat stretches a traveler sideways.
2. The static drainhole (f = (gamma/2)(1 - x), x the arctan-map
   coordinate, an exact solution for every gamma): the generic curvature
   path against the static spherical class formulas, derived separately
   from (f', f'', h) -- different algebra, same metric -- at three radii
   and two speeds.  This exercises the f jets, the frame and the boost.
3. A saved rotating member: exact identities only -- E_rad is invariant
   under the radial boost (the boost spans the same t-eta 2-plane), E is
   symmetric, and the reflection-odd components E_12, E_23 vanish on the
   equator.  The throat eigenvalues are printed for the record.

Numpy only; seconds.  Run from the repo root:

    grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/optimisation/check_tidal.py \\
        [results/spinningwormhole/solutions/fam_b/fam_b_0003.json]
"""

from __future__ import annotations

import math
import sys

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
    ArctanMap,
    lobatto,
)
from grteclyn_wrapper.optimisation.exoticity import throat, tidal

TOL = 1e-12


def _grid(eta0: float, nx: int = 64, ny: int = 12):
    sx, Dx = lobatto(nx)
    sy, Dy = lobatto(ny)
    zero = np.zeros((nx + 1, ny + 1))
    return ArctanMap(eta0=eta0), sx, sy, Dx, Dy, zero


def check_ellis(eta0: float = 2.0) -> bool:
    rmap, sx, sy, Dx, Dy, zero = _grid(eta0)
    ok = True
    for xi in (0.0, 0.5):
        eta = float(rmap.eta(np.array([xi]))[0])
        h = eta**2 + eta0**2
        for v in (0.0, 0.5, 0.9):
            t = tidal(eta0, rmap, sx, sy, Dx, Dy, zero, zero, zero,
                      zero + 1.0, xi, v=v)
            gl2 = 1.0 / (1.0 - v * v)
            want = np.diag([0.0, -gl2 * v**2 * eta0**2 / h**2] * 2)[:3, :3]
            want[2, 2] = want[1, 1]
            err = float(np.max(np.abs(t["E"] - want)))
            good = err <= TOL
            ok = ok and good
            print(f"  ellis eta {eta:4.1f} v {v:.1f}: lat {t['theta']:+.6e}"
                  f" (closed {want[1, 1]:+.6e})  err {err:.1e}"
                  f"  {'PASS' if good else 'FAIL'}")
    return ok


def _drainhole_closed(eta0, gamma, eta, v):
    """E_rad, E_lat of ds^2 = -e^f dt^2 + e^-f (deta^2 + h dOmega^2) from
    the static spherical class formulas: with the 2-plane sectional
    curvatures below (signs anchored at gamma = 0 by part 1's Ellis form),

        E_rad = e^f (f''/2 + f'^2/2),
        E_lat = gamma_L^2 [e^f (f' h'/(4h) - f'^2/4) + v^2 R_etth],
        R_etth = -e^f [h''/(2h) - h'^2/(4h^2) - f' h'/(4h) - f''/2].
    """
    h = eta**2 + eta0**2
    hp, hpp = 2.0 * eta, 2.0
    fp = -(gamma / math.pi) * eta0 / h
    fpp = 2.0 * (gamma / math.pi) * eta0 * eta / h**2
    ef = math.exp(0.5 * gamma * (1.0 - 2.0 / math.pi * math.atan(eta / eta0)))
    gl2 = 1.0 / (1.0 - v * v)
    e_rad = ef * (0.5 * fpp + 0.5 * fp**2)
    r_t = ef * (fp * hp / (4.0 * h) - 0.25 * fp**2)
    r_e = -ef * (hpp / (2.0 * h) - hp**2 / (4.0 * h**2)
                 - fp * hp / (4.0 * h) - 0.5 * fpp)
    return e_rad, gl2 * (r_t + v * v * r_e)


def check_drainhole(eta0: float = 2.0, gamma: float = 0.8) -> bool:
    rmap, sx, sy, Dx, Dy, zero = _grid(eta0)
    F = 0.5 * gamma * (1.0 - sx)[:, None] + zero
    ok = True
    for xi in (-0.4, 0.0, 0.5):
        eta = float(rmap.eta(np.array([xi]))[0])
        for v in (0.0, 0.9):
            t = tidal(eta0, rmap, sx, sy, Dx, Dy, F, zero, zero,
                      zero + 1.0, xi, v=v)
            e_rad, e_lat = _drainhole_closed(eta0, gamma, eta, v)
            err = max(abs(t["rad"] - e_rad), abs(t["theta"] - e_lat),
                      abs(t["phi"] - e_lat),
                      float(np.max(np.abs(t["E"] - np.diag(np.diag(t["E"]))))))
            good = err <= TOL
            ok = ok and good
            print(f"  drainhole eta {eta:+5.2f} v {v:.1f}: rad "
                  f"{t['rad']:+.6e} (closed {e_rad:+.6e})  lat "
                  f"{t['theta']:+.6e} (closed {e_lat:+.6e})  err {err:.1e}"
                  f"  {'PASS' if good else 'FAIL'}")
    return ok


def check_member(path: str) -> bool:
    sol = Solution.load(path)
    rmap = sol.radial_map
    ones = np.ones_like(sol.F)
    th = throat(sol.eta0, rmap, sol.sx, sol.sy, sol._dx, sol.F, sol.N, ones)
    xi_t = float(rmap.xi_of_eta(th["eta_throat"]))
    args = (sol.eta0, rmap, sol.sx, sol.sy, sol._dx, sol._dy,
            sol.F, sol.W, sol.N, ones, xi_t)
    t0 = tidal(*args, v=0.0)
    ok = True
    scale = max(t0["max_abs"], 1.0 / sol.eta0**2)
    for v in (0.0, 0.5, 0.9):
        t = tidal(*args, v=v)
        asym = float(np.max(np.abs(t["E"] - t["E"].T)))
        refl = max(abs(t["E"][0, 1]), abs(t["E"][1, 2]))
        inv = abs(t["rad"] - t0["rad"])
        good = max(asym, refl, inv) <= 1e-11 * scale
        ok = ok and good
        print(f"  member v {v:.1f}: eigs "
              + " ".join(f"{e:+.6e}" for e in t["eigs"])
              + f"  E_13 {t['E'][0, 2]:+.2e}  boost-inv {inv:.1e}"
              f"  refl {refl:.1e}  {'PASS' if good else 'FAIL'}")
    name = path.rsplit("/", 1)[-1]
    print(f"  {name}: throat eta {th['eta_throat']:.6f}, R_e {th['R_e']:.6f},"
          f" max|eig| at v=0.9: {tidal(*args, v=0.9)['max_abs']:.6e}")
    return ok


def main() -> int:
    member = (sys.argv[1] if len(sys.argv) > 1 else
              "results/spinningwormhole/solutions/fam_b/fam_b_0003.json")
    ok = True
    print("static Ellis against Morris-Thorne (gate 1e-12):")
    ok &= check_ellis()
    print("static drainhole against the class formulas (gate 1e-12):")
    ok &= check_drainhole()
    print(f"rotating member identities ({member}):")
    ok &= check_member(member)
    print("ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
