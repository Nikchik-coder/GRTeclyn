"""The compliance factor F: definition, units and the Ford-Roman bound.

One module so a factor of 32 pi^2 / 3, an hbar power or a Planck-length
digit can only be wrong in one place (the spinning solver's conventions.py
pattern).

The bound (Ford & Roman, PRD 51 4277 and PRD 53 5496; flat space, massless
minimally coupled scalar, Lorentzian sampling of width tau0, hbar = c = 1):

    <rho>_tau0  >=  - 3 / (32 pi^2 tau0^4).

For a STATIONARY observer in a stationary spacetime rho is constant along
the worldline, so the sampled average equals the pointwise rho and the
local compliance factor is exact, not an estimate:

    F(x) = |rho_-(x)| * tau0(x)^4 / (3 / 32 pi^2) / hbar.

Units.  The solver works in geometric units (G = c = 1) with an arbitrary
code length unit L; hbar enters only as l_p^2.  fhat() below is F computed
as if L were one Planck length; the physical factor for a background scaled
so that one code unit is lambda metres is

    F = fhat * (lambda / l_p)^2,

so fixing the throat's physical equatorial radius R_phys gives
F = (fhat / R_eq_code^2) * (R_phys / l_p)^2.  The curve F(v_e) at fixed
throat size is therefore fhat / R_eq^2 up to one global constant.

Sampling convention.  tau0 = sampling_fraction * ell_c with ell_c the local
curvature scale (curvature.py) and sampling_fraction = 1 as the anchor
convention; Ford-Roman's f < 1 scales F by f^4 and cancels from every
F(v_e) / F(0) ratio.
"""

from __future__ import annotations

import math

__all__ = [
    "BOUND_COEFF", "L_PLANCK_M", "fhat", "f_physical",
    "static_ellis_fhat", "max_planck_throat",
]

# - 3 / (32 pi^2 tau0^4): the Lorentzian-sampled bound's coefficient.
BOUND_COEFF = 3.0 / (32.0 * math.pi**2)

L_PLANCK_M = 1.616255e-35


def fhat(rho: float, tau0: float) -> float:
    """F with the code length unit read as one Planck length.

    rho is the stationary-observer energy density (code units, negative
    where exotic); positive return = how far above the bound.
    """
    return max(0.0, -rho) * tau0**4 / BOUND_COEFF


def f_physical(fhat_value: float, code_unit_metres: float) -> float:
    """F of the background scaled so one code unit is the given length."""
    return fhat_value * (code_unit_metres / L_PLANCK_M) ** 2


def static_ellis_fhat(a: float) -> float:
    """Closed-form anchor: the massless static Ellis throat.

    rho = -a^2 / (8 pi h^2) and ell_c = h / a (largest orthonormal Riemann
    component a^2/h^2), so at the throat F = (4 pi / 3) a^2 -- the published
    Ford-Roman accounting: a static macroscopic throat overshoots the
    quantum budget by ~ (a / l_p)^2.
    """
    return (4.0 * math.pi / 3.0) * a * a


def max_planck_throat(fhat_per_req2: float) -> float:
    """The largest throat radius (in l_p) with F <= 1, given fhat/R_eq^2."""
    return 1.0 / math.sqrt(fhat_per_req2)
