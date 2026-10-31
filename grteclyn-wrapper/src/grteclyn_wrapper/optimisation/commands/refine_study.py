"""Recheck the best saved fixed-area candidate with independent strict solves."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('study', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--gpu', type=int, required=True)
    args = ap.parse_args(argv)
    from ..solver.device import select_device
    select_device(args.gpu, 512)
    from ..exploration import load_seed
    from ..resolution import check_candidate, save_checked
    from ..study_validation import validate
    import numpy as np
    records = [json.loads(line) for line in
               (args.study/'evaluations.jsonl').read_text().splitlines()]
    candidate = min((r for r in records if r.get('verdict') == 'PASS'),
                    key=lambda r: r['X_full'])
    state, _ = load_seed(args.study/candidate['artifact'])
    base, meta = load_seed(args.study/'reference.npz')
    reference = meta['resolution']['records'][-1]
    manifest = json.loads((args.study/'manifest.json').read_text())
    check = json.loads((args.study/'reference/manifest.json').read_text())
    case = manifest['case']
    validator = lambda s, c, r: validate(
        s, c, r, reference_peak=reference['tidal_peak'],
        tidal_factor=case['tidal_factor'], energy_budget=case['energy_budget'],
        detailed=True)
    result, state = check_candidate(
        state, candidate['config'], check['grids'], tuple(check['pin']),
        (base['psim']/np.pi)**2, args.out, score_key='X_full',
        validator=validator, perturb_seed=True)
    if result['passed']:
        save_checked(args.out/'best_clean.npz', state, candidate['config'],
                     dict(candidate_artifact=candidate['artifact'],
                          X_reference=reference['X_full']), result)
    print(json.dumps(dict(passed=result['passed'], candidate=candidate['artifact']),
                     sort_keys=True), flush=True)
    return 0 if result['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
