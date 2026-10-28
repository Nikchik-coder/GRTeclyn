"""The kink_q shape family against the pure kink and its product form."""

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.potentials import PolynomialPotential


def test_kink_q_empty_is_kink():
    a = PolynomialPotential.kink(0.3, -2.5)
    b = PolynomialPotential.kink_q(0.3, -2.5)
    assert b.coeffs == pytest.approx(a.coeffs)


@pytest.mark.parametrize("q", [(0.5,), (0.5, -0.3), (-0.6, 0.6)])
def test_kink_q_vacua_stay_degenerate(q):
    pot = PolynomialPotential.kink_q(0.4, -3.1, q)
    for psi in (0.0, -3.1):
        assert pot.V(psi) == pytest.approx(0.0, abs=1e-13)
        assert pot.dV(psi) == pytest.approx(0.0, abs=1e-12)


def test_kink_q_matches_product_form():
    m, pm, q = 0.4, -3.1, (0.5, -0.3)
    pot = PolynomialPotential.kink_q(m, pm, q)
    lam = m * m / (pm * pm)
    for psi in np.linspace(pm, 0.5, 9):
        u = psi / pm
        want = lam * psi**2 * (psi - pm) ** 2 * (1 + q[0] * u + q[1] * u * u)
        assert pot.V(psi) == pytest.approx(want, rel=1e-12, abs=1e-14)
        du = 1e-7
        want_d = (pot.V(psi + du) - pot.V(psi - du)) / (2 * du)
        assert pot.dV(psi) == pytest.approx(want_d, rel=2e-6, abs=1e-6)
