"""Two higher-order scalar integrals closing the coarse phase-audit failures."""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
import numpy as np

CONFIG=dict(max_new_quadratures=2,order=32,segments=256,timing_tol=1e-7,
            height_tol=1e-8,conservation_tol=1e-9)
TARGETS=[('requested_offset','zero'),('above_all','negative')]


def preflight(prior,source,profile,config):
    prior,source,profile=Path(prior),Path(source),Path(profile)
    if config!=CONFIG:raise ValueError('only two order-32 phase quadratures with unchanged gates are allowed')
    for root in (prior,profile):
        for line in (root/'sha256sums.txt').read_text().splitlines():
            expected,name=line.split('  ',1)
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError('archive checksum mismatch')
    old=json.loads((prior/'outcome.json').read_text());manifest=json.loads((prior/'manifest.json').read_text())
    pm=json.loads((profile/'manifest.json').read_text());certificate=json.loads((profile/'corridor.json').read_text())
    if (old.get('accepted') is not False or old.get('phase_quadratures')!=32 or old.get('full_mpd_points')!=656
            or manifest['source_sha256']!=pm['source_sha256'] or not certificate.get('accepted')
            or hashlib.sha256(source.read_bytes()).hexdigest()!=pm['source_sha256']):
        raise ValueError('exact matching failed phase audit and accepted source/core required')
    failed=[]
    if sum(map(len,old['independent_timing_comparisons'].values()))!=16:
        raise ValueError('all sixteen checked controls required')
    if any(not row['gates']['accepted'] for group in old['records'].values() for row in group['controls'].values()):
        raise ValueError('all original track conservation gates must pass')
    for regime,rows in old['independent_timing_comparisons'].items():
        for label,row in rows.items():
            if (row['full_mpd_defect']>=1e-9 or row['full_mpd_invariant_error']>=1e-9
                    or row['height_difference']>=1e-8 or not row['same_classification']
                    or (not row['marginal'] and row['saved_track_time_difference']>=1e-7)):
                raise ValueError('only quadrature-order failures can be refined')
            if not row['accepted']:failed.append((regime,label))
    if failed!=TARGETS:raise ValueError('exactly the two documented coarse quadratures required')
    return dict(numerical_execution=False,max_new_quadratures=2,cumulative_quadratures=34,
                new_mpd_tracks=0,new_mpd_points=0,prior=old,profile_manifest=pm)


def run_audit(prior,source,profile,config,directory):
    plan=preflight(prior,source,profile,config)
    from grteclyn_stationary.railgun.workflow import load_state, write_json
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.corridor import CartesianCorridor
    from grteclyn_stationary.railgun.axial_reduction import AxialMetric
    p,u,meta=load_state(source)
    if not meta.get('validated') or p.jax.devices()[0].platform!='gpu':raise ValueError('accepted GPU source required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    for path in Path(prior).glob('*'):
        if path.suffix in ('.npz','.json'):
            name=path.name if path.name not in ('manifest.json','outcome.json') else 'phase_'+path.name
            shutil.copy2(path,directory/name)
    pm=plan['profile_manifest'];geometry=CartesianCorridor(RingGeometry(p,u),radius=pm['corridor_radius'],degree=pm['corridor_degree'])
    axis=AxialMetric.from_corridor(geometry);result=deepcopy(plan['prior'])
    result['prior_phase_comparisons']=deepcopy(result['independent_timing_comparisons'])
    for regime,label in TARGETS:
        row=result['independent_timing_comparisons'][regime][label]
        saved=result['records'][regime+'_rk1']['controls'][label]
        with np.load(Path(prior)/f'{regime}_rk1_{label}.npz',allow_pickle=False) as data:initial=np.array(data['state'][0])
        spin=initial[14]*float(axis.values(initial[3])['C'])
        phase=axis.phase(saved['launch']['energy'],spin,order=32,segments=256)
        previous=row['quadratures'][-1]
        row.update(quadratures=[previous,phase],quadrature_time_difference=abs(previous['coordinate_time']-phase['coordinate_time']),
            saved_track_time_difference=abs(saved['coordinate_time']-phase['coordinate_time']),
            height_difference=abs(saved['final_z']-phase['final_z']),same_classification=saved['classification']==phase['classification'])
        row['accepted']=bool(row['same_classification'] and row['height_difference']<1e-8
            and max(row['quadrature_time_difference'],row['saved_track_time_difference'])<1e-7)
        print(f'[phase-polish] {regime}/{label}: accepted={row["accepted"]}, order error={row["quadrature_time_difference"]:.3e}',flush=True)
    ok=all(row['accepted'] for rows in result['independent_timing_comparisons'].values() for row in rows.values())
    result.update(accepted=bool(ok),phase_quadratures=34,new_phase_quadratures=2,new_mpd_tracks=0,new_mpd_points=0,
                  spin_selective_finite_transit=bool(ok and result['selection_regimes']),seconds=time.monotonic()-started)
    write_json(directory/'outcome.json',result)
    write_json(directory/'manifest.json',dict(config=config,source_sha256=pm['source_sha256'],
        physical_config=dict(launch_z=1.,target_z=-10.,spin=.001),
        commit=source_revision(),platform='gpu',float64=True,
        prior_outcome_sha256=hashlib.sha256((Path(prior)/'outcome.json').read_bytes()).hexdigest(),
        scope='Two order-32 scalar phase integrals; reuse all hash-checked full MPD substitution and invariant checks.'))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config',type=Path)
    for key in ('prior','source','profile','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=preflight(args.prior,args.source,args.profile,config)
    if args.dry_run:print(json.dumps({k:v for k,v in plan.items() if k not in ('prior','profile_manifest')},indent=2));return 0
    if args.gpu<0:parser.error('nonnegative GPU required')
    from grteclyn_stationary.numerics.device import select_device
    select_device(args.gpu,128)
    return 0 if run_audit(args.prior,args.source,args.profile,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
