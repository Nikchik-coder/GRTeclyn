"""Audit saved uphill first crossings without integrating additional tracks."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import numpy as np
from .first_crossing import first_crossing


def audit(source,raw,directory):
    from .workflow import load_state,write_json
    from .geometry import RingGeometry
    from .transport import MPDSystem
    raw=Path(raw);directory=Path(directory)
    original=json.loads((raw/'outcome.json').read_text())
    manifest=json.loads((raw/'manifest.json').read_text())
    if (original['tracks']!=32 or manifest['source_sha256']!=hashlib.sha256(Path(source).read_bytes()).hexdigest()
            or not json.loads((raw/'corridor.json').read_text())['accepted']):
        raise ValueError('complete 32-track study with matching accepted core required')
    p,u,metadata=load_state(source)
    if not metadata.get('validated') or p.jax.devices()[0].platform!='gpu':
        raise ValueError('accepted GPU background required')
    # Every audited terminal point is near z=-10, outside the core. Use the
    # original Cartesian geometry directly for independent terminal invariants.
    engine=MPDSystem(RingGeometry(p,u).metric)
    directory.mkdir(parents=True,exist_ok=False);shutil.copytree(raw,directory/'original')
    started=time.monotonic();result=copy.deepcopy(original);target=manifest['config']['target_z']
    all_ok=True;changes=[];marginal_times=[]
    for regime in original['energies']:
        for rk in (0,1):
            group=result['records'][f'{regime}_rk{rk}']
            for label,row in group['controls'].items():
                name=f'{regime}_rk{rk}_{label}'
                with np.load(raw/f'{name}.npz',allow_pickle=False) as arc:
                    times=np.array(arc['time']);states=np.array(arc['state'])
                if row['stop']=='turnaround' and not row['marginal'] and states[-1,3]<target:
                    resolved=first_crossing(times,states,target)
                    if resolved is None:raise ValueError('reported turnaround below target has no resolved earlier crossing')
                    times,states=resolved['time'],resolved['state']
                    endpoint=engine.invariants(states[-1]);launch=row['launch'];gates=row['gates']
                    for key in ('mass2','spin2','energy','angular_momentum'):
                        scale=abs(launch[key]) if abs(launch[key])>1e-14 else 1.
                        gates['normalised_drift'][key]=max(gates['normalised_drift'][key],abs(endpoint[key]-launch[key])/scale)
                    gates['ssc_max']=max(gates['ssc_max'],endpoint['ssc_max'])
                    gates['norm_error']=max(gates['norm_error'],abs(endpoint['velocity_norm']+1))
                    gates['accepted']=bool(gates['accepted'] and all(v<1e-9 for v in gates['normalised_drift'].values())
                        and gates['ssc_max']<1e-9 and gates['norm_error']<1e-9 and endpoint['spin_curvature_ratio']<=.1)
                    row.update(stop='target_z',classification='transmitted',proper_time=float(times[-1]),
                        coordinate_time=float(states[-1,0]),final_z=float(states[-1,3]),final=endpoint,
                        first_crossing_audit=resolved['audit'])
                    changes.append(name)
                if row['stop']=='target_z' and abs(row['final_z']-target)>1e-8:all_ok=False
                if row['stop']=='turnaround' and row['final_z']<target-1e-8 and not row['marginal']:all_ok=False
                all_ok=all_ok and row['gates']['accepted'] and row['stop'] in ('target_z','turnaround')
                np.savez_compressed(directory/f'{name}.npz',time=times,state=states)
                write_json(directory/f'{name}.json',row)
            positive,reverse=[group['controls'][k] for k in ('positive','reversed')]
            symmetry=max(abs(positive['coordinate_time']-reverse['coordinate_time']),abs(positive['final_z']-reverse['final_z']))
            group['reversal_error']=symmetry
            all_ok=all_ok and symmetry<1e-8 and positive['classification']==reverse['classification']
    comparisons={};selection=[]
    for regime in original['energies']:
        a,b=[result['records'][f'{regime}_rk{i}']['controls'] for i in (0,1)];errors={}
        for label in ('zero','positive','negative'):
            marginal=a[label]['marginal'] or b[label]['marginal']
            dt=abs(a[label]['coordinate_time']-b[label]['coordinate_time'])
            dz=abs(a[label]['final_z']-b[label]['final_z'])
            same=a[label]['classification']==b[label]['classification']
            errors[label]=dict(time=None if marginal else dt,final_z=dz,same_classification=same,marginal=marginal)
            # Exact threshold contact has no stable target-arrival time. It
            # remains a conservation/height control and cannot supply a valve
            # or a transit-time comparison.
            if marginal:marginal_times.append(regime+'_'+label)
            all_ok=all_ok and dz<1e-8 and same and (marginal or dt<1e-7)
        comparisons[regime]=errors
        if {b[k]['classification'] for k in ('positive','negative')}=={'transmitted','reflected'}:
            safe=all(abs(b[k]['endpoint_energy_margin'])>10*b[k]['gates']['normalised_drift']['energy']
                     for k in ('positive','negative'))
            if safe:selection.append(regime)
    result.update(accepted=bool(all_ok),records=result['records'],rk_comparisons=comparisons,
        spin_selective_finite_transit=bool(all_ok and selection),selection_regimes=selection,
        event_audit=dict(corrected_tracks=changes,additional_tracks=0,interpolation_orders=[5,7],
            independent_terminal_invariants=True,marginal_contacts_excluded_from_timing=marginal_times,
            raw_study_accepted=original['accepted'],raw_outcome_sha256=hashlib.sha256((raw/'outcome.json').read_bytes()).hexdigest(),
            seconds=time.monotonic()-started))
    manifest.update(event_audit_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    write_json(directory/'manifest.json',manifest);write_json(directory/'outcome.json',result)
    print(json.dumps(dict(accepted=bool(all_ok),corrected_tracks=changes,selection_regimes=selection,
                         additional_integrated_tracks=0)),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--raw',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--gpu',type=int,required=True)
    args=parser.parse_args()
    if args.gpu<0:parser.error('GPU must be nonnegative')
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform');os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if audit(args.source,args.raw,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
