"""Metric derivatives must retain anisotropy smaller than the nodal ulp."""
import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.smooth_spectral import SmoothSpectralProblem
from grteclyn_wrapper.optimisation.railgun.smooth_cubic import SmoothCubicProblem
from grteclyn_wrapper.optimisation.railgun.model import ScalarField
from grteclyn_wrapper.optimisation.railgun.workflow import save_state,load_state


def problem(nx=12,ny=4):
    return SmoothSpectralProblem([ScalarField(winding=1,mass=1.,amplitude=.1)],
        nx=nx,ny=ny,length=2.5,central_lapse=.9)


def tiny_anisotropy(p):
    u=np.zeros(p.n_unknowns);u[-1]=.8
    c=p.raw_metric(u,'f');c[0,0]=-1.
    c[:3,2]=1e-20*np.array([1.5,2.,.5])
    return u


def test_angular_derivatives_survive_rounding_of_large_background():
    p=problem();u=tiny_anisotropy(p)
    values,_=p.unpack(u)
    np.testing.assert_array_equal(values['f'],-np.ones(p.shape))
    jets=p.state_jets(u)
    expected=4e-20*(1+p.s[1:-1,None])**2*np.ones((1,p.ny+1))
    np.testing.assert_allclose(jets['f_yy'],expected,rtol=2e-13,atol=1e-34)
    # AD differentiates the retained coordinates, not the rounded nodal values.
    jax=p.jax
    fn=lambda a:p.state_jets(a,p.xp)['f_yy']
    actual=np.asarray(jax.jit(fn)(p.xp.asarray(u)))
    np.testing.assert_allclose(actual,expected,rtol=2e-13,atol=1e-34)


def test_low_degree_metric_obeys_the_same_continuous_and_boundary_rows():
    p=problem();u=tiny_anisotropy(p)
    for name in p.spectral_metric_tags:
        c=p.raw_metric(u,name);c[0,0]=-.02;c[1,0]=.003;c[2,2]=.0001
    arrays,freq=p.unpack(u)
    old=SmoothCubicProblem(p.fields,nx=p.nx,ny=p.ny,length=p.length,central_lapse=p.central_lapse)
    old_u=old.pack(arrays,freq)
    a=np.asarray(p.residual(u));b=np.asarray(old.residual(old_u))
    np.testing.assert_allclose(a,b,rtol=2e-10,atol=2e-12)
    assert np.isfinite(np.asarray(p.jacobian(u))).all()
    assert p.omitted_row_count==0


def test_archive_and_geometry_preserve_sub_ulp_coefficients(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.geometry import RingGeometry
    p=problem();u=tiny_anisotropy(p);path=tmp_path/'field.npz'
    save_state(path,p,u);other,v,metadata=load_state(path)
    assert isinstance(other,SmoothSpectralProblem)
    np.testing.assert_array_equal(u,v)
    geometry=RingGeometry(other,v)
    np.testing.assert_array_equal(np.asarray(geometry.coefficients['f']),p.raw_metric(u,'f'))


def test_refinement_retains_every_metric_coefficient():
    old=problem();new=problem(16,6);u=tiny_anisotropy(old)
    v=new.transfer(old,u)
    for name in old.spectral_metric_tags:
        c=new.raw_metric(v,name)
        np.testing.assert_array_equal(c[:old.nx+1,:old.ny+1],old.raw_metric(u,name))
        assert np.max(abs(c[old.nx+1:]))==0
        assert np.max(abs(c[:,old.ny+1:]))==0


def test_plan_keeps_physics_resolution_and_gates():
    from grteclyn_wrapper.optimisation.railgun.smooth_spectral_recovery import plan
    cfg=plan()['config']
    assert cfg['grids']==[[224,28],[256,32],[288,36]]
    assert cfg['equation_tol']==1e-8 and cfg['core']['tolerance']==1e-8
    assert cfg['newton_tol']==1e-14 and cfg['max_solves']==3
