"""Exact-limit and independent checks for the constrained stationary studies."""
import json
import numpy as np
import pytest
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto
from grteclyn_wrapper.optimisation.exoticity import tidal
from grteclyn_wrapper.optimisation.study_diagnostics import volume_budgets
from grteclyn_wrapper.optimisation.surfaces import surface_geometry, verify_surface


def ellis(nx=16,ny=6,sigma=1.):
    sx,dx=lobatto(nx); sy,dy=lobatto(ny)
    zero=np.zeros((nx+1,ny+1))
    return dict(sx=sx,sy=sy,F=zero.copy(),W=zero.copy(),N=zero.copy(),B=zero+1,
                PSI=np.pi/2*(sx[:,None]-1)+zero,sigma=sigma,xi_t=0.,
                surface_coefficients=np.zeros(ny+1),map=ArctanMap(eta0=1.),
                omega=0.,psim=-np.pi,gamma=0.)


@pytest.mark.parametrize('theta',[0.,.2,.7,np.pi/2])
@pytest.mark.parametrize('v',[0.,-.5,.5])
def test_ellis_tides_at_all_latitudes(theta,v):
    s=ellis(); _,dx=lobatto(16); _,dy=lobatto(6)
    xi=.2; eta=s['map'].eta(xi)
    r=tidal(1.,s['map'],s['sx'],s['sy'],dx,dy,s['F'],s['W'],s['N'],s['B'],xi,v,theta)
    expected=-v*v/(1-v*v)/(eta*eta+1)**2
    np.testing.assert_allclose(r['eigs'],[expected,expected,0.],atol=2e-9)


def test_far_end_tides_ignore_a_constant_rotating_coordinate_shift():
    s=ellis(); _,dx=lobatto(16); _,dy=lobatto(6)
    shifted=s['W']+.83
    for xi in (-.9999,.9999):
        args=(1.,s['map'],s['sx'],s['sy'],dx,dy,s['F'])
        reference=tidal(*args,s['W'],s['N'],s['B'],xi,.5,.7)
        rotated=tidal(*args,shifted,s['N'],s['B'],xi,.5,.7)
        np.testing.assert_allclose(rotated['E'],reference['E'],rtol=1e-5,atol=1e-18)


def test_full_budget_and_similarity():
    s=ellis()
    b=volume_budgets(s,{})
    assert b['X_full']==pytest.approx(np.pi,rel=1e-12)
    assert b['X_angular']==pytest.approx(0.,abs=1e-25)
    s['sigma']=3.
    bigger=volume_budgets(s,{})
    assert bigger['X_full']==pytest.approx(b['X_full'])
    assert bigger['local_nec_peak']==pytest.approx(b['local_nec_peak']/9)
    s['PSI']=s['PSI']+.1*(1-s['sx'][:,None]**2)*(1+s['sy'][None,:])
    assert volume_budgets(s,{})['X_angular']>0


def test_direct_ricci_and_scalar_checks_detect_a_wrong_metric():
    from grteclyn_wrapper.optimisation.study_diagnostics import independent_equations
    s=ellis()
    cfg=dict(m=0.,q=[0.,0.,0.])
    exact=independent_equations(s,cfg,radial_points=9,angular_points=5)
    assert exact['offgrid_pass'],exact
    s['F']=.02*(1-s['sx'][:,None]**2)*np.ones((1,len(s['sy'])))
    bad=independent_equations(s,cfg,radial_points=9,angular_points=5)
    assert not bad['offgrid_pass']
    assert bad['offgrid_einstein']>1e-3


def test_ellis_surface_minimum_and_coupled_pin():
    from grteclyn_wrapper.optimisation.matter_equations import MatterCollocationProblem
    s=ellis(8,4)
    g=surface_geometry(1.,s['map'],s['sx'],s['sy'],s['F'],s['N'],s['B'],np.zeros(5))
    assert g['area_throat']==pytest.approx(4*np.pi)
    v=verify_surface(1.,s['map'],s['sx'],s['sy'],s['F'],s['N'],s['B'],np.zeros(5))
    assert v['surface_verified'] and v['surface_hessian_min']>0
    p=MatterCollocationProblem(eta0=1.,gamma=0.,nx=8,ny=4,
                              prescribe=('J',0.),pin=('minimal_area',16*np.pi))
    z=np.zeros((9,5))
    u=p.pack(z,z,z,z,z,omega_inf=0.,psi_minus=-np.pi,sigma=2.,xi_t=0.)
    assert len(u)==p.n_unknowns
    assert np.max(abs(p.residual(u)))<1e-11
    assert np.isfinite(p.jacobian(u)).all()
    assert p.throat(u)['area']==pytest.approx(16*np.pi)


def test_surface_polish_resolves_gradient_below_area_roundoff():
    from grteclyn_wrapper.optimisation.surfaces import _polish_minimum
    h = np.diag([5., 1e4])
    initial = np.array([1e-9, 1e-9])
    fun = lambda x: 1. + .5 * x @ h @ x
    grad = lambda x: h @ x
    polished = _polish_minimum(fun, grad, lambda x: h,
                               lambda x: np.max(abs(x)) < .999, initial)
    assert np.max(abs(grad(initial))) > 1e-7
    assert np.max(abs(grad(polished))) < 1e-9
    assert fun(polished) <= fun(initial)
    # A negative-curvature stationary point must never be polished into
    # something the surface verifier can mistake for a minimum.
    saddle = _polish_minimum(lambda x: -float(x @ x), lambda x: -2*x,
                             lambda x: -2*np.eye(2), lambda x: True, initial)
    np.testing.assert_array_equal(saddle, initial)


def test_d21_refined_reference_surface_multistart():
    from pathlib import Path
    from grteclyn_wrapper.optimisation.exploration import load_seed
    root = Path(__file__).resolve().parents[3]
    saved = root / 'results/optimisation/validation/2026-10-31-area-reference/reference/diagnostic_180x36.npz'
    s, _ = load_seed(saved)
    checked = verify_surface(1., s['map'], s['sx'], s['sy'],
                             s['F'], s['N'], s['B'], s['surface_coefficients'])
    assert checked['surface_verified'], checked
    assert checked['surface_minima'] == 1 and not checked['surface_unresolved']


def test_angular_deformation_changes_true_minimum():
    from grteclyn_wrapper.optimisation.surfaces import find_surface
    from scipy.optimize import minimize_scalar
    s=ellis(20,8)
    s['F']=.1*s['sx'][:,None]*(1-s['sx'][:,None]**2)*s['sy'][None,:]
    def area(c):
        return surface_geometry(1.,s['map'],s['sx'],s['sy'],s['F'],s['N'],s['B'],c)['area_throat']
    constant=minimize_scalar(lambda x:area([x]),bounds=(-.3,.3),method='bounded')
    c=find_surface(1.,s['map'],s['sx'],s['sy'],s['F'],s['N'],s['B'],constant.x)
    assert area(c)<constant.fun-1e-5
    assert np.max(abs(c[1:]))>1e-4


def test_no_linear_mode_still_attempts_finite_branch(monkeypatch):
    from grteclyn_wrapper.optimisation import study,boson_seeds
    calls=[]; expected=(dict(field='solved'),dict(verdict='PASS'))
    def no_mode(*a,**kw): raise RuntimeError('no bound mode')
    monkeypatch.setattr(study,'bound_mode',no_mode)
    monkeypatch.setattr(boson_seeds,'finite_amplitude_seed',lambda s,c:dict(finite=True))
    def solve(s,*a,**kw):
        assert s['finite']; calls.append('finite'); return expected
    monkeypatch.setattr(study,'solve_trial',solve)
    records=[]
    assert list(study.seed_attempts({}, {}, ('minimal_area',1.),(8,4),1.,records.append))==[expected]
    assert calls==['finite'] and records[0]['verdict']=='UNRESOLVED'


def test_boson_workflow_tries_massless_and_repinned_potential_backgrounds(monkeypatch,tmp_path):
    from grteclyn_wrapper.optimisation import study
    from grteclyn_wrapper.optimisation.commands.optimize_potential import build_parser
    s=ellis(8,4); basecfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    row=dict(verdict='PASS',nx=8,ny=4,X=np.pi,X_A=np.pi,X_full=np.pi,R_A=1.,tidal_peak=1.)
    result=dict(passed=True,method='refine',records=[row,row],relative_bill_drift=0.)
    source=tmp_path/'potential.npz'
    study.save_checked(source,s,dict(basecfg,m=.3),{},result)
    config=tmp_path/'study.toml'
    config.write_text('mass_seeds=[1.0]\namplitude_seeds=[0.1]\ncandidate_seeds=['+json.dumps(str(source))+']\n')
    monkeypatch.setattr(study,'source_manifest',lambda *a:{})
    monkeypatch.setattr(study,'massless_state',lambda *a:(s,basecfg))
    monkeypatch.setattr(study,'find_surface',lambda *a:np.zeros(5))
    monkeypatch.setattr(study,'check_candidate',lambda *a,**kw:(result,s))
    monkeypatch.setattr(study,'solve_trial',lambda *a,**kw:(s,row))
    tried=[]
    def seeds(background,c,*a):
        tried.append(c['m']); return iter(())
    monkeypatch.setattr(study,'seed_attempts',seeds)
    args=build_parser().parse_args(['unused.json','--study-config',str(config),
            '--study-case','boson-k1-t2-e0.1','--nx','8','--ny','4','--out',str(tmp_path/'out')])
    assert study.run(args,error=lambda msg:pytest.fail(msg))==2
    assert tried==[0.,.3]


def test_study_config_matrix_and_invalid_bounds(tmp_path):
    from grteclyn_wrapper.optimisation.study import load_config,cases
    p=tmp_path/'study.toml'; p.write_text('version=1\n')
    cfg=load_config(p)
    assert len(cases(cfg))==30 and 'boson-k-1-t2-e0.3' in cases(cfg)
    p.write_text('mass_range=[2.0, 1.0]\n')
    with pytest.raises(ValueError,match='bounds'): load_config(p)


def test_hard_limits_cannot_be_cleared_by_a_small_objective(monkeypatch):
    from grteclyn_wrapper.optimisation import study_validation as v
    monkeypatch.setattr(v,'verify_surface',lambda *a,**kw:dict(surface_verified=True))
    monkeypatch.setattr(v,'independent_equations',lambda *a,**kw:dict(offgrid_pass=True))
    monkeypatch.setattr(v,'tidal_envelope',lambda *a,**kw:dict(tidal_peak=1/3,tidal_drift=0.,tidal_converged=True))
    s=ellis(); cfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    r=v.validate(s,cfg,dict(verdict='PASS'),reference_peak=.1,tidal_factor=2.)
    assert r['verdict']=='ABOVE_GATE' and 'tidal_limit' in r['rejection_reasons']
    r=v.validate(s,cfg,dict(verdict='PASS'),reference_peak=1.,tidal_factor=1.)
    assert r['verdict']=='PASS'
    s['CHI']=.1*(1-s['sx'][:,None]**2)**3*np.ones((1,len(s['sy'])))
    s['frequency']=.8
    cfg.update(matter='cloud',matter_mass=1.,amplitude=.1)
    r=v.validate(s,cfg,dict(verdict='PASS'),reference_peak=1.,tidal_factor=1.,energy_budget=1e-12)
    assert r['verdict']=='ABOVE_GATE' and 'ordinary_energy_budget' in r['rejection_reasons']


def test_bondi_mass_potential_maps_to_solver_normalisation():
    from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
    from grteclyn_wrapper.grtresna.profiles.boson_star_ode import _potential
    m=1.7; phi=.031; chi=np.sqrt(4*np.pi)*phi
    converted=PolynomialPotential.from_evolution((0.,0.,m*m/2))
    assert converted.V(chi)==pytest.approx(m*m*chi*chi)
    assert converted.V(chi)==pytest.approx(8*np.pi*_potential(phi,mass=m,lam=0.,mu=0.))


def test_refinement_with_zero_updates_cannot_certify(monkeypatch,tmp_path):
    from grteclyn_wrapper.optimisation import resolution as r
    s=ellis(8,4)
    def no_correction(seed,*args,**kw):
        assert np.max(abs(seed['F']-s['F']))>0
        assert kw['newton_tol'] == 1e-14
        return s,dict(verdict='PASS',iters=0,X_full=3.14)
    monkeypatch.setattr(r,'solve_trial',no_correction)
    monkeypatch.setattr(r,'save_trial',lambda *a:None)
    result,_=r.check_candidate(s,{},[(8,4),(10,5)],('minimal_area',4*np.pi),1.,
                               tmp_path/'check',score_key='X_full',perturb_seed=True)
    assert not result['passed']


def test_required_newton_update_survives_small_scaled_residual():
    from grteclyn_wrapper.optimisation.solver.newton import newton
    # A row scale can make a real error satisfy the stopping tolerance.
    residual=lambda u:np.array([u[0]**2-1])
    jacobian=lambda u:np.array([[2*u[0]]])
    _,early=newton(residual,jacobian,[1.+1e-7],tol=1e-6)
    solved,checked=newton(residual,jacobian,[1.+1e-7],tol=1e-6,min_updates=1)
    assert early['iters']==0 and len(checked['newton_steps'])>=1
    assert abs(solved[0]-1)<1e-12


def test_infeasible_search_scores_guide_without_overriding_acceptance():
    from grteclyn_wrapper.optimisation.study import search_score
    feasible = search_score(dict(verdict='PASS', X_full=1e6))
    near = search_score(dict(verdict='ABOVE_GATE', E19=2e-8))
    far = search_score(dict(verdict='ABOVE_GATE', E19=1e-3))
    assert feasible < 1 < near < far < 3
    assert search_score(dict(verdict='FAILED')) == 4
    assert search_score(dict(verdict='ABOVE_GATE', E_c=float('nan'))) == 4


def test_signed_winding_reverses_twist_and_preserves_other_equations():
    from grteclyn_wrapper.optimisation.matter_equations import MatterCollocationProblem
    from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
    pot=PolynomialPotential((0.,0.,1.))
    kwargs=dict(eta0=1.,gamma=0.,nx=8,ny=4)
    plus=MatterCollocationProblem(**kwargs,prescribe=('J',.01),winding=(pot,.8,1))
    minus=MatterCollocationProblem(**kwargs,prescribe=('J',-.01),winding=(pot,.8,-1))
    z=np.zeros((9,5)); a=.03*(1-plus.sx[:,None]**2)*(z+1)
    up=plus.pack(z,z,z,z,z,omega_inf=.05,psi_minus=-np.pi,dzeta=a)
    um=minus.pack(z,z,z,z,z,omega_inf=-.05,psi_minus=-np.pi,dzeta=a)
    rp=np.asarray(plus.residual(up)); rm=np.asarray(minus.residual(um))
    expected=rp.copy(); expected[plus.n:2*plus.n]*=-1; expected[6*plus.n]*=-1
    np.testing.assert_allclose(rm,expected,atol=1e-12)
    assert np.isfinite(minus.jacobian(um)).all()


def test_canonical_mass_normalisation_and_noether_sign():
    s=ellis(32,12)
    s['Z']=.1*(1-s['sx'][:,None]**2)**3*np.ones((1,13)); s['frequency']=.7
    cfg=dict(matter='winding',matter_mass=1.,winding_k=1)
    pos=volume_budgets(s,cfg)
    neg=volume_budgets(s,dict(cfg,winding_k=-1))
    assert pos['E_b']>0 and pos['Q_b']>0 and pos['J_b']==-pos['Q_b']
    assert neg['E_b']==pytest.approx(pos['E_b'])
    assert neg['J_b']==pytest.approx(-pos['J_b'])
    # E = 1/2 (omega^2+m^2) int |chi|^2/(4pi) + positive gradients.
    assert pos['E_b']>(.7**2+1)*pos['Q_b']/(2*.7)
    s['sigma']=3.; s['frequency']/=3
    scaled=volume_budgets(s,dict(cfg,matter_mass=1/3))
    assert scaled['E_b']==pytest.approx(3*pos['E_b'])
    assert scaled['E_b_over_R_A']==pytest.approx(pos['E_b_over_R_A'])
    assert scaled['J_b']==pytest.approx(9*pos['J_b'])


def test_matter_roundtrip_and_export_refusal(tmp_path):
    from grteclyn_wrapper.optimisation.exploration import save_trial,load_seed,make_problem,pack_seed
    from grteclyn_wrapper.optimisation.handoff import matter_background
    s=ellis(8,4); s['Z']=.03*(1-s['sx'][:,None]**2)*np.ones((1,5)); s['frequency']=.8
    cfg=dict(m=0.,q=[0,0,0],gamma=0.,J=0.,matter='winding',matter_mass=1.,winding_k=-1,amplitude=.03)
    path=tmp_path/'mixed.npz'
    save_trial(path,s,cfg,dict(frequency=.8),('minimal_area',4*np.pi))
    restored,meta=load_seed(path)
    np.testing.assert_array_equal(restored['Z'],s['Z'])
    assert restored['frequency']==.8 and meta['schema_version']==2
    p=make_problem(restored,cfg,12,6,('minimal_area',4*np.pi),amplitude=.03)
    u=pack_seed(p,restored)
    assert p.omega_z_of(u)==.8
    assert p.fields(u)[5][6,-1]==pytest.approx(.03)
    with pytest.raises(ValueError,match='cannot export'):
        matter_background(path,32,16)
