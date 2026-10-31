"""Continue a saved mixed solution to a reference's area, spin and asymmetry."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('seed', type=Path)
    ap.add_argument('reference', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--gpu', type=int, required=True)
    ap.add_argument('--winding', type=int, choices=(-1, 0, 1), required=True)
    ap.add_argument('--nx', type=int, default=150)
    ap.add_argument('--ny', type=int, default=30)
    args = ap.parse_args(argv)
    from ..solver.device import select_device
    select_device(args.gpu, 512)
    import numpy as np
    from ..boson_continuation import prepare_seed
    from ..exploration import load_seed, physical_throat, solve_trial, save_trial
    from ..study import _clean, release_solver
    from ..resolution import check_candidate, save_checked, refinement_grids
    from ..study_validation import validate

    if args.out.exists():
        ap.error('use a fresh output directory')
    seed, meta = load_seed(args.seed)
    reference, refmeta = load_seed(args.reference)
    refrow = refmeta['resolution']['records'][-1]
    if not refmeta['resolution']['passed']:
        ap.error('reference must have passed refinement')
    area = physical_throat(reference)['area_throat']
    pin = ('minimal_area', area)
    state, config, scale = prepare_seed(seed, meta['config'], area, args.winding)
    refconfig = refmeta.get('config', refmeta)
    target = {key: refconfig[key] for key in ('J', 'gamma')}
    d2 = (state['psim']/np.pi)**2
    args.out.mkdir(parents=True)
    sources = [args.seed, args.reference, *Path(__file__).parents[1].rglob('*.py')]
    manifest = dict(arguments={k: str(v) if isinstance(v, Path) else v
                               for k, v in vars(args).items()},
                    commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    sources={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                    target=target, pin=pin, similarity=scale)
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    records = []
    attempts = 0

    def record(row):
        row = _clean(row)
        records.append(row)
        with (args.out/'steps.jsonl').open('a') as f:
            f.write(json.dumps(row, allow_nan=False)+'\n')
        print(json.dumps(row, allow_nan=False), flush=True)

    def advance(goal, stage, depth=0):
        nonlocal state, config, attempts
        attempts += 1
        if attempts > 80:
            raise RuntimeError('continuation exhausted its 80-solve budget')
        try:
            solved, row = solve_trial(state, goal, args.nx, args.ny, pin, d2,
                                      max_iter=24, newton_tol=1e-12)
            if row['verdict'] != 'PASS':
                raise RuntimeError('stationary or bound-state gate failed: '+
                                   json.dumps(_clean(row)))
        except (RuntimeError, ValueError, FloatingPointError, np.linalg.LinAlgError) as err:
            record(dict(stage=stage, config=goal, verdict='FAILED', error=str(err), depth=depth))
            if depth >= 6 or stage == 'initial':
                raise
            midpoint = dict(goal)
            for key in ('J', 'gamma'):
                midpoint[key] = (config[key]+goal[key])/2
            advance(midpoint, stage, depth+1)
            advance(goal, stage, depth+1)
            return
        finally:
            release_solver()
        state, config = solved, dict(goal)
        name = f'step_{len(records):04d}.npz'
        save_trial(args.out/name, state, config, row, pin)
        record(dict(stage=stage, artifact=name, config=config, **row))

    try:
        advance(config, 'initial')
        initial_j = config['J']
        for value in np.linspace(initial_j, target['J'], 5)[1:]:
            advance(dict(config, J=float(value)), 'spin')
        initial_gamma = config['gamma']
        for value in np.linspace(initial_gamma, target['gamma'], 13)[1:]:
            advance(dict(config, gamma=float(value)), 'asymmetry')
    except (RuntimeError, ValueError, FloatingPointError, np.linalg.LinAlgError) as err:
        outcome = dict(status='continuation_failed', last_config=config,
                       target=target, error=str(err), stability='not_assessed')
        (args.out/'outcome.json').write_text(json.dumps(_clean(outcome), indent=2)+'\n')
        return 2
    validator = lambda s, c, r: validate(s, c, r, reference_peak=refrow['tidal_peak'],
                                         tidal_factor=4., energy_budget=1., detailed=True)
    row = validator(state, config, records[-1])
    save_trial(args.out/'target_seed.npz', state, config, row, pin)
    outcome = dict(status='target_reached_above_gate', candidate=row, stability='not_assessed')
    if row['verdict'] == 'PASS':
        result, state = check_candidate(state, config, refinement_grids(args.nx, args.ny),
                    pin, d2, args.out/'refinement', score_key='X_full',
                    validator=validator, perturb_seed=True)
        outcome['refinement'] = result
        outcome['status'] = 'validated_candidate' if result['passed'] else 'refinement_failed'
        if result['passed']:
            save_checked(args.out/'best_clean.npz', state, config,
                         dict(X_reference=refrow['X_full']), result)
    (args.out/'outcome.json').write_text(json.dumps(_clean(outcome), indent=2)+'\n')
    return 0 if outcome['status'] == 'validated_candidate' else 2


if __name__ == '__main__':
    raise SystemExit(main())
