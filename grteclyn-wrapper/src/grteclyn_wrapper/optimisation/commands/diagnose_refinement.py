"""Separate interpolation, perturbation and Jacobian-reuse refinement errors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('study', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--gpu', type=int, required=True)
    ap.add_argument('--grids', default='150x30,180x36,210x42')
    args = ap.parse_args(argv)
    from ..solver.device import select_device
    select_device(args.gpu, 512)
    import numpy as np
    from ..exploration import load_seed, solve_trial, save_trial
    from ..resolution import screen_trial
    from ..study import release_solver, write_json
    records = [json.loads(line) for line in
               (args.study/'evaluations.jsonl').read_text().splitlines()]
    chosen = min((r for r in records if r.get('verdict') == 'PASS'),
                 key=lambda r: r['X_full'])
    source, _ = load_seed(args.study/chosen['artifact'])
    base, _ = load_seed(args.study/'reference.npz')
    config = chosen['config']
    manifest = json.loads((args.study/'reference/manifest.json').read_text())
    pin, d2 = tuple(manifest['pin']), (base['psim']/np.pi)**2
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out/'manifest.json', dict(candidate=chosen['artifact'],
               config=config, pin=pin, grids=args.grids, target=1e-14,
               min_updates=1, acceptance=1e-8, stability='not_assessed'))
    rows = []
    for grid in args.grids.split(','):
        nx, ny = map(int, grid.split('x'))
        _, screen = screen_trial(source, config, nx, ny, pin, d2)
        screen.update(stage='interpolation_only', grid=grid)
        rows.append(screen)
        print(json.dumps(screen), flush=True)
        for epsilon, chord_ratio in ((0., .1), (1e-6, .1), (1e-6, 0.)):
            start = time.monotonic()
            seed = dict(source)
            seed['F'] = source['F'] + epsilon*(1-source['sx'][:, None]**2)*(
                1+.2*source['sy'][None, :])
            tag = f'{grid}_eps{epsilon:g}_chord{chord_ratio:g}'
            try:
                state, row = solve_trial(seed, config, nx, ny, pin, d2,
                    max_iter=24, newton_tol=1e-14, min_updates=1,
                    chord_ratio=chord_ratio)
                save_trial(args.out/(tag+'.npz'), state, config, row, pin)
            except (RuntimeError, ValueError, FloatingPointError) as err:
                row = dict(verdict='FAILED', error=str(err))
            row.update(stage='solve', grid=grid, perturbation=epsilon,
                       chord_ratio=chord_ratio, seconds=time.monotonic()-start)
            rows.append(row)
            print(json.dumps(row), flush=True)
            write_json(args.out/'records.json', rows)
            release_solver()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
