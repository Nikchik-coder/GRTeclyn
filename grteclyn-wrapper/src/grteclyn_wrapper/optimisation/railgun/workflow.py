"""Bounded solves, three-grid recovery and schema-checked saved ring states."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from .model import ScalarField

SCHEMA = 1


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def save_state(path, problem, u, *, validated=False):
    metadata = dict(schema=SCHEMA, model='canonical_regular_centre', nx=problem.nx,
                    ny=problem.ny, length=problem.length, target_j=problem.target_j,
                    fields=[f.to_dict() for f in problem.fields], validated=bool(validated),
                    stability='not_assessed')
    if getattr(problem, 'central_lapse', None) is not None:
        metadata['central_lapse'] = problem.central_lapse
    if any(t is not None for t in problem.frequency_targets) or getattr(problem, 'central_lapse', None) is not None:
        metadata['frequency_targets']=list(problem.frequency_targets)
        arrays,_=problem.unpack(np.asarray(u))
        metadata['measured_amplitude_pins']=[float(problem.anchors[i]@arrays[f'q{i}'][:,-1])
                                             for i in range(len(problem.fields))]
    np.savez_compressed(path, metadata=json.dumps(metadata), u=np.asarray(u))


def load_state(path):
    from .problem import RingProblem
    with np.load(path, allow_pickle=False) as data:
        metadata = json.loads(str(data['metadata']))
        u = np.array(data['u'], dtype=float)
    if metadata.get('schema') != SCHEMA or metadata.get('model') != 'canonical_regular_centre':
        raise ValueError('unsupported ring solution schema/model')
    p = RingProblem([ScalarField(**f) for f in metadata['fields']], nx=metadata['nx'],
                    ny=metadata['ny'], length=metadata['length'], target_j=metadata['target_j'],
                    frequency_targets=metadata.get('frequency_targets'), central_lapse=metadata.get('central_lapse'))
    if u.shape != (p.n_unknowns,) or not np.isfinite(u).all():
        raise ValueError('saved vector is nonfinite or incompatible with its declared model')
    return p, u, metadata


def branch_checks(record,problem,u,config):
    """Do not accept the trivial vacuum during fixed-frequency continuation."""
    floors=config.get('minimum_charges')
    if floors is not None:
        charges=np.asarray(record.get('charges',[]),float);floors=np.asarray(floors,float)
        if (charges.shape!=floors.shape or not np.isfinite(charges).all()
                or not np.isfinite(floors).all() or np.any(floors<=0) or np.any(charges<floors)):
            record['reasons'].append('branch_charge_floor')
    if config.get('require_nodeless'):
        arrays,_=problem.unpack(np.asarray(u))
        for i in range(len(problem.fields)):
            q=arrays[f'q{i}'];peak=float(np.max(abs(q)));resolved=q[abs(q)>1e-5*peak]
            if not len(resolved) or np.min(resolved)*np.max(resolved)<0:
                record['reasons'].append('branch_scalar_nodes');break
    record['verdict']='PASS' if not record['reasons'] else 'REJECT'
    return record


def run_study(config, directory, *, reference=None, seed_path=None, acceptance_check=None):
    from .problem import RingProblem
    from .diagnostics import converged_records, validate
    from ..solver.newton import newton
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    fields = [ScalarField(**f) for f in config['fields']]
    grids = config.get('grids', [[24, 6], [32, 8], [40, 10]])
    if len(grids) != 3 or any(len(g) != 2 for g in grids) or any(
            b[0] <= a[0] or b[1] <= a[1] for a, b in zip(grids, grids[1:])):
        raise ValueError('exactly three strictly increasing radial/angular grids required')
    canonical = json.dumps(config, sort_keys=True)
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    manifest = dict(config=config, configuration_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
                    commit=git.stdout.strip() if git.returncode == 0 else None,
                    python=platform.python_version(), schema=SCHEMA, stability='not_assessed')
    records = []
    previous = None
    if seed_path is not None:
        old, old_u, _ = load_state(seed_path)
        if [(f.winding, f.parity, f.mass) for f in old.fields] != [(f.winding, f.parity, f.mass) for f in fields]:
            raise ValueError('seed field winding/parity/mass must match; use explicit continuation for a new model')
        if old.target_j != config.get('target_j') or old.length != config.get('length', 6.):
            raise ValueError('seed topology, radial scale and J condition must match')
        previous = old, old_u
        manifest['seed_sha256'] = hashlib.sha256(Path(seed_path).read_bytes()).hexdigest()
    write_json(directory/'manifest.json', manifest)
    if reference is not None:
        write_json(directory/'reference_ode.json', {key: value for key,value in reference.items()
                    if not isinstance(value,np.ndarray)})
        np.savez_compressed(directory/'reference_ode.npz', **{key:value for key,value in reference.items()
                    if isinstance(value,np.ndarray)})
    for index, (nx, ny) in enumerate(grids):
        started = time.monotonic()
        p = RingProblem(fields, nx=nx, ny=ny, length=config.get('length', 6.), target_j=config.get('target_j'),
                        frequency_targets=config.get('frequency_targets'), central_lapse=config.get('central_lapse'))
        if index == 0:
            device = p.jax.devices()[0]
            manifest.update(jax=p.jax.__version__, platform=device.platform,
                            device_kind=device.device_kind, float64=bool(p.jax.config.jax_enable_x64))
            if config.get('require_gpu', True) and device.platform != 'gpu':
                raise RuntimeError('GPU execution required; CPU fallback is refused')
            write_json(directory/'manifest.json', manifest)
            print(json.dumps({'event': 'device', **{k: manifest[k] for k in ('platform','device_kind','float64')}}), flush=True)
        if previous is not None:
            u0 = p.transfer(*previous, perturb=config.get('perturbation', 1e-5))
        elif reference is not None:
            from .reference import reference_seed
            u0 = reference_seed(p, reference)
        else:
            u0 = p.seed()
        # Two real corrections are required on finer grids, not acceptance of
        # an interpolant whose equilibrated residual is already small.
        u, info = newton(p.residual, p.jacobian, u0, tol=config.get('newton_tol', 1e-12),
                         chord_ratio=config.get('chord_ratio', 0.1),
                         max_iter=config.get('max_iter', 30), min_updates=config.get('min_updates',2 if index else 0),
                         verbose=True)
        solve_elapsed = time.monotonic()-started
        save_state(directory/f'grid_{nx}x{ny}.npz', p, u)
        try:
            record = validate(p, u, info, equation_tol=config.get('equation_tol', 1e-8),
                              tail_tol=config.get('tail_tol', 1e-6))
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            record = dict(grid=[nx, ny], newton=info, verdict='REJECT', reasons=[str(error)], stability='not_assessed')
        branch_checks(record,p,u,config)
        record.update(solve_seconds=solve_elapsed, total_seconds=time.monotonic()-started)
        write_json(directory/f'grid_{nx}x{ny}.json', record)
        records.append(record)
        print(json.dumps({'event': 'grid', 'grid': [nx, ny], 'verdict': record['verdict'],
                          'reasons': record['reasons'], 'seconds': record['total_seconds']}), flush=True)
        diagnostic_recovery = (config.get('diagnostic_refinement',False) and info.get('converged')
                               and np.isfinite(u).all() and record.get('B_min',0.) > 0)
        if record['verdict'] != 'PASS' and not diagnostic_recovery:
            break
        previous = p, u
    accepted, drift = converged_records(records, tolerance=config.get('observable_tol', 1e-6))
    outcome = dict(accepted=accepted, observable_relative_drift=drift,
                   grids_attempted=len(records), stability='not_assessed',
                   reasons=[] if accepted else ['background_or_three_grid_validation'], records=records)
    if reference is not None and records and records[-1]['verdict'] == 'PASS':
        errors = dict(mass_relative=abs(records[-1]['M_ADM_estimate']/reference['mass']-1),
                      frequency_relative=abs(float(u[-1])/reference['omega']-1))
        outcome['spherical_reference_errors'] = errors
        if max(errors.values()) > config.get('reference_tol', 1e-5):
            accepted = outcome['accepted'] = False
            outcome['reasons'].append('spherical_reference_mismatch')
    if acceptance_check is not None:
        extra = acceptance_check(records)
        outcome['additional_acceptance'] = extra
        if not extra['passed']:
            accepted = outcome['accepted'] = False
            outcome['reasons'].append('additional_acceptance')
    if accepted:
        save_state(directory/'accepted.npz', p, u, validated=True)
    write_json(directory/'outcome.json', outcome)
    return outcome
