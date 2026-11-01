"""Solve and validate regular-centre canonical scalar rings on a selected GPU.

Configuration listing/dry-run does not import JAX or launch a calculation.
All numerical jobs must be run through capped_job.sh on the cluster.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='verb', required=True)
    solve = sub.add_parser('solve')
    solve.add_argument('config', type=Path)
    solve.add_argument('--out', type=Path, required=True)
    solve.add_argument('--gpu', type=int, required=True)
    solve.add_argument('--jac-chunk', type=int, default=128)
    solve.add_argument('--seed', type=Path)
    solve.add_argument('--dry-run', action='store_true')
    transport = sub.add_parser('transport')
    transport.add_argument('solution', type=Path)
    transport.add_argument('--out', type=Path, required=True)
    transport.add_argument('--gpu', type=int, required=True)
    transport.add_argument('--z', type=float, default=5.)
    transport.add_argument('--spin', type=float, default=1e-3)
    transport.add_argument('--speed', type=float, default=.2)
    transport.add_argument('--duration', type=float, default=10.)
    transport.add_argument('--rtol', type=float, default=1e-9)
    transport.add_argument('--max-step', type=float, default=.2)
    profile = sub.add_parser('profile')
    profile.add_argument('solution', type=Path)
    profile.add_argument('--out', type=Path, required=True)
    profile.add_argument('--gpu', type=int, required=True)
    profile.add_argument('--z-min', type=float, default=.1)
    profile.add_argument('--z-max', type=float, default=30.)
    profile.add_argument('--samples', type=int, default=101)
    args = parser.parse_args(argv)
    if args.verb == 'profile':
        if args.gpu < 0:
            parser.error('gpu must be nonnegative')
        from ..solver.device import select_device
        select_device(args.gpu, 128)
        from ..railgun.workflow import load_state, write_json
        from ..railgun.geometry import RingGeometry
        from ..railgun.profiles import axial_profile
        import numpy as np
        p, u, metadata = load_state(args.solution)
        if not metadata.get('validated') or p.jax.devices()[0].platform != 'gpu':
            parser.error('profile requires a three-grid accepted background and GPU')
        data, description = axial_profile(RingGeometry(p,u), z_min=args.z_min,
                        z_max=args.z_max, samples=args.samples)
        args.out.mkdir(parents=True, exist_ok=False)
        np.savetxt(args.out/'axis.tsv', data, delimiter='\t',header='\t'.join(description['columns']))
        write_json(args.out/'profile.json',description)
        return 0
    if args.verb == 'transport':
        if args.gpu < 0:
            parser.error('gpu must be nonnegative')
        from ..solver.device import select_device
        select_device(args.gpu, 128)
        from ..railgun.workflow import load_state, write_json
        from ..railgun.geometry import RingGeometry
        from ..railgun.transport import MPDSystem, matched_controls
        import numpy as np
        p, u, metadata = load_state(args.solution)
        if not metadata.get('validated'):
            parser.error('transport requires a three-grid accepted background')
        if p.jax.devices()[0].platform != 'gpu':
            parser.error('GPU execution required')
        geometry = RingGeometry(p, u)
        system = MPDSystem(geometry.metric)
        states = matched_controls(system, [0., 0., args.z], spin=args.spin, speed=args.speed)
        args.out.mkdir(parents=True, exist_ok=False)
        summary = dict(background_schema=metadata['schema'], model=metadata['model'],
                       background_stability='not_assessed', controls={},
                       rtol=args.rtol, max_step=args.max_step,
                       interpretation='Finite-radius tracks; no claim of asymptotic escape.')
        for label, state in states.items():
            track = system.integrate(state, duration=args.duration, rtol=args.rtol,
                                     max_step=args.max_step)
            np.savez_compressed(args.out/f'{label}.npz', time=track['time'], state=track['state'])
            small = {k:v for k,v in track.items() if k not in ('time','state')}
            write_json(args.out/f'{label}.json', small)
            summary['controls'][label] = dict(success=track['success'], stop=track['stop'],
                    absolute_drift=track['absolute_drift'], ssc_max=track['ssc_max'],
                    norm_error=track['norm_error'])
        write_json(args.out/'outcome.json', summary)
        return 0 if all(row['success'] for row in summary['controls'].values()) else 2
    config = json.loads(args.config.read_text())
    from ..railgun.model import ScalarField
    if not config.get('fields'):
        parser.error('at least one scalar field is required')
    for value in config['fields']:
        ScalarField(**value)
    if args.gpu < 0 or args.jac_chunk <= 0:
        parser.error('gpu must be nonnegative and jac-chunk positive')
    if args.dry_run:
        print(json.dumps(dict(config=config, gpu=args.gpu, jac_chunk=args.jac_chunk,
                              output=str(args.out), numerical_execution=False), indent=2))
        return 0
    from ..solver.device import select_device
    select_device(args.gpu, args.jac_chunk)
    from ..railgun.workflow import run_study
    reference = None
    if config.get('spherical_reference'):
        from ..railgun.reference import spherical_reference
        reference = spherical_reference(**config['spherical_reference'])
        # The prescribed anchor is the parity-factored field, not its central value.
        import numpy as np
        from dataclasses import replace
        field = ScalarField(**config['fields'][0])
        if len(config['fields']) != 1 or field.degree != 0:
            parser.error('spherical_reference requires one even k=0 scalar')
        amplitude = float(np.interp(field.anchor_radius, reference['isotropic_radius'], reference['chi']))
        config['fields'] = [replace(field, amplitude=amplitude).to_dict()]
    outcome = run_study(config, args.out, reference=reference, seed_path=args.seed)
    print(json.dumps({k: v for k, v in outcome.items() if k != 'records'}), flush=True)
    return 0 if outcome['accepted'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
