"""A bounded counter-rotating branch, seeded by a two-dimensional KG mode.

The rotating metric makes the frequency problem quadratic: omega enters
as (omega+k*w(r,theta))^2. No spherical separation or winding interpolation
is used. A zero total angular momentum is a border, not a frozen estimate
of either individual field's charge.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import subprocess
import time
import numpy as np
from scipy.linalg import eig
from .model import ScalarField,exprel
from .continuation import transfer_fields


def linear_rotating_seed(problem,u,*,index=1):
    """Solve the full 2D quadratic eigenproblem on the fixed rotating metric."""
    arrays,frequencies=problem.unpack(np.asarray(u))
    field=problem.fields[index];ka=abs(field.winding);odd=field.parity=='odd'
    if not field.degree:raise ValueError('the new field needs nonzero regular degree')
    nr,nt=problem.nx-1,problem.ny+1;n=nr*nt
    jets=problem.jets(arrays)
    r,dr,ddr=problem.ri,problem.dr,problem.ddr
    f,w,b,nn=(jets[name] for name in ('f','w','B','N'))
    y=problem.y[None,:];sk=(1-y)/2;oy=1-y*y
    nu=nn*sk;ef=np.exp(-f);env=np.exp(nu-f)
    bx,by=jets['B_x']/b,jets['B_y']/b
    a2=r*r/dr**2;a1=2*r/dr-r*r*ddr/dr**3
    angular=((4*ka+10)*y+4*ka-2 if odd else (4*ka+6)*y+4*ka+2)
    expand=lambda value:np.broadcast_to(value,(nr,nt)).ravel()
    radial=np.kron(problem.dx[1:-1,1:-1],np.eye(nt))
    radial2=np.kron(problem.dxx[1:-1,1:-1],np.eye(nt))
    angular1=np.kron(np.eye(nr),problem.dy)
    angular2=np.kron(np.eye(nr),problem.dyy)
    weight=ef*b*b*r*r*env
    potential=(-field.degree*(field.degree+1)-2*ka*(1+y)*by
               +(2*(1-y)*by if odd else 0.)-field.winding**2*nn*exprel(nu,np)
               -field.mass**2*b*b*r*r*env)
    operator=(expand(a2/weight)[:,None]*radial2
              +expand((a1+a2*bx)/weight)[:,None]*radial
              +expand(4*oy/weight)[:,None]*angular2
              +expand((-angular+4*oy*by)/weight)[:,None]*angular1)
    operator+=np.diag(expand(potential/weight+field.winding**2*w*w))
    linear=expand(2*field.winding*w)
    companion=np.block([[np.zeros((n,n)),np.eye(n)],[-operator,-np.diag(linear)]])
    values,vectors=eig(companion,check_finite=True)
    candidates=[]
    for j,omega in enumerate(values):
        if not np.isfinite(omega) or abs(omega.imag)>1e-8 or not 0<omega.real<field.mass*(1-1e-8):continue
        q=vectors[:n,j].real
        resolved=q[abs(q)>1e-5*np.max(abs(q))]
        if not len(resolved) or np.min(resolved)*np.max(resolved)<0:continue
        full=np.zeros(problem.shape);full[1:-1]=q.reshape(nr,nt)
        anchor=float(problem.anchors[index]@full[:,-1])
        if abs(anchor)<1e-12*np.max(abs(q)):continue
        full*=field.amplitude/anchor
        q=full[1:-1].ravel();omega=float(omega.real)
        error=operator@q+(linear*omega+omega**2)*q
        relative=float(np.max(abs(error))/max(np.max(abs(operator@q)),1e-300))
        if relative>1e-8:continue
        candidates.append((omega,full,relative))
    if not candidates:raise RuntimeError('no resolved nodeless 2D rotating bound KG mode')
    omega,q,error=min(candidates,key=lambda row:row[0])
    arrays[f'q{index}']=q;frequencies[index]=omega
    seed=problem.pack(arrays,frequencies)
    # Check the independently assembled matrix against the printed PDE rows.
    row=problem.rows(seed)[f'E_q{index}']
    pde_error=float(np.max(abs(row/weight))/max(np.max(abs(omega**2*q[1:-1])),1e-300))
    if pde_error>1e-8:raise RuntimeError('quadratic KG mode disagrees with the field equation')
    return seed,dict(frequency=omega,relative_linear_residual=error,
        printed_pde_relative_residual=pde_error,winding=field.winding,
        angular_dimensions=nt,radial_dimensions=nr,
        initialization='nodeless full 2D quadratic KG bound mode on the rotating metric')


def run_counter_rotation(source,transport,config,directory):
    from .problem import RingProblem
    from .workflow import load_state,save_state,write_json
    from .diagnostics import validate,converged_records
    from ..solver.newton import newton
    previous_stage=json.loads((Path(transport)/'outcome.json').read_text())
    if not previous_stage.get('accepted'):raise ValueError('accepted single-ring transport is required first')
    old,old_u,metadata=load_state(source)
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    transport_manifest=json.loads((Path(transport)/'manifest.json').read_text())
    if digest!=transport_manifest['source_sha256']:raise ValueError('transport background mismatch')
    if not metadata.get('validated') or len(old.fields)!=1 or old.fields[0].winding!=1:
        raise ValueError('an accepted pure k=1 background is required')
    target=ScalarField(**config['second_field'])
    if target.winding!=-2:raise ValueError('this bounded study requires k2=-2')
    grids=config['grids'];coarse=config.get('continuation_grid',grids[0])
    if len(grids)!=3 or any(b[0]<=a[0] or b[1]<=a[1] for a,b in zip(grids,grids[1:])):
        raise ValueError('three increasing recovery grids required')
    budget=int(config.get('max_solves',24));max_splits=int(config.get('max_splits',6))
    cap=float(config.get('amplitude_cap',.08));growth=float(config.get('amplitude_growth',1.6))
    if not (budget>=5 and 0<target.amplitude<cap and growth>1):raise ValueError('invalid continuation budget')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    first=RingProblem([old.fields[0],target],nx=coarse[0],ny=coarse[1],length=old.length)
    if first.jax.devices()[0].platform!='gpu':raise ValueError('GPU execution required')
    manifest=dict(config=config,source_sha256=digest,transport_commit=transport_manifest['commit'],
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        platform='gpu',float64=bool(first.jax.config.jax_enable_x64),stability='not_assessed')
    write_json(directory/'manifest.json',manifest)
    print('[counter] solving the full rotating two-dimensional KG mode',flush=True)
    started=time.monotonic()
    try:
        seed,mode=linear_rotating_seed(first,transfer_fields(first,old,old_u))
    except RuntimeError as error:
        outcome=dict(accepted=False,reason=str(error),solves=0,splits=0,seconds=time.monotonic()-started)
        write_json(directory/'outcome.json',outcome);return outcome
    write_json(directory/'linear_mode.json',mode)
    previous=None;solves=0;splits=0;amplitude=target.amplitude;ready=False
    records=[]
    def attempt(p,guess,kind):
        nonlocal solves
        tick=time.monotonic()
        value,info=newton(p.residual,p.jacobian,guess,tol=config.get('newton_tol',1e-12),
                         max_iter=config.get('max_iter',30),min_updates=2,verbose=True)
        solves+=1;save_state(directory/f'attempt_{solves:03d}.npz',p,value)
        row=validate(p,value,info)
        row.update(attempt=solves,kind=kind,seconds=time.monotonic()-tick,
                   second_amplitude=float(np.exp(value[-1])) if p.target_j is not None else p.fields[1].amplitude)
        write_json(directory/f'attempt_{solves:03d}.json',row)
        print(f'[counter] solve={solves} kind={kind} verdict={row["verdict"]} J={row.get("J_volume")}',flush=True)
        return value,row
    reason='continuation_budget'
    while solves<budget-4:
        p=RingProblem([old.fields[0],replace(target,amplitude=amplitude)],nx=coarse[0],ny=coarse[1],length=old.length)
        guess=seed if previous is None else transfer_fields(p,*previous)
        if previous is not None:
            a,f=p.unpack(guess);a['q1']*=amplitude/previous[0].fields[1].amplitude;guess=p.pack(a,f)
        value,row=attempt(p,guess,'amplitude_continuation')
        if row['verdict']=='PASS':
            previous=p,value
            if row['J_volume']>=0 or abs(row['J_volume'])<.1*max(abs(v) for v in row['matter_J']):
                ready=True;break
            if amplitude>=cap:reason='amplitude_cap_before_zero_J';break
            amplitude=min(cap,amplitude*growth)
        elif previous is not None and splits<max_splits:
            amplitude=np.sqrt(amplitude*previous[0].fields[1].amplitude)
            growth=np.sqrt(growth);splits+=1
        else:reason='continuation_validation';break
    if not ready:
        outcome=dict(accepted=False,reason=reason,solves=solves,splits=splits,seconds=time.monotonic()-started)
        write_json(directory/'outcome.json',outcome);return outcome
    p=RingProblem(previous[0].fields,nx=coarse[0],ny=coarse[1],length=old.length,target_j=0.)
    value,row=attempt(p,transfer_fields(p,*previous),'zero_J_border')
    if row['verdict']!='PASS':
        outcome=dict(accepted=False,reason='zero_J_border_validation',solves=solves,splits=splits)
        write_json(directory/'outcome.json',outcome);return outcome
    previous=p,value
    for nx,ny in grids:
        p=RingProblem(previous[0].fields,nx=nx,ny=ny,length=old.length,target_j=0.)
        value,row=attempt(p,p.transfer(*previous,perturb=1e-5),'three_grid_recovery')
        records.append(row);previous=p,value
        if row['verdict']!='PASS':break
    accepted,drift=converged_records(records)
    charge_drift=None
    if len(records)==3:
        a,b=(np.asarray(r['charges']) for r in records[-2:])
        charge_drift=float(np.max(abs(a-b)/np.maximum(abs(a),abs(b))))
        accepted=accepted and charge_drift<=1e-6 and abs(records[-1]['J_volume'])<=1e-8
    outcome=dict(accepted=bool(accepted),solves=solves,splits=splits,records=records,
        observable_relative_drift=drift,component_charge_relative_drift=charge_drift,
        seconds=time.monotonic()-started,stability='not_assessed')
    if accepted:
        save_state(directory/'accepted.npz',p,value,validated=True)
        outcome['dragging_tail']=dragging_profile(p,value,directory)
    write_json(directory/'outcome.json',outcome);return outcome


def dragging_profile(problem,u,directory):
    """Coordinate angular harmonics; no invariant multipole normalisation claim."""
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval
    a,_=problem.unpack(u)
    mu,weights=np.polynomial.legendre.leggauss(64);mu=(mu+1)/2;weights=weights/2
    angular=cheb_eval(problem.y,np.eye(problem.ny+1),2*mu*mu-1)
    radii=problem.length*np.array([12.,16.,22.,30.,42.,60.])
    radial=cheb_eval(problem.s,np.eye(problem.nx+1),(radii-problem.length)/(radii+problem.length))
    w=radial@a['w']@angular.T
    weight=weights*(1-mu*mu);octupole=5*mu*mu-1
    dip=w@weight/np.sum(weight)
    oct=w@(weight*octupole)/np.sum(weight*octupole**2)
    np.savetxt(Path(directory)/'exterior_dragging.tsv',np.column_stack([radii,dip,oct,radii**3*dip/2,radii**5*oct]),
        header='r\tdipole_angular_coefficient\toctupole_angular_coefficient\tr3_dipole_over_2\tr5_octupole',delimiter='\t')
    finite=problem.r[1:];axis=a['w'][1:,0];equator=a['w'][1:,-1]
    np.savetxt(Path(directory)/'interior_dragging.tsv',np.column_stack([finite,axis,equator]),
               header='r\taxial_omega\tequatorial_omega',delimiter='\t')
    slopes=-np.diff(np.log(np.maximum(abs(oct),1e-300)))/np.diff(np.log(radii))
    return dict(octupole_coordinate_decay_orders=slopes.tolist(),
                interpretation='Angular projection onto 1 and 5*cos(theta)^2-1; coordinate tail, not invariant multipole moments.')


def main():
    import argparse
    import os
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--transport',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text())
    if args.gpu<0:parser.error('GPU must be nonnegative')
    if args.dry_run:
        print(json.dumps(dict(config=config,numerical_execution=False),indent=2));return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR','platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE','false')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    result=run_counter_rotation(args.source,args.transport,config,args.out)
    return 0 if result['accepted'] else 2


if __name__=='__main__':raise SystemExit(main())
