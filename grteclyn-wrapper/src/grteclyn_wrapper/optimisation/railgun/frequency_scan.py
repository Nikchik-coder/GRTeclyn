"""Frequency-controlled continuation past a failed fixed-radius amplitude pin."""
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
    with np.load(source,allow_pickle=False) as data:
        meta=json.loads(str(data['metadata']));omega=float(data['u'][-1])
    fields=meta['fields'];targets=config['frequencies'];grids=config['grids']
    if (not meta.get('validated') or len(fields)!=1 or fields[0]['winding']!=1
            or fields[0]['parity']!='even' or fields[0]['mass']!=1.
            or meta.get('target_j') is not None or meta['length']!=5.):
        raise ValueError('accepted pure even k=1, m=1 source at L=5 required')
    profiles=[([.85,.82,.79,.76,.73,.70,.67],[[72,10],[96,12],[128,16]],21),
              ([.70,.67],[[96,12],[128,16],[160,20]],6)]
    if (not any(targets==t and grids==g and config['max_solves']==n for t,g,n in profiles)
            or omega<=targets[0] or config['max_iter']!=30 or config['equation_tol']!=1e-8
            or config['tail_tol']!=1e-6 or config['observable_tol']!=1e-6):
        raise ValueError('one of the bounded frequency/grid continuation profiles is required')
    if targets==[.70,.67] and (abs(omega-.73)>1e-12 or meta.get('frequency_targets')!=[.73]
                              or [meta['nx'],meta['ny']]!=[160,20]):
        raise ValueError('refined tail continuation requires the accepted 160x20 omega=0.73 source')
    return dict(metadata=meta,frequencies=targets,grids=grids,
                max_solves=config['max_solves'],numerical_execution=False)


def run_scan(source,config,directory):
    plan=preflight(source,config)
    from .workflow import load_state,run_study,write_json
    p,u,_=load_state(source)
    if p.jax.devices()[0].platform!='gpu':raise ValueError('GPU execution required')
    floor=.001*float(np.asarray(p.charge_integrals(u))[0])
    if not np.isfinite(floor) or floor<=0:raise ValueError('positive source charge required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    manifest=dict(config=config,source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        minimum_charge=floor,branch='nodeless nonvacuum continuation',stability='not_assessed')
    write_json(directory/'manifest.json',manifest);seed=Path(source);records=[];solves=0
    for index,frequency in enumerate(config['frequencies']):
        study=dict(fields=plan['metadata']['fields'],length=5.,grids=config['grids'],max_iter=30,
            min_updates=2,newton_tol=1e-12,perturbation=1e-5,equation_tol=1e-8,tail_tol=1e-6,
            observable_tol=1e-6,require_gpu=True,frequency_targets=[frequency],
            minimum_charges=[floor],require_nodeless=True)
        name=f'frequency_{index+1:02d}';result=run_study(study,directory/name,seed_path=seed)
        solves+=len(result['records'])
        row=dict(frequency=frequency,accepted=bool(result['accepted']),directory=name)
        if result['accepted']:
            seed=directory/name/'accepted.npz';last=result['records'][-1]
            with np.load(seed,allow_pickle=False) as arc:meta=json.loads(str(arc['metadata']))
            row.update(amplitude=meta['measured_amplitude_pins'][0],**{k:last[k] for k in
                ('M_ADM_estimate','J_volume','lapse_min','dragging_max','gtt_max','shift_norm_over_lapse_max','ergoregion_sampled')})
        records.append(row);write_json(directory/'progress.json',records)
        print(f'[frequency] omega={frequency}, accepted={row["accepted"]}',flush=True)
        if not result['accepted'] or row.get('ergoregion_sampled'):break
        p.jax.clear_caches()
    result=dict(scan_completed=bool(records[-1]['accepted'] and (len(records)==len(config['frequencies']) or records[-1].get('ergoregion_sampled'))),
        records=records,solves=solves,seconds=time.monotonic()-started,stability='not_assessed',
        scope='Frequency continuation of a nodeless nonvacuum stationary branch. No maximum spin or dynamical stability claim.')
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
