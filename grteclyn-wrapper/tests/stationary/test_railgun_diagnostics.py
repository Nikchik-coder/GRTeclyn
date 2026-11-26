"""Independent geometric checks of the mass measured at compactified infinity."""
import numpy as np

from grteclyn_stationary.railgun.problem import RingProblem
from grteclyn_stationary.railgun.geometry import RingGeometry
from grteclyn_stationary.railgun.diagnostics import asymptotic_masses


def test_endpoint_mass_agrees_with_the_cartesian_ADM_surface_integral():
    # A manufactured metric checks the measurement, not the Einstein solver.
    p=RingProblem(nx=16,ny=4,length=2.)
    arrays={tag:np.zeros(p.shape) for tag in p.tags}
    mass,c,d=.4,.02,.03
    arrays['f'][:]=-mass/p.length*(1-p.s[:,None])
    arrays['b'][:]=c*(1-p.s[:,None])*(1+.4*(1+3*p.y[None,:])/4)
    arrays['N'][:]=d*(1-p.s[:,None])
    u=p.pack(arrays,[])
    adm,lapse=asymptotic_masses(p,u)
    expected=mass+2*p.length*c+2*p.length*d/3
    np.testing.assert_allclose([adm,lapse],[expected,mass],atol=1e-13)
    geometry=RingGeometry(p,u)
    jax,xp=p.jax,p.xp
    derivative=jax.jacfwd(lambda x:geometry.metric(x)[1:,1:])

    def flux(point):
        dg=derivative(point)[:,:,1:]
        normal=point[1:]/xp.linalg.norm(point[1:])
        return normal@(xp.einsum('ijj->i',dg)-xp.einsum('jji->i',dg))

    evaluate=jax.jit(jax.vmap(flux))
    mu,weights=np.polynomial.legendre.leggauss(24)
    mu,weights=(mu+1)/2,weights/2
    measured=[]
    for radius in p.length*np.array([1e4,2e4]):
        points=np.column_stack([np.zeros_like(mu),radius*np.sqrt(1-mu*mu),
                                np.zeros_like(mu),radius*mu])
        measured.append(radius**2/4*np.sum(weights*np.asarray(evaluate(xp.asarray(points)))))
    # Remove the leading finite-radius error from the literal Cartesian flux.
    np.testing.assert_allclose(2*measured[1]-measured[0],adm,rtol=3e-8,atol=1e-10)


def test_flat_endpoint_mass_is_zero():
    p=RingProblem(nx=8,ny=4)
    np.testing.assert_array_equal(asymptotic_masses(p,np.zeros(p.n_unknowns)),[0.,0.])
