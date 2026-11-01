"""Safeguards against the tracked accepted spherical fixture; no new PDE solve."""
from pathlib import Path
import numpy as np
import pytest

ARCHIVE=Path(__file__).resolve().parents[3]/'results/railgun/spherical-validated/accepted.npz'
pytestmark=pytest.mark.skipif(not ARCHIVE.exists(),reason='spherical validation archive not present')


def test_saved_spherical_intrinsic_kg_and_regular_cartesian_core():
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state
    from grteclyn_wrapper.optimisation.railgun.geometry import RingGeometry
    from grteclyn_wrapper.optimisation.railgun.corridor import CartesianCorridor
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
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    from grteclyn_wrapper.optimisation.railgun.continuation import transfer_fields,linear_bound_seed
    source,u,_=load_state(ARCHIVE)
    pair=RingProblem([source.fields[0],ScalarField(winding=1,amplitude=.001)],nx=56,ny=8,length=source.length)
    seed,record=linear_bound_seed(pair,transfer_fields(pair,source,u))
    assert record['radial_nodes']==0
    assert record['relative_linear_residual'] < 1e-8
    assert 0 < record['frequency'] < 1.
    assert np.isfinite(seed).all()
