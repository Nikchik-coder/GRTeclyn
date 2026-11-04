"""Recover the same ergoregion ring with explicitly regular origin rows.

Independent original equations and a Cartesian centre certificate remain
mandatory after the three stationary resolutions pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .evolution_source_refinement import plan as refinement_plan,run as refinement_run
from .smooth_origin import SmoothOriginProblem,physical_origin_checks

DEFAULT_CONFIG = Path('research/railgun/studies/ergoregion_origin_recovery.json')


def plan(config=DEFAULT_CONFIG):
    proposed = refinement_plan(config)
    if proposed['config'].get('discretisation') != SmoothOriginProblem.discretisation:
        raise ValueError('the explicit smooth-origin numerical method is required')
    proposed.update(canonical_equations_checked=True,all_interior_rows_retained=True,
                    physical_origin_checked=True)
    return proposed


def canonical_check(problem,state,info,record):
    """The old equations and boundary rows must also pass, unimposed."""
    from .problem import RingProblem
    from .diagnostics import validate
    original = RingProblem(problem.fields,nx=problem.nx,ny=problem.ny,length=problem.length,
        target_j=problem.target_j,frequency_targets=problem.frequency_targets,
        central_lapse=problem.central_lapse)
    audit = validate(original,state,info,equation_tol=1e-8,tail_tol=1e-6,independent=False)
    regularity = physical_origin_checks(problem,state)
    record['canonical_validation'] = audit
    record['origin_regularity'] = regularity
    record['reasons'].extend('canonical_'+reason for reason in audit['reasons'])
    if not np.isfinite(regularity['maximum']) or regularity['maximum'] > 1e-8:
        record['reasons'].append('physical_origin_regularity')
    record['verdict'] = 'PASS' if not record['reasons'] else 'REJECT'
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--gpu',type=int,choices=[0,1])
    parser.add_argument('--out',type=Path)
    parser.add_argument('--resume-from',type=Path,
                        help='two passing grids interrupted before the third first update')
    args = parser.parse_args()
    proposed = plan(args.config)
    if args.dry_run:
        print(json.dumps(proposed,indent=2))
        return 0
    if args.gpu is None or args.out is None:
        parser.error('recovery requires --gpu and --out')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    result = refinement_run(args.config,args.out,problem_factory=SmoothOriginProblem,
                            grid_check=canonical_check,resume_from=args.resume_from)
    print(json.dumps(result,indent=2))
    return 0 if result['evolution_qualified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
