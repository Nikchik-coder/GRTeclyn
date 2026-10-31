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

__all__ = ["PolynomialPotential", "BernsteinKinkPotential", "ZERO"]

FOUR_PI = 4.0 * math.pi
EIGHT_PI = 8.0 * math.pi


@dataclass(frozen=True)
class PolynomialPotential:
    """cal V(psi) = sum_k coeffs[k] psi^k, solver normalization."""

    coeffs: tuple[float, ...] = ()
    # Retain the product form for a kink: expanded Horner evaluation loses
    # the double zero at the nonzero vacuum to cancellation. Compactified
    # far-end equations amplify that tiny fictitious potential.
    _kink_data: tuple | None = None

    def _kink_parts(self, psi):
        m, pm, q = self._kink_data
        u = psi/pm
        shape, first, second = 0.*psi+1., 0.*psi, 0.*psi
        for k, coefficient in enumerate(q, 1):
            shape = shape+coefficient*u**k
            first = first+k*coefficient*u**(k-1)/pm
            if k >= 2:
                second = second+k*(k-1)*coefficient*u**(k-2)/pm**2
        return m*m/(pm*pm), psi-pm, shape, first, second

    def V(self, psi):
        if self._kink_data is not None:
            lam, z, shape, _, _ = self._kink_parts(psi)
            return lam*(psi*z)**2*shape
        out = 0.0 * psi
        for c in reversed(self.coeffs):
            out = out * psi + c
        return out

    def dV(self, psi):
        if self._kink_data is not None:
            lam, z, shape, first, _ = self._kink_parts(psi)
            return lam*(2*psi*z*(psi+z)*shape+(psi*z)**2*first)
        out = 0.0 * psi
        n = len(self.coeffs)
        for k in range(n - 1, 0, -1):
            out = out * psi + k * self.coeffs[k]
        return out

    def d2V(self, psi):
        """cal V''(psi), the radial stability screen's V2 column."""
        if self._kink_data is not None:
            lam, z, shape, first, second = self._kink_parts(psi)
            g, gp = psi*z, psi+z
            return lam*((2*gp**2+4*g)*shape+4*g*gp*first+g*g*second)
        out = 0.0 * psi
        n = len(self.coeffs)
        for k in range(n - 1, 1, -1):
            out = out * psi + k * (k - 1) * self.coeffs[k]
        return out

    def dV_over(self, psi):
        """cal V'(psi) / psi without the division:
        sum_{k >= 2} k coeffs[k] psi^{k-2}.  The winding and layer KG
        rows need the ratio where the field has zeros (the winding
        amplitude vanishes on the axis), so a linear term is refused --
        the ratio would be singular there."""
        if self._kink_data is not None:
            lam, z, shape, first, _ = self._kink_parts(psi)
            return lam*(2*z*(psi+z)*shape+psi*z*z*first)
        if len(self.coeffs) > 1 and self.coeffs[1] != 0.0:
            raise ValueError("dV_over: the potential has a linear term")
        out = 0.0 * psi
        n = len(self.coeffs)
        for k in range(n - 1, 1, -1):
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
                    lam), (m, psi_minus, ()))

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
        return cls(tuple(out), (m, psi_minus, tuple(q)))


@dataclass(frozen=True)
class BernsteinKinkPotential:
    """A kink with a positive Bernstein shape on the vacuum interval.

    Positive controls guarantee Q > 0 for 0 <= psi/psi_minus <= 1.
    The first control is one, preserving the mass at the zero vacuum.
    Evaluation stays in Bernstein form to avoid cancellation at the vacua.
    ``psi_minus`` may be a JAX tracer in a bordered Newton solve.
    """

    m: float
    psi_minus: float
    controls: tuple[float, ...]

    def __post_init__(self):
        if not self.controls or self.controls[0] != 1.0:
            raise ValueError("the first Bernstein control must be one")
        if any(not math.isfinite(c) or c <= 0 for c in self.controls):
            raise ValueError("Bernstein controls must be finite and positive")

    @staticmethod
    def _bernstein(u, controls):
        n = len(controls) - 1
        return sum(c * math.comb(n, i) * u**i * (1-u)**(n-i)
                   for i, c in enumerate(controls))

    def _shape(self, psi, order=0):
        c = self.controls
        factor = 1.0
        for _ in range(order):
            factor *= (len(c) - 1) / self.psi_minus
            c = tuple(b - a for a, b in zip(c, c[1:]))
            if not c:
                return 0.0 * psi
        return factor * self._bernstein(psi / self.psi_minus, c)

    def V(self, psi):
        return (self.m / self.psi_minus)**2 * psi**2 * (
            psi - self.psi_minus)**2 * self._shape(psi)

    def dV(self, psi):
        p = self.psi_minus
        base = psi**2 * (psi-p)**2
        deriv = 2*psi*(psi-p)*(2*psi-p)
        return (self.m/p)**2 * (deriv*self._shape(psi)
                               + base*self._shape(psi, 1))

    def d2V(self, psi):
        p = self.psi_minus
        base = psi**2 * (psi-p)**2
        deriv = 2*psi*(psi-p)*(2*psi-p)
        second = 12*psi**2 - 12*p*psi + 2*p*p
        return (self.m/p)**2 * (second*self._shape(psi)
                               + 2*deriv*self._shape(psi, 1)
                               + base*self._shape(psi, 2))

    @staticmethod
    def elevate_power_shape(q, degree):
        """Represent 1 + sum q[k] u**(k+1) exactly at a higher degree.

        Refuse shapes without positive controls; approximation would change
        the matched baseline before the experiment starts.
        """
        if degree < len(q):
            raise ValueError("degree must cover the original shape")
        a = (1.0, *q)
        controls = tuple(sum(a[k] * math.comb(i, k) / math.comb(degree, k)
                             for k in range(min(i, len(q)) + 1))
                         for i in range(degree + 1))
        if any(c <= 0 or not math.isfinite(c) for c in controls):
            raise ValueError("baseline has nonpositive Bernstein controls")
        return controls


ZERO = PolynomialPotential(())
