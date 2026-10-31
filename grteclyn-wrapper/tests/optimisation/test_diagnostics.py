"""Exact limits and dimensional checks for saved-background diagnostics."""
import numpy as np
import pytest

from grteclyn_wrapper.optimisation.diagnostics import static
from grteclyn_wrapper.optimisation.exoticity import nec_rays


def test_ellis_gradients_null_integral_and_transit():
    b = static(eta0=2., gamma=0., nx=80, ny=8)
    xi = np.array([-.4, 0., .4])
    eta = b.rmap.eta(xi)
    a = b.local(xi, [0., .5, 1.])
    expected = 4/(4*np.pi*(eta**2+4)**2)
    np.testing.assert_allclose(a['nec_r'], np.broadcast_to(expected[:, None], (3, 3)), rtol=1e-10)
    np.testing.assert_allclose(a['nec_theta'], 0., atol=1e-25)
    rays = nec_rays(b.eta0, b.rmap, b.sx, b.sy, b.dx, b.N, b.B, b.PSI, n_x=192)
    np.testing.assert_allclose(list(rays.values()), -1/16, rtol=1e-11)
    ell = np.linspace(-20., 20., 51)
    for mu in (0., 1.):
        x, t = b.crossing(ell, mu=mu)
        np.testing.assert_allclose(b.rmap.eta(x), ell, atol=1e-7)
        np.testing.assert_allclose(t, ell, atol=1e-8)
    with pytest.raises(ValueError, match='constant-theta'):
        b.crossing(ell, mu=.5)


def test_similarity_invariance_and_tidal_normalisation():
    small = static(eta0=2., gamma=0., nx=80, ny=8)
    large = static(eta0=6., gamma=0., nx=80, ny=8)
    np.testing.assert_allclose(small.tide(0., .5), 1/12, rtol=1e-9)
    np.testing.assert_allclose(large.tide(0., .5), small.tide(0., .5)/9, rtol=1e-9)
    np.testing.assert_allclose(large.integral(order=192), 3*small.integral(order=192), rtol=1e-11)
    np.testing.assert_allclose(large.local([0.], [0.])['nec_r'],
                               small.local([0.], [0.])['nec_r']/9, rtol=1e-11)


def test_drainhole_null_transit_independent_quadrature():
    from scipy.integrate import quad
    b = static(nx=80, ny=8)
    ell = np.linspace(-10., 10., 31)
    xi, time = b.crossing(ell)
    for x, l in zip(xi[::10], ell[::10]):
        np.testing.assert_allclose(b.proper_distance(x, order=192), l, atol=2e-7)
    # Direct eta-space null condition: dt/deta = exp(-F), B=1 and nu=0.
    eta = b.rmap.eta(xi[[0, -1]])
    expected = quad(lambda r: np.exp(np.pi/2-np.arctan(r/2)), *eta,
                    epsabs=1e-10, epsrel=1e-10)[0]
    np.testing.assert_allclose(time[-1]-time[0], expected, rtol=2e-9)


def test_saved_static_tides_against_independent_spherical_formula():
    from pathlib import Path
    from grteclyn_wrapper.optimisation.diagnostics import potential, spherical_tidal_check
    root = Path(__file__).resolve().parents[3]
    b = potential(root/'results/optimisation/validation/2026-10-30-alternatives/d0/009_e0211/handoff.npz')
    assert max(r['scaled_error'] for r in spherical_tidal_check(b)) < 1e-5
