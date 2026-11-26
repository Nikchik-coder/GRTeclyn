"""Bounded, fully coupled recovery of a screened concentric-ring candidate.

The linear screen is provenance for a seed, never an accepted background.
Every grid needs fresh Newton corrections, independent field equations, zero
total angular momentum and a resolved component-wise matter gap. Only the
final state of a passing three-grid study can be exported as accepted.
"""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np


def preflight(source,config):
    """Inspect portable data and bound dense storage without importing JAX."""
    source=Path(source)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=config['source_sha256']:raise ValueError('screen seed checksum mismatch')
    with np.load(source,allow_pickle=False) as data:
        meta=json.loads(str(data['metadata']));u=np.asarray(data['u'])
    fields=meta['fields'];grids=config['grids']
    if (meta.get('schema')!=1 or meta.get('model')!='canonical_regular_centre'
            or meta.get('validated') is not False or meta.get('target_j') is not None
            or len(fields)!=2 or [f['winding'] for f in fields]!=[1,config['outer_winding']]
            or config['outer_winding']>=0 or any(f['parity']!='even' for f in fields)
            or meta['length']!=config['length']):
        raise ValueError('an unaccepted matching two-field linear screen seed is required')
    size=6*(meta['nx']+1)*(meta['ny']+1)+2
    if u.shape!=(size,) or not np.isfinite(u).all():raise ValueError('invalid screen vector')
    record=json.loads(source.with_suffix('.json').read_text())
    outcome=json.loads((source.parent/'outcome.json').read_text())
    manifest=json.loads((source.parent/'manifest.json').read_text())
    if (record.get('stage')!='fixed_background_linear_screen' or record.get('self_consistent') is not False
            or not record.get('gap',{}).get('accepted') or record['grid']!=[meta['nx'],meta['ny']]
            or record.get('winding')!=fields[1]['winding']
            or record['gap'].get('relative_density_cutoff')!=1e-6
            or manifest.get('stage')!='fixed_background_linear_screen'
            or not outcome.get('screen_completed') or outcome.get('accepted_background') is not False
            or not any(c.get('seed')==source.name and c.get('winding')==fields[1]['winding']
                       for c in outcome.get('candidates',[]))):
        raise ValueError('passing two-grid linear screen provenance required')
    if (len(grids)!=3 or any(len(g)!=2 or any(isinstance(n,bool) or not isinstance(n,int) for n in g)
                           or g[0]<6 or g[1]<3 for g in grids)
            or any(b[0]<=a[0] or b[1]<=a[1] for a,b in zip(grids,grids[1:]))
            or config['max_solves']!=3 or not 2<config['max_iter']<=30
            or config['target_j']!=0. or config['relative_density_cutoff']!=1e-6
            or config['equation_tol']!=1e-8 or config['tail_tol']!=1e-6
            or config['observable_tol']!=1e-6 or config['edge_tol']!=1e-6
            or config['newton_tol']!=1e-12 or not 0<config['perturbation']<=1e-5
            or not np.isfinite(config['channel_half_height']) or config['channel_half_height']<=0):
        raise ValueError('three bounded increasing solves with unchanged validation gates required')
    unknowns=[6*(nx+1)*(ny+1)+3 for nx,ny in grids]
    # Eight dense buffers reserve space for factorisation, old/new Jacobians,
    # scaling and compiler temporaries. This is a planning bound, not an
    # allocator measurement; the launcher still checks the shared card.
    storage=[8*n*n*8/1024**3 for n in unknowns]
    if max(unknowns)>33000 or max(storage)>64.:
        raise ValueError('dense GPU recovery exceeds the bounded storage plan')
    return dict(source_sha256=digest,screen_commit=manifest['commit'],grids=grids,
                unknowns=unknowns,eight_dense_buffers_GiB=storage,max_solves=3,
                numerical_execution=False,metadata=meta)


def acceptance(records,*,tolerance=1e-6):
    """Joint field, charge, annulus and finite-height acceptance, fail closed."""
    from grteclyn_stationary.railgun.diagnostics import converged_records
    accepted,drift=converged_records(records,tolerance=tolerance)
    result=dict(accepted=False,observable_relative_drift=drift,
                component_charge_relative_drift=None,edge_relative_drift=None)
    if not accepted:return result
    if any(not r.get('annular_gap',{}).get('accepted')
           or not r.get('finite_height_channel',{}).get('accepted')
           or len(r.get('newton',{}).get('newton_steps',[]))<2 for r in records):return result
    a,b=records[-2:];q=np.asarray([a.get('charges',[]),b.get('charges',[])],float)
    j=np.asarray([r.get('J_volume',np.nan) for r in records])
    edges=np.array([[r['annular_gap'].get(k,np.nan) for k in
                    ('inner_ring_outer_radius','outer_ring_inner_radius')] for r in (a,b)],float)
    if (q.shape!=(2,2) or not np.isfinite(q).all() or np.any(q<=0)
            or not np.isfinite(j).all() or np.max(abs(j))>1e-8
            or not np.isfinite(edges).all() or np.any(edges<=0)):return result
    charge_drift=float(np.max(abs(q[0]-q[1])/np.maximum(q[0],q[1])))
    edge_drift=float(np.max(abs(edges[0]-edges[1])/np.maximum(edges[0],edges[1])))
    result.update(accepted=bool(max(charge_drift,edge_drift)<=tolerance),
                  component_charge_relative_drift=charge_drift,edge_relative_drift=edge_drift)
    return result


def measure_channel(meta,u,gap,half_height,directory,name):
    """Check a finite-height annular tube with a quarter-gap radial margin."""
    from grteclyn_stationary.railgun.gap import cylindrical_densities
    if not gap['accepted']:return dict(accepted=False,reason='equatorial_gap_rejected')
    left,right=gap['inner_ring_outer_radius'],gap['outer_ring_inner_radius']
    width=right-left
    rho,z=np.meshgrid(np.linspace(left+width/4,right-width/4,21),np.linspace(-half_height,half_height,81))
    density=cylindrical_densities(meta,u,rho,z)
    peaks=np.array([edge['peak_density'] for edge in gap['edges']])
    maxima=np.max(density/peaks[:,None,None],axis=(1,2))
    np.savetxt(Path(directory)/f'{name}_channel.tsv',
               np.column_stack([rho.ravel(),z.ravel(),density[0].ravel(),density[1].ravel()]),
               delimiter='\t',header='rho\tz\tinner_density\touter_density')
    return dict(accepted=bool(np.isfinite(maxima).all() and np.all(maxima<1e-6)),
                rho_min=float(rho.min()),rho_max=float(rho.max()),z_min=-half_height,z_max=half_height,
                relative_density_max=maxima.tolist(),samples=[21,81],
                normalisation='Each component own equatorial peak; threshold 1e-6.',
                scope='Sampled finite-height matter channel; no particle trajectory certified.')


def correction_plan(prior,config):
    """One extra finest-grid solve, preserving the original rejected study.

    This requires a separate run-specific go. The two previously passing
    recovery grids remain evidence; only the failed finest state is corrected.
    An already corrected study cannot reset this one-solve budget.
    """
    prior=Path(prior)
    checked=set()
    for line in (prior/'sha256sums.txt').read_text().splitlines():
        digest,name=line.split('  ',1)
        if (Path(name).name!=name or name in checked
                or hashlib.sha256((prior/name).read_bytes()).hexdigest()!=digest):
            raise ValueError('prior recovery archive checksum mismatch')
        checked.add(name)
    required={'manifest.json','outcome.json'}|{f'grid_{nx}x{ny}.{ext}'
              for nx,ny in config['grids'] for ext in ('npz','json')}
    if not required<=checked:raise ValueError('prior recovery checksum list is incomplete')
    manifest=json.loads((prior/'manifest.json').read_text())
    outcome=json.loads((prior/'outcome.json').read_text());rows=outcome.get('records',[])
    if (manifest.get('stage')!='nonlinear_annular_recovery' or manifest.get('config')!=config
            or outcome.get('accepted') is not False or outcome.get('solves')!=3 or len(rows)!=3
            or [r.get('grid') for r in rows]!=config['grids']
            or any(r.get('verdict')!='PASS' for r in rows[:2])
            or rows[-1].get('verdict')!='REJECT'
            or rows[-1].get('reasons')!=['angular_momentum_balance']
            or not rows[-1].get('newton',{}).get('converged')):
        raise ValueError('only the original finest-grid flux rejection can receive one correction')
    nx,ny=config['grids'][-1];name=f'grid_{nx}x{ny}.npz'
    return dict(max_additional_solves=1,prior_solves=3,cumulative_solve_cap=4,
                corrected_grid=[nx,ny],source_state=name,
                prior_outcome_sha256=hashlib.sha256((prior/'outcome.json').read_bytes()).hexdigest(),
                source_state_sha256=hashlib.sha256((prior/name).read_bytes()).hexdigest(),
                reused_grids=config['grids'][:2],perturbation=0.,minimum_new_updates=2)


def run_recovery(source,config,directory,*,correct_from=None):
    plan=preflight(source,config)
    correction=correction_plan(correct_from,config) if correct_from is not None else None
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.continuation import transfer_fields
    from grteclyn_stationary.railgun.workflow import load_state, save_state, write_json
    from grteclyn_stationary.railgun.diagnostics import validate
    from grteclyn_stationary.railgun.gap import equatorial_densities, annular_gap
    from grteclyn_stationary.railgun.counter_rotation import dragging_profile
    from grteclyn_stationary.numerics.newton import newton
    state=Path(correct_from)/correction['source_state'] if correction else source
    old,old_u,_=load_state(state)
    device=old.jax.devices()[0]
    if device.platform!='gpu' or not old.jax.config.jax_enable_x64:
        raise ValueError('GPU float64 execution required; no CPU fallback')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    manifest=dict(config=config,source_sha256=plan['source_sha256'],screen_commit=plan['screen_commit'],
        configuration_sha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(),
        commit=source_revision(),
        platform=device.platform,device_kind=device.device_kind,jax=old.jax.__version__,float64=True,
        stage='annular_finest_grid_correction' if correction else 'nonlinear_annular_recovery',
        correction=correction,storage_plan={k:plan[k] for k in
        ('unknowns','eight_dense_buffers_GiB')},stability='not_assessed')
    write_json(directory/'manifest.json',manifest)
    records=(json.loads((Path(correct_from)/'outcome.json').read_text())['records'][:2]
             if correction else [])
    started=time.monotonic();previous=old,old_u
    # Keep the source screen's radial sampling, including both complete tails.
    radius=np.loadtxt(Path(source).with_name(Path(source).stem+'_density.tsv'),usecols=0)
    grids=[config['grids'][-1]] if correction else config['grids']
    for index,(nx,ny) in enumerate(grids):
        tick=time.monotonic();name=f'grid_{nx}x{ny}'
        p=RingProblem(old.fields,nx=nx,ny=ny,length=config['length'],target_j=0.)
        if correction:
            # Correct the saved converged state with a newly assembled LU;
            # no interpolation perturbation or changed physical tolerance.
            guess=p.transfer(*previous,perturb=0.)
        elif index==0:
            # An unbordered seed ends in omega_2, not log(amplitude_2).
            # Repack species explicitly before a same-model perturbation.
            border=transfer_fields(p,*previous)
            guess=p.transfer(p,border,perturb=config['perturbation'])
        else:guess=p.transfer(*previous,perturb=config['perturbation'])
        print(f'[annular] solving {nx}x{ny}, unknowns={p.n_unknowns}, target_J=0',flush=True)
        value,info=newton(p.residual,p.jacobian,guess,tol=config['newton_tol'],
                          max_iter=config['max_iter'],min_updates=2,verbose=True)
        save_state(directory/f'{name}.npz',p,value)
        try:
            row=validate(p,value,info,equation_tol=config['equation_tol'],tail_tol=config['tail_tol'])
            if np.isfinite(value).all():
                meta=dict(nx=nx,ny=ny,length=p.length,fields=[f.to_dict() for f in p.fields])
                density=equatorial_densities(meta,value,radius)
                gap=annular_gap(radius,density,relative_cutoff=config['relative_density_cutoff'])
                np.savetxt(directory/f'{name}_density.tsv',np.column_stack([radius,density.T]),
                           delimiter='\t',header='rho\tinner_density\touter_density')
                row['annular_gap']=gap
                row['finite_height_channel']=measure_channel(meta,value,gap,config['channel_half_height'],directory,name)
                if not gap['accepted']:row['reasons'].append('annular_gap')
                if not row['finite_height_channel']['accepted']:row['reasons'].append('finite_height_channel')
                row['verdict']='PASS' if not row['reasons'] else 'REJECT'
            # JSON serialization is deliberately strict about every diagnostic,
            # including independent checks whose maxima must not hide NaNs.
            json.dumps(row,allow_nan=False)
        except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as error:
            row=dict(grid=[nx,ny],verdict='REJECT',reasons=[str(error)])
        row.update(seconds=time.monotonic()-tick)
        write_json(directory/f'{name}.json',row);records.append(row)
        print(f'[annular] {nx}x{ny}: {row["verdict"]}, reasons={row["reasons"]}',flush=True)
        if row['verdict']!='PASS':break
        previous=p,value
        # Each grid has a separate compiled dense Jacobian. Release completed
        # executables before compiling the next, rather than retaining all three.
        p.jax.clear_caches()
    outcome=acceptance(records,tolerance=config['observable_tol'])
    new_solves=len(records)-(2 if correction else 0)
    outcome.update(records=records,grids_attempted=len(records),solves=new_solves,
                   prior_solves=3 if correction else 0,cumulative_solves=new_solves+(3 if correction else 0),
                   seconds=time.monotonic()-started,stability='not_assessed',
                   reasons=[] if outcome['accepted'] else ['coupled_fields_charges_or_annular_channel'])
    if outcome['accepted']:
        save_state(directory/'accepted.npz',p,value,validated=True)
        outcome['dragging_tail']=dragging_profile(p,value,directory)
    write_json(directory/'outcome.json',outcome)
    return outcome


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--correct-from',type=Path,help='separately approved one-solve correction of the original finest-grid flux rejection')
    parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    if args.gpu<0:parser.error('GPU must be nonnegative')
    config=json.loads(args.config.read_text())
    plan=preflight(args.source,config)
    if args.correct_from is not None:plan['correction']=correction_plan(args.correct_from,config)
    if args.dry_run:
        plan.pop('metadata');print(json.dumps(plan,indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from grteclyn_stationary.numerics.device import select_device
    select_device(args.gpu,128)
    return 0 if run_recovery(args.source,config,args.out,correct_from=args.correct_from)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
