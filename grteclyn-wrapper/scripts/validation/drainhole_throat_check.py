#!/usr/bin/env python3
"""Analytic check of the massive Ellis-Bronnikov drainhole throat.

Why this exists
---------------
``BinaryWormholeMerger`` used to earn its ADM mass by adding a Brill-Lindquist
puncture to the conformal factor, ``psi += m/(2 rbar)``.  That works for black
holes and is fatal for a wormhole: it drives chi -> 0 *at the throat itself*, so
the proper cell width dx/sqrt(chi) at the minimal surface exceeded the throat's
own areal radius and no matter model could be evaluated on the geometry (see
research/merger/MatterDebug.md).

The massive drainhole earns the same ADM mass from the LAPSE instead and leaves
the spatial conformal factor bounded.  In the isotropic radius rbar the code
already uses, with X = (rbar - a^2/(4 rbar))/a the Ellis coordinate and
Omega = 1 + a^2/(4 rbar^2):

    u    = (m/a) (atan X - pi/2)          static lapse exponent, u -> 0 at infinity
    chi  = e^{2u} / Omega^2               gamma_ij = chi^{-1} delta_ij
    alpha= e^{u}                          the exact static lapse
    phi  = sqrt(a^2+m^2)/(a sqrt(4 pi)) * atan X
    K = 0, A_ij = 0, Pi = 0

This is an exact static solution of Einstein + massless phantom scalar, so both
constraints hold identically at t = 0 -- unlike the superposed puncture data,
which carried a Hamiltonian defect by construction.  Its ADM mass is m, so two
of them attract, which a massless Ellis throat (ultrastatic, M_ADM = 0) does not.

Derived properties this script verifies rather than assumes:

  * the minimal surface sits at l = m, i.e. rbar = (m + sqrt(m^2+a^2))/2 -- NOT
    at l = 0 as the massless case would suggest;
  * R_min = e^{-u(m)} sqrt(m^2+a^2);
  * chi at the throat stays in ~[0.15, 0.25] over the whole useful (m/a) range,
    so the proper cell width there is only ~2.0-2.6 dx, against 4 dx for a
    Brill-Lindquist throat at its minimal surface and 12.5 dx at its innermost
    resolved cell;
  * the genuinely unresolvable region (chi < 0.01, the compactified far
    universe) sits well INSIDE the minimal surface -- 0.98 against a throat at
    2.69 for a = 4, m = 1.2 -- so it can be frozen without touching the throat.

Run with no arguments for the default parameter sweep.
"""

from __future__ import annotations

import argparse
import math

import numpy as np


# ---------------------------------------------------------------- the solution
def fields(rbar, a, m):
    """Return (X, Omega, u, chi, alpha, phi) for the massive drainhole."""
    X = (rbar - a * a / (4.0 * rbar)) / a
    omega = 1.0 + a * a / (4.0 * rbar * rbar)
    u = (m / a) * (np.arctan(X) - 0.5 * math.pi)
    chi = np.exp(2.0 * u) / (omega * omega)
    alpha = np.exp(u)
    phi = math.sqrt(a * a + m * m) / (a * math.sqrt(4.0 * math.pi)) * np.arctan(X)
    return X, omega, u, chi, alpha, phi


def throat(a, m):
    """Analytic minimal surface: (rbar_throat, R_min, chi_throat)."""
    rbar = 0.5 * (m + math.hypot(m, a))
    u = (m / a) * (math.atan(m / a) - 0.5 * math.pi)
    r_min = math.exp(-u) * math.hypot(m, a)
    omega = 1.0 + a * a / (4.0 * rbar * rbar)
    return rbar, r_min, math.exp(2.0 * u) / (omega * omega)


# ------------------------------------------------------------ constraint check
def _d1(f, h):
    return (-f[4:] + 8.0 * f[3:-1] - 8.0 * f[1:-3] + f[:-4]) / (12.0 * h)


def _d2(f, h):
    return (-f[4:] + 16.0 * f[3:-1] - 30.0 * f[2:-2] + 16.0 * f[1:-3] - f[:-4]) / (
        12.0 * h * h
    )


def hamiltonian_residual(a, m, h, r_lo=0.2, r_hi=20.0):
    """Relative residual of  lap(Psi) = pi Psi (dphi/dr)^2,  Psi = chi^{-1/4}.

    With K = 0 and a phantom scalar the Hamiltonian constraint in conformally
    flat form is  lap_flat(Psi) = pi Psi |grad phi|^2  (the wrong-sign
    Lichnerowicz equation).  A residual at roundoff proves the closed forms
    above really are a solution and not an ansatz.
    """
    r = np.arange(r_lo, r_hi, h)
    _, _, _, chi, _, phi = fields(r, a, m)
    psi = chi ** -0.25
    lap = _d2(psi, h) + 2.0 / r[2:-2] * _d1(psi, h)
    src = math.pi * psi[2:-2] * _d1(phi, h) ** 2
    return float(np.max(np.abs(lap - src)) / np.max(np.abs(src)))


# ------------------------------------------------------ what it replaces
def puncture_throat(m_bare):
    """The Brill-Lindquist throat this replaces: psi = 1 + m/(2 rbar)."""
    rbar = 0.5 * m_bare  # minimal surface of R = psi^2 rbar
    return rbar, 2.0 * m_bare, 1.0 / 16.0  # (rbar_throat, R_min, chi_throat)


def collar_radius(a, m, chi_cut=0.01, r_hi=None):
    """Largest rbar inside the throat at which chi has fallen below chi_cut.

    This is the compactified far universe -- the region that is genuinely
    unresolvable in one Cartesian box and that the origin-isolating lapse
    exists to freeze.  Its size relative to the throat is what says whether a
    collar is still needed.
    """
    r_th = throat(a, m)[0]
    r = np.linspace(1.0e-4, r_th, 200_000)
    chi = fields(r, a, m)[3]
    below = np.nonzero(chi < chi_cut)[0]
    return float(r[below[-1]]) if below.size else 0.0


def cells_across_throat(a, m, dx, flare=1.1):
    """Level-0 cells between the minimal surface and where R = flare * R_min.

    This, not the areal radius, is what decides the grid.  The puncture failed
    on exactly this number: its throat region spanned ~5 cells of which the
    innermost was wider in proper distance than the throat itself.
    """
    r_th, r_min, _ = throat(a, m)
    r = np.linspace(r_th, r_th + 20.0 * a, 400_000)
    areal = r / np.sqrt(fields(r, a, m)[3])
    above = np.nonzero(areal > flare * r_min)[0]
    if not above.size:
        return float("nan")
    return float((r[above[0]] - r_th) / dx)


def free_fall_time(d, m_each):
    """Newtonian free-fall from rest at separation d for two masses m_each."""
    return math.pi * math.sqrt(d**3 / (8.0 * 2.0 * m_each))


# ------------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dx", type=float, default=0.25,
                    help="evolution level-0 cell width used for the proper-width column")
    ap.add_argument("--separation", type=float, default=None,
                    help="binary separation for the free-fall column (default 8a)")
    args = ap.parse_args()

    print("1. Hamiltonian constraint of the closed form (relative residual, 4th order)")
    print("   convergence to roundoff, growing as h shrinks, IS the pass condition")
    print(f"   {'a':>5} {'m':>5} {'h=1e-3':>10} {'h=5e-4':>10} {'h=2.5e-4':>10}")
    for a, m in [(1.0, 0.0), (1.0, 0.3), (4.0, 1.2), (1.0, 1.0), (2.0, 3.0)]:
        res = [hamiltonian_residual(a, m, h) for h in (1e-3, 5e-4, 2.5e-4)]
        print(f"   {a:5.1f} {m:5.1f} {res[0]:10.2e} {res[1]:10.2e} {res[2]:10.2e}")

    print()
    print(f"2. Throat properties (dx = {args.dx})")
    print(f"   {'a':>5} {'m':>5} {'m/a':>6} {'rbar_th':>8} {'R_min':>8} "
          f"{'chi_th':>8} {'in dx':>7} {'cells':>7} {'collar':>8} {'t_ff':>8}")
    for a in (1.0, 2.0, 4.0):
        for m_over_a in (0.0, 0.1, 0.2, 0.3, 0.5, 1.0):
            m = m_over_a * a
            r_th, r_min, chi_th = throat(a, m)
            # cross-check the closed forms against a direct grid minimisation
            r = np.linspace(1e-4, 50.0 * a, 2_000_001)
            chi = fields(r, a, m)[3]
            areal = r / np.sqrt(chi)
            i = int(np.argmin(np.where(r > 1e-3, areal, np.inf)))
            assert abs(r[i] - r_th) < 1e-3 * a, (a, m, r[i], r_th)
            assert abs(areal[i] - r_min) < 1e-3 * a, (a, m, areal[i], r_min)
            width = args.dx / math.sqrt(chi_th)
            d = args.separation if args.separation else 8.0 * a
            t_ff = free_fall_time(d, m) if m > 0 else float("inf")
            print(f"   {a:5.1f} {m:5.2f} {m_over_a:6.2f} {r_th:8.3f} {r_min:8.3f} "
                  f"{chi_th:8.4f} {width/args.dx:7.2f} "
                  f"{cells_across_throat(a, m, args.dx):7.1f} "
                  f"{collar_radius(a, m):8.3f} {t_ff:8.1f}")

    print()
    print("3. What this replaces -- Brill-Lindquist puncture throat, same ADM mass")
    print(f"   {'m_bare':>7} {'rbar_th':>8} {'R_min':>8} {'chi_th':>8} {'in dx':>7}")
    for m_bare in (0.25, 1.0, 2.0, 4.0):
        r_th, r_min, chi_th = puncture_throat(m_bare)
        width = args.dx / math.sqrt(chi_th)
        print(f"   {m_bare:7.2f} {r_th:8.3f} {r_min:8.3f} {chi_th:8.4f} "
              f"{width/args.dx:7.2f}")
    print()
    print("   The puncture column is optimistic: chi_th = 1/16 is its value AT the")
    print("   minimal surface, and chi keeps falling inwards, so the innermost cells")
    print("   are far worse (measured 6.2 proper units at dx = 0.5 on the m = 2 solve).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
