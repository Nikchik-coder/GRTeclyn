"""Pinned CMA source, true throat sampling and bounded one-case workflow."""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from grteclyn_wrapper.optimisation import railgun_wormhole as module

ROOT=Path(__file__).resolve().parents[3]


def plan():
    return json.loads((ROOT/'grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108.json').read_text())


@pytest.mark.parametrize('change',[
    dict(max_solves=4),dict(max_control_steps=1),dict(throat_radius=1.),
    dict(source_grid=[128,16]),dict(energy_budget=2.),dict(tidal_factor=5.),
    dict(independent_points=[17,9]),dict(checkpoints=True),dict(wall_seconds=7200),
    dict(restart_source='different-source.npz'),
])
def test_new_stage_refuses_undeclared_scope(change):
    p=plan();module.validate_plan(p);p.update(change)
    with pytest.raises(ValueError):module.validate_plan(p)


def test_archived_cma_source_and_unsolved_throat_ergoregion():
    p=plan();meta,arrays,frequency,row=module.read_source(p)
    assert [meta['nx'],meta['ny']]==[192,24]
    assert row['verdict']=='PASS' and frequency==pytest.approx(.655065086594,rel=1e-11)
    s,c=module.prepare_seed(p)
    assert c['rotation_control']=='nonrotating_ends' and s['omega']==0.
    assert c['amplitude']==pytest.approx(.2846529189064392)
    assert s['sigma']==pytest.approx(.8667449203162112)
    diagnostic=module.throat_ergoregion(s)
    assert diagnostic['throat_gtt_max']==pytest.approx(.0086997582871964)
    assert diagnostic['throat_shift_over_lapse_max']==pytest.approx(1.041815869038765)
    # This is an unsolved seed, not an inherited wormhole acceptance.
    assert diagnostic['throat_samples']==129
    p['source_sha256']['grid_192x24.npz']='0'*64
    with pytest.raises(ValueError,match='hash mismatch'):module.read_source(p)


def test_diagnostic_follows_the_deformed_surface_and_has_no_axis_ergoregion():
    s=module.ellis(2.,8,4)
    s['surface_coefficients'][:2]=[.2,.1]
    s['W']=1.1+.2*s['sx'][:,None]+.1*s['sy'][None,:]
    mu=np.linspace(0,1,129);y=2*mu**2-1;x=.2+.1*y
    ratio=(1.1+.2*x+.1*y)*np.sqrt(1+s['map'].eta(x)**2)*np.sqrt(1-mu**2)
    gtt=ratio**2-1
    result=module.throat_ergoregion(s)
    assert result['throat_gtt_max']==pytest.approx(max(gtt),rel=1e-13)
    assert result['throat_gtt_mu']==mu[np.argmax(gtt)]
    assert result['throat_equatorial_gtt']==pytest.approx(gtt[0],rel=1e-13)
    assert gtt[-1]==-1
    s['W']*=0
    assert not module.throat_ergoregion(s)['throat_ergoregion_sampled']


@pytest.mark.parametrize('gtts,ratios,verdict,expected',[
    ([.01,.010000002,.010000003],[1.04]*3,'PASS',True),
    ([.01,.010000002,.010000003],[1.04]*3,'ABOVE_GATE',False),
    ([0.,0.,0.],[1.]*3,'PASS',False),
    ([.01,.03,.02],[1.04]*3,'PASS',False),
    ([.01,np.nan,.01],[1.04]*3,'PASS',False),
])
def test_throat_sign_needs_three_qualified_resolved_grids(gtts,ratios,verdict,expected):
    rows=[dict(verdict=verdict,throat_gtt_max=g,throat_shift_over_lapse_max=r)
          for g,r in zip(gtts,ratios)]
    assert module.throat_ergoregion_convergence(rows)['throat_ergoregion_resolved']==expected
    assert not module.throat_ergoregion_convergence(rows[:2])['throat_ergoregion_resolved']


@pytest.mark.parametrize('accepted,ergoregion',[(True,True),(True,False),(False,True)])
def test_single_case_never_dispatches_control_or_promotes_an_unqualified_throat(monkeypatch,tmp_path,accepted,ergoregion):
    from grteclyn_wrapper.optimisation import exploration,resolution,study_validation,study_diagnostics
    p=plan();s=module.ellis(2.,6,3)
    s['Z']=.1*(1-s['sx'][:,None]**2)*np.ones((1,4));s['frequency']=.8
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=-.2,matter='winding',matter_mass=1.,winding_k=1,
           amplitude=.1,rotation_control='nonrotating_ends')
    monkeypatch.setattr(module,'prepare_seed',lambda p:(s,c))
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    monkeypatch.setattr(study_validation,'validate',lambda s,c,r,**kw:dict(r,X_full=np.pi))
    calls=[]
    def check(*args,**kwargs):
        calls.append(args[2]);row=dict(verdict='PASS' if accepted else 'ABOVE_GATE',X_full=3.,
            E_b=1.,Q_b=.4,J_measured=-.2,ring_peak_radius=6.,equatorial_shift_over_lapse_max=1.05,
            throat_gtt_max=.01 if ergoregion else -.01,throat_shift_over_lapse_max=1.05 if ergoregion else .95)
        return dict(passed=accepted,method='refine',records=[row.copy() for _ in range(3)]),s
    monkeypatch.setattr(resolution,'check_candidate',check)
    monkeypatch.setattr(exploration,'solve_trial',lambda *a,**k:pytest.fail('extra control solve dispatched'))
    out=tmp_path/'out';status=module.run(p,out)
    result=json.loads((out/'outcome.json').read_text())
    assert len(calls)==1 and result['solves']==3
    assert result['ring_accepted']==accepted
    assert result['throat_ergoregion_resolved']==(accepted and ergoregion)
    assert (status==0)==(accepted and ergoregion)
    assert (out/'accepted_ring.npz').exists()==accepted
    assert 'matched_spin_fractional_reduction' not in result


def test_preview_initializes_no_jax_and_writes_nothing(tmp_path):
    out=tmp_path/'out'
    code="from grteclyn_wrapper.optimisation import railgun_wormhole as m; m.main(); import sys; assert 'jax' not in sys.modules"
    result=subprocess.run([sys.executable,'-c',code,'--config','grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108.json',
        '--out',str(out)],cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'PREPARED_ONLY' in result.stdout
    result=subprocess.run(['bash','grteclyn-wrapper/scripts/campaigns/ringwormhole/run_ergoregion108.sh','99999',str(out)],
        cwd=ROOT,capture_output=True,text=True,check=True)
    assert '--mem 160 --timeout 3600' in result.stdout
    assert not out.exists()
