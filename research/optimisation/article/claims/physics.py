"""Check the stationary comparison ledger and generate its article macros."""
import csv
import hashlib
import json

import numpy as np


def load_checked(root):
    pack = root / 'results/optimisation/physics'
    def read(path):
        with path.open() as f:
            return {(r['model'], r['kind']): r for r in csv.DictReader(f, delimiter='\t')}
    rows = read(root / 'results/optimisation/article/ledger_physics.tsv')
    measured = read(pack / 'summary.tsv')
    assert set(rows) == {(m, k) for m in ('D0', 'D21', 'D30')
                         for k in ('classical', 'potential')}
    for key, row in rows.items():
        assert set(row) == set(measured[key])
        for column in row:
            if column not in ('model', 'kind'):
                row[column] = float(row[column])
                np.testing.assert_allclose(row[column], float(measured[key][column]), rtol=1e-12, atol=0)
    for model in ('D0', 'D21', 'D30'):
        for key in ('R_e', 'J'):
            np.testing.assert_allclose(rows[model, 'potential'][key], rows[model, 'classical'][key],
                                       rtol=1e-8, atol=1e-8)
    for entry in json.loads((pack / 'sources.json').read_text()):
        for source in entry['inputs']:
            assert hashlib.sha256((root / source['path']).read_bytes()).hexdigest() == source['sha256']
    for entry in json.loads((pack / 'convergence.json').read_text()):
        assert entry['passed']
    for entry in json.loads((pack / 'angular_checks.json').read_text()):
        assert entry['max_relative_difference'] < 2e-4
    for entry in json.loads((pack / 'tidal_crosscheck.json').read_text()):
        assert max(r['scaled_error'] for r in entry['comparisons']) < 2e-4
    print('Checked six stationary comparison rows, source hashes and numerical checks.')
    return rows


def generate(rows, macro):
    models = ('D0', 'D21', 'D30')
    metrics = [
        ('X', 'Total exoticity $X$', 3),
        ('bill_width90_over_Re', 'Central-90\\% proper width', 4),
        ('radial_nec_peak_Re2', 'Peak radial NEC violation', 2),
        ('nec_ray_equator_Re', 'Ray-integrated NEC magnitude', 2),
        ('tidal_v05_Re2', 'Peak tides, $v=0.5$', 2),
        ('transit_equator_over_Re', 'Light transit time', 3),
    ]
    body = []
    for key, label, digits in metrics:
        ratios = [rows[m, 'potential'][key] / rows[m, 'classical'][key] for m in models]
        body.append(label + ' & ' + ' & '.join(f'${v:.{digits}f}$' for v in ratios) + r' \\')
    macro('clmPhysicsRows', '\n'.join(body) + '\n')
    for kind, suffix in [('classical', 'Classical'), ('potential', 'Potential')]:
        r = rows['D21', kind]
        macro('clmPhysicsWidth' + suffix, f"{r['bill_width90_over_Re']:.2f}")
        macro('clmPhysicsExcursion' + suffix, f"{r['scalar_excursion']:.2f}")
    ratio = rows['D21', 'potential']['radial_nec_peak_Re2']/rows['D21', 'classical']['radial_nec_peak_Re2']
    macro('clmPhysicsPeakRatio', f'{ratio:.1f}')
    reductions = [100*(1-rows[m, 'potential']['X']/rows[m, 'classical']['X']) for m in models]
    macro('clmPhysicsReductionRange', f'{min(reductions):.0f}\\text{{--}}{max(reductions):.0f}')
    area = max(100*abs(rows[m, 'potential']['area_throat']/rows[m, 'classical']['area_throat']-1) for m in models)
    macro('clmPhysicsAreaChange', f'{area:.1f}')
    macro('clmPhysicsDtwentyoneJ', f"{rows['D21', 'potential']['J']:.4f}")
