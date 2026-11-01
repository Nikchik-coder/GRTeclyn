"""Independent full curvature: flat, Schwarzschild and rotating Kerr benchmarks."""
import numpy as np
import pytest

from grteclyn_wrapper.optimisation.solver.device import configure_jax
from grteclyn_wrapper.optimisation.railgun.geometry import curvature, RingGeometry

jax = configure_jax()
xp = jax.numpy


def minkowski(x):
    return xp.diag(xp.array([-1.,1.,1.,1.]))


def kerr_schild(x, mass=1., spin=.4):
    position = x[1:]
    radius2 = xp.sum(position**2)
    r2 = .5*(radius2-spin**2+xp.sqrt((radius2-spin**2)**2+4*spin**2*x[3]**2))
    r = xp.sqrt(r2)
    ell = xp.array([1.,(r*x[1]+spin*x[2])/(r2+spin**2),
                    (r*x[2]-spin*x[1])/(r2+spin**2),x[3]/r])
    h = mass*r**3/(r**4+spin**2*x[3]**2)
    return minkowski(x)+2*h*xp.outer(ell,ell)


@pytest.mark.parametrize('spin', [0.,.4])
@pytest.mark.parametrize('position', [[0.,3.,2.,4.],[0.,0.,0.,5.]])
def test_kerr_ricci_and_kretschmann(spin,position):
    metric = lambda x:kerr_schild(x,spin=spin)
    g,_,riem,ricci = map(np.asarray,jax.jit(curvature(metric,jax))(xp.array(position)))
    np.testing.assert_allclose(ricci,0.,atol=5e-14)
    low = np.einsum('ae,ebcd->abcd',g,riem)
    inv = np.linalg.inv(g)
    upper = np.einsum('ae,bf,cg,dh,efgh->abcd',inv,inv,inv,inv,low)
    measured = np.sum(low*upper)
    x,y,z = position[1:]
    r2 = .5*(x*x+y*y+z*z-spin**2+np.sqrt((x*x+y*y+z*z-spin**2)**2+4*spin**2*z*z))
    az2 = spin**2*z*z/r2
    expected = 48*(r2**3-15*r2*r2*az2+15*r2*az2**2-az2**3)/(r2+az2)**6
    assert measured == pytest.approx(expected,rel=2e-12,abs=1e-14)


def test_cartesian_interpolant_is_flat_and_finite_on_axis():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    p = RingProblem(nx=8,ny=4)
    geom = RingGeometry(p,np.zeros(p.n_unknowns))
    x = xp.array([0.,0.,0.,3.])
    g,_,riem,_ = map(np.asarray,geom.tensors(x))
    np.testing.assert_allclose(g,np.diag([-1.,1.,1.,1.]),atol=1e-14)
    np.testing.assert_allclose(riem,0.,atol=1e-14)
    assert geom.independent([0.,1.,0.,2.])['einstein_max'] < 1e-14
    with pytest.raises(ValueError):
        geom.independent([0.,0.,0.,0.])


def test_metric_interpolation_retains_coordinate_derivatives():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    p = RingProblem(nx=12,ny=4,length=2.)
    arrays = {tag:np.zeros(p.shape) for tag in p.tags}
    arrays['w'] = .01*(1-p.s[:,None])**3*np.ones((1,p.ny+1))
    geom = RingGeometry(p,p.pack(arrays,[]))
    point = xp.array([0.,0.,0.,3.])
    result = geom.tensors(point)
    assert all(np.isfinite(a).all() for a in result)
    assert np.max(abs(np.asarray(result[2]))) > 1e-5
    # Reversing rotation reverses g_ti and the spin-odd curvature components.
    arrays['w'] *= -1
    reverse = RingGeometry(p,p.pack(arrays,[]))
    off = xp.array([0.,1.,0.,3.])
    np.testing.assert_allclose(np.asarray(geom.metric(off))[0,1:],
                               -np.asarray(reverse.metric(off))[0,1:],atol=1e-14)
