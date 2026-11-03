#!/usr/bin/env python3
"""Certify the Cartesian origin of the strongest accepted ergoregion ring."""
import argparse
from pathlib import Path

from grteclyn_wrapper.optimisation.solver.device import select_device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gpu', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    select_device(args.gpu)
    from grteclyn_wrapper.optimisation.railgun.evolution import source_contract, evolution_corridor
    from grteclyn_wrapper.optimisation.railgun.geometry import RingGeometry
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state, write_json
    source = Path('results/railgun/studies/ergoregion-max-r2-seed272/finalists/04/accepted.npz')
    contract = source_contract(source)
    if contract['source_sha256'] != '918323cc935ae66dce851af294fe7c6fbea0e4adbef16e40b43db6e4e4fc425f':
        raise ValueError('selected source identity changed')
    args.out.mkdir(parents=True, exist_ok=False)
    problem, u, _ = load_state(source)
    geometry = evolution_corridor(RingGeometry(problem, u), radius=.04, degree=8)
    result = geometry.certify(tolerance=1e-8)
    result.update(source_sha256=contract['source_sha256'],
                  join_continuity='C6; degree-13 Bernstein step')
    write_json(args.out/'corridor.json', result)
    print(result['accepted'], result['maxima'], flush=True)
    if not result['accepted']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
