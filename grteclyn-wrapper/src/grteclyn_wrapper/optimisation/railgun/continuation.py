"""Bounded two-field homotopy from a spherical star to an integer-winding ring.

The new field starts from a solved bound KG eigenmode on the spherical metric,
not an assumed hydrogenic profile. Its existence and a connecting nonlinear
branch are tested, never guaranteed. k is never interpolated. At the endpoint,
the small k=0 component is explicitly removed together with its undetermined
zero-amplitude frequency, and the pure ring is freshly solved on three grids.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import numpy as np
from scipy.linalg import eig

from .model import ScalarField
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval


def transfer_fields(problem,old,u):
    """Move only matching scalar species; new species keep their own centre BC."""
    arrays,frequencies=problem.unpack(problem.seed())
    source,oldfreq=old.unpack(np.asarray(u))
    s=np.ones(problem.nx+1)
    s[1:]=(problem.r[1:]-old.length)/(problem.r[1:]+old.length)
    bx=cheb_eval(old.s,np.eye(old.nx+1),s)
    by=cheb_eval(old.y,np.eye(old.ny+1),problem.y)
    for name in ('f','w','N','b'):arrays[name]=bx@source[name]@by.T
    signature=lambda f:(f.winding,f.parity,f.mass,f.quartic,f.sextic)
    for i,field in enumerate(problem.fields):
        matches=[j for j,f in enumerate(old.fields) if signature(f)==signature(field)]
        if len(matches)>1:raise ValueError('ambiguous duplicate scalar species in continuation seed')
        if matches:
            j=matches[0]
            arrays[f'q{i}']=bx@source[f'q{j}']@by.T
            frequencies[i]=oldfreq[j]
    return problem.pack(arrays,frequencies)


def linear_bound_seed(problem,u,*,index=1):
    """Integer-l radial KG eigenmode on a demonstrably spherical nonrotating metric."""
    arrays,frequencies=problem.unpack(np.asarray(u))
    field=problem.fields[index]
    if not field.degree:
        raise ValueError('new winding/odd field must have nonzero regular degree')
    for name in ('f','b'):
        if np.max(np.ptp(arrays[name],axis=1)) > 1e-8:
            raise ValueError('linear seed requires a spherical background')
    if max(np.max(abs(arrays['w'])),np.max(abs(arrays['N']))) > 1e-8:
        raise ValueError('linear seed requires a nonrotating spherical background')
    r,dr,ddr=problem.ri[:,0],problem.dr[:,0],problem.ddr[:,0]
    f=arrays['f'][1:-1,-1]
    b=1+arrays['b'][1:-1,-1]
    bs=(problem.dx@arrays['b'])[1:-1,-1]
    a2=r*r/dr**2
    a1=2*r/dr-r*r*ddr/dr**3+a2*bs/b
    operator=(a2[:,None]*problem.dxx[1:-1]+a1[:,None]*problem.dx[1:-1])[:,1:-1]
    operator-=np.diag(field.degree*(field.degree+1)+field.mass**2*b*b*r*r*np.exp(-f))
    weight=b*b*r*r*np.exp(-2*f)
    eigenvalues,vectors=eig(-operator,np.diag(weight))
    candidates=[]
    for j,value in enumerate(eigenvalues):
        if (not np.isfinite(value) or abs(value.imag)>1e-8*max(1.,abs(value.real))
                or not 0 < value.real < field.mass**2*(1-1e-8)):
            continue
        radial=np.r_[0.,vectors[:,j].real,0.]
        resolved=radial[abs(radial)>1e-5*np.max(abs(radial))]
        if np.any(resolved[:-1]*resolved[1:]<0):continue
        anchor=float(problem.anchors[index]@radial)
        if abs(anchor) < 1e-12*np.max(abs(radial)):continue
        radial*=field.amplitude/anchor
        residual=operator@radial[1:-1]+value.real*weight*radial[1:-1]
        relative=float(np.max(abs(residual))/max(np.max(abs(operator@radial[1:-1])),1e-300))
        if relative>1e-8:continue
        candidates.append((float(value.real),radial,relative))
    if not candidates:
        raise RuntimeError('no resolved nodeless bound KG eigenmode; homotopy was not started')
    omega2,radial,error=min(candidates,key=lambda candidate:candidate[0])
    arrays[f'q{index}']=radial[:,None]*np.ones((1,problem.ny+1))
    frequencies[index]=np.sqrt(omega2)
    return problem.pack(arrays,frequencies),dict(frequency=float(np.sqrt(omega2)),
                relative_linear_residual=error,radial_nodes=0,winding=field.winding,
                initialization='bound KG eigenmode on the spherical background')


def run_homotopy(source,config,directory):
    from .problem import RingProblem
    from .workflow import load_state,save_state,write_json,run_study
    from .diagnostics import validate
    from ..solver.newton import newton
    old,old_u,metadata=load_state(source)
    if not metadata.get('validated') or len(old.fields)!=1 or old.fields[0].degree!=0:
        raise ValueError('homotopy requires an accepted one-field even k=0 background')
    target=ScalarField(**config['ring_field'])
    if target.winding==0:raise ValueError('target ring needs a nonzero integer winding')
    steps=int(config.get('steps',8));budget=int(config.get('max_solves',24))
    max_splits=int(config.get('max_splits',6));floor=float(config.get('old_amplitude_floor',1e-3))
    epsilon=float(config.get('initial_amplitude',1e-3))
    if not (steps>=2 and budget>=steps+1 and 0<floor<1 and 0<epsilon<=target.amplitude and max_splits>=0):
        raise ValueError('invalid bounded homotopy schedule')
    grids=config.get('grids',[[56,8],[72,10],[96,12]])
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    write_json(directory/'manifest.json',dict(config=config,source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                                             stability='not_assessed',winding_interpolation=False))
    start=old.fields[0]
    first=RingProblem([start,replace(target,amplitude=epsilon)],nx=grids[0][0],ny=grids[0][1],length=old.length)
    seed=transfer_fields(first,old,old_u)
    try:
        seed,mode=linear_bound_seed(first,seed)
    except RuntimeError as error:
        outcome=dict(accepted=False,reason=str(error),solves=0,stability='not_assessed')
        write_json(directory/'outcome.json',outcome);return outcome
    write_json(directory/'linear_mode.json',mode)
    previous=(first,seed);current=None;splits=0;solves=0;records=[]
    pending=list(np.linspace(0.,1.,steps+1))
    while pending and solves<budget:
        t=float(pending.pop(0))
        fields=[replace(start,amplitude=start.amplitude*max(1-t,floor)),
                replace(target,amplitude=epsilon*(target.amplitude/epsilon)**t)]
        p=RingProblem(fields,nx=grids[0][0],ny=grids[0][1],length=old.length)
        u0=p.transfer(*previous)
        u,info=newton(p.residual,p.jacobian,u0,tol=config.get('newton_tol',1e-12),
                      max_iter=config.get('max_iter',30),verbose=True)
        solves+=1
        save_state(directory/f'attempt_{solves:03d}.npz',p,u)
        record=validate(p,u,info)
        record.update(progress=t,attempt=solves)
        write_json(directory/f'attempt_{solves:03d}.json',record);records.append(record)
        print(f'[homotopy] attempt={solves} t={t:g} verdict={record["verdict"]}',flush=True)
        if record['verdict']=='PASS':
            previous=(p,u);current=t
        elif current is not None and splits<max_splits and t-current>1e-4:
            pending[:0]=[(current+t)/2,t];splits+=1
        else:break
    if current!=1.:
        outcome=dict(accepted=False,reason='homotopy_unresolved',solves=solves,splits=splits,
                     last_progress=current,stability='not_assessed')
        write_json(directory/'outcome.json',outcome);return outcome
    # A zero-amplitude field has no determined eigenfrequency. Remove both its
    # grid block and border explicitly; do not let Newton inherit a null row.
    pure=RingProblem([target],nx=grids[0][0],ny=grids[0][1],length=old.length)
    guess=transfer_fields(pure,*previous)
    seed_path=directory/'pure_ring_seed.npz';save_state(seed_path,pure,guess)
    final_config={k:v for k,v in config.items() if k in ('newton_tol','max_iter','equation_tol','tail_tol','observable_tol')}
    final_config.update(fields=[target.to_dict()],grids=grids,length=old.length)
    outcome=run_study(final_config,directory/'pure_ring',seed_path=seed_path)
    outcome.update(homotopy_solves=solves,old_component_removed=True,stability='not_assessed')
    write_json(directory/'outcome.json',outcome)
    return outcome
