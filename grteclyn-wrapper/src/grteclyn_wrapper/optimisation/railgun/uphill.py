"""Matched-energy uphill transport: finite endpoint selection, not escape."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np


def validate_config(config):
    if (config['launch_z']!=1. or config['target_z']!=-10. or config['spin']!=.001
            or config['energy_margin']!=1e-7 or config['max_tracks']!=32
            or config['rtols']!=[2e-11,2e-12] or config['max_step']!=.4
            or not 0<config['duration']<=250.):
        raise ValueError('bounded z=1 to -10 uphill controls and fixed accuracy required')
    return dict(tracks=32,launch_z=1.,target_z=-10.,numerical_execution=False,
                scope='Finite endpoint versus turnaround; no asymptotic escape claim.')


def energy_regimes(thresholds,margin):
    """Shared energies bracket measured spin-dependent endpoint thresholds."""
    values=np.array([thresholds[k] for k in ('zero','positive','negative')],float)
    if not np.isfinite(values).all() or not np.isfinite(margin) or margin<=0:
        raise ValueError('finite rest-energy thresholds and positive margin required')
    return dict(requested_offset=float(thresholds['zero']+margin),
                between_spin_thresholds=float((thresholds['positive']+thresholds['negative'])/2),
                below_all=float(np.min(values)-margin),above_all=float(np.max(values)+margin))


def run_uphill(source,profile,config,directory):
    validate_config(config)
    from scipy.optimize import brentq
    from .workflow import load_state,write_json
    from .geometry import RingGeometry
    from .corridor import CartesianCorridor
    from .transport import MPDSystem,matched_controls
    from .transit import strict_gates
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    prior=json.loads((Path(profile)/'outcome.json').read_text())
    pm=json.loads((Path(profile)/'manifest.json').read_text())
    if not prior.get('accepted') or pm['source_sha256']!=digest:
        raise ValueError('accepted core profile for this exact source required')
    p,u,metadata=load_state(source)
    if not metadata.get('validated') or len(p.fields)!=1 or p.fields[0].winding!=1:
        raise ValueError('accepted pure k=1 background required')
    if p.jax.devices()[0].platform!='gpu' or not p.jax.config.jax_enable_x64:
        raise ValueError('GPU float64 execution required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    manifest=dict(config=config,source_sha256=digest,profile_manifest=pm,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),platform='gpu',float64=True)
    write_json(directory/'manifest.json',manifest)
    geometry=CartesianCorridor(RingGeometry(p,u),radius=pm['corridor_radius'],degree=pm['corridor_degree'])
    certificate=geometry.certify();write_json(directory/'corridor.json',certificate)
    if not certificate['accepted']:
        result=dict(accepted=False,reason='core_certification');write_json(directory/'outcome.json',result);return result
    system=MPDSystem(geometry.metric,regular_origin=True)
    xp=p.xp;reflection=xp.diag(xp.array([1.,1.,-1.,1.]))
    reverse=MPDSystem(lambda x:reflection@geometry.metric(reflection@x)@reflection,regular_origin=True)
    spins=dict(zero=0.,positive=config['spin'],negative=-config['spin'])
    endpoint=[0.,0.,config['target_z']];position=[0.,0.,config['launch_z']]
    thresholds={k:system.invariants(system.initial_state(endpoint,spin=s,speed=0.))['energy'] for k,s in spins.items()}
    energies=energy_regimes(thresholds,config['energy_margin'])
    write_json(directory/'thresholds.json',dict(rest_energy=thresholds,energies=energies,
        interpretation='Measured full spin-corrected Killing energy of a resting body at z=-10; predictions are checked by actual tracks.'))
    records={};all_ok=True;tracks_run=0
    for regime,energy in energies.items():
        speed=brentq(lambda v:system.invariants(system.initial_state(position,speed=v))['energy']-energy,-.95,0.,xtol=1e-14)
        states=matched_controls(system,position,spin=config['spin'],speed=speed)
        transformed=states['positive'].copy();d=np.diag([1.,1.,-1.,1.])
        transformed[:4]=d@transformed[:4];transformed[4:8]=d@transformed[4:8]
        transformed[8:]=(d@transformed[8:].reshape(4,4)@d).ravel();states['reversed']=transformed
        for rk,rtol in enumerate(config['rtols']):
            controls={}
            for label,state in states.items():
                engine=reverse if label=='reversed' else system
                track=engine.integrate(state,duration=config['duration'],rtol=rtol,atol=rtol*.01,
                    max_step=config['max_step'],inner_radius=0.,target_z=config['target_z'],samples=1001,
                    stop_at_turnaround=True)
                tracks_run+=1;name=f'{regime}_rk{rk}_{label}'
                np.savez_compressed(directory/f'{name}.npz',time=track['time'],state=track['state'])
                gates=strict_gates(track)
                threshold=thresholds['positive' if label=='reversed' else label]
                marginal=abs(energy-threshold)<1e-10
                row=dict(gates=gates,stop=track['stop'],energy=energy,launch=track['invariants'][0],
                    final=track['invariants'][-1],proper_time=float(track['time'][-1]),
                    coordinate_time=float(track['state'][-1,0]),final_z=float(track['state'][-1,3]),
                    endpoint_energy_margin=float(energy-threshold),marginal=bool(marginal),
                    classification='marginal' if marginal else 'transmitted' if track['stop']=='target_z'
                        else 'reflected' if track['stop']=='turnaround' else 'unresolved')
                all_ok=all_ok and gates['accepted'] and track['stop'] in ('target_z','turnaround')
                controls[label]=row;write_json(directory/f'{name}.json',row)
                print(f'[uphill] {name}: {row["classification"]}, z={row["final_z"]:.10f}, strict={gates["accepted"]}',flush=True)
            a,b=controls['positive'],controls['reversed']
            symmetry=max(abs(a['coordinate_time']-b['coordinate_time']),abs(a['final_z']-b['final_z']))
            all_ok=all_ok and symmetry<1e-8 and a['classification']==b['classification']
            records[f'{regime}_rk{rk}']=dict(controls=controls,reversal_error=symmetry)
            write_json(directory/'progress.json',records)
    comparisons={};selection=[]
    for regime in energies:
        a,b=[records[f'{regime}_rk{i}']['controls'] for i in range(2)]
        errors={k:dict(time=abs(a[k]['coordinate_time']-b[k]['coordinate_time']),
                      final_z=abs(a[k]['final_z']-b[k]['final_z']),
                      same_classification=a[k]['classification']==b[k]['classification']) for k in spins}
        comparisons[regime]=errors
        all_ok=all_ok and all(r['time']<1e-7 and r['final_z']<1e-8 and r['same_classification'] for r in errors.values())
        if {b[k]['classification'] for k in ('positive','negative')}=={'transmitted','reflected'}:
            # Require a margin larger than the observed conservation error;
            # an unresolved or marginal event cannot become a selection claim.
            safe=all(abs(b[k]['endpoint_energy_margin'])>10*b[k]['gates']['normalised_drift']['energy']
                     for k in ('positive','negative'))
            if safe:selection.append(regime)
    result=dict(accepted=bool(all_ok and tracks_run==config['max_tracks']),tracks=tracks_run,
        thresholds=thresholds,energies=energies,records=records,rk_comparisons=comparisons,
        spin_selective_finite_transit=bool(all_ok and selection),selection_regimes=selection,
        seconds=time.monotonic()-started,
        scope='Finite uphill z=+1 to z=-10 transit or first turnaround. This does not establish escape, long-term trapping or energy gain.',
        stability='not_assessed')
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=validate_config(config)
    if args.gpu<0:parser.error('GPU must be nonnegative')
    if args.dry_run:print(json.dumps(plan,indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform');os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if run_uphill(args.source,args.profile,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
