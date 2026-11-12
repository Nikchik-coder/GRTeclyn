"""Bounded, matched-energy axial transport with explicit finite-radius endpoints."""
from __future__ import annotations
from grteclyn_stationary.provenance import source_revision
import hashlib
from pathlib import Path
import time
import numpy as np
from grteclyn_stationary.railgun.transport import MPDSystem, matched_controls
from grteclyn_stationary.railgun.workflow import load_state, write_json
from grteclyn_stationary.railgun.geometry import RingGeometry
from grteclyn_stationary.railgun.corridor import CartesianCorridor


def strict_gates(track,tolerance=1e-9):
    first=track['invariants'][0]
    # Zero spin/axial J have no meaningful relative error; use unit mass
    # units for zero invariants, and relative errors for nonzero invariants.
    drift={key:value/(abs(first[key]) if abs(first[key])>1e-14 else 1.)
           for key,value in track['absolute_drift'].items()}
    accepted=(track['integrator_success'] and track['stop']!='spin_limit'
              and all(np.isfinite(v) and v<tolerance for v in drift.values())
              and track['ssc_max']<tolerance and track['norm_error']<tolerance)
    return dict(accepted=bool(accepted),normalised_drift=drift,tolerance=tolerance,
                zero_invariant_scale='unit rest mass units',ssc_max=track['ssc_max'],
                norm_error=track['norm_error'])


def run_transit(source,profile,directory,*,spin=1e-3,z0=10.,speed=-.5,duration=120.,
                rtols=(2e-11,2e-12),max_step=.4,energy_offsets=(-2e-5,0.,2e-5)):
    """Four controls, two tolerances, high-speed and near-E=1 finite transits.

    E=1 is the asymptotic unit-mass threshold in an asymptotically flat
    stationary geometry. Reaching z=-z0 establishes transit, not escape.
    """
    import json
    from scipy.optimize import brentq
    if spin<=0 or z0<=0 or speed>=0 or duration<=0 or len(rtols)!=2:
        raise ValueError('positive spin/z0/duration, inward speed and two RK tolerances required')
    profile=Path(profile)
    prior=json.loads((profile/'outcome.json').read_text())
    manifest=json.loads((profile/'manifest.json').read_text())
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    if not prior['accepted'] or digest!=manifest['source_sha256']:
        raise ValueError('an accepted Run A for this exact background is required')
    p,u,meta=load_state(source)
    if not meta.get('validated') or p.jax.devices()[0].platform!='gpu':
        raise ValueError('an accepted GPU background is required')
    started=time.monotonic();directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    config=dict(source_sha256=digest,profile_manifest=manifest,spin=spin,z0=z0,
                speed=speed,duration=duration,rtols=list(rtols),max_step=max_step,
                energy_offsets=list(energy_offsets),commit=source_revision(),platform='gpu',float64=True)
    write_json(directory/'manifest.json',config)
    geometry=CartesianCorridor(RingGeometry(p,u),radius=manifest['corridor_radius'],
                                degree=manifest['corridor_degree'])
    certificate=geometry.certify();write_json(directory/'corridor.json',certificate)
    if not certificate['accepted']:
        outcome=dict(accepted=False,reason='core_certification');write_json(directory/'outcome.json',outcome);return outcome
    system=MPDSystem(geometry.metric,regular_origin=True)
    # Reflect phi -> -phi. This reverses the background angular momentum;
    # an axial spin is a pseudovector and reverses under this reflection.
    xp=p.xp if hasattr(p,'xp') else p.jax.numpy
    reflection=xp.diag(xp.array([1.,1.,-1.,1.]))
    reverse=MPDSystem(lambda x:reflection@geometry.metric(reflection@x)@reflection,regular_origin=True)
    position=[0.,0.,z0]
    target=system.invariants(system.initial_state(position,speed=speed))['energy']
    regimes=[('fast',target)]+[(f'near_{i}',1.+offset) for i,offset in enumerate(energy_offsets)]
    records={};all_ok=True
    for regime,energy in regimes:
        def error(v):return system.invariants(system.initial_state(position,speed=v))['energy']-energy
        branch_speed=brentq(error,-.95,0.,xtol=1e-14)
        states=matched_controls(system,position,spin=spin,speed=branch_speed)
        for index,rtol in enumerate(rtols):
            controls={}
            tracks={}
            for label,state in states.items():
                track=system.integrate(state,duration=duration,rtol=rtol,atol=rtol*.01,
                       max_step=max_step,inner_radius=0.,target_z=-z0,samples=1001)
                tracks[label]=track
                prefix=f'{regime}_rk{index}_{label}'
                np.savez_compressed(directory/f'{prefix}.npz',time=track['time'],state=track['state'])
                gates=strict_gates(track);all_ok=all_ok and gates['accepted']
                last=track['state'][-1];velocity=np.asarray(system._rhs_jit(xp.asarray(last)))[:4]
                g=np.asarray(geometry.metric(last[:4]));alpha=np.sqrt(-1/np.linalg.inv(g)[0,0])
                controls[label]=dict(gates=gates,stop=track['stop'],launch=track['invariants'][0],
                     final=track['invariants'][-1],proper_time=float(track['time'][-1]),
                     coordinate_time=float(last[0]),final_z=float(last[3]),
                     final_local_axial_speed=float(np.sqrt(g[3,3])*velocity[3]/(alpha*velocity[0])),
                     crossed_centre=bool(np.min(track['state'][:,3])<0.))
                write_json(directory/f'{prefix}.json',controls[label])
                print(f'[transit] {prefix} {track["stop"]} strict={gates["accepted"]}',flush=True)
            # Use the fully reflected initial tensor, rather than independently
            # choosing a different energy root, for the exact reversal control.
            initial=states['positive'].copy();d=np.diag([1.,1.,-1.,1.])
            initial[:4]=d@initial[:4];initial[4:8]=d@initial[4:8]
            initial[8:]=(d@initial[8:].reshape(4,4)@d).ravel()
            track=reverse.integrate(initial,duration=duration,rtol=rtol,atol=rtol*.01,
                  max_step=max_step,inner_radius=0.,target_z=-z0,samples=1001)
            prefix=f'{regime}_rk{index}_reversed'
            np.savez_compressed(directory/f'{prefix}.npz',time=track['time'],state=track['state'])
            gates=strict_gates(track)
            # Both sample grids span their terminal event; compare the transit
            # times as well as the signed axial curves at the same time fraction.
            axial_error=float(np.max(abs(track['state'][:,3]-tracks['positive']['state'][:,3])))
            time_error=abs(float(track['time'][-1]-tracks['positive']['time'][-1]))
            symmetry_ok=axial_error<1e-9 and time_error<1e-9
            controls['reversed']=dict(gates=gates,stop=track['stop'],
                axial_symmetry_error=axial_error,proper_time_symmetry_error=time_error,
                symmetry_accepted=bool(symmetry_ok))
            write_json(directory/f'{prefix}.json',controls['reversed'])
            all_ok=all_ok and gates['accepted'] and symmetry_ok
            records[f'{regime}_rk{index}']=dict(energy=energy,controls=controls,
                coordinate_transit_split=(controls['positive']['coordinate_time']-controls['negative']['coordinate_time'])
                     if all(controls[k]['stop']=='target_z' for k in ('positive','negative')) else None)
            if regime=='fast':
                all_ok=all_ok and all(controls[k]['stop']=='target_z' for k in ('zero','positive','negative','reversed'))
            write_json(directory/'progress.json',records)
    comparisons={}
    for regime,_ in regimes:
        a,b=(records[f'{regime}_rk{i}'] for i in range(2))
        errors={label:abs(a['controls'][label]['coordinate_time']-b['controls'][label]['coordinate_time'])
                for label in ('zero','positive','negative')}
        comparisons[regime]=errors
        all_ok=all_ok and max(errors.values())<1e-8
    outcome=dict(accepted=bool(all_ok),records=records,rk_coordinate_time_difference=comparisons,
        seconds=time.monotonic()-started,with_ring_spin='negative' if prior['observables']['J_volume']<0 else 'positive',
        scope='Finite z=+10 to z=-10 transit. E near one brackets the asymptotic threshold; it does not establish escape.',
        asymptotic_speed='Equal Killing energy and rest mass imply equal speeds at infinity.',
        valve='No spin-selective escape claim follows from finite-radius transit.')
    write_json(directory/'outcome.json',outcome);return outcome
