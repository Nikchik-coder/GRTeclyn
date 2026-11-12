"""Two tighter integrations auditing the only failed strong-ring timing controls."""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import numpy as np

TARGETS=[('requested_offset','zero'),('above_all','negative')]


def preflight(prior,source,profile,config):
    prior,source,profile=Path(prior),Path(source),Path(profile)
    for line in (prior/'sha256sums.txt').read_text().splitlines():
        expected,name=line.split('  ',1)
        if hashlib.sha256((prior/name).read_bytes()).hexdigest()!=expected:raise ValueError('prior checksum mismatch')
    for line in (profile/'sha256sums.txt').read_text().splitlines():
        expected,name=line.split('  ',1)
        if hashlib.sha256((profile/name).read_bytes()).hexdigest()!=expected:raise ValueError('profile checksum mismatch')
    old=json.loads((prior/'outcome.json').read_text());manifest=json.loads((prior/'manifest.json').read_text())
    pm=json.loads((profile/'manifest.json').read_text());po=json.loads((profile/'outcome.json').read_text())
    certificate=json.loads((profile/'corridor.json').read_text())
    if (old.get('accepted') is not False or old.get('tracks')!=32 or not po.get('accepted')
            or not certificate.get('accepted') or manifest['source_sha256']!=pm['source_sha256']
            or hashlib.sha256(source.read_bytes()).hexdigest()!=pm['source_sha256']
            or config!=dict(max_new_tracks=2,rtol=2e-13,max_step=.4,duration=250.,timing_tol=1e-7,
                           height_tol=1e-8,conservation_tol=1e-9)):
        raise ValueError('fixed two-track precision audit and accepted matching profile required')
    failed=[]
    for regime,rows in old['rk_comparisons'].items():
        for label,row in rows.items():
            if not row['accepted']:
                if row['marginal'] or not row['same_classification'] or row['final_z']>=1e-8:
                    raise ValueError('only two nonmarginal timing failures can be refined')
                failed.append((regime,label))
    if failed!=TARGETS or any(v['reversal_error']>=1e-8 for v in old['records'].values()):
        raise ValueError('unexpected prior failed controls or symmetry')
    if any(not r['gates']['accepted'] for group in old['records'].values() for r in group['controls'].values()):
        raise ValueError('all prior conservation controls must already pass')
    return dict(max_new_tracks=2,reused_tracks=30,prior_tracks=32,cumulative_tracks=34,
                failed_controls=failed,numerical_execution=False,certificate=certificate,
                profile_manifest=pm,prior=old)


def run_audit(prior,source,profile,config,directory):
    plan=preflight(prior,source,profile,config)
    from grteclyn_stationary.railgun.workflow import load_state, write_json
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.corridor import CartesianCorridor
    from grteclyn_stationary.railgun.transport import MPDSystem
    from grteclyn_stationary.railgun.transit import strict_gates
    from grteclyn_stationary.railgun.uphill import compare_rk_controls
    p,u,_=load_state(source)
    if p.jax.devices()[0].platform!='gpu':raise ValueError('GPU required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    shutil.copytree(prior,directory/'original')
    for path in Path(prior).glob('*'):
        if path.suffix in ('.npz','.json') and path.name not in ('outcome.json','manifest.json'):
            shutil.copy2(path,directory/path.name)
    pm=plan['profile_manifest'];geometry=CartesianCorridor(RingGeometry(p,u),
        radius=pm['corridor_radius'],degree=pm['corridor_degree'])
    geometry.certificate=plan['certificate']
    system=MPDSystem(geometry.metric,regular_origin=True)
    write_json(directory/'manifest.json',dict(config=config,source_sha256=pm['source_sha256'],
        prior_outcome_sha256=hashlib.sha256((Path(prior)/'outcome.json').read_bytes()).hexdigest(),
        commit=source_revision(),
        certificate_reused=True,certificate_source_sha256=hashlib.sha256((Path(profile)/'corridor.json').read_bytes()).hexdigest(),
        scope='Two new tighter tracks; original failed study retained unchanged.'))
    result=deepcopy(plan['prior']);new_rows=[]
    for regime,label in TARGETS:
        stem=f'{regime}_rk1_{label}'
        with np.load(Path(prior)/f'{stem}.npz',allow_pickle=False) as data:state=np.array(data['state'][0])
        old=result['records'][f'{regime}_rk1']['controls'][label]
        track=system.integrate(state,duration=250.,rtol=2e-13,atol=2e-15,max_step=.4,
                               inner_radius=0.,target_z=-10.,samples=1001,stop_at_turnaround=True)
        gates=strict_gates(track);row=deepcopy(old)
        row.update(gates=gates,stop=track['stop'],launch=track['invariants'][0],final=track['invariants'][-1],
                   proper_time=float(track['time'][-1]),coordinate_time=float(track['state'][-1,0]),
                   final_z=float(track['state'][-1,3]),rtol=2e-13)
        row['classification']='transmitted' if track['stop']=='target_z' else 'reflected' if track['stop']=='turnaround' else 'unresolved'
        shutil.copy2(Path(prior)/f'{stem}.npz',directory/f'{regime}_rk0_{label}.npz')
        write_json(directory/f'{regime}_rk0_{label}.json',old)
        np.savez_compressed(directory/f'{stem}.npz',time=track['time'],state=track['state'])
        write_json(directory/f'{stem}.json',row)
        result['records'][f'{regime}_rk0']['controls'][label]=deepcopy(old)
        result['records'][f'{regime}_rk1']['controls'][label]=row
        new_rows.append(dict(regime=regime,label=label,rtols=[2e-12,2e-13],gates=gates))
        print(f'[precision] {regime}/{label}: stop={row["stop"]}, strict={gates["accepted"]}',flush=True)
    ok=all(row['gates']['accepted'] and row['stop'] in ('target_z','turnaround')
           for group in result['records'].values() for row in group['controls'].values())
    for regime in result['rk_comparisons']:
        a,b=(result['records'][f'{regime}_rk{i}']['controls'] for i in range(2))
        comparisons,consistent=compare_rk_controls(a,b);result['rk_comparisons'][regime]=comparisons;ok=ok and consistent
    result.update(accepted=bool(ok),tracks=32,new_tracks=2,prior_tracks=32,cumulative_tracks=34,
        refined_controls=new_rows,seconds=time.monotonic()-started,
        spin_selective_finite_transit=bool(ok and result['selection_regimes']),
        tolerance_pairs='Unchanged passing pairs retained; only the two failed controls use 2e-12 / 2e-13.',
        scope='Finite uphill selection only; no escape, trapping or energy gain. Original failed archive immutable.')
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config',type=Path)
    for name in ('prior','source','profile','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=preflight(args.prior,args.source,args.profile,config)
    if args.gpu<0:parser.error('nonnegative GPU required')
    if args.dry_run:
        print(json.dumps({k:v for k,v in plan.items() if k not in ('certificate','profile_manifest','prior')},indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform');os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from grteclyn_stationary.numerics.device import select_device
    select_device(args.gpu,128)
    return 0 if run_audit(args.prior,args.source,args.profile,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
