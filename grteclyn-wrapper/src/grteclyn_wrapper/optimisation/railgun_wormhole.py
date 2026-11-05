"""A bounded, symmetric throat insertion starting from the weak railgun ring.

The archive supplies an initial guess, never a superposed solution. Both ends
are nonrotating at infinity; ring matter sources all frame dragging. V=0 is
kept fixed. This first experiment establishes a branch and matched controls,
not an optimisation or a stability result. No stronger ring is auto-dispatched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, cheb_eval, lobatto


def validate_plan(plan):
    """Keep the prepared pilot inside its declared resource and solve budget."""
    stage=plan.get('stage','ring_and_control')
    if stage not in ('ring_and_control','ring_validation'):
        raise ValueError('unknown study stage')
    validation_only=stage=='ring_validation'
    ceiling=(240,40) if validation_only else (210,36)
    grids=plan['grids']
    if (len(grids)!=3 or any(len(g)!=2 or g[0]%2 or not 6<=g[0]<=ceiling[0]
                            or not 3<=g[1]<=ceiling[1] for g in grids)
            or any(a[0]>=b[0] or a[1]>=b[1] for a,b in zip(grids,grids[1:]))):
        raise ValueError('expected three increasing grids within the pilot ceiling')
    if validation_only:
        if (plan['max_control_steps']!=0 or plan['max_solves']!=3
                or plan.get('independent_points')!=[49,21]
                or not plan.get('restart_source') or len(plan.get('restart_sha256',''))!=64):
            raise ValueError('validation-only stage needs three solves, dense checks and a pinned restart')
    elif (not 1<=plan['max_control_steps']<=12
            or not 2*len(grids)+plan['max_control_steps']<=plan['max_solves']<=18
            or 'restart_source' in plan or 'independent_points' in plan):
        raise ValueError('invalid bounded solve budget')
    if plan['max_newton_iterations']!=24:
        raise ValueError('invalid bounded solve budget')
    if (plan['wall_seconds']!=3600 or plan['threads']!=4 or plan['memory_gib']!=160
            or plan['checkpoints'] is not False):
        raise ValueError('resource caps differ from the prepared dispatcher')
    for key in ('throat_radius','control_J_step','tidal_factor','energy_budget'):
        if not np.isfinite(plan[key]) or plan[key]<=0:
            raise ValueError(f'{key} must be finite and positive')


def read_source(plan):
    """Read the pinned nodal archive without starting JAX or a GPU."""
    root = Path(plan['source_directory'])
    for name, digest in plan['source_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'railgun source hash mismatch: {name}')
    outcome = json.loads((root/'outcome.json').read_text())
    record = json.loads((root/'grid_128x16.json').read_text())
    if not outcome.get('accepted') or record['verdict'] != 'PASS':
        raise ValueError('source lacks accepted three-grid evidence')
    with np.load(root/'grid_128x16.npz', allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.array(data['u'])
    if (meta['model'] != 'canonical_regular_centre' or meta.get('representation')
            or len(meta['fields']) != 1):
        raise ValueError('bridge supports only the pinned single-field nodal source')
    field = meta['fields'][0]
    if (field['winding'] != 1 or field['parity'] != 'even'
            or field['quartic'] != 0 or field['sextic'] != 0):
        raise ValueError('expected the canonical free even k=1 ring')
    shape = (meta['nx']+1, meta['ny']+1)
    n = math.prod(shape)
    if u.shape != (5*n+1,) or not np.isfinite(u).all():
        raise ValueError('invalid source vector')
    arrays = {k:u[i*n:(i+1)*n].reshape(shape) for i,k in enumerate(('F','W','N','b','Z'))}
    return meta, arrays, float(u[-1]), record


def ellis(radius, nx, ny):
    sx,_ = lobatto(nx); sy,_ = lobatto(ny)
    zero = np.zeros((nx+1,ny+1))
    return dict(sx=sx,sy=sy,F=zero.copy(),W=zero.copy(),N=zero.copy(),B=zero+1,
                PSI=np.pi/2*(sx[:,None]-1)+zero,sigma=radius,xi_t=0.,
                surface_coefficients=np.zeros(ny+1),map=ArctanMap(eta0=1.),
                omega=0.,psim=-np.pi,gamma=0.)


def prepare_seed(plan):
    """Smoothly pull the ring onto r=sigma*sqrt(eta^2+1), on both ends.

    This changes the radial metric and topology and therefore is NOT a
    coordinate transformation of a solution. The phantom kink, geometry,
    frequency and entire ring profile must subsequently be solved together.
    """
    if plan.get('stage')=='ring_validation':
        return read_restart(plan)
    from scipy.optimize import brentq
    from .exploration import matter_anchor
    meta, arrays, frequency, record = read_source(plan)
    radius = float(plan['throat_radius'])
    nx,ny = plan['grids'][0]
    s = ellis(radius,nx,ny)
    source_x,_ = lobatto(meta['nx']); source_y,_ = lobatto(meta['ny'])
    def at(key, r, y):
        r = np.asarray(r)
        xr = 1-2*meta['length']/(r+meta['length'])
        return cheb_eval(source_y,cheb_eval(source_x,arrays[key],xr).T,y).T
    mu,weight = np.polynomial.legendre.leggauss(64)
    y = 2*mu**2-1
    def area_sigma(sig):
        f,n,b = (at(key,[sig],y)[0] for key in ('F','N','b'))
        return 2*np.pi*sig**2*np.sum(weight*(1+b)**2*np.exp(-f+n*(1-mu**2)/2))
    sigma = brentq(lambda sig:area_sigma(sig)-4*np.pi*radius**2,radius/4,2*radius)
    eta = s['map'].eta(s['sx'])
    r = sigma*np.sqrt(1+eta**2)
    for key in arrays:
        values = at(key,r,s['sy'])
        values[[0,-1]] = 0.
        s['B' if key=='b' else key] = 1+values if key=='b' else values
    s['W'] *= sigma  # archive W is physical, wormhole W is in grid units
    s.update(sigma=sigma,frequency=frequency)
    anchor_r = meta['fields'][0]['anchor_radius']
    if anchor_r <= sigma:
        raise ValueError('source amplitude anchor lies inside the inserted throat')
    xi = float(s['map'].xi_of_eta(np.sqrt((anchor_r/sigma)**2-1)))
    config = dict(m=0.,q=[0.,0.,0.],gamma=0.,J=record['J_volume'],
                  rotation_control='nonrotating_ends',matter='winding',winding_k=1,
                  matter_mass=meta['fields'][0]['mass'],zeta_anchor_xi=xi)
    config['amplitude'] = matter_anchor(s['Z'],s['sx'],config)
    return s,config


def read_restart(plan):
    """Reuse the original amplitude border and fields, without inheriting PASS."""
    from .exploration import load_seed
    path=Path(plan['restart_source'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=plan['restart_sha256']:
        raise ValueError('restart hash mismatch')
    state,meta=load_seed(path)
    config=meta['config']
    expected=dict(m=0.,q=[0.,0.,0.],gamma=0.,rotation_control='nonrotating_ends',
                  matter='winding',winding_k=1,matter_mass=1.)
    if (any(config.get(k)!=v for k,v in expected.items()) or
            meta.get('pin')!=['minimal_area',4*np.pi*plan['throat_radius']**2] or
            state['omega']!=0. or not 0<config.get('zeta_anchor_xi',0)<1 or
            config.get('amplitude',0)<=0 or
            not np.isfinite(config.get('amplitude',np.nan))):
        raise ValueError('restart is not the same fixed-area weak-ring model')
    return state,config


def ring_geometry(state, config):
    """Common-point diagnostics; matter edges mean half peak, not vacuum."""
    from .exoticity import _grid_eval
    from .exploration import physical_throat
    sx,sy = state['sx'],state['sy']; _,dx=lobatto(len(sx)-1)
    x = np.linspace(-.995,.995,1601)
    def at(a): return _grid_eval(sx,sy,a,x,[-1.])[:,0]
    f,w,n,b,z = (at(state[k]) for k in ('F','W','N','B','Z'))
    sig = state['sigma']; eta=state['map'].eta(x); h=1+eta**2
    dr = at(dx@state['Z'])/state['map'].deta(x)
    nu=n; inverse=np.exp(f-nu)/(sig*b)**2
    freq=(state['frequency']+config['winding_k']*w/sig)*np.exp(-f/2)
    rho=(freq**2*z*z+inverse*dr*dr+
         config['winding_k']**2*z*z*np.exp(f)/(sig**2*b*b*h)
         +config['matter_mass']**2*z*z)/(8*np.pi)
    circumference_radius=sig*b*np.exp(-f/2)*np.sqrt(h)
    throat=physical_throat(state)
    positive=np.flatnonzero(x>0); peak=positive[np.argmax(rho[positive])]
    throat_x=float(np.polynomial.chebyshev.chebval(-1,state['surface_coefficients']))
    ratio=float(np.interp(throat_x,x,rho)/rho[peak]) if rho[peak]>0 else float('inf')
    defects=[np.max(abs(state[k]-state[k][::-1]))/max(1.,np.max(abs(state[k])))
             for k in ('F','W','N','B','Z')]
    defects.append(np.max(abs(state['PSI']+state['PSI'][::-1]-state['psim'])))
    beta_over_alpha=abs(b*w)*np.exp(-f)*np.sqrt(h)
    gtt=-np.exp(f)*(1-beta_over_alpha**2)
    return dict(ring_peak_radius=float(circumference_radius[peak]),
                ring_peak_xi=float(x[peak]),throat_density_over_peak=ratio,
                ring_outside_throat=bool(x[peak]>throat_x and
                    circumference_radius[peak]>throat['R_e'] and ratio<.5),
                reflection_defect=float(max(defects)),
                equatorial_shift_over_lapse_max=float(max(beta_over_alpha)),
                equatorial_gtt_max=float(max(gtt)),equatorial_ergoregion_sampled=bool(max(gtt)>0))


def run(plan, out):
    from .exploration import solve_trial,save_trial
    from .resolution import check_candidate,save_checked
    from .study import release_solver,write_json
    from .study_validation import validate
    from .study_diagnostics import tidal_envelope
    validate_plan(plan)
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    write_json(out/'plan.json',plan)
    package=Path(__file__).parent
    paths=list(package.rglob('*.py'))+list((package.parent/'analysis/spinning_wormhole').glob('*.py'))
    write_json(out/'code.json',dict(commit=subprocess.check_output(
        ['git','rev-parse','HEAD'],text=True).strip(),
        sha256={str(p.relative_to(package.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(paths)}))
    seed,config=prepare_seed(plan)
    radius=plan['throat_radius']; pin=('minimal_area',4*np.pi*radius**2)
    d2=radius**2; grids=[tuple(g) for g in plan['grids']]
    baseline=ellis(radius,*grids[0]); basecfg=dict(m=0.,q=[0.,0.,0.],gamma=0.,J=0.)
    reference_peak=tidal_envelope(baseline)['tidal_peak']
    def validator(s,c,r):
        r=validate(s,c,r,reference_peak=reference_peak,tidal_factor=plan['tidal_factor'],
                   energy_budget=plan['energy_budget'] if c.get('matter') else None,
                   independent_points=plan.get('independent_points'))
        if c.get('matter'):
            r.update(ring_geometry(s,c))
            resolved=s['Z'][abs(s['Z'])>1e-5*np.max(abs(s['Z']))]
            if r['Q_b']<=1e-8 or not len(resolved) or np.min(resolved)*np.max(resolved)<0:
                r['rejection_reasons'].append('nonzero_nodeless_ring')
            if not r['ring_outside_throat']:
                r['rejection_reasons'].append('ring_does_not_surround_throat')
            if r['reflection_defect']>1e-7:
                r['rejection_reasons'].append('reflection_symmetry')
            if abs(r['J_b']/2-r['J_measured'])>1e-6*max(1.,abs(r['J_measured'])):
                r['rejection_reasons'].append('symmetric_angular_momentum_balance')
            if r['rejection_reasons']: r['verdict']='ABOVE_GATE'
        return r
    baseline_row=validator(baseline,basecfg,dict(verdict='PASS'))
    save_trial(out/'static_reference.npz',baseline,basecfg,baseline_row,pin)
    if baseline_row['verdict']!='PASS':
        write_json(out/'outcome.json',dict(reason='static_reference_failed',solves=0))
        return 2
    seed_name='restart_seed.npz' if plan.get('stage')=='ring_validation' else 'mapped_seed.npz'
    save_trial(out/seed_name,seed,config,dict(verdict='UNSOLVED',source=plan.get(
        'restart_source',plan['source_directory'])),pin)
    result,ring=check_candidate(seed,config,grids,pin,d2,out/'ring',
                  validator=validator,score_key='X_full',perturb_seed=True)
    outcome=dict(ring_accepted=False,source=plan['source_directory'],
                 stage=plan.get('stage','ring_and_control'),
                 stability='not_assessed',solves=len(result['records']))
    if not result['passed']:
        outcome['reason']='ring_refinement_failed'
        write_json(out/'outcome.json',outcome); return 2
    rows=result['records']; last=rows[-1]
    drift=max(abs(rows[-1][k]-rows[-2][k])/max(abs(rows[-1][k]),1e-12)
              for k in ('E_b','Q_b','J_measured','ring_peak_radius','equatorial_shift_over_lapse_max'))
    outcome['ring_observable_relative_drift']=float(drift)
    if drift>1e-6:
        outcome['reason']='ring_observable_refinement_failed'
        write_json(out/'outcome.json',outcome); return 2
    config=dict(config,J=last['J_measured'])
    save_checked(out/'accepted_ring.npz',ring,config,dict(source=plan['source_directory'],pin=list(pin)),result)
    outcome.update(ring_accepted=True,J=config['J'],X_ring=last['X_full'],
                   X_static=baseline_row['X_full'],static_fractional_reduction=1-last['X_full']/baseline_row['X_full'])
    write_json(out/'outcome.json',outcome)
    if plan.get('stage')=='ring_validation':
        outcome.update(reason='ring_validation_complete',matched_control_status='not_run')
        write_json(out/'outcome.json',outcome)
        return 0
    # A failed matched control gives no ring-only reduction claim. One fixed
    # step ladder, no retries, no bisection, no alternate source or larger grid.
    count=max(1,math.ceil(abs(config['J'])/plan['control_J_step']))
    if count>plan['max_control_steps']:
        outcome['reason']='matched_control_outside_budget'
        write_json(out/'outcome.json',outcome); return 2
    control=baseline
    try:
        for i,j in enumerate(np.linspace(0,config['J'],count+1)[1:]):
            cc=dict(basecfg,J=float(j))
            outcome['solves']+=1
            control,row=solve_trial(control,cc,*grids[0],pin,d2,max_iter=24,newton_tol=1e-14)
            save_trial(out/f'control_step_{i+1:02d}.npz',control,cc,row,pin)
            release_solver()
            if row['verdict']!='PASS': raise RuntimeError('matched control constraints failed')
        control_result,control=check_candidate(control,cc,grids,pin,d2,out/'matched_spin',
                    validator=validator,score_key='X_full',perturb_seed=True)
        outcome['solves']+=len(control_result['records'])
        if not control_result['passed']: raise RuntimeError('matched control refinement failed')
        save_checked(out/'matched_spin.npz',control,cc,dict(pin=list(pin)),control_result)
        xc=control_result['records'][-1]['X_full']
        outcome.update(X_matched_spin=xc,matched_spin_fractional_reduction=1-last['X_full']/xc,
                       matched_control_accepted=True)
    except (ValueError,RuntimeError,FloatingPointError) as err:
        outcome.update(matched_control_accepted=False,reason=str(err))
    write_json(out/'outcome.json',outcome)
    return 0 if outcome.get('matched_control_accepted') else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--gpu',type=int);parser.add_argument('--run',action='store_true')
    args=parser.parse_args();plan=json.loads(Path(args.config).read_text())
    validate_plan(plan)
    read_source(plan)
    if not args.run:
        print(json.dumps(dict(plan=plan,output=args.out,status='PREPARED_ONLY'),indent=2));return 0
    if args.gpu is None: parser.error('--run needs an explicitly selected GPU')
    from .solver.device import select_device,configure_jax
    select_device(args.gpu,256)
    jax=configure_jax()
    if jax.default_backend()!='gpu' or not jax.config.x64_enabled:
        raise RuntimeError('the pilot requires CUDA and float64')
    print('devices:',jax.devices(),'float64:',jax.config.x64_enabled,flush=True)
    return run(plan,args.out)


if __name__=='__main__':
    raise SystemExit(main())
