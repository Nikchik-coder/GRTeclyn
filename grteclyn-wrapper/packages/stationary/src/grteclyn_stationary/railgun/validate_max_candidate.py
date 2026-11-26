"""Three-grid validation of one hash-checked saved maximisation candidate.

No new CMA proposal or source-reproduction solve is performed. The stopped
search evidence remains immutable; all new corrections use a separate output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from grteclyn_stationary.railgun.ergoregion_cma import Search, SolveBudget, preflight, write

SOURCE = Path('results/railgun/studies/ergoregion-cma/finalists/01/accepted.npz')
SNAPSHOT = Path('results/railgun/reports/ergoregion-comparison/search-snapshot.json')


def candidate_plan(seed, *, snapshot=SNAPSHOT):
    if seed not in (271, 272):
        raise ValueError('saved maximisation seed 271 or 272 required')
    config = json.loads(Path(f'grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_max_seed{seed}.json').read_text())
    initial = preflight(SOURCE, config)
    cases = json.loads(Path(snapshot).read_text())['cases']
    case = next(c for c in cases if c['provisional'] and c['title'].endswith(f'seed {seed}'))
    source, record = Path(case['source']), Path(case['record'])
    for path, key in ((source, 'source_sha256'), (record, 'record_sha256')):
        if hashlib.sha256(path.read_bytes()).hexdigest() != case[key]:
            raise ValueError(f'saved candidate {key} mismatch')
    row = json.loads(record.read_text())
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.asarray(data['u'])
    if (row.get('verdict') != 'PASS' or not row.get('independent')
            or row.get('grid') != [160, 20] or [meta['nx'], meta['ny']] != [160, 20]
            or meta.get('validated') or meta.get('model') != 'canonical_regular_centre'
            or meta['fields'] != initial['metadata']['fields'] or meta['length'] != 2.5
            or u.shape != (5*161*21+1,) or not np.isfinite(u).all()
            or not 0 < float(u[-1]) < 1
            or not .08 <= meta['central_lapse'] <= .32):
        raise ValueError('hash-checked independently passing 160x20 candidate required')
    return dict(seed=seed, source=str(source), source_sha256=case['source_sha256'],
        record=str(record), record_sha256=case['record_sha256'], central_lapse=meta['central_lapse'],
        grids=config['grids'], maximum_new_solves=3, max_iterations=30, minimum_updates=2,
        equation_tol=1e-8, tail_tol=1e-6, observable_tol=1e-6, newton_tol=1e-14,
        search_proposals=0, source_reproduction_solves=0, checkpoints=False,
        numerical_execution=False, config=config)


def run(plan, directory):
    search = Search(SOURCE, plan['config'], directory)
    search.budget = SolveBudget(0, 3)
    search.manifest['validation_only'] = plan
    write(search.directory/'manifest.json', search.manifest)
    result = search.refine(dict(path=plan['source'], log=math.log(plan['central_lapse'])))
    accepted = bool(result['accepted'] and result['checks']['ergoregion_resolved'])
    write(search.directory/'outcome.json', dict(stage='complete', accepted=accepted,
        candidate=plan, refinement=result, search_solves=0,
        refinement_solves=search.budget.refinement_used,
        best_validated_ratio=search.best_ratio, best_path=search.best_path,
        stability='not_assessed', global_maximum_established=False))
    return accepted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, choices=(271, 272), required=True)
    parser.add_argument('--gpu', type=int, choices=(0, 1), required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    plan = candidate_plan(args.seed)
    if args.out.exists():
        raise ValueError('existing evidence is immutable; select a new approved output')
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    from grteclyn_stationary.numerics.device import select_device
    select_device(args.gpu, 128)
    return 0 if run(plan, args.out) else 2


if __name__ == '__main__':
    raise SystemExit(main())
