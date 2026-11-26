"""Small CPU checks that travel with the standalone source distribution."""
import numpy as np

from grteclyn_stationary.numerics.newton import newton
from grteclyn_stationary.numerics.spectral import lobatto
from grteclyn_stationary.profiles.qball_couplings import QBallCouplings


def test_newton_solves_nonlinear_system():
    u, info = newton(lambda x: np.array([x[0]**2 - 2., x[1]**3 - 8.]),
                     lambda x: np.diag([2*x[0], 3*x[1]**2]), np.array([1., 1.]))
    assert info['converged']
    np.testing.assert_allclose(u, [np.sqrt(2), 2.], atol=1e-12)


def test_spectral_derivative_of_polynomial():
    x, D = lobatto(12)
    np.testing.assert_allclose(D @ x**4, 4*x**3, atol=1e-12)


def test_scalar_decay_scale_without_evolution_bridge():
    couplings = QBallCouplings.free_field(mass=1., omega=.8)
    np.testing.assert_allclose(couplings.bound_state_width, 1 / .6)
