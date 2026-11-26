"""Sign and normalization conventions of the fast-spin background solver.

One module, so a mu sign, a factor of 2 in J or an eta0 power can only be
wrong in one place (SpinningSolver.md P0).  Everything follows
Chew-Kleihaus-Kunz (arXiv:1608.05253) with two corrections: mu_+ = -gamma eta0 / (2 pi) (CKK print it without the
minus sign), and the extremal trend J/R_e^2 -> 1/4 (CKK Fig. 2 plots
2J/R_0^2; Volkov 2026 section X).

The conventions:
- x = (2/pi) atan(eta/eta0); y = cos 2 theta (axis y = +1, equator -1).
- f -> -2 mu_+ / eta as eta -> +inf and f -> gamma + 2 mu_- / eta as
  eta -> -inf, so on the arctan grid mu_+ = (eta0/pi) f_x(+1) and
  mu_- = -(eta0/pi) f_x(-1); map-free, mu_+/- = +/- eta^2 f_eta / 2 at the
  ends.  M_ADM of the +inf universe is mu_+.
- omega -> 2 J / eta^3 as eta -> +inf; J(x), the conserved radial flux of
  eq. (11), is -(eta0^3 / 4 pi C^2) int (1 - mu^2) e^{-2f} w_x dmu
  (observables.py does the quadrature) and equals J_+ for every x.
- Smarr (CKK eq. 28): mu_+ + mu_- = 2 omega_{-inf} J_+.
- D: the scalar charge, psi = (D/eta0)(atan(eta/eta0) - pi/2), so the
  table's phi = psi / sqrt(4 pi); static D^2 = eta0^2 + mu_+^2.
- v_e = R_eq Omega_throat at the area-minimizing eta = const surface,
  R_eq = e^{-f/2} sqrt(h) on the equator; extremal Kerr is v_e -> 1.
- gamma = -2 pi m / eta0 rotates the static drainhole of mass m (family
  (a): eta0 = 2, m = 1, gamma = -pi; family (b): gamma = 0).
"""

from __future__ import annotations

import math

__all__ = [
    "gamma_of_mass", "mass_of_gamma", "mu_plus_from_fx", "mu_minus_from_fx",
    "smarr_residual", "v_e", "static_member", "static_f_of_x",
    "static_phi_of_x",
]


def gamma_of_mass(mass: float, eta0: float) -> float:
    """f(-inf) of the static drainhole of mass m: gamma = -2 pi m / eta0."""
    return -2.0 * math.pi * mass / eta0


def mass_of_gamma(gamma: float, eta0: float) -> float:
    """mu_+ of the static member: -gamma eta0 / (2 pi)."""
    return -gamma * eta0 / (2.0 * math.pi)


def mu_plus_from_fx(fx_plus: float, eta0: float) -> float:
    """mu_+ from f_x at x = +1 on the arctan grid."""
    return eta0 / math.pi * fx_plus


def mu_minus_from_fx(fx_minus: float, eta0: float) -> float:
    """mu_- from f_x at x = -1 on the arctan grid."""
    return -eta0 / math.pi * fx_minus


def smarr_residual(mu_plus: float, mu_minus: float, omega_minus_inf: float,
                   J_plus: float) -> float:
    """Relative Smarr defect |mu_+ + mu_- - 2 omega_{-inf} J_+| / scale
    (CKK eq. 28; gate 1e-10).  The scale floors at eta0-free 1e-300 only
    when every term vanishes (the static member: defect exactly 0)."""
    lhs = mu_plus + mu_minus
    rhs = 2.0 * omega_minus_inf * J_plus
    scale = max(abs(mu_plus), abs(mu_minus), abs(rhs), 1e-300)
    return abs(lhs - rhs) / scale


def v_e(r_eq: float, omega_throat: float) -> float:
    """The throat equator's rotation speed; extremal Kerr is v_e -> 1."""
    return r_eq * omega_throat


def static_f_of_x(x, gamma: float):
    """f of the static member: exactly linear on the arctan grid."""
    return 0.5 * gamma * (1.0 - x)


def static_phi_of_x(x, eta0: float, gamma: float):
    """The table's phi (= psi / sqrt(4 pi)) of the static member."""
    mu_p = mass_of_gamma(gamma, eta0)
    d = math.sqrt(eta0 * eta0 + mu_p * mu_p)
    return (d / eta0) * 0.5 * math.pi * (x - 1.0) / math.sqrt(4.0 * math.pi)


def static_member(eta0: float, gamma: float) -> dict[str, float]:
    """Closed-form observables of the v_e = 0 member."""
    mu_p = mass_of_gamma(gamma, eta0)
    return {
        "mu_plus": mu_p,
        "mu_minus": -mu_p,
        "M_ADM": mu_p,
        "J": 0.0,
        "omega_minus_inf": 0.0,
        "D": math.sqrt(eta0 * eta0 + mu_p * mu_p),
        "gamma": gamma,
        "eta_throat": mu_p,   # the area minimum of the static drainhole
        "v_e": 0.0,
    }
