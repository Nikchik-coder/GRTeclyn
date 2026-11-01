"""Bounded independent phase audit of saved strong-ring MPD tracks."""
from __future__ import annotations
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import numpy as np

CONFIG=dict(orders=[8,16],segments=256,max_quadratures=32,max_mpd_points=656,
            timing_tol=1e-7,height_tol=1e-8,conservation_tol=1e-9,mpd_defect_tol=1e-9)


def preflight(prior,source,profile,config):
    prior,source,profile=Path(prior),Path(source),Path(profile)
    if config!=CONFIG:raise ValueError('fixed 32 phase quadratures, no new MPD tracks and unchanged gates required')
    for root in (prior,profile):
        for line in (root/'sha256sums.txt').read_text().splitlines():
            expected,name=line.split('  ',1)
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError('archive checksum mismatch')
    old=json.loads((prior/'outcome.json').read_text());pm=json.loads((profile/'manifest.json').read_text())
    certificate=json.loads((profile/'corridor.json').read_text());manifest=json.loads((prior/'manifest.json').read_text())
    if (old.get('accepted') is not False or old.get('cumulative_tracks')!=34
            or not certificate.get('accepted') or manifest['source_sha256']!=pm['source_sha256']
            or hashlib.sha256(source.read_bytes()).hexdigest()!=pm['source_sha256']):
        raise ValueError('failed 34-track audit and exact accepted source/core required')
    if any(not v['gates']['accepted'] for group in old['records'].values() for v in group['controls'].values()):
        raise ValueError('saved full-track conservation must already pass')
    return dict(numerical_execution=False,max_quadratures=32,new_mpd_tracks=0,
                max_mpd_points=656,prior=old,profile_manifest=pm,certificate=certificate)


def run_audit(prior,source,profile,config,directory):
    plan=preflight(prior,source,profile,config)
    from .workflow import load_state,write_json
    from .geometry import RingGeometry
    from .corridor import CartesianCorridor
    from .transport import MPDSystem
    from .axial_reduction import AxialMetric
    p,u,meta=load_state(source)
    if not meta.get('validated') or p.jax.devices()[0].platform!='gpu':raise ValueError('accepted GPU background required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    for path in Path(prior).glob('*'):
        if path.suffix in ('.npz','.json'):shutil.copy2(path,directory/path.name if path.name not in ('manifest.json','outcome.json') else directory/('prior_'+path.name))
    pm=plan['profile_manifest'];geometry=CartesianCorridor(RingGeometry(p,u),radius=pm['corridor_radius'],degree=pm['corridor_degree'])
    geometry.certificate=plan['certificate']
    xp=p.xp;reflection=xp.diag(xp.array([1.,1.,-1.,1.]))
    systems=[MPDSystem(geometry.metric,regular_origin=True),
             MPDSystem(lambda x:reflection@geometry.metric(reflection@x)@reflection,regular_origin=True)]
    axes=[AxialMetric.from_corridor(geometry,orientation=o) for o in (1,-1)]
    manifest=dict(config=config,source_sha256=pm['source_sha256'],certificate_reused=True,
        certificate_sha256=hashlib.sha256((Path(profile)/'corridor.json').read_bytes()).hexdigest(),
        prior_outcome_sha256=hashlib.sha256((Path(prior)/'outcome.json').read_bytes()).hexdigest(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),platform='gpu',float64=True,
        extended_spectral_precision_bits=int(np.finfo(np.longdouble).nmant),new_mpd_tracks=0,
        scope='Independent axis first integrals, checked by full Cartesian MPD substitution; original failed studies retained.')
    write_json(directory/'manifest.json',manifest)
    old=plan['prior'];comparisons={};count=0;points=0;ok=True
    for regime,energy in old['energies'].items():
        comparisons[regime]={}
        for label in ('zero','positive','negative','reversed'):
            reverse=label=='reversed';axis,system=axes[int(reverse)],systems[int(reverse)]
            row=old['records'][regime+'_rk1']['controls'][label]
            with np.load(Path(prior)/f'{regime}_rk1_{label}.npz',allow_pickle=False) as data:initial=np.array(data['state'][0])
            launch=system.invariants(initial);spin=initial[14]*float(axis.values(initial[3])['C'])
            phases=[axis.phase(launch['energy'],spin,order=order,segments=256) for order in config['orders']];count+=2
            a,b=phases;time_error=abs(a['coordinate_time']-b['coordinate_time'])
            saved_error=abs(b['coordinate_time']-row['coordinate_time']);height_error=abs(b['final_z']-row['final_z'])
            same=bool(row['marginal'] or row['classification']==b['classification'])
            defect=0.;invariant_error=0.
            zpoints=np.linspace(float(initial[3]),float(b['final_z'])+1e-4,33)
            zpoints=np.r_[zpoints,[-.99,-.7,-.51,-.49,.49,.51,.7,.99]*np.asarray(pm['corridor_radius'])]
            for z in zpoints:
                state,rhs=axis.state_and_rhs(z,launch['energy'],spin)
                actual=np.asarray(system._rhs_jit(state));defect=max(defect,float(np.max(abs(actual-rhs)/(1+abs(rhs)))))
                inv=system.invariants(state)
                invariant_error=max(invariant_error,abs(inv['mass2']-1),abs(inv['energy']-launch['energy']),
                    abs(inv['spin2']-spin*spin),inv['ssc_max'],abs(inv['velocity_norm']+1))
                points+=1
            accepted=bool(same and height_error<1e-8 and (row['marginal'] or max(time_error,saved_error)<1e-7)
                          and defect<1e-9 and invariant_error<1e-9)
            comparisons[regime][label]=dict(accepted=accepted,quadratures=phases,quadrature_time_difference=time_error,
                saved_track_time_difference=saved_error,height_difference=height_error,same_classification=same,
                marginal=row['marginal'],timing_claim=not row['marginal'],full_mpd_defect=defect,
                full_mpd_invariant_error=invariant_error)
            ok=ok and accepted
            print(f'[axis-audit] {regime}/{label}: accepted={accepted}, timing={saved_error:.3e}, defect={defect:.3e}',flush=True)
            write_json(directory/'progress.json',comparisons)
    result=deepcopy(old)
    result['prior_rk_comparisons']=result.pop('rk_comparisons')
    result.update(accepted=bool(ok and count==32 and points==656),accuracy_method='Independent first-integral phase quadrature and full MPD substitution',
        independent_timing_comparisons=comparisons,new_mpd_tracks=0,phase_quadratures=count,full_mpd_points=points,
        seconds=time.monotonic()-started,spin_selective_finite_transit=bool(ok and old['selection_regimes']))
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config',type=Path)
    for key in ('prior','source','profile','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=preflight(args.prior,args.source,args.profile,config)
    if args.dry_run:print(json.dumps({k:v for k,v in plan.items() if k not in ('prior','profile_manifest','certificate')},indent=2));return 0
    if args.gpu<0:parser.error('nonnegative GPU required')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if run_audit(args.prior,args.source,args.profile,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
