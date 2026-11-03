"""Bounded refinement of the same stationary ring before Cartesian export.

Planning never starts JAX. Three-grid stationary acceptance and a separate
Cartesian-origin certificate are both required to qualify for evolution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evolution import digest, source_contract

DEFAULT_CONFIG = Path('research/railgun/studies/ergoregion_source_refined.json')


def plan(config=DEFAULT_CONFIG):
    cfg = json.loads(Path(config).read_text())
    source = Path(cfg['source'])
    contract = source_contract(source)
    original = json.loads((source.parent/'manifest.json').read_text())['config']
    invariant = set(original)-{'grids'}
    if (contract['source_sha256'] != cfg['source_sha256']
            or any(cfg.get(key) != original[key] for key in invariant)
            or cfg['grids'] != [[224,28],[256,32],[288,36]]
            or cfg['max_solves'] != 3
            or cfg['core'] != dict(radius=.04,degree=12,tolerance=1e-8)):
        raise ValueError('same ring, three prepared refinement grids and unchanged gates required')
    return dict(config=cfg, source_sha256=contract['source_sha256'], max_solves=3,
        unknowns=[5*(nx+1)*(ny+1)+1 for nx,ny in cfg['grids']],
        jacobian_GiB=[8*(5*(nx+1)*(ny+1)+1)**2/2**30 for nx,ny in cfg['grids']],
        numerical_execution=False, checkpoints=False)


def run(config, directory, *, problem_factory=None, grid_check=None):
    proposed = plan(config)
    cfg = proposed['config']
    from .ergoregion_scan import extra_checks
    from .workflow import load_state, run_study, write_json
    from .geometry import RingGeometry
    from .evolution import evolution_corridor
    directory = Path(directory)
    numerical = {key:value for key,value in cfg.items()
                 if key not in ('source','source_sha256','max_solves','core','approval')}
    def acceptance(rows):
        # Resolve the same physical ring rather than accidentally adopting a
        # different root of the nonlinear equations at the same central lapse.
        import numpy as np
        from .ergoregion_scan import common_metric_samples
        result = extra_checks(directory,rows,cfg['source'],cfg)
        if not result['passed']:
            return result
        original = json.loads((Path(cfg['source']).parent/'grid_224x28.json').read_text())
        sampled = common_metric_samples(cfg['source'])
        final = dict(rows[-1],**result['common_point_extrema'][-1])
        old = dict(original,**sampled)
        keys = ('M_ADM_estimate','J_volume','lapse_min','gtt_max','shift_norm_over_lapse_max')
        changes = {key:abs(final[key]-old[key])/max(1.,abs(old[key]),abs(final[key]))
                   for key in keys}
        with np.load(cfg['source'],allow_pickle=False) as source:
            changes['frequency'] = abs(result['frequencies'][-1]-float(source['u'][-1]))
        result['source_differences'] = changes
        result['passed'] = bool(all(np.isfinite(value) and value <= cfg['observable_tol']
                                    for value in changes.values()))
        return result
    result = run_study(numerical, directory, seed_path=cfg['source'],
                       acceptance_check=acceptance,problem_factory=problem_factory,
                       grid_check=grid_check)
    qualification = dict(stationary_accepted=result['accepted'], evolution_qualified=False,
                          source_sha256=proposed['source_sha256'], checkpoints=False)
    if result['accepted']:
        source = directory/'accepted.npz'
        problem, state, _ = load_state(source)
        core = cfg['core']
        geometry = evolution_corridor(RingGeometry(problem,state),
                                      radius=core['radius'],degree=core['degree'])
        certificate = geometry.certify(tolerance=core['tolerance'])
        certificate.update(source_sha256=digest(source),
                           join_continuity='C6; degree-13 Bernstein step')
        write_json(directory/'corridor.json',certificate)
        qualification.update(evolution_qualified=certificate['accepted'],
                              refined_source_sha256=digest(source))
    write_json(directory/'evolution_qualification.json',qualification)
    return qualification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--gpu',type=int,choices=[0,1])
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps(plan(args.config),indent=2))
        return 0
    if args.gpu is None or args.out is None:
        parser.error('numerical refinement requires --gpu and --out')
    plan(args.config)
    from ..solver.device import select_device
    select_device(args.gpu,128)
    result = run(args.config,args.out)
    print(json.dumps(result,indent=2))
    return 0 if result['evolution_qualified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
