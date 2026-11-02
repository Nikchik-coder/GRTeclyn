"""Bounded amplitude continuation with a physical-radius map and secant guesses.

The pin is fixed at the initial scalar maximum, not moved between solves.
This parameter can also turn: rejection stops the study, without claiming a
branch endpoint or guaranteeing a nonsingular Jacobian or an ergoregion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np
from scipy.optimize import minimize_scalar
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval, lobatto


def remap_arrays(arrays, old_s, old_y, old_length, new_s, new_y, new_length):
    """Evaluate the old solution at the NEW nodes' physical radii.

    The fractional-linear coordinate transformation includes both endpoints
    exactly and avoids constructing infinity/infinity at spatial infinity.
    """
    a = new_length * (1 + new_s)
    b = old_length * (1 - new_s)
    mapped_s = (a - b) / (a + b)
    bx = cheb_eval(old_s, np.eye(len(old_s)), mapped_s)
    by = cheb_eval(old_y, np.eye(len(old_y)), new_y)
    return {tag: bx @ value @ by.T for tag, value in arrays.items()}


def secant_guess(current, previous, target_pin, current_pin, previous_pin):
    """Both vectors must already use the same map, grid and variable ordering."""
    if (np.shape(current) != np.shape(previous)
            or not np.isfinite([target_pin, current_pin, previous_pin]).all()
            or not target_pin > current_pin > previous_pin):
        raise ValueError('finite, increasing pins and matching vectors required')
    guess = current + (target_pin-current_pin)/(current_pin-previous_pin)*(current-previous)
    if not np.isfinite(guess).all():
        raise ValueError('nonfinite secant prediction')
    return guess


def preflight(source, config):
    """Read NumPy data only; this function never imports or starts JAX."""
    if (set(config) != {'source_sha256', 'length', 'grids', 'amplitude_factors', 'max_solves',
                       'max_iter', 'newton_tol', 'equation_tol', 'tail_tol', 'observable_tol'}
            or config['source_sha256'] != 'bf92fd0c8a9be3bb75481e693f6927ea82757e30f843d06305e053a77280d82e'
            or config['length'] != 2.5 or config['grids'] != [[128, 16], [160, 20], [192, 24]]
            or len(config['amplitude_factors']) != 9
            or not np.allclose(config['amplitude_factors'], 1.06**np.arange(9), rtol=0, atol=1e-14)
            or config['max_solves'] != 27 or config['max_iter'] != 30 or config['newton_tol'] != 1e-14
            or config['equation_tol'] != 1e-8 or config['tail_tol'] != 1e-6
            or config['observable_tol'] != 1e-6):
        raise ValueError('the bounded 27-solve amplitude profile and unchanged gates are required')
    if hashlib.sha256(Path(source).read_bytes()).hexdigest() != config['source_sha256']:
        raise ValueError('the accepted omega=0.70 source hash must match')
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.array(data['u'], float)
    fields = meta['fields']
    if (not meta.get('validated') or meta.get('model') != 'canonical_regular_centre'
            or meta.get('schema') != 1 or meta.get('target_j') is not None
            or len(fields) != 1 or fields[0]['winding'] != 1 or fields[0]['mass'] != 1
            or fields[0]['parity'] != 'even' or fields[0]['quartic'] or fields[0]['sextic']
            or meta['length'] != 5 or [meta['nx'], meta['ny']] != [160, 20]
            or meta.get('frequency_targets') != [0.70]
            or u.shape != (5*161*21+1,) or not np.isfinite(u).all()
            or abs(u[-1]-.70) > 1e-12):
        raise ValueError('accepted pure even massive k=1 omega=0.70 source required')
    s, _ = lobatto(meta['nx'])
    q = u[4*161*21:5*161*21].reshape(161, 21)[:, -1]
    index = int(np.argmax(q))
    if not 0 < index < len(s)-1:
        raise ValueError('positive scalar maximum must be interior')
    def evaluate(x):
        return float(cheb_eval(s, q[:, None], np.atleast_1d(x))[0, 0])
    peak = minimize_scalar(lambda x: -evaluate(x), bounds=(s[index+1], s[index-1]),
                           method='bounded', options={'xatol': 1e-13})
    if not peak.success or not -peak.fun > 0:
        raise ValueError('could not locate a positive scalar maximum')
    return dict(metadata=meta, anchor_radius=float(meta['length']*(1+peak.x)/(1-peak.x)),
                initial_pin=float(-peak.fun), source_frequency=float(u[-1]),
                amplitudes=[float(-peak.fun*f) for f in config['amplitude_factors']],
                max_solves=config['max_solves'], grids=config['grids'], numerical_execution=False)


def convergence_checks(records, frequencies, tolerance=1e-6):
    """Additional strong-field observable checks; original gates still apply."""
    if len(records) != 3 or any(row.get('verdict') != 'PASS' for row in records):
        return dict(passed=False, ergoregion_resolved=False, drifts={})
    keys = ('lapse_min', 'gtt_max', 'shift_norm_over_lapse_max')
    if (len(frequencies) != 3 or not np.isfinite(frequencies).all()
            or not np.isfinite([[row[key] for key in keys] for row in records]).all()):
        return dict(passed=False, ergoregion_resolved=False, drifts={}, reason='nonfinite_observables')
    a, b = records[-2:]
    drifts = {key: abs(b[key]-a[key])/max(1., abs(a[key]), abs(b[key])) for key in keys}
    drifts['frequency'] = abs(frequencies[-1]-frequencies[-2])
    passed = bool(np.isfinite(list(drifts.values())).all() and max(drifts.values()) <= tolerance
                  and all(np.isfinite(frequencies)) and all(0 < w < 1 for w in frequencies))
    spread = np.ptp([row['gtt_max'] for row in records])
    resolved = bool(passed and min(row['gtt_max'] for row in records) > max(1e-8, spread)
                    and all(row['shift_norm_over_lapse_max'] > 1 for row in records))
    return dict(passed=passed, drifts=drifts, ergoregion_resolved=resolved,
                gtt_three_grid_spread=float(spread))


def common_metric_samples(source):
    """Use identical physical points on every resolution, including the equator.

    These are sampled extrema, not claims of continuous global optimisation.
    Positive g_tt at a resolved point suffices to establish an ergoregion.
    Provisional states are permitted for diagnosis, never promoted here.
    """
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.asarray(data['u'])
    nx, ny = meta['nx'], meta['ny']
    n = (nx+1)*(ny+1)
    if (meta.get('schema') != 1 or meta.get('model') != 'canonical_regular_centre'
            or meta['length'] != 2.5 or len(meta['fields']) != 1
            or u.shape != (5*n+1,) or not np.isfinite(u).all()):
        raise ValueError('finite canonical single-ring state at radial scale 2.5 required')
    arrays = u[:5*n].reshape(5, nx+1, ny+1)
    s = np.r_[-1., np.polynomial.legendre.leggauss(384)[0]]
    mu = np.r_[0., (np.polynomial.legendre.leggauss(48)[0]+1)/2, 1.]
    old_s, _ = lobatto(nx)
    old_y, _ = lobatto(ny)
    bx = cheb_eval(old_s, np.eye(nx+1), s)
    by = cheb_eval(old_y, np.eye(ny+1), 2*mu**2-1)
    f, w, b = [bx@arrays[i]@by.T for i in (0, 1, 3)]
    r = 2.5*(1+s)/(1-s)
    rho = r[:, None]*np.sqrt(1-mu[None, :]**2)
    lapse = np.exp(f/2)
    ratio = (1+b)*np.exp(-f)*abs(w)*rho
    gtt = -lapse**2*(1-ratio**2)
    if not np.isfinite([lapse, ratio, gtt]).all() or np.min(1+b) <= 0:
        raise ValueError('invalid interpolated metric')
    i, j = np.unravel_index(np.argmax(gtt), gtt.shape)
    return dict(lapse_min=float(lapse.min()), gtt_max=float(gtt.max()),
                shift_norm_over_lapse_max=float(ratio.max()),
                gtt_max_point=dict(rho=float(rho[i, j]), z=float(r[i]*mu[j])),
                sampling='385 radial x 50 angular common physical points, including origin/axis/equator')


def extra_checks(directory, rows, source, config, *, reproduce=False):
    frequencies, samples = [], []
    for nx, ny in [r['grid'] for r in rows]:
        path = Path(directory)/f'grid_{nx}x{ny}.npz'
        with np.load(path, allow_pickle=False) as data:
            frequencies.append(float(data['u'][-1]))
        if len(rows) == 3 and all(row.get('verdict') == 'PASS' for row in rows):
            samples.append(common_metric_samples(path))
    common_rows = [dict(row, **sample) for row, sample in zip(rows, samples)]
    extra = convergence_checks(common_rows, frequencies, config['observable_tol'])
    extra.update(frequencies=frequencies, common_point_extrema=samples)
    if reproduce and extra['passed']:
        original = json.loads((Path(source).parent/'grid_160x20.json').read_text())
        drift = max(abs(rows[-1][k]-original[k])/max(1., abs(original[k]))
                    for k in ('M_ADM_estimate', 'J_volume'))
        extra['reparameterisation_drift'] = max(drift, abs(frequencies[-1]-.70))
        extra['passed'] = extra['reparameterisation_drift'] <= config['observable_tol']
    return extra


def bootstrap_preflight(previous, source, config, plan):
    """Recertify the three completed solves without modifying their evidence."""
    previous = Path(previous)
    manifest = json.loads((previous/'manifest.json').read_text())
    outcome = json.loads((previous/'outcome.json').read_text())
    directory = previous/'amplitude_00'
    study = json.loads((directory/'outcome.json').read_text())
    if (manifest['config'] != config or outcome['solves'] != 3
            or len(outcome['records']) != 1 or outcome['records'][0]['accepted']
            or outcome['records'][0]['index'] != 0
            or study['accepted'] or study['reasons'] != ['additional_acceptance']
            or [row['grid'] for row in study['records']] != config['grids']
            or any(row['verdict'] != 'PASS' or not row['newton']['converged']
                   or len(row['newton']['newton_steps']) < 2 for row in study['records'])):
        raise ValueError('only the stopped three-grid reproduction can be reused')
    files = [previous/'manifest.json', previous/'outcome.json', directory/'manifest.json',
             directory/'outcome.json']
    for nx, ny in config['grids']:
        path = directory/f'grid_{nx}x{ny}.npz'
        with np.load(path, allow_pickle=False) as data:
            meta = json.loads(str(data['metadata']))
        field = dict(plan['metadata']['fields'][0], amplitude=plan['initial_pin'],
                     anchor_radius=plan['anchor_radius'])
        if (meta.get('validated') or meta['fields'] != [field] or meta.get('frequency_targets')
                or meta['nx'] != nx or meta['ny'] != ny or meta['target_j'] is not None):
            raise ValueError('bootstrap field model or pin mismatch')
        record = directory/f'grid_{nx}x{ny}.json'
        if json.loads(record.read_text()) != next(r for r in study['records'] if r['grid'] == [nx, ny]):
            raise ValueError('bootstrap grid report mismatch')
        files.extend([path, record])
    checks = extra_checks(directory, study['records'], source, config, reproduce=True)
    if not checks['passed']:
        raise ValueError('saved bootstrap fails the corrected common-point comparison')
    return dict(directory=str(previous), solves_spent=3, solves_remaining=24, checks=checks,
                hashes={str(path.relative_to(previous)): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in files})


def run_scan(source, config, directory, *, resume_bootstrap=None):
    plan = preflight(source, config)
    resume = bootstrap_preflight(resume_bootstrap, source, config, plan) if resume_bootstrap else None
    from .problem import RingProblem
    from .model import ScalarField
    from .workflow import load_state, run_study, save_state, write_json
    old, old_u, _ = load_state(source)
    if old.jax.devices()[0].platform != 'gpu':
        raise RuntimeError('GPU execution required; CPU fallback refused')
    floor = .001*float(np.asarray(old.charge_integrals(old_u))[0])
    if not np.isfinite(floor) or floor <= 0:
        raise ValueError('positive source charge required')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    manifest = dict(config=config, source=str(source), plan=plan,
                    commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    minimum_charge=floor, stability='not_assessed')
    if resume:
        manifest['bootstrap_reuse'] = resume
    write_json(directory/'manifest.json', manifest)
    started = time.monotonic()
    records, states, pins = [], [], []
    solves = 0
    if resume:
        target = directory/'amplitude_00'
        shutil.copytree(Path(resume_bootstrap)/'amplitude_00', target)
        shutil.copy2(target/'outcome.json', target/'outcome.original.json')
        outcome = json.loads((target/'outcome.json').read_text())
        outcome.update(accepted=True, reasons=[], additional_acceptance=resume['checks'])
        write_json(target/'outcome.json', outcome)
        with np.load(target/'grid_192x24.npz', allow_pickle=False) as data:
            meta = json.loads(str(data['metadata']))
            value = data['u'].copy()
        meta['validated'] = True
        np.savez_compressed(target/'accepted.npz', metadata=json.dumps(meta), u=value)
        records.append(dict(index=0, pin=plan['initial_pin'], directory='amplitude_00', accepted=True,
                            predictor='reused_bootstrap', checks=resume['checks']))
        states.append(load_state(target/'accepted.npz')[:2])
        pins.append(plan['initial_pin'])
        solves = 3
        write_json(directory/'progress.json', dict(solves=solves, records=records))
    for index, pin in enumerate(plan['amplitudes']):
        if resume and index == 0:
            continue
        field = ScalarField(**dict(plan['metadata']['fields'][0],
                                   amplitude=pin, anchor_radius=plan['anchor_radius']))
        p = RingProblem([field], nx=config['grids'][0][0], ny=config['grids'][0][1],
                        length=config['length'])
        if states:
            current = p.transfer(*states[-1])
            guess = (secant_guess(current, p.transfer(*states[-2]), pin, pins[-1], pins[-2])
                     if len(states) >= 2 else current)
            method = 'secant' if len(states) >= 2 else 'previous_solution'
        else:
            arrays, frequencies = old.unpack(old_u)
            arrays = remap_arrays(arrays, old.s, old.y, old.length, p.s, p.y, p.length)
            guess = p.pack(arrays, frequencies)
            method = 'physical_radius_remap_and_repin'
        # Predictions are explicitly provisional, never accepted fields.
        guess_path = directory/f'guess_{index:02d}.npz'
        save_state(guess_path, p, guess)
        study = dict(fields=[field.to_dict()], length=config['length'], grids=config['grids'],
                     max_iter=config['max_iter'], min_updates=2, newton_tol=config['newton_tol'],
                     chord_ratio=0., perturbation=1e-5, equation_tol=config['equation_tol'],
                     tail_tol=config['tail_tol'], observable_tol=config['observable_tol'],
                     require_gpu=True, minimum_charges=[floor], require_nodeless=True)
        name = f'amplitude_{index:02d}'
        def extra_check(rows):
            return extra_checks(directory/name, rows, source, config, reproduce=index == 0)
        result = run_study(study, directory/name, seed_path=guess_path, acceptance_check=extra_check)
        solves += len(result['records'])
        checks = result['additional_acceptance']
        row = dict(index=index, pin=pin, predictor=method, directory=name,
                   accepted=bool(result['accepted'] and checks['passed']), checks=checks,
                   frequencies=checks['frequencies'])
        records.append(row)
        write_json(directory/'progress.json', dict(solves=solves, records=records))
        print(json.dumps(dict(event='amplitude', **row)), flush=True)
        if not row['accepted'] or checks['ergoregion_resolved']:
            break
        states.append(load_state(directory/name/'accepted.npz')[:2])
        pins.append(pin)
        states, pins = states[-2:], pins[-2:]
        old.jax.clear_caches()
    outcome = dict(scan_completed=bool(records[-1]['accepted']), solves=solves, records=records,
                   ergoregion_resolved=bool(records[-1]['accepted'] and
                                            records[-1]['checks']['ergoregion_resolved']),
                   seconds=time.monotonic()-started, stability='not_assessed',
                   scope='Stationary k=1 amplitude continuation; sampled ergoregion sign needs '
                         'three-grid agreement. No horizon or dynamical stability claim.')
    write_json(directory/'outcome.json', outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--gpu', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--resume-bootstrap', type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    plan = preflight(args.source, config)
    if args.resume_bootstrap:
        plan['bootstrap_reuse'] = bootstrap_preflight(args.resume_bootstrap, args.source, config, plan)
    if args.gpu < 0:
        parser.error('GPU must be nonnegative')
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR', 'platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE', 'false')
    from ..solver.device import select_device
    select_device(args.gpu, 128)
    return 0 if run_scan(args.source, config, args.out,
                         resume_bootstrap=args.resume_bootstrap)['scan_completed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
