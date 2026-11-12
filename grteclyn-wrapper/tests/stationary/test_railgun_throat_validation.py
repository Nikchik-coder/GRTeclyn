"""The refinement stage preserves the model and cannot dispatch a control."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from grteclyn_stationary.ringwormhole import workflow as module

ROOT=Path(__file__).resolve().parents[3]


def plan():
    return json.loads((ROOT/'grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat_validation.json').read_text())


@pytest.mark.parametrize('change',[
    dict(max_solves=4),dict(max_control_steps=1),dict(stage='ring_and_control'),
    dict(grids=[[210,36],[224,38],[242,40]]),dict(independent_points=[17,9]),
    dict(checkpoints=True),dict(wall_seconds=7200),dict(restart_sha256=''),
])
def test_validation_budget_cannot_expand(change):
    p=plan(); module.validate_plan(p)
    p.update(change)
    with pytest.raises(ValueError): module.validate_plan(p)


def saved_seed(tmp_path):
    from grteclyn_stationary.workflows.common import save_trial
    s=module.ellis(2.,8,4)
    s['Z']=.1*(1-s['sx'][:,None]**2)*np.ones((1,5));s['frequency']=.8
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=-.2,matter='winding',matter_mass=1.,winding_k=1,
           amplitude=.08,zeta_anchor_xi=.4,rotation_control='nonrotating_ends')
    path=tmp_path/'seed.npz'
    save_trial(path,s,c,dict(verdict='ABOVE_GATE'),('minimal_area',16*np.pi))
    p=plan();p.update(restart_source=str(path),restart_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return p,s,c


def test_restart_is_hashed_and_preserves_the_original_border(tmp_path):
    p,s,c=saved_seed(tmp_path)
    loaded,config=module.prepare_seed(p)
    assert config==c
    np.testing.assert_array_equal(loaded['Z'],s['Z'])
    p['restart_sha256']='0'*64
    with pytest.raises(ValueError,match='restart hash'): module.prepare_seed(p)


@pytest.mark.parametrize('passed',[False,True])
def test_validation_stops_after_three_solves_and_does_not_inherit_verdict(monkeypatch,tmp_path,passed):
    from grteclyn_stationary.workflows import common as exploration; from grteclyn_stationary.validation import resolution; from grteclyn_stationary.studies import validation as study_validation; from grteclyn_stationary.studies import diagnostics as study_diagnostics
    p,s,c=saved_seed(tmp_path)
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    calls=[]
    def validate(s,c,row,**kwargs):
        assert kwargs['independent_points']==[49,21]
        return dict(row,X_full=np.pi)
    monkeypatch.setattr(study_validation,'validate',validate)
    def check(s,c,grids,*args,**kw):
        calls.append(grids)
        assert kw['perturb_seed'] is True
        row=dict(verdict='PASS' if passed else 'ABOVE_GATE',X_full=3.1,E_b=1.,Q_b=.4,
                 J_measured=-.2,ring_peak_radius=6.,equatorial_shift_over_lapse_max=.01)
        return dict(passed=passed,method='refine',records=[row]*3),s
    monkeypatch.setattr(resolution,'check_candidate',check)
    def forbidden(*a,**kw):
        pytest.fail('validation stage dispatched a matched-spin control')
    monkeypatch.setattr(exploration,'solve_trial',forbidden)
    out=tmp_path/'out'; status=module.run(p,out)
    result=json.loads((out/'outcome.json').read_text())
    assert (status==0)==passed and result['ring_accepted']==passed
    assert result['solves']==3 and len(calls)==1
    assert (out/'accepted_ring.npz').exists()==passed
    assert 'matched_spin_fractional_reduction' not in result
    if passed: assert result['matched_control_status']=='not_run'


def test_validation_preview_starts_no_jax_and_writes_nothing(tmp_path):
    out=tmp_path/'out'
    script="from grteclyn_stationary.ringwormhole import workflow as m; m.main(); import sys; assert 'jax' not in sys.modules"
    cmd=[sys.executable,'-c',script,'--config','grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat_validation.json','--out',str(out)]
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'PREPARED_ONLY' in result.stdout
    result=subprocess.run(['bash','grteclyn-wrapper/scripts/campaigns/optimisation/run_railgun_throat_validation.sh','99999',str(out)],
                          cwd=ROOT,capture_output=True,text=True,check=True)
    assert '--mem 160 --timeout 3600' in result.stdout
    assert not out.exists()


def test_dense_equation_sampler_reaches_validator(monkeypatch):
    from grteclyn_stationary.studies import validation as v
    s=module.ellis(2.,8,4); calls=[]
    monkeypatch.setattr(v,'volume_budgets',lambda *a,**kw:dict(X_full=3.,E_b=0.,B_min=1.,lapse_min=1.,R_A=2.))
    monkeypatch.setattr(v,'verify_surface',lambda *a,**kw:dict(surface_verified=True))
    def check(*a,**kw):
        calls.append(kw)
        return dict(offgrid_pass=False,offgrid_einstein=2e-8,offgrid_scalar=0.)
    monkeypatch.setattr(v,'independent_equations',check)
    row=v.validate(s,{},dict(verdict='PASS'),reference_peak=None,tidal_factor=4.,independent_points=[49,21])
    assert calls==[dict(radial_points=49,angular_points=21)]
    assert row['verdict']=='ABOVE_GATE' and 'offgrid_equations' in row['rejection_reasons']
    with pytest.raises(ValueError):
        v.validate(s,{},dict(verdict='PASS'),reference_peak=None,tidal_factor=4.,independent_points=[9,5])
