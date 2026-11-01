"""Bounded bound-mode starts for discrete-winding mixed-mass and odd branches.

The accepted k=1 background remains in field 0. A new field gets its own
integer winding, parity and frequency. These are linear two-field homotopy
starts, never accepted final mixed-mass or stacked geometries.
"""
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
    from .model import ScalarField
    source=Path(source)
    with np.load(source,allow_pickle=False) as data:meta=json.loads(str(data['metadata']))
    if (not meta.get('validated') or meta.get('model')!='canonical_regular_centre'
            or meta['target_j'] is not None or len(meta['fields'])!=1
            or meta['fields'][0]['winding']!=1 or meta['fields'][0]['mass']!=1.
            or meta['fields'][0]['parity']!='even' or meta['length']!=5.
            or hashlib.sha256(source.read_bytes()).hexdigest()!=config['source_sha256']):
        raise ValueError('pinned accepted pure k=1 background required')
    expected=[('mixed_inner_m2p5',2,2.5,'even',1.5),('mixed_inner_m3',2,3.,'even',1.5),
              ('stacked_odd',1,1.,'odd',6.)]
    actual=[(r['name'],r['field']['winding'],r['field']['mass'],r['field']['parity'],
             r['field']['anchor_radius']) for r in config['branches']]
    if (actual!=expected or config['grids']!=[[96,12],[128,16]] or config['max_eigenproblems']!=6
            or config['frequency_grid_tol']!=1e-6 or config['outer_candidates']!=[-6,-8]
            or any(ScalarField(**r['field']).amplitude!=1e-3 or r['field']['quartic']!=0.
                   or r['field']['sextic']!=0. for r in config['branches'])):
        raise ValueError('fixed six-mode, three-branch seed budget required')
    return dict(metadata=meta,max_eigenproblems=6,numerical_execution=False,
                scope='New fields on a fixed metric; no accepted final branch or matter gap.')


def run_screen(source,config,directory):
    plan=preflight(source,config)
    from .workflow import load_state,save_state,write_json
    from .model import ScalarField
    from .problem import RingProblem
    from .continuation import transfer_fields
    from .counter_rotation import linear_rotating_seed
    old,value,_=load_state(source)
    if old.jax.devices()[0].platform!='gpu':raise ValueError('GPU required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    write_json(directory/'manifest.json',dict(config=config,source_sha256=config['source_sha256'],
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        stage='discrete_field_homotopy_starts',accepted_background=False,platform='gpu',float64=True))
    records=[];started=time.monotonic()
    for branch in config['branches']:
        for nx,ny in config['grids']:
            name=f'{branch["name"]}_{nx}x{ny}';target=ScalarField(**branch['field'])
            p=RingProblem([old.fields[0],target],nx=nx,ny=ny,length=5.)
            row=dict(branch=branch['name'],grid=[nx,ny],linear_mode_found=False,self_consistent=False)
            try:
                seed,mode=linear_rotating_seed(p,transfer_fields(p,old,value),index=1,eigensolver='cusolver')
                save_state(directory/f'{name}.npz',p,seed,validated=False)
                row.update(linear_mode_found=True,mode=mode,seed=f'{name}.npz')
            except RuntimeError as error:row['reason']=str(error)
            records.append(row);write_json(directory/f'{name}.json',row)
            write_json(directory/'progress.json',records)
            print(f'[branch-seed] {name}: found={row["linear_mode_found"]}',flush=True)
            p.jax.clear_caches()
    branches=[]
    for branch in config['branches']:
        pair=[r for r in records if r['branch']==branch['name']]
        ok=all(r['linear_mode_found'] for r in pair);drift=None
        if ok:
            f=[r['mode']['frequency'] for r in pair];drift=abs(f[0]-f[1])/max(f)
            ok=drift<=1e-6
        branches.append(dict(name=branch['name'],resolved_linear_seed=bool(ok),frequency_relative_drift=drift))
    result=dict(screen_completed=True,eigenproblems=len(records),branches=branches,records=records,
        accepted_background=False,seconds=time.monotonic()-started,
        next='Continue the new field up and original field down; validate the pure new branch before adding any outer field.',
        scope='No fractional winding, relabelled source, final two-ring state or demonstrated annular gap.')
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
    return 0 if run_screen(args.source,config,args.out)['screen_completed'] else 2


if __name__=='__main__':raise SystemExit(main())
