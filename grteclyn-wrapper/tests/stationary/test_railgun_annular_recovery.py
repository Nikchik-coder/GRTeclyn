"""A screened gap is a seed; acceptance needs coupled three-grid evidence."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from grteclyn_stationary.railgun.annular_recovery import preflight,acceptance,measure_channel,correction_plan
from grteclyn_stationary.railgun.model import ScalarField

ROOT=Path(__file__).resolve().parents[3]


def config():
    return json.loads((ROOT/'grteclyn-wrapper/scripts/campaigns/railgun/configs/annular_recovery_k12.json').read_text())


def seed(tmp_path,*,validated=False):
    source=tmp_path/'seed.npz'
    meta=dict(schema=1,model='canonical_regular_centre',nx=6,ny=3,length=50.,target_j=None,
              validated=validated,fields=[ScalarField(winding=1).to_dict(),
              ScalarField(winding=-12,amplitude=.00038,anchor_radius=160.).to_dict()])
    np.savez(source,metadata=json.dumps(meta),u=np.zeros(6*7*4+2))
    source.with_suffix('.json').write_text(json.dumps(dict(stage='fixed_background_linear_screen',
        self_consistent=False,winding=-12,grid=[6,3],gap=dict(accepted=True,relative_density_cutoff=1e-6))))
    (tmp_path/'manifest.json').write_text(json.dumps(dict(stage='fixed_background_linear_screen',commit='test')))
    (tmp_path/'outcome.json').write_text(json.dumps(dict(screen_completed=True,accepted_background=False,
        candidates=[dict(seed=source.name,winding=-12)])))
    cfg=config();cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    return source,cfg


def test_preflight_never_starts_jax_and_bounds_all_three_grids(tmp_path,monkeypatch):
    import builtins
    original=builtins.__import__
    def guard(name,*args,**kwargs):
        if name=='jax' or name.startswith('jax.'):raise AssertionError('dry run imported JAX')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guard)
    source,cfg=seed(tmp_path);plan=preflight(source,cfg)
    assert not plan['numerical_execution']
    assert plan['unknowns']==[19689,25653,32385]
    assert max(plan['eight_dense_buffers_GiB'])<64.


@pytest.mark.parametrize('change',[
    {'grids':[[192,16],[224,18],[320,24]]},
    {'grids':[[192,16],[192,18],[256,20]]},
    {'max_solves':4},{'max_iter':31},{'equation_tol':1e-7},
    {'relative_density_cutoff':1e-5},{'channel_half_height':float('nan')},
])
def test_run_budget_and_physical_gates_cannot_silently_change(tmp_path,change):
    source,cfg=seed(tmp_path);cfg.update(change)
    with pytest.raises(ValueError):preflight(source,cfg)


def test_seed_checksum_and_screen_provenance_are_required(tmp_path):
    source,cfg=seed(tmp_path)
    cfg['source_sha256']='0'*64
    with pytest.raises(ValueError,match='checksum'):preflight(source,cfg)
    cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    (tmp_path/'outcome.json').write_text(json.dumps(dict(screen_completed=True,accepted_background=False,candidates=[])))
    with pytest.raises(ValueError,match='provenance'):preflight(source,cfg)


def test_an_accepted_state_cannot_masquerade_as_a_linear_screen(tmp_path):
    source,cfg=seed(tmp_path,validated=True)
    with pytest.raises(ValueError,match='unaccepted'):preflight(source,cfg)


def test_correction_has_one_additional_solve_and_cannot_change_the_model():
    prior=ROOT/'results/railgun/studies/annular-recovery-k12'
    plan=correction_plan(prior,config())
    assert plan['max_additional_solves']==1 and plan['cumulative_solve_cap']==4
    assert plan['corrected_grid']==[256,20] and plan['minimum_new_updates']==2
    cfg=config();cfg['equation_tol']=2e-8
    with pytest.raises(ValueError,match='original finest-grid'):correction_plan(prior,cfg)


def test_correction_verifies_prior_archive_before_reusing_passing_grids(tmp_path):
    import shutil
    prior=ROOT/'results/railgun/studies/annular-recovery-k12'
    shutil.copytree(prior,tmp_path/'prior');prior=tmp_path/'prior'
    with (prior/'grid_192x16.json').open('a') as stream:stream.write(' ')
    with pytest.raises(ValueError,match='checksum'):correction_plan(prior,config())


def records():
    return [dict(verdict='PASS',length_scale=50.,M_ADM_estimate=1.,J_volume=0.,dragging_max=.002,
                 charges=[1.,1/12],newton=dict(newton_steps=[1.,1.]),
                 annular_gap=dict(accepted=True,inner_ring_outer_radius=33.,outer_ring_inner_radius=41.),
                 finite_height_channel=dict(accepted=True)) for _ in range(3)]


def test_joint_acceptance_requires_gap_on_every_grid_and_component_convergence():
    rows=records();assert acceptance(rows)['accepted']
    rows[0]['annular_gap']['accepted']=False
    assert not acceptance(rows)['accepted']
    rows=records();rows[1]['charges']=[2.,2/12]
    # J still cancels: convergence of the two separately measured charges matters.
    assert not acceptance(rows)['accepted']
    rows=records();rows[1]['annular_gap']['outer_ring_inner_radius']+=.01
    assert not acceptance(rows)['accepted']


def test_no_acceptance_from_two_grids_missing_corrections_or_nonfinite_charges():
    assert not acceptance(records()[:2])['accepted']
    rows=records();rows[0]['newton']['newton_steps']=[]
    assert not acceptance(rows)['accepted']
    rows=records();rows[-1]['charges'][1]=np.nan
    assert not acceptance(rows)['accepted']
    rows=records();rows[-1]['finite_height_channel']['accepted']=False
    assert not acceptance(rows)['accepted']


def test_finite_height_measurement_can_reject_an_equatorially_clear_gap(tmp_path,monkeypatch):
    import grteclyn_stationary.railgun.gap as gap_module
    gap=dict(accepted=True,inner_ring_outer_radius=30.,outer_ring_inner_radius=40.,
             edges=[dict(peak_density=1.),dict(peak_density=.1)])
    def density(meta,u,rho,z):return np.array([1e-8+2e-8*z*z,np.full_like(z,1e-9)])
    monkeypatch.setattr(gap_module,'cylindrical_densities',density)
    row=measure_channel({},[],gap,10.,tmp_path,'test')
    assert not row['accepted']
    assert row['rho_min']==32.5 and row['rho_max']==37.5
    assert (tmp_path/'test_channel.tsv').exists()


def test_unbordered_promotion_preserves_both_frequencies_and_adds_log_pin():
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.continuation import transfer_fields
    fields=[ScalarField(winding=1),ScalarField(winding=-12,amplitude=.00038,anchor_radius=160.)]
    old=RingProblem(fields,nx=8,ny=3,length=50.)
    arrays,_=old.unpack(old.seed());frequencies=[.932,.997]
    value=old.pack(arrays,frequencies)
    p=RingProblem(fields,nx=12,ny=4,length=50.,target_j=0.)
    promoted=transfer_fields(p,old,value)
    promoted=p.transfer(p,promoted,perturb=1e-5)
    _,actual=p.unpack(promoted)
    np.testing.assert_array_equal(actual,frequencies)
    assert promoted[-1]==pytest.approx(np.log(.00038))
    assert promoted[-1]!=value[-1]


@pytest.mark.parametrize('winding',[-2,-12])
@pytest.mark.parametrize('parity',['even','odd'])
def test_cylindrical_energy_per_component_matches_cartesian_ad(winding,parity):
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.gap import cylindrical_densities,equatorial_densities
    fields=[ScalarField(winding=1,quartic=.2,parity=parity),ScalarField(winding=winding,sextic=.1,parity=parity)]
    p=RingProblem(fields,nx=12,ny=4,length=5.)
    a,f=p.unpack(p.seed())
    shape=(1-p.s[:,None]**2)*(1+.1*p.y[None,:])
    a['q0']=.03*shape;a['q1']=.02*shape
    a['N']=.02*shape;a['w']=.001*shape
    u=p.pack(a,f);geom=RingGeometry(p,u);jax,xp=p.jax,p.xp
    def independent(point):
        g=geom.metric(point);alpha=1/xp.sqrt(-xp.linalg.inv(g)[0,0])
        normal=xp.concatenate((xp.ones(1),-xp.linalg.solve(g[1:,1:],g[0,1:])))/alpha
        inverse=xp.linalg.inv(g[1:,1:]);out=[]
        for i,field in enumerate(fields):
            scalar=lambda x:geom.scalar(x,i)
            value=scalar(point);gradient=jax.jacfwd(scalar)(point);a2=xp.sum(value*value)
            potential=field.mass**2*a2+field.quartic*a2*a2+field.sextic*a2**3
            out.append((xp.sum((gradient@normal)**2)
                +xp.einsum('ij,ai,aj->',inverse,gradient[:,1:],gradient[:,1:])+potential)/(8*xp.pi))
        return xp.array(out)
    rho=np.array([3.,7.,11.]);z=np.array([-4.,0.,6.])
    points=np.column_stack([np.zeros(3),rho,np.zeros(3),z])
    reference=np.asarray(jax.jit(jax.vmap(independent))(xp.asarray(points))).T
    meta=dict(nx=p.nx,ny=p.ny,length=p.length,fields=[field.to_dict() for field in fields])
    actual=cylindrical_densities(meta,u,rho,z)
    np.testing.assert_allclose(actual,reference,rtol=2e-11,atol=1e-17)
    if parity=='even':
        np.testing.assert_allclose(cylindrical_densities(meta,u,rho,0.),equatorial_densities(meta,u,rho),rtol=1e-12)
    else:
        # The odd scalar vanishes on z=0; its transverse gradient still carries energy.
        assert np.all(cylindrical_densities(meta,u,rho,0.)>0.)
    np.testing.assert_allclose(actual,cylindrical_densities(meta,u,rho,-z),rtol=1e-13)
