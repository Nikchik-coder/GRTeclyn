"""Bounded fresh recovery of the gapped k2=-12 state with cubic dragging falloff."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np


def preflight(source,config):
    source=Path(source)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=config['source_sha256']:raise ValueError('correction-state checksum mismatch')
    with np.load(source,allow_pickle=False) as data:meta=json.loads(str(data['metadata']))
    original=json.loads(source.with_suffix('.json').read_text())
    if (meta.get('model')!='canonical_regular_centre' or meta.get('validated') is not False
            or meta['target_j']!=0. or meta['length']!=50. or [meta['nx'],meta['ny']]!=[256,20]
            or [f['winding'] for f in meta['fields']]!=[1,-12]
            or original.get('reasons')!=['angular_momentum_balance']):
        raise ValueError('original corrected 256x20 flux rejection required')
    fixed=dict(grids=[[192,16],[224,18],[256,20]],max_solves=3,max_iter=30,newton_tol=1e-12,
               equation_tol=1e-8,tail_tol=1e-6,observable_tol=1e-6,edge_tol=1e-6,
               relative_density_cutoff=1e-6,channel_half_height=10.,perturbation=0.)
    if any(config.get(k)!=v for k,v in fixed.items()):raise ValueError('fixed three-solve falloff recovery budget and unchanged gates required')
    return dict(metadata=meta,source_sha256=digest,max_solves=3,
                grids=config['grids'],numerical_execution=False,
                representation='w=(1-s)^3 H; two omitted outer PDE rows checked independently')


def run_recovery(source,config,directory):
    plan=preflight(source,config)
    from .workflow import load_state as load_canonical,write_json
    from .dragging_falloff import FactoredDraggingProblem,save_state,validate,MODEL
    from .annular_recovery import acceptance,measure_channel
    from .gap import equatorial_densities,annular_gap
    from ..solver.newton import newton
    old,old_u,_=load_canonical(source)
    if old.jax.devices()[0].platform!='gpu':raise ValueError('GPU required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    write_json(directory/'manifest.json',dict(config=config,source_sha256=plan['source_sha256'],
        source_model='canonical_regular_centre',output_model=MODEL,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        platform='gpu',float64=bool(old.jax.config.jax_enable_x64),stability='not_assessed',
        tau='Infinity and two outermost w-PDE rows replaced by three zero auxiliary rows; omitted PDEs tested.'))
    previous=old,old_u;records=[];started=time.monotonic()
    radius=np.loadtxt(Path('results/railgun/studies/annular-recovery-k12/grid_192x16_density.tsv'),usecols=0)
    for nx,ny in config['grids']:
        tick=time.monotonic();name=f'grid_{nx}x{ny}'
        p=FactoredDraggingProblem(old.fields,nx=nx,ny=ny,length=50.,target_j=0.)
        guess=p.transfer(*previous,perturb=0.)
        save_state(directory/f'{name}_initial.npz',p,guess)
        print(f'[falloff] solve {nx}x{ny}, unknowns={p.n_unknowns}',flush=True)
        value,info=newton(p.residual,p.jacobian,guess,tol=1e-12,max_iter=30,min_updates=2,verbose=True)
        save_state(directory/f'{name}.npz',p,value)
        try:
            row=validate(p,value,info,equation_tol=1e-8,tail_tol=1e-6)
            base,physical=p.physical_vector(value)
            meta=dict(nx=nx,ny=ny,length=50.,fields=[f.to_dict() for f in p.fields])
            density=equatorial_densities(meta,physical,radius)
            gap=annular_gap(radius,density,relative_cutoff=1e-6)
            np.savetxt(directory/f'{name}_density.tsv',np.column_stack((radius,density.T)),
                       delimiter='\t',header='rho\tinner_density\touter_density')
            row['annular_gap']=gap
            row['finite_height_channel']=measure_channel(meta,physical,gap,10.,directory,name)
            if not gap['accepted']:row['reasons'].append('annular_gap')
            if not row['finite_height_channel']['accepted']:row['reasons'].append('finite_height_channel')
            row['verdict']='PASS' if not row['reasons'] else 'REJECT'
            json.dumps(row,allow_nan=False)
        except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as error:
            row=dict(grid=[nx,ny],verdict='REJECT',reasons=[str(error)])
        row['seconds']=time.monotonic()-tick;records.append(row)
        write_json(directory/f'{name}.json',row)
        print(f'[falloff] {nx}x{ny}: {row["verdict"]}, reasons={row["reasons"]}',flush=True)
        if row['verdict']!='PASS':break
        previous=p,value;p.jax.clear_caches()
    result=acceptance(records,tolerance=1e-6)
    result.update(records=records,solves=len(records),seconds=time.monotonic()-started,
                  stability='not_assessed',scope='Coupled stationary annular field; no particle passage or stability claim.')
    if result['accepted']:save_state(directory/'accepted.npz',p,value,validated=True)
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config',type=Path)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=preflight(args.source,config)
    if args.gpu<0:parser.error('nonnegative GPU required')
    if args.dry_run:plan.pop('metadata');print(json.dumps(plan,indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform');os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if run_recovery(args.source,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
