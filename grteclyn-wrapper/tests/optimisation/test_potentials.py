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


def test_positive_bernstein_family_embeds_existing_cubic():
    from grteclyn_wrapper.optimisation.potentials import BernsteinKinkPotential
    q = (.672, .048, .310)
    controls = BernsteinKinkPotential.elevate_power_shape(q, 6)
    new = BernsteinKinkPotential(.4, -3.1, controls)
    old = PolynomialPotential.kink_q(.4, -3.1, q)
    psi = np.linspace(-3.1, 0, 101)
    for method in ("V", "dV", "d2V"):
        np.testing.assert_allclose(getattr(new, method)(psi), getattr(old, method)(psi),
                                   rtol=1e-10, atol=1e-11)


def test_positive_bernstein_vacua_and_derivatives():
    from grteclyn_wrapper.optimisation.potentials import BernsteinKinkPotential
    pot = BernsteinKinkPotential(.7, -2.3, (1., .2, 4., .1, 2., .3, 1.5))
    psi = np.linspace(-2.3, 0, 101)
    assert np.min(pot.V(psi)) >= 0
    assert np.all(pot.V(psi[1:-1]) > 0)
    for vacuum in (-2.3, 0.):
        assert pot.V(vacuum) == 0
        assert pot.dV(vacuum) == 0
        assert pot.d2V(vacuum) > 0
    h = 1e-5
    np.testing.assert_allclose(pot.dV(psi), (pot.V(psi+h)-pot.V(psi-h))/(2*h), atol=1e-8)
    np.testing.assert_allclose(pot.d2V(psi), (pot.dV(psi+h)-pot.dV(psi-h))/(2*h), atol=1e-7)
    with pytest.raises(ValueError):
        BernsteinKinkPotential(.3, -3., (1., -1., 2.))
