"""Scalar potentials for the campaign-M matter solver.

Two normalizations meet here.  The evolution code (ExoticScalarField with
PhantomDecayPotential) works with phi and V_evo(phi); the background
solver works in the CKK normalization of spinning_wormhole/conventions.py,

    psi = sqrt(4 pi) phi,        cal V(psi) = 8 pi V_evo(phi),

in which the field equations read R_ab = -2 psi_a psi_b - cal V g_ab and
box psi = cal V'(psi) / 2 (exotic scalar: canonical KG, flipped T_ab).
``PolynomialPotential`` stores cal V as a plain polynomial in psi and
evaluates with the caller's array type (numpy, jax.numpy or sympy), so
the same object feeds the residual forms under every backend.

A pure mass term admits no wormhole in this convention: multiplying the
KG equation by psi and integrating over the static slice forces
psi == 0 unless cal V has degenerate vacua at BOTH scalar boundary
values, psi(+inf) = 0 and psi(-inf) = psi_minus -- cal V and cal V' must
vanish at both ends or the asymptotics are not flat.  Hence the kink
constructors: every nontrivial potential here is of the form
psi^2 (psi - psi_minus)^2 Q(psi).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["PolynomialPotential", "ZERO"]

FOUR_PI = 4.0 * math.pi
EIGHT_PI = 8.0 * math.pi


@dataclass(frozen=True)
class PolynomialPotential:
    """cal V(psi) = sum_k coeffs[k] psi^k, solver normalization."""

    coeffs: tuple[float, ...] = ()

    def V(self, psi):
        out = 0.0 * psi
        for c in reversed(self.coeffs):
            out = out * psi + c
        return out

    def dV(self, psi):
        out = 0.0 * psi
        n = len(self.coeffs)
        for k in range(n - 1, 0, -1):
            out = out * psi + k * self.coeffs[k]
        return out

    @property
    def is_zero(self) -> bool:
        return all(c == 0.0 for c in self.coeffs)

    # -- constructors ---------------------------------------------------------

    @classmethod
    def from_evolution(cls, a: tuple[float, ...]) -> "PolynomialPotential":
        """From V_evo(phi) = sum_k a[k] phi^k: cal V = 8 pi V_evo, and each
        phi^k = psi^k / (4 pi)^{k/2}."""
        return cls(tuple(EIGHT_PI * ak / FOUR_PI ** (k / 2.0)
                         for k, ak in enumerate(a)))

    @classmethod
    def mass(cls, m: float) -> "PolynomialPotential":
        """V_evo = m^2 phi^2 / 2, i.e. cal V = m^2 psi^2.  No wormhole can
        carry it (see the module docstring) -- kept for the no-go check and
        for perturbative limits only."""
        return cls((0.0, 0.0, m * m))

    @classmethod
    def solitonic(cls, m: float, phi_c: float) -> "PolynomialPotential":
        """The dressed-star form V_evo = m^2 phi^2 (1 - phi^2/phi_c^2)^2 / 2:
        degenerate vacua at phi = 0 and phi = +-phi_c, so a kink reaching
        psi(-inf) = +-sqrt(4 pi) phi_c is admissible."""
        m2 = m * m
        return cls.from_evolution(
            (0.0, 0.0, m2 / 2.0, 0.0, -m2 / (phi_c * phi_c), 0.0,
             m2 / (2.0 * phi_c ** 4)))

    @classmethod
    def kink(cls, m: float, psi_minus: float) -> "PolynomialPotential":
        """The minimal quartic double well with vacua exactly at the two
        scalar boundary values: cal V = lam psi^2 (psi - psi_minus)^2 with
        lam = m^2 / psi_minus^2, so cal V'' (0) = 2 m^2 (the psi = 0 well
        has mass m in the cal V = m^2 psi^2 sense)."""
        lam = m * m / (psi_minus * psi_minus)
        return cls((0.0, 0.0, lam * psi_minus**2, -2.0 * lam * psi_minus,
                    lam))

    @classmethod
    def kink_q(cls, m: float, psi_minus: float,
               q: tuple[float, ...] = ()) -> "PolynomialPotential":
        """The kink times a shape factor, campaign step 3's scan family:

            cal V = lam psi^2 (psi - psi_minus)^2 Q(psi),
            Q = 1 + sum_k q[k] u^{k+1},   u = psi / psi_minus in [0, 1],

        lam = m^2 / psi_minus^2.  Q(0) = 1 keeps cal V''(0) = 2 m^2, and
        both vacua stay degenerate for any q (double zeros); the
        psi_minus well stays a minimum only while Q > 0 on the kink, so
        a scan checks min Q before solving.  q = () is ``kink``."""
        lam = m * m / (psi_minus * psi_minus)
        base = (0.0, 0.0, lam * psi_minus**2, -2.0 * lam * psi_minus, lam)
        shape = (1.0,) + tuple(qk / psi_minus ** (k + 1)
                               for k, qk in enumerate(q))
        out = [0.0] * (len(base) + len(shape) - 1)
        for i, b in enumerate(base):
            for j, c in enumerate(shape):
                out[i + j] += b * c
        return cls(tuple(out))


ZERO = PolynomialPotential(())
