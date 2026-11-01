"""Bounded off-axis MPD passage through a validated concentric matter gap."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np

CONFIG=dict(max_tracks=8,launch_z=10.,target_z=-10.,speed=-.5,spin=.001,
            duration=100.,rtols=[2e-11,2e-12],max_step=.4,samples=1001,
            conservation_tol=1e-9,timing_tol=1e-7,position_tol=1e-7,relative_density_cutoff=1e-6)


def preflight(source,config):
    source=Path(source)
    if config!=CONFIG:raise ValueError('fixed eight-track annular pilot and unchanged matter/conservation gates required')
    for line in (source.parent/'sha256sums.txt').read_text().splitlines():
        expected,name=line.split('  ',1)
        if hashlib.sha256((source.parent/name).read_bytes()).hexdigest()!=expected:raise ValueError('source study checksum mismatch')
    result=json.loads((source.parent/'outcome.json').read_text())
    with np.load(source,allow_pickle=False) as data:meta=json.loads(str(data['metadata']))
    if (not result.get('accepted') or not meta.get('validated') or result.get('solves')!=3
            or meta.get('representation')!='dragging_quintic_regular_operator_v2'
            or [f['winding'] for f in meta['fields']]!=[1,-12] or meta.get('target_j')!=0.
            or [r.get('grid') for r in result['records']]!=[[192,16],[224,18],[256,20]]
            or any(r.get('verdict')!='PASS' for r in result['records'])):
        raise ValueError('accepted three-grid regular-operator zero-J annular field required')
    channels=[r['finite_height_channel'] for r in result['records']]
    lo=max(r['rho_min'] for r in channels);hi=min(r['rho_max'] for r in channels)
    if not lo<hi or any(not r['accepted'] or r['z_min']>-10 or r['z_max']<10 for r in channels):
        raise ValueError('a common validated finite-height annular tube is required')
    peaks=[r['peak_density'] for r in result['records'][-1]['annular_gap']['edges']]
    return dict(numerical_execution=False,max_tracks=8,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                rho_min=lo,rho_max=hi,launch_rho=(lo+hi)/2,peak_densities=peaks)


def channel_gate(states,densities,peaks,rho_min,rho_max):
    states=np.asarray(states);densities=np.asarray(densities);peaks=np.asarray(peaks)
    rho=np.hypot(states[:,1],states[:,2]);relative=densities/peaks[:,None]
    finite=bool(np.isfinite(states).all() and np.isfinite(relative).all())
    maxima=np.max(relative,axis=1)
    return dict(accepted=bool(finite and np.all(densities>=0) and np.all(maxima<1e-6)
                             and np.all(rho>=rho_min) and np.all(rho<=rho_max)
                             and np.all(states[:,3]>=-10.-1e-10) and np.all(states[:,3]<=10.+1e-10)),
        rho_min=float(rho.min()),rho_max=float(rho.max()),relative_density_max=maxima.tolist(),
        samples=len(states),normalisation='Each source component own equatorial energy-density peak.')


def density_evaluator(geometry):
    """Independent Cartesian Eulerian energy, using the actual factored metric."""
    jax,xp=geometry.jax,geometry.xp
    def evaluate(x):
        g=geometry.metric(x);inverse=xp.linalg.inv(g)
        alpha=1/xp.sqrt(-inverse[0,0]);normal=-alpha*inverse[:,0]
        result=[]
        for i,field in enumerate(geometry.fields):
            scalar=lambda point:geometry.scalar(point,i)
            value=scalar(x);gradient=jax.jacfwd(scalar)(x);amp2=xp.sum(value*value)
            potential=field.mass**2*amp2+field.quartic*amp2**2+field.sextic*amp2**3
            energy=(2*xp.sum((gradient@normal)**2)+xp.einsum('ia,ab,ib->',gradient,inverse,gradient)+potential)/(8*xp.pi)
            result.append(energy)
        return xp.stack(result)
    return jax.jit(jax.vmap(evaluate))


def run_transit(source,config,directory):
    plan=preflight(source,config)
    from .dragging_falloff import load_state,FactoredDraggingGeometry
    from .transport import MPDSystem,matched_controls
    from .transit import strict_gates
    from .workflow import write_json
    p,u,_=load_state(source)
    if p.jax.devices()[0].platform!='gpu':raise ValueError('GPU required')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    geometry=FactoredDraggingGeometry(p,u);xp=p.xp;d=xp.diag(xp.array([1.,1.,-1.,1.]))
    system=MPDSystem(geometry.metric);reverse=MPDSystem(lambda x:d@geometry.metric(d@x)@d)
    states=matched_controls(system,[plan['launch_rho'],0.,10.],spin=.001,speed=-.5)
    reflected=states['positive'].copy();r=np.diag([1.,1.,-1.,1.])
    reflected[:4]=r@reflected[:4];reflected[4:8]=r@reflected[4:8]
    reflected[8:]=(r@reflected[8:].reshape(4,4)@r).ravel();states['reversed']=reflected
    write_json(directory/'manifest.json',dict(config=config,plan=plan,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),platform='gpu',float64=True,
        scope='Finite matched-energy off-axis annular transit; no escape, trapping, acceleration or stability claim.'))
    density=density_evaluator(geometry);records={};tracks={};ok=True;count=0
    for rk,rtol in enumerate(config['rtols']):
        rows={}
        for label,initial in states.items():
            engine=reverse if label=='reversed' else system
            track=engine.integrate(initial,duration=100.,rtol=rtol,atol=rtol*.01,max_step=.4,
                                   inner_radius=1.,outer_radius=100.,target_z=-10.,samples=1001)
            count+=1;name=f'rk{rk}_{label}';points=track['state'][:,:4]
            energies=np.concatenate([np.asarray(density(xp.asarray(points[i:i+32]))) for i in range(0,len(points),32)]).T
            channel=channel_gate(track['state'],energies,plan['peak_densities'],plan['rho_min'],plan['rho_max'])
            gates=strict_gates(track)
            row=dict(gates=gates,channel=channel,stop=track['stop'],launch=track['invariants'][0],
                     final=track['invariants'][-1],coordinate_time=float(track['state'][-1,0]),
                     proper_time=float(track['time'][-1]),final_position=track['state'][-1,1:4].tolist())
            np.savez_compressed(directory/f'{name}.npz',time=track['time'],state=track['state'],density=energies)
            write_json(directory/f'{name}.json',row);rows[label]=row;tracks[name]=track
            ok=ok and gates['accepted'] and channel['accepted'] and track['stop']=='target_z'
            print(f'[annular-transit] {name}: stop={track["stop"]}, conservation={gates["accepted"]}, channel={channel["accepted"]}',flush=True)
        a,b=tracks[f'rk{rk}_positive'],tracks[f'rk{rk}_reversed']
        symmetry=float(np.max(abs(a['state'][:,:4]-b['state'][:,:4]@r)))
        records[f'rk{rk}']=dict(controls=rows,reversal_error=symmetry);ok=ok and symmetry<1e-7
        write_json(directory/'progress.json',records)
    comparisons={}
    for label in states:
        a,b=tracks['rk0_'+label],tracks['rk1_'+label]
        timing=abs(float(a['state'][-1,0]-b['state'][-1,0]))
        position=float(np.max(abs(a['state'][:,1:4]-b['state'][:,1:4])))
        comparisons[label]=dict(time=timing,position=position,accepted=bool(max(timing,position)<1e-7))
        ok=ok and comparisons[label]['accepted']
    launch_energies=[v['launch']['energy'] for group in records.values() for v in group['controls'].values()]
    energy_error=max(launch_energies)-min(launch_energies)
    result=dict(accepted=bool(ok and count==8 and energy_error<1e-12),matched_energy_error=energy_error,
        tracks=count,records=records,rk_comparisons=comparisons,
        seconds=time.monotonic()-started,stability='not_assessed',
        scope='Finite passage inside the component-wise 1e-6 matter gap; no asymptotic ejection or stability claim.')
    write_json(directory/'outcome.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config',type=Path)
    for key in ('source','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());plan=preflight(args.source,config)
    if args.dry_run:print(json.dumps(plan,indent=2));return 0
    if args.gpu<0:parser.error('nonnegative GPU required')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    return 0 if run_transit(args.source,config,args.out)['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
