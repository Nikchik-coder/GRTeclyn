"""Derivative checks for small corrections to finite asymptotic fields."""
from types import SimpleNamespace
import numpy as np
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
from grteclyn_wrapper.optimisation.matter_equations import MatterCollocationProblem


def test_small_correction_derivatives_do_not_inherit_constant_roundoff():
    x, dx = lobatto(180)
    y, dy = lobatto(36)
    p = SimpleNamespace(sx=x, sy=y, Dx=dx, Dy=dy, Dxx=dx@dx, Dyy=dy@dy)
    a = 1+1e-4*(1-x[:, None]**2)*np.ones((1, len(y)))
    jets = MatterCollocationProblem._jets(p, {'B': a})
    direct_error = np.max(abs(p.Dxx@a+2e-4))
    assert np.max(abs(jets['B_xx']+2e-4)) < direct_error/5
    np.testing.assert_allclose(jets['B_x'], -2e-4*x[:, None]*np.ones_like(a), atol=1e-11)
    np.testing.assert_allclose(jets['B_xy'], 0., atol=1e-12)


def test_mixed_derivative_preserves_a_manufactured_polynomial():
    x, dx = lobatto(24)
    y, dy = lobatto(12)
    p = SimpleNamespace(sx=x, sy=y, Dx=dx, Dy=dy, Dxx=dx@dx, Dyy=dy@dy)
    a = 1+.2*x[:, None]**2*y[None, :]**3
    jets = MatterCollocationProblem._jets(p, {'B': a})
    np.testing.assert_allclose(jets['B_xy'], 1.2*x[:, None]*y[None, :]**2, atol=2e-11)
    np.testing.assert_allclose(jets['B_yy'], 1.2*x[:, None]**2*y[None, :], atol=2e-11)
