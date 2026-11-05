"""Continuation rollback, budgets, target clamping and rejected iterates."""
import json
from pathlib import Path
import numpy as np
import pytest
from grteclyn_wrapper.optimisation import ringwormhole_continuation as m

ROOT=Path(__file__).resolve().parents[3]
def plan():return json.loads((ROOT/'grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108_continuation.json').read_text())

@pytest.mark.parametrize('key,value',[('max_attempts',33),('min_damping',0.),('amplitude_growth',2.),('restart_sha256','short')])
def test_budget_is_closed(key,value):
    p=plan();m.validate_plan(p);p[key]=value
    with pytest.raises(ValueError):m.validate_plan(p)


def test_failed_attempt_rolls_back_and_final_step_does_not_overshoot(tmp_path):
    p=plan();seen=[];saved=[];released=[]
    def solve(s,c,*a,**kw):
        seen.append((s,c['amplitude']))
        if len(seen)==1:raise RuntimeError('line search stalled')
        return c['amplitude'],dict(verdict='PASS')
    state,c,rows,ok=m.trace('original',dict(amplitude=.1),.14,p,tmp_path/'trace',solve,
        lambda *a:saved.append(a),lambda:released.append(1),lambda *a:{})
    assert ok and c['amplitude']==.14 and state==.14
    assert seen[0][0]==seen[1][0]=='original'
    assert seen[1][1]<seen[0][1]
    assert all(x[1]<=.14 for x in seen)
    assert len(released)==len(rows) and len(saved)==len(rows)-1
    assert not rows[0]['continuation_converged']


def test_nonpassing_collocation_is_not_used_as_next_seed(tmp_path):
    p=plan();seen=[]
    def solve(s,c,*a,**kw):
        seen.append(s);return 'rejected',dict(verdict='ABOVE_GATE')
    s,c,rows,ok=m.trace('original',dict(amplitude=.1),.2,p,tmp_path/'trace',solve,
        lambda *a:None,lambda:None,lambda *a:{})
    assert not ok and s=='original' and c['amplitude']==.1
    assert len(rows)<=32 and set(seen)=={'original'}


def test_failed_solve_retains_raw_iterate_and_history(tmp_path,monkeypatch):
    from grteclyn_wrapper.optimisation import exploration as e
    from grteclyn_wrapper.optimisation.solver import newton as n
    # Exercise the real failure path without evaluating Einstein equations.
    class P:
        sx=np.array([1.,0.,-1.]);sy=np.array([1.,-1.])
        residual=staticmethod(lambda u:u);jacobian=staticmethod(lambda u:u)
    monkeypatch.setattr(e,'make_problem',lambda *a,**k:P())
    monkeypatch.setattr(e,'pack_seed',lambda *a:np.array([1.]))
    monkeypatch.setattr(n,'newton',lambda *a,**k:(np.array([.5]),dict(res_scaled_inf=.5,
        newton_steps=[.001],res_history=[1.,.5],reason='line search stalled')))
    path=tmp_path/'failure.npz'
    with pytest.raises(RuntimeError,match='line search stalled'):
        e.solve_trial({},dict(m=0),2,1,('minimal_area',16*np.pi),4.,failure_path=path)
    with np.load(path,allow_pickle=False) as z:
        assert z['u'][0]==.5
        meta=json.loads(str(z['metadata']))
    assert meta['accepted'] is False and meta['newton']['res_history']==[1.,.5]


def test_throat_reanchor_preserves_the_seed_and_uses_cma_throat_target(tmp_path,monkeypatch):
    import hashlib
    from grteclyn_wrapper.optimisation import exploration as e
    p=plan();p.update(continuation_anchor='throat',max_attempts=8)
    s=m.bridge.ellis(2.,6,3);s['Z']=np.full_like(s['F'],.3);s['frequency']=.8
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,rotation_control='nonrotating_ends',
           matter='winding',winding_k=1,matter_mass=1.,amplitude=.1,zeta_anchor_xi=.48)
    mapped=dict(s,Z=np.full_like(s['Z'],.39))
    path=tmp_path/'restart.npz';path.write_bytes(b'pinned restart')
    p.update(restart_source=str(path),restart_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    monkeypatch.setattr(e,'load_seed',lambda path:(s,dict(config=c,pin=['minimal_area',16*np.pi])))
    monkeypatch.setattr(m.bridge,'prepare_seed',lambda p:(mapped,c.copy()))
    state,config,target=m.initial_state(p)
    assert state is s and target==pytest.approx(.39)
    assert config['zeta_anchor_xi']==0 and config['amplitude']==pytest.approx(.3)
    assert c['zeta_anchor_xi']==.48
    p['max_attempts']=32
    with pytest.raises(ValueError):m.validate_plan(p)
