"""A bounded ring-free, same-area and same-angular-momentum comparison.

The qualified ring is read only. A fresh V=0 control starts from static
Ellis, walks a fixed angular-momentum ladder, then passes three independent
re-solves. No stronger ring or evolution is dispatched by this stage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np


def validate_plan(plan):
    if (plan['stage'] != 'matched_control' or plan['throat_radius'] != 2.
            or plan['grids'] != [[210,36],[224,38],[240,40]]
            or plan['independent_points'] != [49,21]):
        raise ValueError('control must match the qualified three-grid ring')
    if (plan['control_J_step'] != .1 or plan['max_control_steps'] != 10
            or plan['max_solves'] != 13 or plan['max_newton_iterations'] != 24
            or plan['tidal_factor'] != 4.):
        raise ValueError('control solve budget or gates changed')
    if (plan['wall_seconds'] != 3600 or plan['threads'] != 4
            or plan['memory_gib'] != 160 or plan['checkpoints'] is not False):
        raise ValueError('control resource caps changed')
    target = plan['target_J']
    if not np.isfinite(target) or target == 0 or math.ceil(abs(target)/.1) > 10:
        raise ValueError('target angular momentum exceeds the fixed ladder')
    for key in ('ring', 'static'):
        ref = plan['references'][key]
        if not ref['path'] or len(ref['sha256']) != 64:
            raise ValueError('both references must be hash-pinned')
    if set(plan['references']) != {'ring','static'}:
        raise ValueError('unexpected comparison reference')


def read_references(plan):
    """Verify the comparison identity before any JAX or GPU startup."""
    from .exploration import load_seed
    validate_plan(plan)
    loaded = {}
    for key, ref in plan['references'].items():
        path = Path(ref['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
            raise ValueError(f'{key} reference hash mismatch')
        loaded[key] = load_seed(path)
    ring, meta = loaded['ring']
    baseline, base = loaded['static']
    pin = ['minimal_area', 4*np.pi*plan['throat_radius']**2]
    expected = dict(m=0., q=[0.,0.,0.], gamma=0., matter='winding',
                    matter_mass=1., winding_k=1, rotation_control='nonrotating_ends')
    if (any(meta.get(k) != v for k,v in expected.items()) or meta.get('pin') != pin
            or meta.get('resolution_validated') is not True or meta.get('verdict') != 'PASS'
            or ring['omega'] != 0. or 'Z' not in ring
            or not np.isfinite(meta.get('X_full', np.nan)) or meta['X_full'] <= 0
            or abs(meta.get('J', np.inf)-plan['target_J']) > 1e-12):
        raise ValueError('ring reference is not the qualified fixed-area model')
    result = meta.get('resolution', {})
    records = result.get('records', [])
    if (result.get('passed') is not True or result.get('method') != 'refine'
            or [[r.get('nx'),r.get('ny')] for r in records] != plan['grids']
            or any(r.get('verdict') != 'PASS' or r.get('offgrid_pass') is not True
                   or r.get('offgrid_sampling') != [49,21]
                   or r.get('newton_updates',0) < 1
                   or abs(r.get('J_measured',np.inf)-plan['target_J']) > 1e-6
                   for r in records)):
        raise ValueError('ring lacks three passing independent re-solves')
    cfg, row = base.get('config', {}), base.get('diagnostics', {})
    if (cfg != dict(m=0., q=[0.,0.,0.], gamma=0., J=0.) or base.get('pin') != pin
            or row.get('verdict') != 'PASS' or row.get('offgrid_pass') is not True
            or not np.isfinite(row.get('tidal_peak',np.nan)) or row['tidal_peak'] <= 0
            or any(k in baseline for k in ('Z','CHI'))):
        raise ValueError('static reference does not match the V=0 area and tidal limit')
    return baseline, meta, row


def run(plan, directory):
    from .exploration import solve_trial, save_trial
    from .resolution import check_candidate, save_checked
    from .study import release_solver, write_json
    from .study_validation import validate

    control, ring_meta, static_row = read_references(plan)
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'plan.json', plan)
    package = Path(__file__).parent
    paths = list(package.rglob('*.py')) + list((package.parent/'analysis/spinning_wormhole').glob('*.py'))
    write_json(out/'code.json', dict(commit=subprocess.check_output(
        ['git','rev-parse','HEAD'], text=True).strip(), sha256={
            str(p.relative_to(package.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}))
    pin = ('minimal_area', 4*np.pi*plan['throat_radius']**2)
    d2 = plan['throat_radius']**2
    target = float(plan['target_J'])
    config = dict(m=0., q=[0.,0.,0.], gamma=0., J=target, rotation_control='J')
    outcome = dict(matched_control_accepted=False, solves=0,
                   target_J=target, X_ring=ring_meta['X_full'],
                   X_static=static_row['X_full'], stability='not_assessed')
    write_json(out/'outcome.json', outcome)

    def validator(state, cfg, row):
        row = validate(state, cfg, row, reference_peak=static_row['tidal_peak'],
                       tidal_factor=plan['tidal_factor'], independent_points=plan['independent_points'])
        if abs(row.get('J_measured', np.inf)-target) > 1e-6*max(1.,abs(target)):
            row['rejection_reasons'].append('angular_momentum_match')
            row['verdict'] = 'ABOVE_GATE'
        return row

    count = max(1, math.ceil(abs(target)/plan['control_J_step']))
    try:
        for i, angular_momentum in enumerate(np.linspace(0,target,count+1)[1:]):
            cfg = dict(config, J=float(angular_momentum))
            outcome['solves'] += 1
            write_json(out/'outcome.json', outcome)
            try:
                control, row = solve_trial(control, cfg, *plan['grids'][0], pin, d2,
                                           max_iter=plan['max_newton_iterations'], newton_tol=1e-14)
                save_trial(out/f'control_step_{i+1:02d}.npz', control, cfg, row, pin)
            finally:
                release_solver()
            print(f'control step {i+1}/{count}: {json.dumps(row)}', flush=True)
            if row['verdict'] != 'PASS':
                raise RuntimeError('control continuation constraints failed')
        result, checked = check_candidate(control, config, plan['grids'], pin, d2,
                            out/'matched_spin', validator=validator, score_key='X_full',
                            perturb_seed=True)
        outcome['solves'] += len(result['records'])
        if not result['passed'] or len(result['records']) != 3:
            raise RuntimeError('matched control three-grid validation failed')
        save_checked(out/'matched_spin.npz', checked, config,
                     dict(pin=list(pin), ring_reference=plan['references']['ring']), result)
        value = result['records'][-1]['X_full']
        outcome.update(matched_control_accepted=True, X_matched_spin=value,
                       matched_spin_fractional_reduction=1-ring_meta['X_full']/value,
                       reason='matched_control_complete')
    except (RuntimeError, ValueError, FloatingPointError) as exc:
        outcome['reason'] = str(exc)
    write_json(out/'outcome.json', outcome)
    return 0 if outcome['matched_control_accepted'] else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--gpu', type=int)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan = json.loads(Path(args.config).read_text())
    validate_plan(plan)
    if not args.run:
        print(json.dumps(dict(plan=plan, output=args.out, status='PREPARED_ONLY'), indent=2))
        return 0
    read_references(plan)
    if args.gpu is None:
        parser.error('--run requires an explicitly selected GPU')
    from .solver.device import select_device, configure_jax
    select_device(args.gpu, 256)
    jax = configure_jax()
    if jax.default_backend() != 'gpu' or not jax.config.x64_enabled:
        raise RuntimeError('matched control requires CUDA and float64')
    print('devices:',jax.devices(),'float64:',jax.config.x64_enabled, flush=True)
    return run(plan,args.out)


if __name__ == '__main__':
    raise SystemExit(main())
