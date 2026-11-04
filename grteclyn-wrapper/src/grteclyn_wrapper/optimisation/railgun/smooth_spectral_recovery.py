"""Three-resolution coefficient solve of the same ring, without nodal metric rounding."""
import argparse
import json
from pathlib import Path

from .evolution_source_refinement import plan as source_plan,run
from .smooth_spectral import SmoothSpectralProblem,REPRESENTATION
from .smooth_cubic import validate

DEFAULT_CONFIG = Path('research/railgun/studies/ergoregion_smooth_spectral_372.json')


def plan(config=DEFAULT_CONFIG):
    result = source_plan(config)
    if result['config'].get('discretisation') != REPRESENTATION:
        raise ValueError('explicit metric coefficients, cubic tail and regular origin required')
    result.update(all_interior_rows_retained=True,independent_cartesian_flux=True,
                  infinity_angular_momentum_measured=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--gpu',type=int,choices=[0])
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    proposed = plan(args.config)
    if args.dry_run:
        print(json.dumps(proposed,indent=2));return 0
    if args.gpu is None or args.out is None:
        parser.error('GPU 0 and a new output directory required')
    from ..solver.device import select_device
    select_device(args.gpu,128)
    result = run(args.config,args.out,problem_factory=SmoothSpectralProblem,validator=validate)
    print(json.dumps(result,indent=2))
    return 0 if result['evolution_qualified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
