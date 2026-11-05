"""Reference identity, fixed spin ladder and fail-closed control comparison."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from grteclyn_wrapper.optimisation import railgun_control as module

ROOT=Path(__file__).resolve().parents[3]


def plan():
    return json.loads((ROOT/'research/optimisation/studies/railgun_matched_control.json').read_text())


@pytest.mark.parametrize('change',[
    dict(max_solves=14),dict(max_control_steps=11),dict(control_J_step=.2),
    dict(max_newton_iterations=25),dict(wall_seconds=7200),dict(checkpoints=True),
    dict(independent_points=[17,9]),dict(throat_radius=3.),dict(target_J=1.1),
    dict(grids=[[150,24],[180,30],[210,36]]),dict(tidal_factor=5.),
])
def test_plan_refuses_changed_scope(change):
    p=plan();module.validate_plan(p)
    p.update(change)
    with pytest.raises(ValueError):module.validate_plan(p)


def references(tmp_path):
    from grteclyn_wrapper.optimisation.railgun_wormhole import ellis
    from grteclyn_wrapper.optimisation.exploration import save_trial
    from grteclyn_wrapper.optimisation.resolution import save_checked
    p=plan();pin=('minimal_area',16*np.pi)
    base=ellis(2.,210,36)
    cfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    save_trial(tmp_path/'static.npz',base,cfg,
               dict(verdict='PASS',offgrid_pass=True,tidal_peak=1/12,X_full=np.pi),pin)
    ring=ellis(2.,240,40)
    ring['Z']=.1*(1-ring['sx'][:,None]**2)*np.ones((1,41));ring['frequency']=.9
    cfg.update(matter='winding',matter_mass=1.,winding_k=1,
               rotation_control='nonrotating_ends',J=p['target_J'])
    records=[dict(nx=nx,ny=ny,verdict='PASS',X_full=3.1,J_measured=p['target_J'],
                  offgrid_pass=True,offgrid_sampling=[49,21],newton_updates=1)
             for nx,ny in p['grids']]
    result=dict(passed=True,method='refine',records=records)
    save_checked(tmp_path/'ring.npz',ring,cfg,dict(pin=list(pin)),result)
    for name in ('ring','static'):
        path=tmp_path/f'{name}.npz'
        p['references'][name]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return p


def test_references_are_hashed_and_target_is_the_measured_ring_spin(tmp_path):
    p=references(tmp_path)
    baseline,ring,static=module.read_references(p)
    assert 'Z' not in baseline and ring['J']==p['target_J']
    assert ring['X_full']==3.1 and static['X_full']==np.pi
    p['target_J']=-.2
    with pytest.raises(ValueError,match='qualified fixed-area'):module.read_references(p)
    p['references']['ring']['sha256']='0'*64
    with pytest.raises(ValueError,match='hash mismatch'):module.read_references(p)


@pytest.mark.parametrize('failure,value',[(None,3.12),(None,3.),('step',3.12),('grid',3.12)])
def test_control_never_changes_ring_or_reports_unqualified_gain(monkeypatch,tmp_path,failure,value):
    from grteclyn_wrapper.optimisation import exploration,resolution,study
    p=references(tmp_path);calls=[];checks=[]
    original=Path(p['references']['ring']['path']).read_bytes()
    def solve(state,config,nx,ny,pin,d2,**kw):
        assert 'matter' not in config and 'Z' not in state
        assert config['rotation_control']=='J' and pin==('minimal_area',16*np.pi)
        assert [nx,ny]==p['grids'][0] and d2==4.
        assert kw==dict(max_iter=24,newton_tol=1e-14)
        calls.append(config['J'])
        return state,dict(verdict='ABOVE_GATE' if failure=='step' else 'PASS')
    def check(state,config,grids,pin,d2,out,**kw):
        checks.append(config.copy())
        assert grids==p['grids'] and config['J']==p['target_J']
        assert kw['perturb_seed'] and kw['score_key']=='X_full'
        records=[dict(nx=nx,ny=ny,verdict='PASS',X_full=value,J_measured=config['J'])
                 for nx,ny in grids]
        return dict(passed=failure!='grid',method='refine',records=records),state
    monkeypatch.setattr(exploration,'solve_trial',solve)
    monkeypatch.setattr(resolution,'check_candidate',check)
    monkeypatch.setattr(study,'release_solver',lambda:None)
    status=module.run(p,tmp_path/'out')
    outcome=json.loads((tmp_path/'out/outcome.json').read_text())
    assert Path(p['references']['ring']['path']).read_bytes()==original
    assert outcome['solves']<=13
    if failure:
        assert status==2 and not outcome['matched_control_accepted']
        assert 'matched_spin_fractional_reduction' not in outcome
        assert not (tmp_path/'out/matched_spin.npz').exists()
        if failure=='step':assert len(calls)==1 and checks==[]
    else:
        np.testing.assert_allclose(calls,np.linspace(0,p['target_J'],11)[1:])
        assert len(checks)==1 and outcome['solves']==13
        assert status==0 and outcome['matched_control_accepted']
        assert outcome['matched_spin_fractional_reduction']==pytest.approx(1-3.1/value)
        assert (tmp_path/'out/matched_spin.npz').exists()


def test_preview_has_no_gpu_startup_and_no_output(tmp_path):
    out=tmp_path/'out'
    script="from grteclyn_wrapper.optimisation import railgun_control as m; m.main(); import sys; assert 'jax' not in sys.modules"
    result=subprocess.run([sys.executable,'-c',script,'--config',
        'research/optimisation/studies/railgun_matched_control.json','--out',str(out)],
        cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'PREPARED_ONLY' in result.stdout
    result=subprocess.run(['bash','research/optimisation/studies/run_railgun_matched_control.sh',
        '99999',str(out)],cwd=ROOT,capture_output=True,text=True,check=True)
    assert '--mem 160 --timeout 3600' in result.stdout
    assert 'XLA_PYTHON_CLIENT_ALLOCATOR=platform' in result.stdout
    assert not out.exists()
