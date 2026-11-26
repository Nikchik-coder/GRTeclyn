"""Bounded linear-mode screening for a concentric annular low-density channel.

This screens possible seeds on a fixed accepted inner-ring metric. It never
labels a two-field configuration self-consistent or exports an accepted state.
Nonlinear backreaction and three-grid recovery remain separate requirements.
"""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np


def run_screen(source,config,directory):
    from grteclyn_stationary.railgun.workflow import load_state, save_state, write_json
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.model import ScalarField
    from grteclyn_stationary.railgun.continuation import transfer_fields
    from grteclyn_stationary.railgun.counter_rotation import linear_rotating_seed
    from grteclyn_stationary.railgun.diagnostics import observables
    from grteclyn_stationary.railgun.gap import annular_gap, equatorial_densities
    old,old_u,meta=load_state(source)
    if not meta.get('validated') or len(old.fields)!=1 or old.fields[0].winding!=1:
        raise ValueError('an accepted pure k=1 inner ring is required')
    if old.jax.devices()[0].platform!='gpu':raise ValueError('GPU execution required')
    grids=config['grids'];windings=config['outer_windings']
    if (len(grids)!=2 or any(len(g)!=2 for g in grids)
            or grids[1][0]<=grids[0][0] or grids[1][1]<=grids[0][1]
            or not windings or len(windings)*2>int(config['max_eigenproblems'])
            or any(isinstance(k,bool) or int(k)!=k or k>=0 for k in windings)
            or config['relative_density_cutoff']!=1e-6):
        raise ValueError('two increasing grids, negative integer windings, finite budget and fixed 1e-6 cutoff required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    mass=observables(old,old_u)['M_ADM_estimate']
    charge=float(np.asarray(old.charge_integrals(old_u))[0])
    started=time.monotonic();records=[]
    manifest=dict(config=config,source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        commit=source_revision(),
        platform='gpu',float64=bool(old.jax.config.jax_enable_x64),
        stage='fixed_background_linear_screen',self_consistent=False)
    write_json(directory/'manifest.json',manifest)
    for winding in windings:
        # A scale estimate chooses an anchor only; the full rotating 2D
        # eigenproblem supplies the actual mode and frequency.
        anchor=max(10.,abs(winding)*(abs(winding)+1)/mass)
        upper=max(120.,4*anchor)
        r=np.r_[np.linspace(.001,50.,2501),np.geomspace(50.02,upper,5001)]
        inner_density=equatorial_densities(meta,old_u,r)[0]
        for nx,ny in grids:
            tick=time.monotonic();name=f'k{abs(winding)}_{nx}x{ny}'
            field=ScalarField(winding=winding,amplitude=.001,anchor_radius=anchor)
            p=RingProblem([old.fields[0],field],nx=nx,ny=ny,length=config['radial_scale'])
            try:
                seed,mode=linear_rotating_seed(p,transfer_fields(p,old,old_u),eigensolver='cusolver')
                arrays,frequencies=p.unpack(seed)
                mode_charge=float(np.asarray(p.charge_integrals(seed))[1])
                if not np.isfinite(mode_charge) or mode_charge<=0:raise RuntimeError('invalid bound-mode charge')
                scale=np.sqrt(charge/(abs(winding)*mode_charge))
                arrays['q1']*=scale;seed=p.pack(arrays,frequencies)
                screen_meta=dict(nx=nx,ny=ny,length=p.length,fields=[f.to_dict() for f in p.fields])
                outer_density=equatorial_densities(screen_meta,seed,r)[1]
                gap=annular_gap(r,np.array([inner_density,outer_density]),relative_cutoff=1e-6)
                row=dict(name=name,winding=winding,grid=[nx,ny],mode=mode,gap=gap,
                    charge_scaled_to_cancel_fixed_inner_J=True,
                    self_consistent=False,second_pin=field.amplitude*scale,
                    target_inner_charge=charge,quadratic_eigensolver='cusolver_gpu',
                    stage='fixed_background_linear_screen',seconds=time.monotonic()-tick)
                # Store the scaled pin consistently in the portable seed.
                scaled=RingProblem([old.fields[0],replace(field,amplitude=field.amplitude*scale)],
                         nx=nx,ny=ny,length=p.length)
                save_state(directory/f'{name}.npz',scaled,seed,validated=False)
                np.savetxt(directory/f'{name}_density.tsv',np.column_stack([r,inner_density,outer_density]),
                           delimiter='\t',header='rho\tinner_density\touter_mode_density')
                print(f'[gap-screen] {name} gap={gap["accepted"]} width={gap["gap_width"]}',flush=True)
            except (RuntimeError,ValueError,np.linalg.LinAlgError) as error:
                row=dict(name=name,winding=winding,grid=[nx,ny],stage='fixed_background_linear_screen',
                         self_consistent=False,error=str(error),seconds=time.monotonic()-tick)
                print(f'[gap-screen] {name} unresolved: {error}',flush=True)
            records.append(row);write_json(directory/f'{name}.json',row)
    candidates=[]
    for winding in windings:
        pair=[r for r in records if r['winding']==winding]
        if len(pair)!=2 or any(not r.get('gap',{}).get('accepted') for r in pair):continue
        frequency_drift=abs(pair[0]['mode']['frequency']/pair[1]['mode']['frequency']-1)
        edge_drift=max(abs(pair[0]['gap'][k]-pair[1]['gap'][k])/max(1.,abs(pair[1]['gap'][k]))
                       for k in ('inner_ring_outer_radius','outer_ring_inner_radius'))
        if frequency_drift<=config['screen_frequency_tol'] and edge_drift<=config['screen_edge_tol']:
            candidates.append(dict(winding=winding,seed=pair[1]['name']+'.npz',
                                   frequency_relative_drift=frequency_drift,edge_relative_drift=edge_drift,
                                   gap_width=pair[1]['gap']['gap_width']))
    outcome=dict(screen_completed=True,accepted_background=False,self_consistent=False,
                 candidates=candidates,records=records,eigenproblems_attempted=len(records),
                 seconds=time.monotonic()-started)
    write_json(directory/'outcome.json',outcome);return outcome


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if args.gpu<0:parser.error('GPU must be nonnegative')
    if args.dry_run:print(json.dumps(dict(config=config,numerical_execution=False),indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from grteclyn_stationary.numerics.device import select_device
    select_device(args.gpu,128);run_screen(args.source,config,args.out);return 0


if __name__=='__main__':raise SystemExit(main())
