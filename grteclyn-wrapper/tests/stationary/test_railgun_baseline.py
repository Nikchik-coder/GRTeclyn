"""Safeguards against the tracked accepted spherical fixture; no new PDE solve."""
from pathlib import Path
import numpy as np
import pytest

ARCHIVE=Path(__file__).resolve().parents[3]/'results/railgun/studies/spherical-validated/accepted.npz'
pytestmark=pytest.mark.skipif(not ARCHIVE.exists(),reason='spherical validation archive not present')


def test_saved_spherical_intrinsic_kg_and_regular_cartesian_core():
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.corridor import CartesianCorridor
    p,u,metadata=load_state(ARCHIVE)
    assert metadata['validated']
    original=RingGeometry(p,u)
    row=original.independent([0.,.1,0.,.2])
    assert row['kg_intrinsic_max'] < 1e-8
    assert row['kg_coordinate_difference'] < 1e-8
    core=CartesianCorridor(original)
    certificate=core.certify()
    assert certificate['accepted'],certificate['maxima']
    assert np.isfinite(core.tensors(np.zeros(4))[2]).all()


def test_saved_spherical_metric_supplies_a_bound_integer_winding_mode():
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.model import ScalarField
    from grteclyn_stationary.railgun.continuation import transfer_fields,linear_bound_seed
    source,u,_=load_state(ARCHIVE)
    pair=RingProblem([source.fields[0],ScalarField(winding=1,amplitude=.001)],nx=56,ny=8,length=source.length)
    seed,record=linear_bound_seed(pair,transfer_fields(pair,source,u))
    assert record['radial_nodes']==0
    assert record['relative_linear_residual'] < 1e-8
    assert 0 < record['frequency'] < 1.
    assert np.isfinite(seed).all()


def test_partial_ring_exact_flux_resolves_the_truncated_asymptotic_fit():
    import json
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.diagnostics import validate
    directory=ARCHIVE.parent.parent/'spherical-to-ring-first'
    if not directory.exists():pytest.skip('first ring pilot archive not present')
    old=json.loads((directory/'attempt_005.json').read_text())
    p,u,_=load_state(directory/'attempt_005.npz')
    assert old['reasons']==['angular_momentum_balance']
    assert abs(old['J_volume']-old['J_asymptotic_estimate'])>1e-8
    measured=validate(p,u,old['newton'],independent=False)
    assert measured['verdict']=='PASS',measured['reasons']
    assert measured['angular_momentum_surface_error']<1e-8


def test_saved_spherical_flux_preserves_the_accepted_baseline():
    import json
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.diagnostics import validate
    p,u,_=load_state(ARCHIVE)
    old=json.loads((ARCHIVE.parent/'grid_96x12.json').read_text())
    row=validate(p,u,old['newton'],independent=False)
    assert row['verdict']=='PASS',row['reasons']


def test_mass_correction_keeps_the_unresolved_ring_rejected():
    import json
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.diagnostics import validate
    directory=ARCHIVE.parent.parent/'spherical-to-ring-resumed'
    if not directory.exists():pytest.skip('resumed ring archive not present')
    old=json.loads((directory/'attempt_017.json').read_text())
    assert old['M_fit_drift']>1e-6
    p,u,_=load_state(directory/'attempt_017.npz')
    row=validate(p,u,old['newton'])
    assert abs(row['M_ADM_estimate']-row['M_Komar_volume'])<1e-6
    assert 'mass_balance' not in row['reasons']
    assert 'mass_lapse_balance' not in row['reasons']
    assert row['verdict']=='REJECT'
    assert 'independent_equations' in row['reasons']
    assert 'intrinsic_kg_crosscheck' in row['reasons']
    assert 'angular_momentum_balance' in row['reasons']
