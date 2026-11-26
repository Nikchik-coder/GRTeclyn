"""One independently spinning wormhole + scalar ring, with a matched control.

The ring-driven seed is continued in total J with its scalar amplitude and
true throat area held fixed. Relative asymptotic rotation becomes an unknown;
reflection symmetry and J_b/2=J are not imposed on this different family.
All independent equation, energy, surface and tidal checks remain unchanged.
"""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from grteclyn_stationary.ringwormhole import workflow as bridge


def j_ladder(start,target,max_step):
    if not all(np.isfinite(v) for v in (start,target,max_step)) or max_step<=0:
        raise ValueError('finite J values and positive step required')
    count=max(1,int(np.ceil(abs(target-start)/max_step-1e-12)))
    return np.linspace(start,target,count+1)[1:].tolist()


def validate_plan(p):
    if (p['grids']!=[[210,36],[224,38],[240,40]] or p['throat_radius']!=2.
            or p['max_newton_iterations']!=24 or p['max_solves']!=14
            or p['wall_seconds']!=3600 or p['threads']!=4 or p['memory_gib']!=160
            or p['checkpoints'] is not False or p['independent_points']!=[49,21]
            or p['tidal_factor']!=4. or p['energy_budget']!=1.
            or p['ring_J_step']!=.02 or p['control_J_step']!=.05
            or p['added_total_J']!=-.08 or p['matter_may_overlap_throat'] is not True):
        raise ValueError('configuration differs from the bounded spin+ring pilot')
    for key in ('ring_seed','control_seed'):
        if len(p[key]['sha256'])!=64:raise ValueError('hash-pinned seeds required')


def read_seeds(p):
    from grteclyn_stationary.workflows.common import load_seed, matter_anchor
    validate_plan(p)
    seeds=[]
    for key in ('ring_seed','control_seed'):
        path=Path(p[key]['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=p[key]['sha256']:
            raise ValueError(key+' hash mismatch')
        s,m=load_seed(path);c=m.get('config',m)
        if (m.get('pin')!=['minimal_area',16*np.pi] or c.get('m')!=0.
                or c.get('q')!=[0.,0.,0.] or c.get('gamma')!=0.
                or not m.get('resolution_validated')):
            raise ValueError('seed lacks the same independently validated fixed-area model')
        cfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,rotation_control='J',
                 J=float(c.get('J_measured',c['J'])))
        if key=='ring_seed':
            if (c.get('matter')!='winding' or c.get('winding_k')!=1
                    or c.get('matter_mass')!=1. or s['omega']!=0.):
                raise ValueError('ring seed must be the accepted ring-driven canonical family')
            cfg.update(matter='winding',winding_k=1,matter_mass=1.,zeta_anchor_xi=0.)
            cfg['amplitude']=matter_anchor(s['Z'],s['sx'],cfg)
        elif any(k in s for k in ('Z','CHI')):
            raise ValueError('control seed must contain no canonical matter')
        seeds.append((s,cfg))
    target=seeds[0][1]['J']+p['added_total_J']
    ladders=[j_ladder(seeds[0][1]['J'],target,p['ring_J_step']),
             j_ladder(seeds[1][1]['J'],target,p['control_J_step'])]
    if sum(map(len,ladders))+6>p['max_solves']:
        raise ValueError('continuation ladders exceed the solve budget')
    return seeds,target,ladders


def rotation_diagnostics(state,row):
    """Killing angular-momentum flux across xi=0, a specified coordinate cut.

    This residual flux is not a unique global split into object spins. Together
    with nonzero relative asymptotic rotation it distinguishes this family
    from the previous zero-flux, matter-driven symmetric seed.
    """
    matter=float(row['J_matter_positive_half'])
    flux=float(row['J_measured']-matter)
    omega=float(state['omega']/state['sigma'])
    return dict(J_geometric_flux_xi0=flux,J_matter_xi0_to_plus=matter,
        relative_end_angular_velocity=omega,
        independent_rotation_present=bool(abs(flux)>1e-5 and abs(omega)>1e-6),
        geometric_and_matter_flux_aligned=bool(flux*matter>0))


def continue_j(state,cfg,targets,plan,directory):
    from grteclyn_stationary.workflows.common import solve_trial, save_trial
    from grteclyn_stationary.studies.runner import release_solver
    directory.mkdir();records=[];pin=('minimal_area',16*np.pi)
    for i,target in enumerate(targets):
        cfg=dict(cfg,J=target);start=time.monotonic()
        try:
            state,row=solve_trial(state,cfg,*plan['grids'][0],pin,4.,max_iter=24,
                newton_tol=1e-14,min_damping=1/4096,verbose=True,
                failure_path=directory/f'failed_{i:02d}.npz')
            if cfg.get('matter'):row.update(rotation_diagnostics(state,row))
            save_trial(directory/f'step_{i:02d}.npz',state,cfg,row,pin)
        except (RuntimeError,ValueError,FloatingPointError) as err:
            row=dict(verdict='FAILED',error=str(err))
        row.update(target_J=target,seconds=time.monotonic()-start);records.append(row)
        with (directory/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        print('spin continuation: '+json.dumps(row),flush=True);release_solver()
        if row['verdict']!='PASS':return state,cfg,records,False
    return state,cfg,records,True


def read_remaining_control(p,parent):
    """Identify the unstarted control arm; never retry a coupled solve.

    The original co-rotation verdict remains rejected. An equation-qualified
    counter-rotating diagnostic can still be compared with the already planned
    ring-free control, without treating it as the intended co-rotating case.
    """
    from grteclyn_stationary.workflows.common import load_seed
    from grteclyn_stationary.validation.resolution import consistent
    seeds,target,ladders=read_seeds(p);parent=Path(parent)
    if json.loads((parent/'plan.json').read_text())!=p:
        raise ValueError('parent plan differs from the approved comparison')
    old=json.loads((parent/'outcome.json').read_text())
    result=json.loads((parent/'ring/result.json').read_text());rows=result['records']
    if (old.get('reason')!='ring_validation_failed' or old.get('solves')!=7
            or old.get('ring_accepted') or old.get('control_accepted')
            or (parent/'control').exists() or (parent/'control_continuation').exists()
            or (parent/'control_arm_started.json').exists()
            or [(r.get('nx'),r.get('ny')) for r in rows]!=[tuple(g) for g in p['grids']]):
        raise ValueError('control is not an unstarted seven-solve remainder')
    for r in rows:
        if (r.get('rejection_reasons')!=['fluxes_not_co_rotating']
                or r.get('verdict')!='ABOVE_GATE' or not r.get('offgrid_pass')
                or not r.get('surface_verified') or not r.get('tidal_converged')
                or not r.get('independent_rotation_present')
                or r.get('geometric_and_matter_flux_aligned') is not False
                or r.get('offgrid_sampling')!=[49,21]
                or r.get('newton_updates',0)<1 or r.get('newton',np.inf)>1e-9
                or abs(r.get('J_measured',np.inf)-target)>1e-6):
            raise ValueError('coupled arm has failures beyond the orientation target')
    checked=[dict(r,verdict='PASS') for r in rows]
    ok,_=consistent(checked,'X_full')
    drift=max(abs(rows[-1][k]-rows[-2][k])/max(abs(rows[-1][k]),1e-12)
        for k in ('E_b','Q_b','J_measured','ring_peak_radius','equatorial_shift_over_lapse_max'))
    if not ok or not np.isfinite(drift) or drift>1e-6:
        raise ValueError('coupled observables lack three-grid agreement')
    _,base=load_seed(parent/'static_reference.npz');reference=base['diagnostics']
    if reference.get('verdict')!='PASS' or not reference.get('offgrid_pass'):
        raise ValueError('missing checked static reference')
    if old['solves']+len(ladders[1])+3!=p['max_solves']:
        raise ValueError('remaining control exceeds the original total solve budget')
    return seeds[1],target,ladders[1],rows[-1],reference


def run_remaining_control(p,out,parent):
    from grteclyn_stationary.validation.resolution import check_candidate, save_checked
    from grteclyn_stationary.studies.runner import write_json
    from grteclyn_stationary.studies.validation import validate
    (state,cfg),target,targets,ring,reference=read_remaining_control(p,parent)
    out=Path(out);out.mkdir(parents=True,exist_ok=False);parent=Path(parent)
    with (parent/'control_arm_started.json').open('x') as f:
        json.dump(dict(output=str(out),target_J=target,max_remaining_solves=7),f)
    write_json(out/'plan.json',p)
    inputs=['plan.json','outcome.json','ring/result.json','ring/diagnostic_240x40.npz','static_reference.npz']
    write_json(out/'code.json',dict(commit=source_revision(),
        parent=str(parent),parent_sha256={k:hashlib.sha256((parent/k).read_bytes()).hexdigest() for k in inputs}))
    outcome=dict(original_solves=7,solves_this_arm=0,total_solves=7,target_J=target,
        original_co_rotation_target_reached=False,coupled_orientation='counter_rotating',
        coupled_physical_checks_passed=True,control_accepted=False,stability='not_assessed')
    write_json(out/'outcome.json',outcome)
    state,cfg,steps,ok=continue_j(state,cfg,targets,p,out/'control_continuation')
    outcome.update(solves_this_arm=len(steps),total_solves=7+len(steps))
    if not ok:
        outcome['reason']='control_continuation_failed';write_json(out/'outcome.json',outcome);return 2
    def validator(s,c,r):
        return validate(s,c,r,reference_peak=reference['tidal_peak'],tidal_factor=4.,independent_points=[49,21])
    result,state=check_candidate(state,cfg,[tuple(g) for g in p['grids']],('minimal_area',16*np.pi),4.,
        out/'control',validator=validator,score_key='X_full',perturb_seed=True)
    outcome['solves_this_arm']+=len(result['records']);outcome['total_solves']=7+outcome['solves_this_arm']
    if not result['passed']:
        outcome['reason']='control_validation_failed';write_json(out/'outcome.json',outcome);return 2
    control=result['records'][-1]
    match=abs(control['J_measured']-ring['J_measured'])/max(1.,abs(target))
    if match>1e-6:
        outcome['reason']='total_J_mismatch';write_json(out/'outcome.json',outcome);return 2
    save_checked(out/'control_accepted.npz',state,cfg,dict(pin=['minimal_area',16*np.pi]),result)
    outcome.update(control_accepted=True,X_ring=ring['X_full'],X_control=control['X_full'],
        X_static=reference['X_full'],static_fractional_reduction=1-ring['X_full']/reference['X_full'],
        matched_spin_fractional_reduction=1-ring['X_full']/control['X_full'],total_J_match_error=match,
        reason='original_control_complete_counter_rotating_diagnostic')
    write_json(out/'outcome.json',outcome);return 0


def run(p,out):
    from grteclyn_stationary.workflows.common import save_trial
    from grteclyn_stationary.validation.resolution import check_candidate, save_checked
    from grteclyn_stationary.studies.runner import write_json
    from grteclyn_stationary.studies.validation import validate
    from grteclyn_stationary.studies.diagnostics import tidal_envelope
    seeds,target,ladders=read_seeds(p);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    pin=('minimal_area',16*np.pi);grids=[tuple(g) for g in p['grids']]
    write_json(out/'plan.json',p)
    write_json(out/'code.json',dict(commit=source_revision()))
    static=bridge.ellis(2.,*grids[0]);basecfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    peak=tidal_envelope(static)['tidal_peak']
    reference=validate(static,basecfg,dict(verdict='PASS'),reference_peak=peak,
        tidal_factor=4.,independent_points=[49,21])
    save_trial(out/'static_reference.npz',static,basecfg,reference,pin)
    outcome=dict(target_J=target,solves=0,ring_accepted=False,control_accepted=False,
                 stability='not_assessed',matter_may_overlap_throat=True)
    if reference['verdict']!='PASS':
        outcome['reason']='static_reference_failed';write_json(out/'outcome.json',outcome);return 2
    def validator(s,c,r):
        r=validate(s,c,r,reference_peak=peak,tidal_factor=4.,
            energy_budget=1. if c.get('matter') else None,independent_points=[49,21])
        if c.get('matter'):
            r.update(bridge.ring_geometry(s,c),**bridge.throat_ergoregion(s),**rotation_diagnostics(s,r))
            resolved=s['Z'][abs(s['Z'])>1e-5*np.max(abs(s['Z']))]
            if r['Q_b']<=1e-8 or not len(resolved) or np.min(resolved)*np.max(resolved)<0:
                r['rejection_reasons'].append('nonzero_nodeless_ring')
            if not r['independent_rotation_present']:
                r['rejection_reasons'].append('no_independent_wormhole_rotation')
            if not r['geometric_and_matter_flux_aligned']:
                r['rejection_reasons'].append('fluxes_not_co_rotating')
            if r['rejection_reasons']:r['verdict']='ABOVE_GATE'
        return r
    results=[]
    for label,(s,cfg),targets in zip(('ring','control'),seeds,ladders):
        s,cfg,steps,ok=continue_j(s,cfg,targets,p,out/(label+'_continuation'))
        outcome['solves']+=len(steps)
        if not ok:
            outcome['reason']=label+'_continuation_failed';write_json(out/'outcome.json',outcome);return 2
        result,s=check_candidate(s,cfg,grids,pin,4.,out/label,
                   validator=validator,score_key='X_full',perturb_seed=True)
        outcome['solves']+=len(result['records'])
        if not result['passed']:
            outcome['reason']=label+'_validation_failed';write_json(out/'outcome.json',outcome);return 2
        rows=result['records']
        keys=('E_b','Q_b','J_measured','ring_peak_radius','equatorial_shift_over_lapse_max') if label=='ring' else ('J_measured',)
        drift=max(abs(rows[-1][k]-rows[-2][k])/max(abs(rows[-1][k]),1e-12) for k in keys)
        if not np.isfinite(drift) or drift>1e-6:
            outcome['reason']=label+'_observable_refinement_failed';write_json(out/'outcome.json',outcome);return 2
        save_checked(out/(label+'_accepted.npz'),s,cfg,dict(pin=list(pin)),result)
        outcome[label+'_accepted']=True;results.append(rows[-1])
        write_json(out/'outcome.json',outcome)
    ring,control=results
    match=abs(ring['J_measured']-control['J_measured'])/max(1.,abs(target))
    outcome['total_J_match_error']=match
    if match>1e-6:
        outcome['reason']='total_J_mismatch';write_json(out/'outcome.json',outcome);return 2
    outcome.update(X_ring=ring['X_full'],X_control=control['X_full'],X_static=reference['X_full'],
        static_fractional_reduction=1-ring['X_full']/reference['X_full'],
        matched_spin_fractional_reduction=1-ring['X_full']/control['X_full'],
        J_geometric_flux_xi0=ring['J_geometric_flux_xi0'],
        relative_end_angular_velocity=ring['relative_end_angular_velocity'],
        reason='paired_validation_complete')
    write_json(out/'outcome.json',outcome);return 0


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--config',required=True)
    ap.add_argument('--out',required=True);ap.add_argument('--gpu',type=int);ap.add_argument('--run',action='store_true')
    ap.add_argument('--control-only-from',type=Path)
    a=ap.parse_args();p=json.loads(Path(a.config).read_text());seeds,target,ladders=read_seeds(p)
    if a.control_only_from:
        _,target,targets,_,_=read_remaining_control(p,a.control_only_from)
        if not a.run:
            print(json.dumps(dict(status='PREPARED_ONLY',target_J=target,planned_solves=len(targets)+3,
                original_solves=7,total_solves=14,mode='original_unstarted_control')));return 0
    if not a.run:
        print(json.dumps(dict(status='PREPARED_ONLY',target_J=target,J_ladders=ladders,
            planned_solves=sum(map(len,ladders))+6,ring_amplitude=seeds[0][1]['amplitude'])));return 0
    if a.gpu is None:ap.error('explicit GPU required')
    from grteclyn_stationary.numerics.device import select_device
    from grteclyn_stationary.numerics.device import configure_jax
    select_device(a.gpu,256);jax=configure_jax()
    if jax.default_backend()!='gpu' or not jax.config.x64_enabled:raise RuntimeError('CUDA float64 required')
    print('devices:',jax.devices(),'float64:',jax.config.x64_enabled,flush=True)
    if a.control_only_from:return run_remaining_control(p,a.out,a.control_only_from)
    return run(p,a.out)

if __name__=='__main__':raise SystemExit(main())
