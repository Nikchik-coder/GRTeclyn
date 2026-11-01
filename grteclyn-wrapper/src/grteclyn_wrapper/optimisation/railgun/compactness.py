"""Bounded amplitude continuation on the accepted pure rotating-ring branch."""
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
    with np.load(source,allow_pickle=False) as data:meta=json.loads(str(data['metadata']))
    fields=meta.get('fields',[]);amplitudes=config['amplitudes'];grids=config['grids']
    if (not meta.get('validated') or meta.get('target_j') is not None or len(fields)!=1
            or fields[0]['winding']!=1 or fields[0]['parity']!='even'
            or meta['length']!=config['length']):raise ValueError('accepted pure even k=1 source required')
    if (len(amplitudes)!=7 or not np.isfinite(amplitudes).all()
            or any(b<=a for a,b in zip([fields[0]['amplitude']]+amplitudes,amplitudes))
            or max(amplitudes)>.23 or config['max_solves']!=21
            or len(grids)!=3 or any(len(g)!=2 or g[0]>128 or g[1]>16 for g in grids)
            or any(b[0]<=a[0] or b[1]<=a[1] for a,b in zip(grids,grids[1:]))
            or config['max_iter']!=30 or config['equation_tol']!=1e-8
            or config['tail_tol']!=1e-6 or config['observable_tol']!=1e-6):
        raise ValueError('seven increasing bounded amplitudes, three grids and unchanged gates required')
    return dict(metadata=meta,max_solves=21,amplitudes=amplitudes,grids=grids,numerical_execution=False)


def run_scan(source,config,directory):
    plan=preflight(source,config)
    from .workflow import run_study,write_json
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    manifest=dict(config=config,source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),stability='not_assessed')
    write_json(directory/'manifest.json',manifest);started=time.monotonic();records=[];seed=Path(source)
    for index,amplitude in enumerate(config['amplitudes']):
        field=dict(plan['metadata']['fields'][0],amplitude=amplitude)
        study=dict(fields=[field],length=config['length'],grids=config['grids'],max_iter=30,
            min_updates=2,newton_tol=1e-12,perturbation=1e-5,equation_tol=1e-8,tail_tol=1e-6,
            observable_tol=1e-6,require_gpu=True)
        name=f'amplitude_{index+1:02d}'
        result=run_study(study,directory/name,seed_path=seed)
        row=dict(amplitude=amplitude,accepted=bool(result['accepted']),directory=name)
        if result['accepted']:
            seed=directory/name/'accepted.npz';last=result['records'][-1]
            with np.load(seed,allow_pickle=False) as data:omega=float(data['u'][-1])
            row.update(frequency=omega,**{k:last[k] for k in ('M_ADM_estimate','J_volume','lapse_min',
                'dragging_max','gtt_max','shift_norm_over_lapse_max','ergoregion_sampled')})
        records.append(row);write_json(directory/'progress.json',records)
        print(f'[compactness] amplitude={amplitude}, accepted={row["accepted"]}',flush=True)
        if not result['accepted'] or row.get('ergoregion_sampled'):break
        import jax
        jax.clear_caches()
    result=dict(scan_completed=bool(records[-1]['accepted'] and (len(records)==7 or records[-1].get('ergoregion_sampled'))),
        records=records,seconds=time.monotonic()-started,stability='not_assessed',
        scope='Stationary branch continuation; no guaranteed ergoregion, spin valve, maximum spin or dynamical stability.')
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--dry-run',action='store_true');args=parser.parse_args();config=json.loads(args.config.read_text())
    plan=preflight(args.source,config)
    if args.gpu<0:parser.error('GPU must be nonnegative')
    if args.dry_run:plan.pop('metadata');print(json.dumps(plan,indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform');os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if run_scan(args.source,config,args.out)['scan_completed'] else 2


if __name__=='__main__':raise SystemExit(main())
