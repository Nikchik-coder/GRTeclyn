"""Independent rotation, fixed solve scope and honest paired comparisons."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
from grteclyn_wrapper.optimisation import ringwormhole_spin_ring as m

ROOT=Path(__file__).resolve().parents[3]
CONFIG=ROOT/'grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/spin_ring_co_rotating.json'
def plan():return json.loads(CONFIG.read_text())


@pytest.mark.parametrize('change',[dict(max_solves=15),dict(checkpoints=True),dict(added_total_J=-.2),
    dict(energy_budget=2.),dict(tidal_factor=5.),dict(grids=[[64,8],[80,10],[96,12]]),
    dict(max_newton_iterations=48),dict(wall_seconds=7200)])
def test_scope_is_bounded(change):
    p=plan();m.validate_plan(p);p.update(change)
    with pytest.raises(ValueError):m.validate_plan(p)


def test_ladders_end_exactly_and_respect_step_size():
    a=m.j_ladder(-.7163901140129952,-.7963901140129952,.02)
    b=m.j_ladder(-.9477747390613108,-.7963901140129952,.05)
    assert len(a)==len(b)==4 and a[-1]==b[-1]
    assert max(abs(np.diff([-.7163901140129952]+a)))<=.02+1e-15
    assert max(abs(np.diff([-.9477747390613108]+b)))<=.05+1e-15


def test_ring_dragging_alone_is_not_independent_wormhole_rotation():
    r=dict(J_measured=-.7,J_matter_positive_half=-.7)
    d=m.rotation_diagnostics(dict(omega=0.,sigma=2.),r)
    assert not d['independent_rotation_present']
    r['J_measured']=-1.
    d=m.rotation_diagnostics(dict(omega=.2,sigma=2.),r)
    assert d['independent_rotation_present'] and d['geometric_and_matter_flux_aligned']
    r['J_measured']=-.5
    assert not m.rotation_diagnostics(dict(omega=-.2,sigma=2.),r)['geometric_and_matter_flux_aligned']


def seeded_plan(tmp_path):
    from grteclyn_wrapper.optimisation.exploration import save_trial
    p=plan();seeds=[]
    for key,j in [('ring_seed',-.7163901140129952),('control_seed',-.9477747390613108)]:
        s=m.bridge.ellis(2.,6,3)
        c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=j,rotation_control='nonrotating_ends' if key=='ring_seed' else 'J')
        if key=='ring_seed':
            s.update(Z=.3*(1-s['sx'][:,None]**2)*np.ones((1,4)),frequency=.8)
            c.update(matter='winding',matter_mass=1.,winding_k=1,amplitude=.2,zeta_anchor_xi=.4)
        path=tmp_path/(key+'.npz');save_trial(path,s,c,{},('minimal_area',16*np.pi))
        with np.load(path,allow_pickle=False) as z:arrays={k:np.array(z[k]) for k in z}
        meta=json.loads(str(arrays['meta']));meta['resolution_validated']=True
        arrays['meta']=json.dumps(meta);np.savez_compressed(path,**arrays)
        p[key]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        seeds.append((s,c))
    return p,seeds


def test_preview_reads_pinned_fields_without_jax_or_writes(tmp_path):
    p,_=seeded_plan(tmp_path);config=tmp_path/'plan.json';config.write_text(json.dumps(p))
    out=tmp_path/'out'
    code="import sys; from grteclyn_wrapper.optimisation import ringwormhole_spin_ring as m; m.main(); assert 'jax' not in sys.modules"
    done=subprocess.run([sys.executable,'-c',code,'--config',str(config),'--out',str(out)],
                        capture_output=True,text=True,check=True)
    preview=json.loads(done.stdout);assert preview['planned_solves']==14
    assert not out.exists()
    p['ring_seed']['sha256']='0'*64
    with pytest.raises(ValueError,match='hash mismatch'):m.read_seeds(p)


@pytest.mark.parametrize('ring_ok,control_ok,j_mismatch',[(True,True,False),(False,True,False),
    (True,False,False),(True,True,True)])
def test_comparison_requires_both_qualified_arms_and_matching_J(tmp_path,monkeypatch,ring_ok,control_ok,j_mismatch):
    from grteclyn_wrapper.optimisation import resolution,study_validation,study_diagnostics,study
    p,seeds=seeded_plan(tmp_path);target=-.7963901140129952
    monkeypatch.setattr(m,'read_seeds',lambda p:(seeds,target,[[target]*4,[target]*4]))
    monkeypatch.setattr(m,'continue_j',lambda s,c,t,p,d:(s,dict(c,J=target),[{}]*4,True))
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    monkeypatch.setattr(study_validation,'validate',lambda s,c,r,**kw:dict(verdict='PASS',X_full=np.pi))
    calls=[]
    def check(s,c,grids,*a,**kw):
        ring=bool(c.get('matter'));calls.append(ring)
        r=dict(X_full=2.5 if ring else 2.,J_measured=target+(1e-3 if j_mismatch and not ring else 0.),
               E_b=1.,Q_b=1.,ring_peak_radius=2.,equatorial_shift_over_lapse_max=.8,
               J_geometric_flux_xi0=-.1,relative_end_angular_velocity=.1)
        return dict(passed=ring_ok if ring else control_ok,records=[r.copy() for _ in grids]),s
    monkeypatch.setattr(resolution,'check_candidate',check)
    monkeypatch.setattr(resolution,'save_checked',lambda *a,**kw:None)
    out=tmp_path/'out';status=m.run(p,out);o=json.loads((out/'outcome.json').read_text())
    passed=ring_ok and control_ok and not j_mismatch
    assert (status==0)==passed
    assert ('matched_spin_fractional_reduction' in o)==passed
    if passed:assert o['matched_spin_fractional_reduction']==pytest.approx(-.25)
    assert o['solves']<=14 and len(calls)==(2 if ring_ok else 1)
