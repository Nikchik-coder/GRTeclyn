#!/usr/bin/env python3
"""Certify the Cartesian origin of a hash-checked accepted ergoregion ring."""
from grteclyn_stationary.provenance import source_revision
import argparse
import json
from pathlib import Path

from grteclyn_stationary.numerics.device import select_device


DEFAULT_CONFIG = Path('grteclyn-wrapper/scripts/campaigns/railgun/configs/evolution_ergoregion_best.json')


def plan(config=DEFAULT_CONFIG):
    from grteclyn_stationary.railgun.evolution_amr import load_plan
    cfg = json.loads(Path(config).read_text())
    cfg, contract = load_plan(config,cfg['base_N'][0])
    return cfg, contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gpu', type=int, choices=[0,1])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    cfg, contract = plan(args.config)
    if args.dry_run:
        print(json.dumps(dict(source=cfg['source'],source_sha256=contract['source_sha256'],
                              core=cfg['core'],numerical_execution=False),indent=2))
        return
    if args.gpu is None or args.out is None:
        parser.error('certification requires --gpu and --out')
    args.out.mkdir(parents=True, exist_ok=False)
    select_device(args.gpu)
    from grteclyn_stationary.railgun.evolution import digest
    from grteclyn_stationary.railgun.evolution import evolution_corridor
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.workflow import write_json
    source = Path(cfg['source'])
    problem, u, _ = load_state(source)
    if problem.jax.devices()[0].platform != 'gpu':
        raise ValueError('origin certification requires CUDA')
    core = cfg['core']
    geometry = evolution_corridor(RingGeometry(problem, u), radius=core['radius'],degree=core['degree'])
    write_json(args.out/'manifest.json',dict(source=cfg['source'],
        source_sha256=contract['source_sha256'],core=core,
        configuration_sha256=digest(args.config),
        commit=source_revision(),
        checkpoints=False))
    result = geometry.certify(tolerance=core['tolerance'])
    result.update(source_sha256=contract['source_sha256'],
                  join_continuity='C6; degree-13 Bernstein step')
    write_json(args.out/'corridor.json', result)
    print(result['accepted'], result['maxima'], flush=True)
    if not result['accepted']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
