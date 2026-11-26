"""Signed-axis diagnostics and the distinction between field and gradient energy."""
from types import SimpleNamespace
import numpy as np
import pytest
from grteclyn_stationary.numerics.device import configure_jax
from grteclyn_stationary.railgun.profiles import axial_profile,matter_sampler


def test_signed_flat_profile_is_regular_and_has_zero_curvature():
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.corridor import CartesianCorridor
    p=RingProblem(nx=8,ny=4)
    core=CartesianCorridor(RingGeometry(p,np.zeros(p.n_unknowns)),radius=.4,degree=3)
    assert core.certify()['accepted']
    data,description=axial_profile(core,z_min=-1.,z_max=1.,samples=9)
    columns={name:data[:,i] for i,name in enumerate(description['columns'])}
    np.testing.assert_allclose(columns['proper_distance_from_z_min'],data[:,0]+1.,atol=1e-13)
    np.testing.assert_allclose(columns['lapse'],1.,atol=1e-13)
    for name in ('magnetic_tidal_zz','electric_tidal_zz','scalar_amplitude_squared',
                 'Eulerian_matter_energy_density','shift_norm_over_lapse'):
        np.testing.assert_allclose(columns[name],0.,atol=1e-13)
    with pytest.raises(ValueError,match='regular core'):
        axial_profile(core.parent,z_min=-1.,z_max=1.)


def test_winding_one_axis_has_gradient_energy_despite_zero_amplitude():
    jax=configure_jax();xp=jax.numpy
    # Local chi=a(x+iy): its axis value vanishes but two transverse
    # derivatives contribute 2*a^2/(8*pi) to Eulerian energy density.
    a=.03
    geometry=SimpleNamespace(jax=jax,xp=xp,
        metric=lambda point:xp.diag(xp.array([-1.,1.,1.,1.])),
        scalar=lambda point,index:a*xp.array([point[1],point[2]]),
        fields=[SimpleNamespace(mass=1.,quartic=0.,sextic=0.)])
    amplitude,density=np.asarray(matter_sampler(geometry)(xp.array([0.,0.,0.,.2])))
    assert amplitude==0.
    assert density==pytest.approx(a*a/(4*np.pi),rel=1e-13)


def test_profile_bounds_are_checked_before_sampling():
    for bounds in ((0.,0.),(1.,-1.),(0.,np.nan)):
        with pytest.raises(ValueError,match='finite'):
            axial_profile(None,z_min=bounds[0],z_max=bounds[1])
