"""Compare archived D0/D21/D30 mechanisms and stationary trade-offs on CPU."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from grteclyn_wrapper.core.config import resolve_repo_root
from ..diagnostics import analyse, classical, potential, spherical_tidal_check, static

SOURCES = {
    'D0': 'results/optimisation/validation/2026-10-30-alternatives/d0/009_e0211/handoff.npz',
    'D21': 'results/optimisation/article/d21_e140_210x42.npz',
    'D30': 'results/optimisation/completed/2026-10-31/d30/fam_a_r1_0005_cma_resolution_20261030_best_clean.npz',
}
REFERENCES = {
    'D21': 'results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0000.json',
    'D30': 'results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0005.json',
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=Path('results/optimisation/physics'))
    args = ap.parse_args(argv)
    root = resolve_repo_root(); args.out.mkdir(parents=True, exist_ok=True)
    rows, checks, manifest, extent_checks, tidal_checks, angular_checks = [], [], [], [], [], []
    for model, source in SOURCES.items():
        opt = potential(root/source)
        ref = static() if model == 'D0' else classical(root/REFERENCES[model])
        np.testing.assert_allclose(opt.J, ref.J, atol=1e-8, rtol=1e-8)
        np.testing.assert_allclose(opt.geometry['R_e'], ref.geometry['R_e'], rtol=1e-8)
        np.testing.assert_allclose(opt.F[[0, -1], 0], ref.F[[0, -1], 0], atol=1e-9)
        for kind, bg in (('classical', ref), ('potential', opt)):
            start = time.monotonic()
            coarse, _ = analyse(bg, order=192, samples=81, rtol=1e-9)
            fine, profile = analyse(bg, order=384, samples=161, rtol=1e-11)
            q, w = np.polynomial.legendre.leggauss(384)
            angular = {str(n): float(w @ bg.shell(q, n_mu=n)[0]) for n in (32, 64, 128)}
            angular_error = max(abs(v/angular['128']-1) for v in angular.values())
            assert angular_error < 2e-4, (model, kind, angular)
            angular_checks.append(dict(model=model, kind=kind, absolute_VIQ=angular,
                                       max_relative_difference=angular_error))
            errors = {k: abs(coarse[k]-fine[k])/max(abs(fine[k]), 1e-12)
                      for k in fine if isinstance(fine[k], (int, float))}
            # Sampled peaks are distinguished from quadrature and refined tides.
            numerical = ['X', 'bill_width90_over_Re', 'nec_ray_equator_Re', 'nec_ray_axis_Re',
                         'transit_equator_over_Re', 'transit_axis_over_Re',
                         'tidal_v0_Re2', 'tidal_v05_Re2']
            good = all(errors[k] < 2e-4 for k in numerical)
            checks.append(dict(model=model, kind=kind, passed=good, relative_errors=errors))
            row = dict(model=model, kind=kind, **fine)
            rows.append(row)
            np.savez_compressed(args.out/f'{model}_{kind}_profiles.npz', **profile)
            print(json.dumps(dict(model=model, kind=kind, X=fine['X'],
                                  passed=good, max_error=max(errors[k] for k in numerical),
                                  seconds=time.monotonic()-start)), flush=True)
            if not good:
                (args.out/'convergence.json').write_text(json.dumps(checks, indent=2)+'\n')
                raise RuntimeError(f'{model} {kind}: quadrature/profile checks failed')
            re = bg.geometry['R_e']
            for extent in (5., 10., 20.):
                for ray, mu in (('equator', 0.), ('axis', 1.)):
                    _, t = bg.crossing(np.array([-extent, extent])*re, mu=mu, rtol=1e-11)
                    extent_checks.append(dict(model=model, kind=kind, ray=ray,
                                              extent_Re=extent, transit_over_Re=float(np.diff(t)[0]/re)))
            if model == 'D0':
                checks_fd = spherical_tidal_check(bg)
                assert max(r['scaled_error'] for r in checks_fd) < 2e-4
                tidal_checks.append(dict(model=model, kind=kind, comparisons=checks_fd))
        files = [source] + ([REFERENCES[model], str(Path(REFERENCES[model]).with_suffix('.npz'))]
                            if model in REFERENCES else [])
        manifest.append(dict(model=model, inputs=[dict(path=f, sha256=hashlib.sha256((root/f).read_bytes()).hexdigest())
                                                  for f in files],
                             analytic_reference='eta0=2, gamma=-pi static drainhole' if model=='D0' else None))
    with (args.out/'summary.tsv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    (args.out/'convergence.json').write_text(json.dumps(checks, indent=2)+'\n')
    (args.out/'sources.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (args.out/'endpoint_checks.json').write_text(json.dumps(extent_checks, indent=2)+'\n')
    (args.out/'tidal_crosscheck.json').write_text(json.dumps(tidal_checks, indent=2)+'\n')
    (args.out/'angular_checks.json').write_text(json.dumps(angular_checks, indent=2)+'\n')
    # Saved refinements can be interpolants; this alone is not continuum convergence.
    field_checks = []
    for model, directory in (
        ('D0', root/'results/optimisation/validation/2026-10-30-alternatives/d0/009_e0211'),
        ('D30', root/'results/optimisation/completed/2026-10-31/d30/resolution/e0316_refine')):
        baseline = next(r for r in rows if r['model']==model and r['kind']=='potential')
        for grid in ('150x30', '180x36'):
            source = directory/f'diagnostic_{grid}.npz'
            bg = potential(source)
            result, _ = analyse(bg, order=384, samples=161, rtol=1e-11)
            keys = ['X', 'radial_nec_peak_Re2', 'tidal_v05_Re2', 'nec_ray_equator_Re',
                    'transit_equator_over_Re', 'bill_width90_over_Re']
            delta = {k: abs(result[k]/baseline[k]-1) for k in keys}
            assert max(delta.values()) < 2e-4, (model, grid, delta)
            field_checks.append(dict(model=model, grid=grid, source=str(source.relative_to(root)),
                                     sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                     relative_difference_from_210=delta))
    (args.out/'field_checks.json').write_text(json.dumps(field_checks, indent=2)+'\n')


if __name__ == '__main__':
    main()
