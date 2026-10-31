"""Resumable, one-case-at-a-time stationary studies with shared hard gates.

Legacy optimisation uses search/driver.py unchanged. This workflow accepts
an explicit study configuration and never launches an evolution or a job.
"""
from __future__ import annotations
import dataclasses
import hashlib
import json
from pathlib import Path
import time
import numpy as np

from .exploration import (load_seed,save_trial,solve_trial,physical_throat,bound_mode)
from .resolution import check_candidate,refinement_grids,save_checked
from .surfaces import find_surface
from .study_validation import validate


def release_solver():
    """Compiled closures own problem constants; bound their lifetime per trial."""
    import gc
    import jax
    jax.clear_caches()
    gc.collect()


def load_config(path):
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    with open(path,'rb') as f:
        cfg=tomllib.load(f)
    allowed={'version','tidal_factors','energy_budgets','windings','mass_range',
             'amplitude_seeds','amplitude_max','mass_seeds','candidate_seeds',
             'matter_candidate_seeds'}
    if set(cfg)-allowed:
        raise ValueError(f'unknown study keys: {sorted(set(cfg)-allowed)}')
    defaults=dict(version=1,tidal_factors=[1.,2.,4.],energy_budgets=[.1,.3,1.],
                  windings=[-1,0,1],mass_range=[.5,8.],mass_seeds=[.5,1.,2.,4.,8.],
                  amplitude_seeds=[.01,.03,.1,.3],amplitude_max=.5,candidate_seeds=[],
                  matter_candidate_seeds=[])
    defaults.update(cfg); cfg=defaults
    if cfg['version']!=1: raise ValueError('unsupported study version')
    for key in ('tidal_factors','energy_budgets','mass_seeds','amplitude_seeds'):
        a=np.asarray(cfg[key],dtype=float)
        if a.ndim!=1 or not len(a) or not np.isfinite(a).all() or np.min(a)<=0:
            raise ValueError(f'{key} must contain finite positive numbers')
        if len(set(a))!=len(a): raise ValueError(f'duplicate {key}')
    if any(k not in (-1,0,1) for k in cfg['windings']) or len(set(cfg['windings']))!=len(cfg['windings']):
        raise ValueError('windings must be distinct members of -1,0,1')
    lo,hi=cfg['mass_range']
    if not 0<lo<hi or not np.isfinite([lo,hi,cfg['amplitude_max']]).all():
        raise ValueError('invalid mass/amplitude bounds')
    if not all(lo<=m<=hi for m in cfg['mass_seeds']): raise ValueError('mass seeds outside bounds')
    if not 0<max(cfg['amplitude_seeds'])<=cfg['amplitude_max']:
        raise ValueError('amplitude seeds outside bounds')
    return cfg


def cases(cfg):
    out={}
    for t in cfg['tidal_factors']:
        out[f'potential-t{t:g}']=dict(tidal_factor=t,energy_budget=None,winding=None)
        for k in cfg['windings']:
            for b in cfg['energy_budgets']:
                out[f'boson-k{k}-t{t:g}-e{b:g}']=dict(tidal_factor=t,energy_budget=b,winding=k)
    return out


def _clean(value):
    """JSON has no NaN/Infinity; failures retain their reasons explicitly."""
    if isinstance(value,dict): return {k:_clean(v) for k,v in value.items()}
    if isinstance(value,(tuple,list,np.ndarray)): return [_clean(v) for v in value]
    if isinstance(value,(np.floating,float)): return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer): return int(value)
    if isinstance(value,np.bool_): return bool(value)
    return value


def write_json(path,data):
    path=Path(path); tmp=path.with_suffix('.tmp.json')
    tmp.write_text(json.dumps(_clean(data),indent=2,allow_nan=False)+'\n')
    tmp.replace(path)


def search_score(row):
    """Guide infeasible proposals toward the unchanged hard acceptance gates."""
    if row.get('verdict') == 'PASS':
        x = float(row['X_full'])
        return x/(1+x) if np.isfinite(x) and x > 0 else 4.
    if row.get('verdict') == 'FAILED':
        return 4.
    penalty = .1*len(row.get('rejection_reasons', []))
    for key, limit in (('E19', 1e-8), ('E_c', 1e-8), ('J_error', 1e-6),
                       ('pin_error', 1e-8), ('volume_relative_drift', 1e-6),
                       ('amplitude_error', 1e-6)):
        value = float(row.get(key, 0.))
        if not np.isfinite(value):
            return 4.
        penalty += np.log1p(max(0., abs(value)/limit-1))
    if row.get('tidal_limit', 0.) > 0:
        penalty += np.log1p(max(0., row['tidal_peak']/row['tidal_limit']-1))
    if row.get('ordinary_energy_limit', 0.) > 0:
        penalty += np.log1p(max(0., row['E_b_over_R_A']/row['ordinary_energy_limit']-1))
    # Feasible < 1; solved but rejected in [2,3); failed solves score 4.
    return 2+penalty/(1+penalty)


def source_manifest(solution,cfg,args,case):
    paths=[Path(solution).with_suffix(ext) for ext in ('.json','.npz')]
    paths += [Path(p) for p in cfg['candidate_seeds']]
    paths += [Path(p) for p in cfg.get('matter_candidate_seeds', [])]
    sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    package=Path(__file__).parent
    dependencies=list(package.rglob('*.py'))
    dependencies+=list((package.parent/'analysis/spinning_wormhole').glob('*.py'))
    dependencies+=[package.parent/'grtresna/profiles'/name for name in
                   ('boson_star_ode.py','qball_couplings.py')]
    code={str(p.relative_to(package.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(dependencies)}
    return dict(version=1,sources=sources,code=code,study=cfg,case=case,
                search={k:getattr(args,k) for k in ('nx','ny','x0','m_min','m_max','q_min','q_max',
                        'maxfev','engine','seed','sigma0','popsize','fatol','m_step',
                        'walk_max_splits','walk_max_iter')},
                resume_mode='restart_from_best_with_saved_continuation_seeds',
                stability='not_assessed')


def massless_state(path):
    from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
    sol=Solution.load(path)
    rmap=dataclasses.replace(sol.radial_map,eta0=1.)
    pm=-np.pi*sol.observables['D']/sol.eta0
    profile=.5-np.arctan(rmap.eta(sol.sx))/np.pi
    profile[0],profile[-1]=0.,1.
    state=dict(F=sol.F.copy(),W=sol.W*sol.eta0,N=sol.N.copy(),B=np.ones_like(sol.F),
               PSI=pm*profile[:,None]*np.ones(len(sol.sy)),sx=sol.sx,sy=sol.sy,map=rmap,
               sigma=sol.eta0,omega=sol.omega_inf*sol.eta0,psim=pm,gamma=sol.gamma)
    th=physical_throat(state)
    xi=float(rmap.xi_of_eta(th['eta_throat']/state['sigma']))
    c=find_surface(1.,rmap,sol.sx,sol.sy,state['F'],state['N'],state['B'],xi)
    state.update(xi_t=float(c[0]),surface_coefficients=c)
    config=dict(m=0.,q=[0.,0.,0.],gamma=sol.gamma,J=float(sol.meta['prescribed']['J']))
    return state,config


def continue_to(state,start,target,grid,pin,d2,*,max_splits=6,max_iter=24):
    """Bounded bisection continuation; numerical solves never imply acceptance."""
    def blend(a,b,t):
        c=dict(b)
        for key in ('m','matter_mass','amplitude'):
            if key in a and key in b: c[key]=(1-t)*a[key]+t*b[key]
        c['q']=((1-t)*np.asarray(a['q'])+t*np.asarray(b['q'])).tolist()
        return c
    pending=[target]; current=dict(start); splits=0; row=None
    while pending:
        trial=pending[-1]
        try:
            nxt,row=solve_trial(state,trial,*grid,pin,d2,max_iter=max_iter,newton_tol=1e-12)
        except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError):
            if splits>=max_splits: raise
            splits+=1; pending.append(blend(current,trial,.5)); continue
        finally:
            release_solver()
        state,current=nxt,trial; pending.pop()
    return state,row


def seed_attempts(state,config,pin,grid,d2,record):
    """No linear mode is an inconclusive result; always try the finite branch."""
    from .boson_seeds import finite_amplitude_seed
    try:
        mode=bound_mode(state,config,pin)
        try:
            yield solve_trial(state,config,*grid,pin,d2,mode=mode,max_iter=24)
        except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError) as err:
            record(dict(stage='linear_seed',verdict='FAILED',error=str(err)))
    except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError) as err:
        record(dict(stage='linear_mode',verdict='UNRESOLVED',error=str(err)))
    try:
        seed=finite_amplitude_seed(state,config)
        yield solve_trial(seed,config,*grid,pin,d2,max_iter=24)
    except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError) as err:
        record(dict(stage='finite_seed',verdict='FAILED',error=str(err)))
    finally:
        release_solver()


def run(args,*,error):
    cfg=load_config(args.study_config); matrix=cases(cfg)
    if not args.study_case:
        for name in matrix: print(name)
        return 0
    if args.study_case not in matrix: error('unknown study case')
    if args.stability or args.free_J or args.J_pin is not None or args.no_save:
        error('study fixes reference J and requires saved fields; stability is unavailable')
    if args.maxfev<1: error('maxfev must be positive')
    x_input=np.array([float(v) for v in args.x0.split(',')])
    if (len(x_input)!=4 or not np.isfinite(x_input).all() or
            not 0<=args.m_min<args.m_max or not args.q_min<args.q_max or
            not args.m_min<=x_input[0]<=args.m_max or
            np.any(x_input[1:]<args.q_min) or np.any(x_input[1:]>args.q_max)):
        error('study needs four finite x0 parameters inside ordered bounds')
    if args.nx is not None and (args.nx<4 or args.nx%2): error('nx must be even and >=4')
    if args.ny is not None and args.ny<2: error('ny must be >=2')
    from .solver.device import select_device
    select_device(args.gpu,args.jac_chunk)
    case=matrix[args.study_case]
    out=Path(args.out or 'runs/optimisation/fixed_area')/args.study_case
    manifest=source_manifest(args.solution,cfg,args,case)
    if out.exists():
        if not args.resume: error('study output exists; use --resume or a fresh --out')
        if json.loads((out/'manifest.json').read_text())!=manifest:
            error('resume refused: configuration, source or implementation changed')
    else:
        out.mkdir(parents=True)
        write_json(out/'manifest.json',manifest)
    started=time.monotonic()
    records=[]
    log=out/'evaluations.jsonl'
    if log.exists():
        # A power loss may leave one incomplete trailing line; retain only
        # complete records and repair that tail before appending.
        lines=log.read_text().splitlines()
        for i,line in enumerate(lines):
            try: records.append(json.loads(line))
            except json.JSONDecodeError:
                if i!=len(lines)-1: raise
        log.write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in records))
    def record(row):
        row=_clean(row); records.append(row)
        with log.open('a') as f: f.write(json.dumps(row,allow_nan=False)+'\n')
        print(json.dumps(row,allow_nan=False),flush=True)
    base,basecfg=massless_state(args.solution)
    pin=('minimal_area',physical_throat(base)['area_throat'])
    d2=(base['psim']/np.pi)**2
    grid=(args.nx or len(base['sx'])-1,args.ny or len(base['sy'])-1)
    grids=refinement_grids(*grid)
    ref_dir=out/'reference'
    if (out/'reference.npz').exists():
        base,meta=load_seed(out/'reference.npz')
        refrow=meta['resolution']['records'][-1]
    else:
        # Preserve interrupted diagnostics; rerun into a distinct directory.
        idx=0
        while ref_dir.exists(): idx+=1; ref_dir=out/f'reference_{idx}'
        reference_validator=lambda s,c,r:validate(s,c,r,reference_peak=None,tidal_factor=1.,detailed=True)
        result,base=check_candidate(base,basecfg,grids,pin,d2,ref_dir,score_key='X_full',
                                    validator=reference_validator,perturb_seed=True)
        if not result['passed']:
            write_json(out/'outcome.json',dict(status='reference_failed',checks=result))
            return 2
        save_checked(out/'reference.npz',base,basecfg,{},result)
        refrow=result['records'][-1]
    peak=refrow['tidal_peak']; ra=refrow['R_A']
    validator=lambda s,c,r:validate(s,c,r,reference_peak=peak,tidal_factor=case['tidal_factor'],
                                   energy_budget=case['energy_budget'],detailed=True)
    solved=[]; finalists=[]; backgrounds=[(base,basecfg)]
    def accept_seed(s,c,r,x,stage):
        index=len(records)
        r=validate(s,c,r,reference_peak=peak,tidal_factor=case['tidal_factor'],energy_budget=case['energy_budget'])
        label=f'candidate_{index:05d}.npz'
        save_trial(out/label,s,c,_clean(r),pin)
        rec=dict(stage=stage,parameters=list(map(float,x)),config=c,artifact=label,**r)
        record(rec); solved.append((np.asarray(x),s,c))
        if r['verdict']=='PASS': finalists.append((r['X_full'],label,c))
        return r
    for r in records[:]:
        if r.get('artifact'):
            s,_=load_seed(out/r['artifact'])
            if case['winding'] is not None and not r['config'].get('matter'):
                backgrounds.append((s,r['config']))
                continue
            solved.append((np.asarray(r['parameters']),s,r['config']))
            if r['verdict']=='PASS': finalists.append((r['X_full'],r['artifact'],r['config']))
    def parameters(c):
        x=[c['m'],*c['q']]
        if case['winding'] is not None: x += [np.log(c['matter_mass']*ra),np.log(c['amplitude'])]
        return np.asarray(x)
    # Saved potential candidates must be re-solved at the new geometric area.
    if not records:
        for path in cfg['candidate_seeds']:
            seed,meta=load_seed(path); c=dict(basecfg,m=meta['m'],q=meta['q'])
            try:
                # Do not carry a constant-eta surface into the new pin.
                seed['surface_coefficients']=find_surface(1.,seed['map'],seed['sx'],seed['sy'],
                           seed['F'],seed['N'],seed['B'],seed['xi_t'])
                seed['xi_t']=float(seed['surface_coefficients'][0])
                s,r=solve_trial(seed,c,*grid,pin,d2,max_iter=24)
                if case['winding'] is None:
                    accept_seed(s,c,r,parameters(c),'repin_existing')
                else:
                    # A bosonic branch can require a nonzero phantom potential.
                    # Keep these re-pinned backgrounds as seeds, never finalists.
                    label=f'background_{len(records):05d}.npz'
                    save_trial(out/label,s,c,_clean(r),pin)
                    backgrounds.append((s,c))
                    record(dict(stage='boson_background',verdict='SEED_ONLY',
                                stationary_verdict=r['verdict'],config=c,artifact=label,
                                parameters=[c['m'],*c['q']]))
            except (RuntimeError,ValueError,FloatingPointError) as err:
                record(dict(stage='repin_existing',verdict='FAILED',error=str(err)))
    if case['winding'] is not None and not solved:
        for path in cfg.get('matter_candidate_seeds', []):
            seed, meta = load_seed(path)
            c = meta['config']
            expected = 'cloud' if case['winding'] == 0 else 'winding'
            if (c.get('matter') != expected or c.get('winding_k', 0) != case['winding']
                    or not np.isclose(c['gamma'], basecfg['gamma'], atol=1e-12, rtol=0)
                    or not np.isclose(c['J'], basecfg['J'], atol=1e-10, rtol=0)
                    or meta['pin'][0] != pin[0]
                    or not np.isclose(meta['pin'][1], pin[1], atol=0, rtol=1e-10)):
                raise ValueError('matter seed does not match the study geometry and winding')
            try:
                # Re-solve under this implementation; old acceptance is not inherited.
                s, r = solve_trial(seed, c, *grid, pin, d2, max_iter=24)
                r['seed_source'] = str(path)
                accept_seed(s, c, r, parameters(c), 'matter_warm_seed')
            except (RuntimeError, ValueError, FloatingPointError) as err:
                record(dict(stage='matter_warm_seed', verdict='FAILED',
                            seed_source=str(path), error=str(err)))
            finally:
                release_solver()
    if case['winding'] is not None and not solved:
        for bi,(background,background_config) in enumerate(backgrounds):
            for mass in cfg['mass_seeds']:
                for amplitude in cfg['amplitude_seeds']:
                    c=dict(background_config,matter='cloud' if case['winding']==0 else 'winding',
                           winding_k=case['winding'],matter_mass=mass/ra,amplitude=amplitude)
                    def seed_record(r):
                        record(dict(r,seed_config=c,background_index=bi))
                    for s,r in seed_attempts(background,c,pin,grid,d2,seed_record):
                        r['seed_background']=bi
                        accept_seed(s,c,r,parameters(c),'boson_seed')
        if not solved:
            write_json(out/'outcome.json',dict(status='nonzero_branch_unresolved',
                       elapsed_seconds=time.monotonic()-started,reference=refrow))
            return 2
    x0=np.array([float(v) for v in args.x0.split(',')])
    if len(x0)!=4: error('study x0 requires m,q1,q2,q3')
    lo=np.array([args.m_min,*([args.q_min]*3)] + ([np.log(cfg['mass_range'][0]),np.log(1e-5)] if case['winding'] is not None else []))
    hi=np.array([args.m_max,*([args.q_max]*3)] + ([np.log(cfg['mass_range'][1]),np.log(cfg['amplitude_max'])] if case['winding'] is not None else []))
    scales=np.array([args.m_step,.3,.3,.3]+([.3,.3] if case['winding'] is not None else []))
    if case['winding'] is not None:
        start=min(solved,key=lambda item:np.linalg.norm(item[0][:4]-x0))
        x0=np.r_[x0,start[0][4:]]
    if np.any(x0<lo) or np.any(x0>hi): error('study x0 outside bounds')
    if args.resume and finalists:
        best=min(finalists)
        rec=next(r for r in records if r.get('artifact')==best[1])
        x0=np.clip(np.asarray(rec['parameters']),lo,hi)
    count=sum(r.get('stage')=='search' for r in records)
    remaining=max(0,args.maxfev-count)
    def objective(x):
        nonlocal count
        count+=1; start_time=time.monotonic()
        try:
            if not np.isfinite(x).all() or np.any(x<lo) or np.any(x>hi):
                raise ValueError('parameter_bounds')
            u=np.linspace(0.,1.,1001)
            if np.min(1+x[1]*u+x[2]*u**2+x[3]*u**3)<=0:
                raise ValueError('potential_positivity')
            c=dict(basecfg,m=float(x[0]),q=list(map(float,x[1:4])))
            if case['winding'] is not None:
                c.update(matter='cloud' if case['winding']==0 else 'winding',winding_k=case['winding'],
                         matter_mass=float(np.exp(x[4])/ra),amplitude=float(np.exp(x[5])))
            if solved:
                _,seed,previous=min(solved,key=lambda item:np.sum(abs((item[0]-x)/scales)))
            else: seed,previous=base,basecfg
            s,r=continue_to(seed,previous,c,grid,pin,d2,max_splits=args.walk_max_splits,
                            max_iter=args.walk_max_iter)
            r['seconds']=time.monotonic()-start_time
            r=accept_seed(s,c,r,x,'search')
            # Infeasible scores cannot outrank any positive feasible objective.
            return search_score(r)
        except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError) as err:
            record(dict(stage='search',parameters=list(map(float,x)),verdict='FAILED',
                        rejection_reasons=[str(err)],seconds=time.monotonic()-start_time))
            return 4.
        finally:
            release_solver()
    if remaining:
        if args.engine=='cma':
            import cma
            options=dict(CMA_stds=list(scales),bounds=[list(lo),list(hi)],maxfevals=remaining,
                         seed=args.seed,verbose=-9)
            if args.popsize is not None: options['popsize']=args.popsize
            es=cma.CMAEvolutionStrategy(list(x0),args.sigma0,options)
            while not es.stop() and count<args.maxfev:
                xs=es.ask(); vals=[]
                for x in xs:
                    vals.append(objective(np.asarray(x)) if count<args.maxfev else 3.)
                es.tell(xs,vals)
            write_json(out/'search_stop.json',dict(criteria=es.stop(),evaluations=count))
        else:
            from scipy.optimize import minimize
            simplex=np.vstack([x0]+[np.clip(x0+scales[i]*np.eye(len(x0))[i],lo,hi) for i in range(len(x0))])
            minimize(objective,x0,method='Nelder-Mead',bounds=list(zip(lo,hi)),
                     options=dict(maxfev=remaining,fatol=args.fatol,xatol=1e-3,
                                  adaptive=True,initial_simplex=simplex))
    # Validate the strongest provisional candidate first, then try the next
    # if refinement invalidates it. Never copy a provisional file to best_clean.
    winner=None
    for _,artifact,c in sorted(set((score,name,json.dumps(c,sort_keys=True)) for score,name,c in finalists)):
        c=json.loads(c); s,_=load_seed(out/artifact)
        directory=out/(Path(artifact).stem+'_refine')
        if directory.exists():
            old=json.loads((directory/'result.json').read_text()) if (directory/'result.json').exists() else {}
            if old.get('passed') and (out/'best_clean.npz').exists():
                _,saved=load_seed(out/'best_clean.npz')
                if saved.get('candidate_artifact')==artifact:
                    winner=saved; break
            suffix=1
            while directory.with_name(directory.name+f'_{suffix}').exists(): suffix+=1
            directory=directory.with_name(directory.name+f'_{suffix}')
        result,checked=check_candidate(s,c,grids,pin,d2,directory,score_key='X_full',
                                       validator=validator,perturb_seed=True)
        if result['passed']:
            save_checked(out/'best_clean.npz',checked,c,
                         dict(X_reference=refrow['X_full'],candidate_artifact=artifact),result)
            winner=result['records'][-1]; break
    improvement=None
    if winner:
        gain=1-winner['X_full']/refrow['X_full']
        uncertainty=max(2e-6,refrow.get('volume_relative_drift',0.)+winner.get('volume_relative_drift',0.))
        improvement=gain if gain>uncertainty else None
    outcome=dict(status='validated_candidate' if winner else 'no_validated_improvement',
                 reference=refrow,winner=winner,validated_fractional_improvement=improvement,
                 elapsed_seconds=time.monotonic()-started,search_evaluations=count,
                 stability='not_assessed')
    write_json(out/'outcome.json',outcome)
    from .study_report import plot_comparison
    plot_comparison(out)
    return 0 if winner else 2
