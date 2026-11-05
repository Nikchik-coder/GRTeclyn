"""Bounded co-aligned scalar-matter pilot with a directly pinned xi=0 flux.

The rotation border fixes geometric Killing flux across the coordinate cut,
not total plus-end angular momentum. Each continuation point must pass the
alignment and independent physical checks before finer-grid work starts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from . import railgun_wormhole as bridge
from .ringwormhole_spin_ring import j_ladder, rotation_diagnostics, continue_j


def validate_plan(p):
    expected = dict(grids=[[210,36],[224,38],[240,40]], throat_radius=2.,
        target_geometric_flux_xi0=-.08, flux_step=.02, control_J_step=.05,
        max_solves=14, max_newton_iterations=24, independent_points=[49,21],
        energy_budget=1., tidal_factor=4., matter_may_overlap_throat=True,
        wall_seconds=3600, threads=4, memory_gib=160, checkpoints=False)
    if any(p.get(k)!=v for k,v in expected.items()):
        raise ValueError('configuration differs from the bounded direct-flux pilot')
    if p['checkpoints'] is not False:
        raise ValueError('checkpoints must remain off')
    for k in ('ring_seed','control_seed'):
        if len(p[k]['sha256'])!=64:
            raise ValueError('hash-pinned seeds required')


def read_seeds(p):
    from .exploration import load_seed, matter_anchor
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
            raise ValueError('seed lacks the validated fixed-area massless model')
        cfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=float(c.get('J_measured',c['J'])))
        if key=='ring_seed':
            if (c.get('matter')!='winding' or c.get('winding_k')!=1
                    or c.get('matter_mass')!=1. or s['omega']!=0.):
                raise ValueError('ring seed must be the symmetric matter-driven family')
            cfg.update(matter='winding',winding_k=1,matter_mass=1.,zeta_anchor_xi=0.,
                       rotation_control='J_xi0',J_xi0=0.)
            cfg['amplitude']=matter_anchor(s['Z'],s['sx'],cfg)
        else:
            if any(k in s for k in ('Z','CHI')):
                raise ValueError('control must contain no canonical matter')
            cfg['rotation_control']='J'
        seeds.append((s,cfg))
    return seeds


def validate_ring(s,c,r,p,peak):
    from .study_validation import validate
    r=validate(s,c,r,reference_peak=peak,tidal_factor=p['tidal_factor'],
        energy_budget=p['energy_budget'],independent_points=p['independent_points'])
    # Preserve the directly evaluated flux and cross-check the integral balance.
    direct=r['J_geometric_flux_xi0']
    r.update(bridge.ring_geometry(s,c),**bridge.throat_ergoregion(s),**rotation_diagnostics(s,r))
    r['J_flux_balance_error']=abs(direct-r['J_geometric_flux_xi0'])
    r['J_geometric_flux_xi0']=direct
    r['geometric_and_matter_flux_aligned']=bool(direct*r['J_matter_xi0_to_plus']>0.)
    r['J_flux_target_error']=abs(direct-c['J_xi0'])
    resolved=s['Z'][abs(s['Z'])>1e-5*np.max(abs(s['Z']))]
    reasons=r['rejection_reasons']
    if r['Q_b']<=1e-8 or not len(resolved) or np.min(resolved)*np.max(resolved)<0:
        reasons.append('nonzero_nodeless_ring')
    if not r['independent_rotation_present']:
        reasons.append('no_independent_wormhole_rotation')
    if not r['geometric_and_matter_flux_aligned']:
        reasons.append('fluxes_not_co_rotating')
    if max(r['J_flux_target_error'],r['J_flux_balance_error'])>1e-6:
        reasons.append('geometric_flux_target')
    if reasons:r['verdict']='ABOVE_GATE'
    return r


def continue_flux(s,c,p,directory,peak):
    from .exploration import solve_trial,save_trial
    from .study import release_solver
    directory.mkdir();records=[]
    for i,target in enumerate(j_ladder(0.,p['target_geometric_flux_xi0'],p['flux_step'])):
        c=dict(c,J_xi0=target);start=time.monotonic()
        try:
            s,r=solve_trial(s,c,*p['grids'][0],('minimal_area',16*np.pi),4.,
                max_iter=24,newton_tol=1e-14,min_damping=1/4096,verbose=True,
                failure_path=directory/f'failed_{i:02d}.npz')
            c['J']=r['J_measured']
            r=validate_ring(s,c,r,p,peak)
            save_trial(directory/f'step_{i:02d}.npz',s,c,r,('minimal_area',16*np.pi))
        except (RuntimeError,ValueError,FloatingPointError) as err:
            r=dict(verdict='FAILED',error=str(err))
        r.update(target_geometric_flux_xi0=target,seconds=time.monotonic()-start)
        records.append(r)
        with (directory/'steps.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
        print('flux continuation: '+json.dumps(r),flush=True);release_solver()
        if r['verdict']!='PASS':return s,c,records,False
    return s,c,records,True


def run(p,out):
    from .exploration import save_trial
    from .resolution import check_candidate,save_checked
    from .study import write_json
    from .study_validation import validate
    from .study_diagnostics import tidal_envelope
    seeds=read_seeds(p);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    pin=('minimal_area',16*np.pi);grids=[tuple(g) for g in p['grids']]
    write_json(out/'plan.json',p)
    write_json(out/'code.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()))
    static=bridge.ellis(2.,*grids[0]);cfg0=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    peak=tidal_envelope(static)['tidal_peak']
    reference=validate(static,cfg0,dict(verdict='PASS'),reference_peak=peak,
        tidal_factor=4.,independent_points=[49,21])
    save_trial(out/'static_reference.npz',static,cfg0,reference,pin)
    o=dict(solves=0,ring_accepted=False,control_accepted=False,stability='not_assessed',
           target_geometric_flux_xi0=p['target_geometric_flux_xi0'])
    def finish(reason):
        o['reason']=reason;write_json(out/'outcome.json',o);return 2
    write_json(out/'outcome.json',o)
    if reference['verdict']!='PASS':return finish('static_reference_failed')
    s,c,steps,ok=continue_flux(*seeds[0],p,out/'flux_continuation',peak)
    o['solves']=len(steps);write_json(out/'outcome.json',o)
    if not ok:return finish('flux_continuation_failed_before_refinement')
    result,s=check_candidate(s,c,grids,pin,4.,out/'ring',score_key='X_full',perturb_seed=True,
        validator=lambda s,c,r:validate_ring(s,c,r,p,peak))
    o['solves']+=len(result['records'])
    if not result['passed']:return finish('ring_validation_failed')
    ring=result['records'][-1]
    # Flux, matter and total-J must each reproduce on the finer pair.
    keys=('J_geometric_flux_xi0','J_matter_positive_half','J_measured','E_b','Q_b')
    drift=max(abs(ring[k]-result['records'][-2][k])/max(abs(ring[k]),1e-12) for k in keys)
    if not np.isfinite(drift) or drift>1e-6:return finish('ring_observable_refinement_failed')
    target=ring['J_measured'];c=dict(c,J=target)
    save_checked(out/'ring_accepted.npz',s,c,dict(pin=list(pin)),result)
    o.update(ring_accepted=True,target_J=target,X_ring=ring['X_full'],
        J_geometric_flux_xi0=ring['J_geometric_flux_xi0'],
        J_matter_xi0_to_plus=ring['J_matter_xi0_to_plus'],
        relative_end_angular_velocity=ring['relative_end_angular_velocity'])
    write_json(out/'outcome.json',o)
    cs,cc=seeds[1];targets=j_ladder(cc['J'],target,p['control_J_step'])
    if o['solves']+len(targets)+len(grids)>p['max_solves']:
        return finish('matched_control_outside_solve_budget')
    cs,cc,steps,ok=continue_j(cs,cc,targets,p,out/'control_continuation')
    o['solves']+=len(steps)
    if not ok:return finish('control_continuation_failed')
    result,cs=check_candidate(cs,cc,grids,pin,4.,out/'control',score_key='X_full',perturb_seed=True,
        validator=lambda s,c,r:validate(s,c,r,reference_peak=peak,tidal_factor=4.,independent_points=[49,21]))
    o['solves']+=len(result['records'])
    if not result['passed']:return finish('control_validation_failed')
    control=result['records'][-1];match=abs(control['J_measured']-target)/max(1.,abs(target))
    if match>1e-6:return finish('total_J_mismatch')
    save_checked(out/'control_accepted.npz',cs,cc,dict(pin=list(pin)),result)
    o.update(control_accepted=True,X_control=control['X_full'],X_static=reference['X_full'],
        static_fractional_reduction=1-ring['X_full']/reference['X_full'],
        matched_spin_fractional_reduction=1-ring['X_full']/control['X_full'],
        total_J_match_error=match,reason='co_aligned_paired_validation_complete')
    write_json(out/'outcome.json',o);return 0


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--gpu',type=int);ap.add_argument('--run',action='store_true')
    a=ap.parse_args();p=json.loads(Path(a.config).read_text());seeds=read_seeds(p)
    if not a.run:
        print(json.dumps(dict(status='PREPARED_ONLY',max_solves=p['max_solves'],
            target_geometric_flux_xi0=p['target_geometric_flux_xi0'],
            flux_ladder=j_ladder(0.,p['target_geometric_flux_xi0'],p['flux_step']),
            control_target='measured final plus-end J',ring_amplitude=seeds[0][1]['amplitude'])));return 0
    if a.gpu is None:ap.error('explicit GPU required')
    from .solver.device import select_device,configure_jax
    select_device(a.gpu,256);jax=configure_jax()
    if jax.default_backend()!='gpu' or not jax.config.x64_enabled:raise RuntimeError('CUDA float64 required')
    print('devices:',jax.devices(),'float64:',jax.config.x64_enabled,flush=True)
    return run(p,a.out)

if __name__=='__main__':raise SystemExit(main())
