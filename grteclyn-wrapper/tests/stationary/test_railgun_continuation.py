"""Discrete-winding transfer and the bound-mode gate before nonlinear homotopy."""
import numpy as np
import pytest
from grteclyn_stationary.railgun.model import ScalarField
from grteclyn_stationary.railgun.problem import RingProblem
from grteclyn_stationary.railgun.continuation import transfer_fields,linear_bound_seed


def test_new_winding_field_keeps_its_own_regular_origin_and_frequency():
    old=RingProblem([ScalarField(winding=0)],nx=16,ny=4)
    u=old.seed()
    arrays,_=old.unpack(u)
    assert np.max(arrays['q0'][-1]) > 0
    pair=RingProblem([old.fields[0],ScalarField(winding=1,amplitude=.001)],nx=16,ny=4)
    transferred=transfer_fields(pair,old,u)
    new,freq=pair.unpack(transferred)
    np.testing.assert_allclose(new['q0'],arrays['q0'],atol=1e-14)
    assert np.max(abs(new['q1'][-1]))==0.
    assert np.max(abs(new['q1'][1:-1])) > 0.
    assert len(freq)==2
    pure=RingProblem([pair.fields[1]],nx=16,ny=4)
    alone=transfer_fields(pure,pair,transferred)
    single,frequency=pure.unpack(alone)
    np.testing.assert_allclose(single['q0'],new['q1'],atol=1e-14)
    assert frequency[0]==freq[1]


def test_flat_space_does_not_supply_a_self_bound_massive_seed():
    p=RingProblem([ScalarField(winding=0),ScalarField(winding=1,amplitude=.001)],nx=32,ny=4)
    arrays,freq=p.unpack(p.seed())
    for tag in ('f','w','N','b'):arrays[tag]*=0.
    with pytest.raises(RuntimeError,match='no resolved nodeless bound'):
        linear_bound_seed(p,p.pack(arrays,freq))


def test_a_synthetic_binding_well_has_a_pinned_nodeless_linear_mode():
    # A manufactured external metric tests the linear eigensolver only. It is
    # not supplied as an Einstein solution or an accepted boson-star seed.
    p=RingProblem([ScalarField(winding=0),ScalarField(winding=1,amplitude=.001)],nx=48,ny=4,length=5.)
    arrays,freq=p.unpack(p.seed())
    for tag in ('w','N','b'):arrays[tag]*=0.
    arrays['f'][1:]=-.8/np.sqrt(1+(p.r[1:,None]/5)**2)
    seeded,info=linear_bound_seed(p,p.pack(arrays,freq))
    values,frequencies=p.unpack(seeded)
    assert 0 < info['frequency'] < 1.
    assert info['relative_linear_residual'] < 1e-8
    assert frequencies[1]==info['frequency']
    assert float(p.anchors[1]@values['q1'][:,-1])==pytest.approx(.001,abs=1e-14)
    np.testing.assert_array_equal(values['q1'][[0,-1]],0.)


def test_resume_preserves_spent_budgets_and_refuses_changed_experiments(tmp_path):
    import json
    from grteclyn_stationary.railgun.continuation import resume_record
    config=dict(max_solves=24,max_splits=6)
    (tmp_path/'manifest.json').write_text(json.dumps(dict(config=config,source_sha256='abc')))
    (tmp_path/'outcome.json').write_text(json.dumps(dict(accepted=False,solves=15,splits=6)))
    for attempt,progress,verdict in ((4,.375,'PASS'),(5,.5,'REJECT'),(13,.40625,'PASS')):
        (tmp_path/f'attempt_{attempt:03d}.json').write_text(json.dumps(dict(attempt=attempt,progress=progress,verdict=verdict)))
    path,progress,solves,splits=resume_record(tmp_path,config,'abc')
    assert path.name=='attempt_013.npz'
    assert (progress,solves,splits)==(.40625,15,6)
    for changed,source in ((dict(config,max_solves=25),'abc'),(config,'different')):
        with pytest.raises(ValueError,match='must match'):
            resume_record(tmp_path,changed,source)
    (tmp_path/'outcome.json').write_text(json.dumps(dict(accepted=False,solves=24,splits=6)))
    with pytest.raises(ValueError,match='remaining solve budget'):
        resume_record(tmp_path,config,'abc')


def test_refined_resume_changes_only_grids_and_preserves_budgets(tmp_path):
    import json
    from grteclyn_stationary.railgun.continuation import resume_record
    config=dict(max_solves=24,max_splits=6,grids=[[56,8],[72,10],[96,12]],initial_amplitude=.001)
    refined=dict(config,grids=[[72,10],[96,12],[128,16]])
    (tmp_path/'manifest.json').write_text(json.dumps(dict(config=config,source_sha256='abc')))
    (tmp_path/'outcome.json').write_text(json.dumps(dict(accepted=False,solves=17,splits=6)))
    (tmp_path/'attempt_016.json').write_text(json.dumps(dict(attempt=16,progress=.5,verdict='PASS')))
    with pytest.raises(ValueError,match='must match'):
        resume_record(tmp_path,refined,'abc')
    path,progress,solves,splits=resume_record(tmp_path,refined,'abc',refine=True)
    assert (path.name,progress,solves,splits)==('attempt_016.npz',.5,17,6)
    for changed in (dict(refined,max_solves=25),dict(refined,initial_amplitude=.002),
                    dict(refined,grids=[[56,8],[96,12],[128,16]])):
        with pytest.raises(ValueError,match='larger grids and identical'):
            resume_record(tmp_path,changed,'abc',refine=True)
    (tmp_path/'outcome.json').write_text(json.dumps(dict(accepted=True)))
    with pytest.raises(ValueError,match='unresolved'):
        resume_record(tmp_path,refined,'abc',refine=True)


def test_resolution_recovery_performs_fresh_Newton_updates():
    from grteclyn_stationary.railgun.continuation import recover_resolution
    old=RingProblem(nx=8,ny=4)
    p,u,info=recover_resolution(old,np.zeros(old.n_unknowns),(12,6),verbose=False)
    assert info['converged'],info
    assert len(info['newton_steps'])>=2
    assert np.max(abs(p.residual(u)))<1e-8
    with pytest.raises(ValueError,match='both grid dimensions'):
        recover_resolution(old,np.zeros(old.n_unknowns),(12,4),verbose=False)
