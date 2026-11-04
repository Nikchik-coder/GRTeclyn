"""Source identity, two-ended boundaries and exterior amplitude borders."""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun_wormhole import read_source,prepare_seed,ellis,ring_geometry
from grteclyn_wrapper.optimisation.exploration import make_problem,pack_seed,matter_anchor

ROOT=Path(__file__).resolve().parents[3]


def plan():
    return json.loads((ROOT/'research/optimisation/studies/railgun_throat.json').read_text())


def test_exact_archived_source_and_hash_rejection(monkeypatch):
    monkeypatch.chdir(ROOT)
    p=plan(); meta,arrays,freq,row=read_source(p)
    assert meta['fields'][0]['winding']==1
    assert freq==pytest.approx(.932692332164,rel=1e-10)
    assert row['gtt_max']<0 and row['verdict']=='PASS'
    p['source_sha256']['grid_128x16.npz']='0'*64
    with pytest.raises(ValueError,match='hash mismatch'): read_source(p)


def test_bridge_uses_archived_metric_ring_and_frequency(monkeypatch):
    from grteclyn_wrapper.optimisation.exploration import physical_throat
    monkeypatch.chdir(ROOT)
    p=plan();s,c=prepare_seed(p)
    assert physical_throat(s)['area_throat']==pytest.approx(16*np.pi,rel=1e-10)
    assert s['frequency']==pytest.approx(.932692332164,rel=1e-10)
    assert np.max(abs(s['W']))>1e-4 and np.max(abs(s['F']))>.1
    for key in ('F','W','N','Z'):
        np.testing.assert_allclose(s[key][[0,-1]],0,atol=1e-15)
        np.testing.assert_allclose(s[key],s[key][::-1],atol=1e-14)
    assert c['rotation_control']=='nonrotating_ends' and s['omega']==0
    assert c['m']==0 and c['matter_mass']==1 and c['winding_k']==1
    assert .1<c['zeta_anchor_xi']<.95
    assert matter_anchor(s['Z'],s['sx'],c)==pytest.approx(c['amplitude'])
    g=ring_geometry(s,c)
    assert g['ring_outside_throat'] and not g['equatorial_ergoregion_sampled']
    assert g['ring_peak_radius']>5


def test_zero_end_dragging_area_pin_preserves_exact_ellis():
    s=ellis(2.,8,4);c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=999.,rotation_control='nonrotating_ends')
    p=make_problem(s,c,8,4,('minimal_area',16*np.pi))
    u=pack_seed(p,s)
    assert len(u)==p.n_unknowns
    assert p.mode=='omega_inf' and p.value==0
    assert np.max(abs(p.residual(u)))<1e-11
    assert np.isfinite(p.jacobian(u)).all()
    assert p.throat(u)['area']==pytest.approx(16*np.pi)
    from grteclyn_wrapper.optimisation.solver.newton import newton
    perturbed=dict(s,F=s['F']+1e-4*(1-s['sx'][:,None]**2)*np.ones((1,5)))
    recovered,info=newton(p.residual,p.jacobian,pack_seed(p,perturbed),tol=1e-14,max_iter=12)
    assert info['converged'] and len(info['newton_steps'])>0
    assert np.max(abs(np.asarray(p.fields(recovered)[0])))<1e-10
    assert np.max(abs(p.diagnostics(recovered)['E19']))<1e-9
    from grteclyn_wrapper.optimisation.matter_equations import MatterCollocationProblem
    with pytest.raises(ValueError,match='prescribe'):
        MatterCollocationProblem(eta0=1.,gamma=0.,nx=8,ny=4,
            prescribe=('omega_inf',.1),pin=('minimal_area',16*np.pi))


@pytest.mark.parametrize('nx',[8,12])
def test_off_throat_border_and_derivative_are_refinement_invariant(nx):
    s=ellis(2.,nx,4);sx=s['sx'];xi=.37
    s['Z']=.1*(1-sx[:,None]**2)*(1+sx[:,None]**2)*np.ones((1,5))
    s['frequency']=.8
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.,rotation_control='nonrotating_ends',
           matter='winding',matter_mass=1.,winding_k=1,zeta_anchor_xi=xi,amplitude=.1*(1-xi**4))
    p=make_problem(s,c,nx,4,('minimal_area',16*np.pi),amplitude=c['amplitude'])
    u=pack_seed(p,s)
    border=p.nf*p.n+1 # scalar constraint, then scalar-amplitude border; no J border
    assert abs(float(p.residual(u)[border]))<1e-14
    assert matter_anchor(s['Z'],sx,c)==pytest.approx(c['amplitude'])
    jac=np.asarray(p.jacobian(u))
    zrow=jac[border,5*p.n:6*p.n].reshape(nx+1,5)
    np.testing.assert_allclose(zrow[:,-1],p.zeta_anchor,atol=1e-13)
    np.testing.assert_allclose(zrow[:,:-1],0,atol=1e-13)


def test_preview_never_initializes_jax_or_writes(tmp_path):
    script='''import sys
from grteclyn_wrapper.optimisation import railgun_wormhole as r
r.main()
assert 'jax' not in sys.modules
'''
    cmd=[sys.executable,'-c',script,'--config','research/optimisation/studies/railgun_throat.json',
         '--out',str(tmp_path/'out')]
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'PREPARED_ONLY' in result.stdout
    result=subprocess.run(['bash','research/optimisation/studies/run_railgun_throat.sh',
           '99999',str(tmp_path/'out')],cwd=ROOT,capture_output=True,text=True,check=True)
    assert '--mem 160 --timeout 3600' in result.stdout
    assert 'XLA_PYTHON_CLIENT_ALLOCATOR=platform' in result.stdout
    assert not (tmp_path/'out').exists()


@pytest.mark.parametrize('key,value', [('max_solves',19),('max_control_steps',13),
    ('max_newton_iterations',25),('wall_seconds',7200),('checkpoints',True)])
def test_plan_refuses_expanded_budget(key,value):
    from grteclyn_wrapper.optimisation.railgun_wormhole import validate_plan
    p=plan();p[key]=value
    with pytest.raises(ValueError): validate_plan(p)


@pytest.mark.parametrize('ring_pass,control_pass,j',[(False,True,-.2),(True,False,-.2),
                                                     (True,True,-.2),(True,True,-1.3)])
def test_workflow_never_claims_an_unchecked_matched_gain(monkeypatch,tmp_path,ring_pass,control_pass,j):
    from grteclyn_wrapper.optimisation import railgun_wormhole as module
    from grteclyn_wrapper.optimisation import exploration,resolution,study,study_validation,study_diagnostics
    p=plan();p['grids']=[[6,3],[8,4],[10,5]]
    s=ellis(2.,6,3);s['Z']=.1*(1-s['sx'][:,None]**2)*np.ones((1,4));s['frequency']=.8
    c=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=j,matter='winding',matter_mass=1.,winding_k=1,
           amplitude=.1,rotation_control='nonrotating_ends')
    monkeypatch.setattr(module,'prepare_seed',lambda p:(s,c))
    monkeypatch.setattr(study_diagnostics,'tidal_envelope',lambda s:dict(tidal_peak=1.))
    monkeypatch.setattr(study_validation,'validate',lambda s,c,r,**kw:dict(r,X_full=np.pi))
    def record(matter):
        return dict(verdict='PASS',X_full=2.8 if matter else 3.,E_b=1.,Q_b=-2*j,J_measured=j,
                    ring_peak_radius=6.,equatorial_shift_over_lapse_max=.005)
    checks=[]
    def check(s,c,grids,*args,**kwargs):
        checks.append(c.copy());matter=c.get('matter')
        passed=ring_pass if matter else control_pass
        return dict(passed=passed,method='refine',records=[record(matter)]*3),s
    monkeypatch.setattr(resolution,'check_candidate',check)
    steps=[]
    def solve(s,c,*args,**kw):
        steps.append(c['J']);return s,dict(verdict='PASS')
    monkeypatch.setattr(exploration,'solve_trial',solve)
    monkeypatch.setattr(study,'release_solver',lambda:None)
    out=tmp_path/'run';status=module.run(p,out)
    result=json.loads((out/'outcome.json').read_text())
    qualified=ring_pass and control_pass and abs(j)<=1.2
    assert (status==0)==qualified
    assert ('matched_spin_fractional_reduction' in result)==qualified
    assert len(steps)<=12 and result['solves']<=18
    if qualified:
        assert checks[-1]['J']==j
        assert checks[-1].get('rotation_control','J')=='J'
        assert not checks[-1].get('matter')
        assert result['matched_spin_fractional_reduction']==pytest.approx(1-2.8/3)
    if abs(j)>1.2:
        assert not steps and result['reason']=='matched_control_outside_budget'
