"""The ring correction retains its physical equations and exact archive field."""
import json

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.smooth_cubic import SmoothCubicProblem,REPRESENTATION
from grteclyn_wrapper.optimisation.railgun.model import ScalarField
from grteclyn_wrapper.optimisation.railgun.workflow import save_state,load_state


def problem(nx=12,ny=4):
    return SmoothCubicProblem([ScalarField(winding=1,mass=1.,amplitude=.1)],
                             nx=nx,ny=ny,length=2.5,central_lapse=.12993066385192364)


def state(p):
    u=np.zeros(p.n_unknowns);u[:p.n]=2*np.log(p.central_lapse);u[-1]=.674
    raw=p.raw_dragging(u);raw[0]=.03;raw[1]=-.01
    return u


def test_all_dragging_pdes_are_retained_and_origin_is_isotropic():
    p=problem();u=state(p)
    residual=np.asarray(p.residual(u))[p.n:2*p.n].reshape(p.shape)
    np.testing.assert_allclose(residual[1:-1],p.regular_rows(u),atol=1e-12)
    np.testing.assert_allclose(residual[0],p.infinity_boundary(u),atol=1e-12)
    assert p.omitted_row_count==0
    assert np.max(abs(residual[-1]))>0
    assert np.isfinite(np.asarray(p.jacobian(u))).all()


def test_physical_and_factored_archive_roundtrip_retains_fixed_lapse(tmp_path):
    p=problem();u=state(p);path=tmp_path/'state.npz';save_state(path,p,u)
    other,v,meta=load_state(path)
    assert meta['representation']==REPRESENTATION
    assert other.central_lapse==p.central_lapse
    np.testing.assert_array_equal(v,u)
    base,physical=p.physical_vector(u)
    assert base.central_lapse==p.central_lapse
    with np.load(path) as data:
        np.testing.assert_array_equal(data['u'],physical)
    assert abs(float(base.residual(physical)[-1]))<1e-15


def test_archive_rejects_inconsistent_solver_coordinates(tmp_path):
    p=problem();u=state(p);path=tmp_path/'state.npz';save_state(path,p,u)
    with np.load(path) as data:
        content=dict(data)
    content['solver_u'][p.n]+=.01
    np.savez(path,**content)
    with pytest.raises(ValueError,match='disagree'):
        load_state(path)


def test_refinement_and_perturbation_preserve_the_resolved_tail():
    old=problem();new=problem(16,6);u=state(old)
    v=new.transfer(old,u,perturb=1e-5)
    s=np.array([.9,.9999]);y=np.array([-.6,.4])
    np.testing.assert_allclose(new.dragging_sample(v,s,y),old.dragging_sample(u,s,y),rtol=2e-14)
    assert np.max(abs(v[:new.n]-2*np.log(new.central_lapse)))>1e-6


def test_cartesian_geometry_and_core_polynomial_describe_the_same_field():
    from grteclyn_wrapper.optimisation.railgun.geometry import RingGeometry
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import surface_flux
    p=problem();u=state(p);geometry=RingGeometry(p,u)
    for s in (-1.,-.8,.2,.99):
        expected=p.dragging_sample(u,[s],[.3])[0,0]
        assert float(geometry.sample('w',s,.3))==pytest.approx(expected,rel=1e-13)
        polynomial=np.polynomial.chebyshev.chebval2d(s,.3,np.asarray(geometry.coefficients['w']))
        assert polynomial==pytest.approx(expected,abs=1e-16)
    assert geometry.coefficients['w'].shape[0]==p.nx+4
    # The cubic coefficient determines finite J, with no imposed target J.
    u[:p.n]=0.  # Flat lapse for the analytic far-field flux normalization.
    expected=4*p.length**3*.02
    assert surface_flux(p,u,[1e10])[0]==pytest.approx(expected,rel=2e-9)


def test_common_point_samples_read_factored_archives(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.ergoregion_scan import common_metric_samples
    p=problem();path=tmp_path/'state.npz';save_state(path,p,state(p))
    result=common_metric_samples(path)
    assert np.isfinite(result['gtt_max'])


def test_plan_preserves_the_accepted_ring_and_all_limits():
    from grteclyn_wrapper.optimisation.railgun.smooth_cubic_recovery import plan
    record=plan();cfg=record['config']
    assert cfg['grids']==[[224,28],[256,32],[288,36]]
    assert record['all_interior_rows_retained'] and record['independent_cartesian_flux']
    assert cfg['newton_tol']==1e-14 and cfg['core']['tolerance']==1e-8
