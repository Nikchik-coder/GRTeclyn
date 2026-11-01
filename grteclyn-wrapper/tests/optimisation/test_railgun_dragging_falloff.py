"""Factored boundary checks against manufactured fields and metric-ratio AD."""
import json
from pathlib import Path
import numpy as np
import pytest


def test_cubic_polynomial_projection_preserves_a_factored_field_and_zero_columns():
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import project_coefficients
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
    s,_=lobatto(24);h=.2+.1*s+.05*s*s
    values=(1-s[:,None])**3*h[:,None]*np.array([[1.,0.,2.,.3]])
    coeff=project_coefficients(values)
    reconstructed=(1-s[:,None])**3*(np.polynomial.chebyshev.chebvander(s,21)@coeff)
    np.testing.assert_allclose(reconstructed,values,atol=5e-10,rtol=1e-10)
    assert np.array_equal(coeff[:,1],np.zeros(22))


def test_factored_flux_and_cartesian_ad_agree_with_an_analytic_finite_sphere(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import (
        FactoredDraggingProblem,surface_flux,cartesian_surface_flux,save_state,load_state)
    p=FactoredDraggingProblem(nx=16,ny=4,length=3.)
    u=np.zeros(p.n_unknowns);c=2e-5
    raw=u[p.n:2*p.n].reshape(p.shape);raw[0]=c
    radii=np.array([30.,300.,3000.,1e8])
    expected=4*c*p.length**3*(radii/(radii+p.length))**4
    np.testing.assert_allclose(surface_flux(p,u,radii),expected,atol=1e-13,rtol=1e-11)
    np.testing.assert_allclose(cartesian_surface_flux(p,u,radii),expected,atol=1e-13,rtol=1e-10)
    jets=p.dragging_jets(u)
    for key in ('w','w_x','w_xx'):np.testing.assert_array_equal(jets[key][0],0.)
    path=tmp_path/'state.npz';save_state(path,p,u)
    restored,value,metadata=load_state(path)
    np.testing.assert_array_equal(value,u)
    assert metadata['validated'] is False
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state as canonical_load
    with pytest.raises(ValueError,match='schema/model'):canonical_load(path)


def test_tau_rows_do_not_hide_the_two_unimposed_outer_pdes():
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import FactoredDraggingProblem
    p=FactoredDraggingProblem(nx=10,ny=4,length=3.)
    u=np.zeros(p.n_unknowns);raw=u[p.n:2*p.n].reshape(p.shape);raw[0]=1e-4
    residual=np.asarray(p.residual(u))[p.n:2*p.n].reshape(p.shape)
    np.testing.assert_array_equal(residual[:3],0.)
    assert np.max(abs(p.rows(u)['E_w'][:2]))>0
    np.testing.assert_allclose(residual[3:-1],p.rows(u)['E_w'][2:],rtol=1e-12,atol=1e-15)
    raw[-3:]=[[.01],[.02],[.03]]
    np.testing.assert_allclose(np.asarray(p.residual(u))[p.n:2*p.n].reshape(p.shape)[:3],raw[-3:])


def test_falloff_recovery_budget_requires_the_saved_flux_rejection():
    from grteclyn_wrapper.optimisation.railgun.falloff_recovery import preflight
    root=Path(__file__).resolve().parents[3]
    config=json.loads((root/'research/railgun/studies/annular_falloff_k12.json').read_text())
    source=root/'results/railgun/studies/annular-correction-k12/grid_256x20.npz'
    assert preflight(source,config)['max_solves']==3
    for key,value in [('max_solves',4),('equation_tol',1e-7),('perturbation',1e-5)]:
        changed=dict(config,**{key:value})
        with pytest.raises(ValueError):preflight(source,changed)


def test_quintic_projection_is_a_stable_fit_of_physical_values():
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import project_coefficients
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
    s,_=lobatto(32);values=(1-s[:,None])**5*(.2+.1*s[:,None])*np.array([[1.,0.,2.]])
    c=project_coefficients(values,power=5)
    restored=(1-s[:,None])**5*(np.polynomial.chebyshev.chebvander(s,27)@c)
    np.testing.assert_allclose(restored,values,atol=1e-10,rtol=1e-10)
    np.testing.assert_array_equal(c[:,1],0.)


def test_quintic_zero_j_flux_and_omitted_rows_are_explicit():
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import FactoredDraggingProblem,surface_flux,cartesian_surface_flux
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    p=FactoredDraggingProblem([ScalarField(),ScalarField(winding=-1)],nx=12,ny=4,length=3.,target_j=0.,power=5)
    u=np.zeros(p.n_unknowns);raw=u[p.n:2*p.n].reshape(p.shape);c=2e-5;raw[0]=c
    radii=np.array([30.,300.,3000.]);expected=5/6*c*(2*p.length)**5*radii**4/(radii+p.length)**6
    np.testing.assert_allclose(surface_flux(p,u,radii),expected,rtol=1e-10,atol=1e-13)
    np.testing.assert_allclose(cartesian_surface_flux(p,u,radii),expected,rtol=1e-10,atol=1e-13)
    for name in ('w','w_x','w_xx'):np.testing.assert_array_equal(p.dragging_jets(u)[name][0],0.)
    residual=np.asarray(p.residual(u))[p.n:2*p.n].reshape(p.shape)
    np.testing.assert_array_equal(residual[:5],0.)
    np.testing.assert_allclose(residual[5:-1],p.rows(u)['E_w'][4:],rtol=1e-12,atol=1e-15)
    assert np.max(abs(p.rows(u)['E_w'][:4]))>0
    with pytest.raises(ValueError):FactoredDraggingProblem(nx=12,ny=4,power=5)
