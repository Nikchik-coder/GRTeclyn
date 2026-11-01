"""Frequency control replaces the pin and must not accept the vacuum branch."""
from pathlib import Path
from types import SimpleNamespace
import json
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]


def test_vacuum_and_nodal_branch_guards_fail_closed():
    from grteclyn_wrapper.optimisation.railgun.workflow import branch_checks
    problem=SimpleNamespace(fields=[object()],unpack=lambda u:({'q0':np.ones((3,3))},[.85]))
    cfg=dict(minimum_charges=[.001],require_nodeless=True)
    assert branch_checks(dict(reasons=[],charges=[0.]),problem,[],cfg)['verdict']=='REJECT'
    assert branch_checks(dict(reasons=[],charges=[1.]),problem,[],cfg)['verdict']=='PASS'
    problem.unpack=lambda u:({'q0':np.array([[-1.,1.]])},[.85])
    assert branch_checks(dict(reasons=[],charges=[1.]),problem,[],cfg)['verdict']=='REJECT'
    cfg['minimum_charges']=[np.nan]
    assert branch_checks(dict(reasons=[],charges=[1.]),problem,[],cfg)['verdict']=='REJECT'


def test_frequency_dry_plan_is_bounded_and_uses_an_accepted_source():
    from grteclyn_wrapper.optimisation.railgun.frequency_scan import preflight
    source=ROOT/'results/railgun/studies/compactness-scan/amplitude_03/accepted.npz'
    config=json.loads((ROOT/'research/railgun/studies/frequency_scan.json').read_text())
    assert preflight(source,config)['max_solves']==21
    config['frequencies'].append(.64)
    with pytest.raises(ValueError):preflight(source,config)


def test_refined_tail_budget_rejects_more_points_or_a_coarser_source():
    from grteclyn_wrapper.optimisation.railgun.frequency_scan import preflight
    source=ROOT/'results/railgun/studies/frequency-073-refined/accepted.npz'
    config=json.loads((ROOT/'research/railgun/studies/frequency_deep.json').read_text())
    assert preflight(source,config)['max_solves']==6
    assert preflight(source,config)['frequencies']==[.70,.67]
    with pytest.raises(ValueError):preflight(ROOT/'results/railgun/studies/compactness-scan/amplitude_03/accepted.npz',config)
    config['frequencies'].append(.64)
    with pytest.raises(ValueError):preflight(source,config)


def test_frequency_border_and_portable_state_preserve_measured_pin(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    from grteclyn_wrapper.optimisation.railgun.workflow import save_state,load_state
    p=RingProblem([ScalarField()],nx=12,ny=4,frequency_targets=[.85])
    arrays,_=p.unpack(p.seed());arrays['q0']*=1.4
    value=p.pack(arrays,[.85])
    assert float(np.asarray(p.residual(value))[-1])==0.
    assert abs(float(p.anchors[0]@arrays['q0'][:,-1])-p.fields[0].amplitude)>1e-3
    path=tmp_path/'state.npz';save_state(path,p,value)
    recovered,u,meta=load_state(path)
    assert recovered.frequency_targets==(.85,)
    assert meta['measured_amplitude_pins'][0]==pytest.approx(float(p.anchors[0]@arrays['q0'][:,-1]))
    np.testing.assert_array_equal(u,value)
    with pytest.raises(ValueError):RingProblem([ScalarField()],frequency_targets=[1.1])


def test_fixed_frequency_recovers_the_same_saved_rotating_star():
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state,branch_checks
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.diagnostics import validate
    from grteclyn_wrapper.optimisation.solver.newton import newton
    source=ROOT/'results/railgun/studies/compactness-scan/amplitude_03/accepted.npz'
    old,value,_=load_state(source);frequency=float(value[-1])
    p=RingProblem(old.fields,nx=72,ny=10,length=old.length,frequency_targets=[frequency])
    initial=p.transfer(old,value,perturb=1e-5)
    u,info=newton(p.residual,p.jacobian,initial,max_iter=30,min_updates=2)
    row=validate(p,u,info)
    branch_checks(row,p,u,dict(minimum_charges=[.001],require_nodeless=True))
    assert row['verdict']=='PASS',row['reasons']
    assert float(u[-1])==pytest.approx(frequency,abs=1e-12)
    assert row['J_volume']==pytest.approx(-1.2418771253603433,rel=1e-6)
