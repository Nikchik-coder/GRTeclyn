"""Direct geometric-flux borders and fail-fast co-alignment qualification."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from grteclyn_stationary.ringwormhole import flux as m
from grteclyn_stationary.workflows.common import angular_momentum_diagnostics

ROOT=Path(__file__).resolve().parents[3]
CONFIG=ROOT/'grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/spin_ring_flux.json'
def plan():return json.loads(CONFIG.read_text())


@pytest.mark.parametrize('change',[dict(max_solves=15),dict(checkpoints=True),
    dict(target_geometric_flux_xi0=.08),dict(flux_step=.08),dict(energy_budget=2.),
    dict(tidal_factor=5.),dict(wall_seconds=7200)])
def test_fixed_scope(change):
    p=plan();m.validate_plan(p);p.update(change)
    with pytest.raises(ValueError):m.validate_plan(p)


def test_geometric_pin_keeps_total_flux_conservation_independent():
    p=SimpleNamespace(mid=2)
    d=dict(j_of_x=np.array([-.04,-.02,.01]),j_matter_tail=np.array([-.16,-.18,-.21]),
           C2_i=np.ones(3))
    cfg=dict(rotation_control='J_xi0',J=-999.,J_xi0=-.08)
    r=angular_momentum_diagnostics(p,d,2.,cfg)
    assert r['J_measured']==pytest.approx(-.8)
    assert r['J_geometric_flux_xi0']==pytest.approx(-.08)
    assert r['J_error']<1e-15
    # The same desired cut flux cannot excuse a nonconserved total profile.
    d['j_of_x'][0]+=.01
    assert angular_momentum_diagnostics(p,d,2.,cfg)['J_error']>.03
    d['j_of_x'][0]-=.01;cfg['J_xi0']=+.08
    assert angular_momentum_diagnostics(p,d,2.,cfg)['J_flux_error']==pytest.approx(.16)


@pytest.mark.parametrize('matter',[False,True])
def test_only_rotation_border_changes_and_all_unknowns_are_preserved(matter):
    from grteclyn_stationary.matter.equations import MatterCollocationProblem
    from grteclyn_stationary.matter.potentials import PolynomialPotential
    kw=dict(eta0=1.,gamma=0.,nx=8,ny=4,pin=('minimal_area',16*np.pi))
    if matter:kw.update(winding=(PolynomialPotential((0.,0.,1.)),.8,1),pin_zeta=.1)
    a=MatterCollocationProblem(**kw,prescribe=('J',-.08))
    b=MatterCollocationProblem(**kw,prescribe=('J_xi0',-.08))
    x=(1-a.sx[:,None]**2)*np.ones((1,5));z=np.zeros_like(x)
    fields=[.01*x,.02*x,.01*x,.01*x,.01*x]
    packing=dict(omega_inf=-.05,psi_minus=-np.pi,sigma=2.,xi_t=.01)
    if matter:packing.update(dzeta=.1*x,omega_z=.8)
    ua=a.pack(*fields,**packing);ub=b.pack(*fields,**packing)
    np.testing.assert_array_equal(ua,ub)
    assert len(ub)==b.n_unknowns==a.n_unknowns
    ra=np.asarray(a.residual(ua));rb=np.asarray(b.residual(ub));row=a.nf*a.n
    np.testing.assert_allclose(np.delete(ra,row),np.delete(rb,row),rtol=0,atol=2e-12)
    F,W,N,B,*_=b.fields(ub)
    flux=4*float(b.j_flux(F,B,b.Dx@W))
    assert rb[row]==pytest.approx(flux+.08,abs=1e-13)
    if matter:
        jm=4*float(a.j_matter(F,N,B,W,.1*x,2*.8))
        assert abs(jm)>.01
        assert ra[row]-rb[row]==pytest.approx(jm,abs=1e-12)
        assert b.omega_z_of(ub)==.8
    else:np.testing.assert_allclose(ra,rb,rtol=0,atol=2e-12)
    # Verify the new border participates in AD, including physical scaling.
    import jax
    import jax.numpy as jnp
    direction=np.zeros(len(ub));direction[-2]=1.
    _,jvp=jax.jvp(b.residual,(jnp.asarray(ub),),(jnp.asarray(direction),))
    eps=1e-5
    fd=(np.asarray(b.residual(ub+eps*direction))-np.asarray(b.residual(ub-eps*direction)))/(2*eps)
    np.testing.assert_allclose(np.asarray(jvp),fd,rtol=1e-7,atol=1e-7)


@pytest.mark.parametrize('aligned',[False,True])
def test_continuation_checks_alignment_before_any_refinement(tmp_path,monkeypatch,aligned):
    from grteclyn_stationary.workflows import common as exploration; from grteclyn_stationary.studies import runner as study
    calls=[]
    def solve(s,c,*a,**kw):
        calls.append(c['J_xi0']);return s,dict(verdict='PASS',J_measured=-.7)
    monkeypatch.setattr(exploration,'solve_trial',solve)
    monkeypatch.setattr(exploration,'save_trial',lambda *a,**kw:None)
    monkeypatch.setattr(study,'release_solver',lambda:None)
    monkeypatch.setattr(m,'validate_ring',lambda *a,**kw:dict(
        verdict='PASS' if aligned else 'ABOVE_GATE',geometric_and_matter_flux_aligned=aligned))
    _,_,rows,ok=m.continue_flux({},dict(J=0.),plan(),tmp_path/'continuation',1.)
    assert ok==aligned and len(calls)==(4 if aligned else 1)
    assert len(rows)==len(calls)
    assert not (tmp_path/'ring').exists()


def test_failed_orientation_never_starts_refinement_or_control(tmp_path,monkeypatch):
    from grteclyn_stationary.validation import resolution; from grteclyn_stationary.studies import diagnostics as study_diagnostics; from grteclyn_stationary.studies import validation as study_validation; from grteclyn_stationary.workflows import common as exploration; from grteclyn_stationary.studies import runner as study
    monkeypatch.setattr(m,'read_seeds',lambda p:[({},{}),({},{})])
    monkeypatch.setattr(m,'continue_flux',lambda *a:({},{},[{}],False))
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    monkeypatch.setattr(study_validation,'validate',lambda *a,**kw:dict(verdict='PASS'))
    monkeypatch.setattr(exploration,'save_trial',lambda *a:None)
    def forbidden(*a,**kw):raise AssertionError('refinement/control started after wrong orientation')
    monkeypatch.setattr(resolution,'check_candidate',forbidden)
    monkeypatch.setattr(m,'continue_j',forbidden)
    out=tmp_path/'out';assert m.run(plan(),out)==2
    result=json.loads((out/'outcome.json').read_text())
    assert result['solves']==1 and not result['ring_accepted']
    assert 'matched_spin_fractional_reduction' not in result


def test_direct_flux_enters_solve_and_screen_with_exact_ellis_limit():
    from grteclyn_stationary.workflows.common import solve_trial
    from grteclyn_stationary.validation.resolution import screen_trial
    s=m.bridge.ellis(2.,8,4)
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=-999.,rotation_control='J_xi0',J_xi0=0.)
    s,r=solve_trial(s,c,8,4,('minimal_area',16*np.pi),4.,max_iter=1)
    assert r['verdict']=='PASS' and r['J_flux_error']<1e-14
    _,screen=screen_trial(s,c,8,4,('minimal_area',16*np.pi),4.)
    assert screen['verdict']=='PASS' and screen['J_error']<1e-14


def test_preview_is_hash_pinned_and_does_not_import_jax(tmp_path):
    import subprocess
    import sys
    from test_ringwormhole_spin_ring import seeded_plan
    old,_=seeded_plan(tmp_path);p=plan()
    for k in ('ring_seed','control_seed'):p[k]=old[k]
    path=tmp_path/'plan.json';path.write_text(json.dumps(p));out=tmp_path/'out'
    code="import sys; from grteclyn_stationary.ringwormhole import flux as m; m.main(); assert 'jax' not in sys.modules"
    done=subprocess.run([sys.executable,'-c',code,'--config',str(path),'--out',str(out)],
                        capture_output=True,text=True,check=True)
    result=json.loads(done.stdout)
    assert result['flux_ladder']==[-.02,-.04,-.06,-.08] and result['max_solves']==14
    assert not out.exists()
    p['ring_seed']['sha256']='0'*64
    with pytest.raises(ValueError,match='hash mismatch'):m.read_seeds(p)


@pytest.mark.parametrize('failure',[None,'ring','control','mismatch','budget'])
def test_paired_claim_requires_alignment_qualification_match_and_budget(tmp_path,monkeypatch,failure):
    from grteclyn_stationary.validation import resolution; from grteclyn_stationary.studies import diagnostics as study_diagnostics; from grteclyn_stationary.studies import validation as study_validation; from grteclyn_stationary.workflows import common as exploration; from grteclyn_stationary.studies import runner as study
    cc=dict(J=-1. if failure=='budget' else -.7)
    monkeypatch.setattr(m,'read_seeds',lambda p:[({},{}),({},cc)])
    monkeypatch.setattr(m,'continue_flux',lambda *a:({},dict(J_xi0=-.08),[{}]*4,True))
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    monkeypatch.setattr(study_validation,'validate',lambda *a,**kw:dict(verdict='PASS',X_full=np.pi))
    monkeypatch.setattr(exploration,'save_trial',lambda *a:None)
    monkeypatch.setattr(resolution,'save_checked',lambda *a:None)
    calls=[]
    def check(s,c,grids,pin,d2,directory,**kw):
        ring=directory.name=='ring';calls.append(directory.name)
        row=dict(X_full=2.5 if ring else 2.,J_measured=-.6,
            J_geometric_flux_xi0=-.08,J_matter_positive_half=-.52,
            J_matter_xi0_to_plus=-.52,relative_end_angular_velocity=-.04,E_b=1.,Q_b=1.)
        if failure=='mismatch' and not ring:row['J_measured']+=.01
        return dict(passed=failure!=directory.name,records=[row.copy() for _ in grids]),s
    monkeypatch.setattr(resolution,'check_candidate',check)
    def control(s,c,targets,*a):return s,dict(c,J=targets[-1]),[{}]*len(targets),True
    monkeypatch.setattr(m,'continue_j',control)
    out=tmp_path/'out';code=m.run(plan(),out);r=json.loads((out/'outcome.json').read_text())
    assert (code==0)==(failure is None)
    assert ('matched_spin_fractional_reduction' in r)==(failure is None)
    assert r['solves']<=14
    if failure in ('ring','budget'):assert calls==['ring']
    if failure is None:assert r['matched_spin_fractional_reduction']==pytest.approx(-.25)
