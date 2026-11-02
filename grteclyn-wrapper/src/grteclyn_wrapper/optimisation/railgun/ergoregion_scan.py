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


def run_scan(source, config, directory):
    plan = preflight(source, config)
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
    write_json(directory/'manifest.json', manifest)
    started = time.monotonic()
    records, states, pins = [], [], []
    solves = 0
    original = json.loads((Path(source).parent/'grid_160x20.json').read_text())
    for index, pin in enumerate(plan['amplitudes']):
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
        frequencies = []
        def extra_check(rows):
            for nx, ny in [r['grid'] for r in rows]:
                with np.load(directory/name/f'grid_{nx}x{ny}.npz', allow_pickle=False) as data:
                    frequencies.append(float(data['u'][-1]))
            extra = convergence_checks(rows, frequencies, config['observable_tol'])
            if index == 0 and extra['passed']:
                final = rows[-1]
                drift = max(abs(final[k]-original[k])/max(1., abs(original[k]))
                            for k in ('M_ADM_estimate', 'J_volume'))
                extra['reparameterisation_drift'] = max(drift, abs(frequencies[-1]-.70))
                extra['passed'] = extra['reparameterisation_drift'] <= config['observable_tol']
            return extra
        result = run_study(study, directory/name, seed_path=guess_path, acceptance_check=extra_check)
        solves += len(result['records'])
        checks = result['additional_acceptance']
        row = dict(index=index, pin=pin, predictor=method, directory=name,
                   accepted=bool(result['accepted'] and checks['passed']), checks=checks,
                   frequencies=frequencies)
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
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    plan = preflight(args.source, config)
    if args.gpu < 0:
        parser.error('GPU must be nonnegative')
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR', 'platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE', 'false')
    from ..solver.device import select_device
    select_device(args.gpu, 128)
    return 0 if run_scan(args.source, config, args.out)['scan_completed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
