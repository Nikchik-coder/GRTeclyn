"""Bounded physical amplitude continuation from an accepted ring–wormhole.

Continuation iterates are diagnostic. Only the final independent three-grid
checks can qualify a solution; energy and exterior-ring gates stay unchanged.
"""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
from grteclyn_stationary.ringwormhole import workflow as bridge


def validate_plan(plan):
    bridge.validate_plan(plan['target'])
    anchor=plan.get('continuation_anchor','outer')
    if anchor not in ('outer','throat'):
        raise ValueError('unknown amplitude continuation anchor')
    if (plan['max_attempts'] != (8 if anchor=='throat' else 32) or plan['amplitude_growth'] != 1.2
            or plan['min_amplitude_step'] != 1e-5 or plan['min_damping'] != 1/4096
            or len(plan['restart_sha256']) != 64):
        raise ValueError('undeclared continuation budget')


def initial_state(plan):
    from grteclyn_stationary.workflows.common import load_seed, matter_anchor
    validate_plan(plan)
    path=Path(plan['restart_source'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=plan['restart_sha256']:
        raise ValueError('restart hash mismatch')
    state,meta=load_seed(path)
    old=meta.get('config',meta)
    expected=dict(m=0.,q=[0.,0.,0.],gamma=0.,rotation_control='nonrotating_ends',
                  matter='winding',winding_k=1,matter_mass=1.)
    if any(old.get(k)!=v for k,v in expected.items()) or state['omega']!=0.:
        raise ValueError('restart model mismatch')
    if meta.get('pin')!=['minimal_area',16*np.pi]:
        raise ValueError('restart area mismatch')
    mapped,config=bridge.prepare_seed(plan['target'])
    target=config['amplitude']
    if plan.get('continuation_anchor')=='throat':
        config['zeta_anchor_xi']=0.
        target=matter_anchor(mapped['Z'],mapped['sx'],config)
    config['amplitude']=matter_anchor(state['Z'],state['sx'],config)
    if not 0<config['amplitude']<target:
        raise ValueError('continuation must increase a positive amplitude')
    return state,config,target


def next_amplitude(current,step,target):
    return min(target,current+step)


def trace(state,config,target,plan,directory,solve,save,release,diagnose):
    """Failed steps never replace the last converged physical solution."""
    directory=Path(directory);directory.mkdir()
    current=config['amplitude'];step=current*(plan['amplitude_growth']-1)
    pin=('minimal_area',16*np.pi);nx,ny=plan['target']['grids'][0]
    records=[]
    for attempt in range(plan['max_attempts']):
        trial=next_amplitude(current,step,target);cfg=dict(config,amplitude=trial)
        start=time.monotonic()
        try:
            candidate,row=solve(state,cfg,nx,ny,pin,4.,max_iter=24,newton_tol=1e-14,
                min_damping=plan['min_damping'],verbose=True,
                failure_path=directory/f'failed_{attempt:02d}.npz')
            # Newton convergence alone does not establish a physical branch.
            if row['verdict']!='PASS':
                save(directory/f'unqualified_{attempt:02d}.npz',candidate,cfg,row,pin)
                raise RuntimeError('continuation collocation constraints failed')
            row.update(diagnose(candidate,cfg))
            save(directory/f'step_{attempt:02d}.npz',candidate,cfg,row,pin)
            state,config,current=candidate,cfg,trial
            step=min(step*1.4,current*(plan['amplitude_growth']-1))
            row.update(attempt=attempt,amplitude=trial,continuation_converged=True)
        except (RuntimeError,ValueError,FloatingPointError) as err:
            row=dict(attempt=attempt,amplitude=trial,continuation_converged=False,error=str(err))
            step*=.5
        row['seconds']=time.monotonic()-start;records.append(row)
        with (directory/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        print('continuation: '+json.dumps(row),flush=True)
        release()
        if current==target:return state,config,records,True
        if step<plan['min_amplitude_step']:break
    return state,config,records,False


def run(plan,out):
    from grteclyn_stationary.workflows.common import solve_trial, save_trial
    from grteclyn_stationary.validation.resolution import check_candidate, save_checked
    from grteclyn_stationary.studies.runner import release_solver, write_json
    from grteclyn_stationary.studies.validation import validate
    from grteclyn_stationary.studies.diagnostics import tidal_envelope
        state,config,target=initial_state(plan)
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    write_json(out/'plan.json',plan)
    write_json(out/'code.json',dict(commit=source_revision()))
    baseline=bridge.ellis(2.,*plan['target']['grids'][0]);pin=('minimal_area',16*np.pi)
    peak=tidal_envelope(baseline)['tidal_peak']
    base=validate(baseline,dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.),dict(verdict='PASS'),
                  reference_peak=peak,tidal_factor=4.,independent_points=[49,21])
    save_trial(out/'static_reference.npz',baseline,dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.),base,pin)
    if base['verdict']!='PASS':
        write_json(out/'outcome.json',dict(reason='static_reference_failed'));return 2
    def diagnose(s,c):return dict(bridge.ring_geometry(s,c),**bridge.throat_ergoregion(s))
    state,config,steps,reached=trace(state,config,target,plan,out/'continuation',
                                    solve_trial,save_trial,release_solver,diagnose)
    outcome=dict(target_amplitude=target,last_amplitude=config['amplitude'],
        continuation_attempts=len(steps),target_reached=reached,ring_accepted=False,
        throat_ergoregion_resolved=False,stability='not_assessed',matched_control_status='not_run')
    if not any(r['continuation_converged'] for r in steps):
        outcome['reason']='continuation_target_not_reached'
        write_json(out/'outcome.json',outcome);return 2
    # Qualify the strongest converged point even if a fold blocks the target.
    # target_reached remains explicit; a weaker point cannot inherit the target.
    save_trial(out/'validation_seed.npz',state,config,dict(verdict='UNQUALIFIED'),pin)
    def validator(s,c,r):
        r=validate(s,c,r,reference_peak=peak,tidal_factor=4.,energy_budget=1.,independent_points=[49,21])
        r.update(diagnose(s,c));resolved=s['Z'][abs(s['Z'])>1e-5*np.max(abs(s['Z']))]
        if r['Q_b']<=1e-8 or not len(resolved) or np.min(resolved)*np.max(resolved)<0:
            r['rejection_reasons'].append('nonzero_nodeless_ring')
        if not r['ring_outside_throat']:r['rejection_reasons'].append('ring_does_not_surround_throat')
        if r['reflection_defect']>1e-7:r['rejection_reasons'].append('reflection_symmetry')
        if abs(r['J_b']/2-r['J_measured'])>1e-6*max(1.,abs(r['J_measured'])):
            r['rejection_reasons'].append('symmetric_angular_momentum_balance')
        if r['rejection_reasons']:r['verdict']='ABOVE_GATE'
        return r
    result,state=check_candidate(state,config,[tuple(g) for g in plan['target']['grids']],pin,4.,
                    out/'ring',validator=validator,score_key='X_full',perturb_seed=True)
    rows=result['records'];outcome['validation_solves']=len(rows)
    if result['passed']:
        drift=max(abs(rows[-1][k]-rows[-2][k])/max(abs(rows[-1][k]),1e-12)
            for k in ('E_b','Q_b','J_measured','ring_peak_radius','equatorial_shift_over_lapse_max'))
        outcome['ring_observable_relative_drift']=drift
        if drift<=1e-6:
            config=dict(config,J=rows[-1]['J_measured'])
            save_checked(out/'accepted_ring.npz',state,config,dict(pin=list(pin)),result)
            outcome.update(ring_accepted=True,X_ring=rows[-1]['X_full'],X_static=base['X_full'],
                static_fractional_reduction=1-rows[-1]['X_full']/base['X_full'],
                **bridge.throat_ergoregion_convergence(rows))
    outcome['reason']='throat_ergoregion_validated' if outcome['throat_ergoregion_resolved'] else 'target_not_qualified'
    write_json(out/'outcome.json',outcome)
    return 0 if outcome['throat_ergoregion_resolved'] else 2


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',required=True);p.add_argument('--out',required=True)
    p.add_argument('--gpu',type=int);p.add_argument('--run',action='store_true');a=p.parse_args()
    plan=json.loads(Path(a.config).read_text());s,c,target=initial_state(plan)
    if not a.run:
        print(json.dumps(dict(status='PREPARED_ONLY',start_amplitude=c['amplitude'],
             target_amplitude=target,max_attempts=plan['max_attempts'],
             validation_grids=plan['target']['grids'])));return 0
    if a.gpu is None:p.error('explicit GPU required')
    from grteclyn_stationary.numerics.device import select_device
    from grteclyn_stationary.numerics.device import configure_jax
    select_device(a.gpu,256);jax=configure_jax()
    if jax.default_backend()!='gpu' or not jax.config.x64_enabled:raise RuntimeError('CUDA float64 required')
    print('devices:',jax.devices(),'float64:',jax.config.x64_enabled,flush=True)
    return run(plan,a.out)

if __name__=='__main__':raise SystemExit(main())
