"""Three-grid Richardson analysis of matched-time, fixed-box ring evolutions.

Constraint norms have exact continuum value zero. Integrated matter observables
instead use signed differences between three resolutions, with their unequal
refinement ratios. No assumed fourth order is substituted for a measured order.
This module uses NumPy only and never starts a GPU.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

TIMES = (0., .5, 1., 1.5, 2.)
RESOLUTIONS = (96, 128, 192)
CONSTRAINTS = {'Ham L0': 'L2_Ham_int', 'Mom L0': 'L2_Mom_int'}
OBSERVABLES = ('Q_box', 'Jz_matter_box', 'integral_abs_Phi_sq')
PATH_KEYS = {'output_path', 'recipe_initial_data_file', 'amr.plot_file', 'amr.check_file'}


def table(path):
    header = None
    for line in Path(path).read_text().splitlines():
        if line.startswith('#'):
            header = line.lstrip('#').split()
        elif line.strip():
            break
    values = np.loadtxt(path, ndmin=2)
    if not header or len(header) != values.shape[1] or not np.isfinite(values).all():
        raise ValueError(f'invalid diagnostic table: {path}')
    data = dict(zip(header, values.T))
    if 'time' not in data or np.any(np.diff(data['time']) <= 0):
        raise ValueError('diagnostic times must be strictly increasing')
    return data


def at_times(data, column, times=TIMES):
    """Select actual samples; interpolation must not create apparent order."""
    result = []
    for time in times:
        indices = np.flatnonzero(np.isclose(data['time'], time, rtol=0, atol=5e-8))
        if len(indices) != 1:
            raise ValueError(f'exactly one sample required at t={time:g}')
        result.append(float(data[column][indices[0]]))
    return result


def spacing_triplet(spacings):
    h = np.asarray(spacings, dtype=float)
    if h.shape != (3,) or not np.isfinite(h).all() or not (h[0] > h[1] > h[2] > 0):
        raise ValueError('three decreasing positive grid spacings required')
    return h


def constraint_orders(values, spacings):
    h = spacing_triplet(spacings)
    values = np.asarray(values, dtype=float)
    if values.shape != (3,) or not np.isfinite(values).all() or np.any(values <= 0):
        return [None, None]
    return (np.log(values[:-1]/values[1:])/np.log(h[:-1]/h[1:])).tolist()


def difference_factor(order, spacings):
    h = spacing_triplet(spacings)
    a, b = np.log(h[0]/h[1]), np.log(h[1]/h[2])
    return float(np.exp(order*b)*np.expm1(order*a)/np.expm1(order*b))


def richardson(values, spacings, *, difference_floor=1e-9):
    """Fit f(h)=f(0)+C h**p, reporting unresolved/oscillatory triples honestly.

    The 1e-9 absolute difference floor exceeds the archived diagnostic printing
    uncertainty. The fit interval is 0<p<=12; orders outside it are not certified.
    The reported error is an asymptotic estimate, not an independent error bound.
    """
    h = spacing_triplet(spacings)
    f = np.asarray(values, dtype=float)
    if f.shape != (3,) or not np.isfinite(f).all() or difference_floor < 0:
        raise ValueError('three finite observables and a nonnegative floor required')
    d12, d23 = float(f[0]-f[1]), float(f[1]-f[2])
    result = dict(values=f.tolist(), differences=[d12, d23], order=None,
                  continuum=None, estimated_fine_error=None, factor=None)
    if min(abs(d12), abs(d23)) <= difference_floor:
        return dict(result, status='unresolved_differences')
    if d12*d23 <= 0:
        return dict(result, status='nonmonotone')
    factor = d12/d23
    low, high = 1e-6, 12.
    if not difference_factor(low, h) < factor <= difference_factor(high, h):
        return dict(result, factor=factor, status='outside_positive_order_bracket')
    for _ in range(80):
        middle = (low+high)/2
        if difference_factor(middle, h) < factor:
            low = middle
        else:
            high = middle
    order = (low+high)/2
    correction = -d23/np.expm1(order*np.log(h[1]/h[2]))
    return dict(result, factor=factor, status='fitted', order=order,
                continuum=float(f[2]+correction), estimated_fine_error=abs(float(correction)))


def parameters(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        line = line.split('#', 1)[0].strip()
        if '=' in line:
            key, value = line.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def verify_archive(folder):
    folder = Path(folder)
    covered = set()
    for line in (folder/'sha256sums.txt').read_text().splitlines():
        expected, name = line.split(None, 1)
        covered.add(name.strip())
        path = (folder/name.strip()).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError('archive checksum path escapes its directory')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'archive checksum mismatch: {name}')
    required = {'params.txt', 'run_manifest.json', 'summary.json',
                'export/manifest.json', 'export/corridor.json',
                'data/constraint_norms.dat', 'data/complex_scalar_diagnostics.dat'}
    if not required <= covered:
        raise ValueError('archive checksums do not cover the comparison inputs')


def load_triplet(folders):
    """Refuse altered physics, source, core, binary or an unfinished member."""
    if len(folders) != 3:
        raise ValueError('Richardson analysis requires exactly three run archives')
    records = []
    for folder, n in zip(map(Path, folders), RESOLUTIONS):
        verify_archive(folder)
        export = json.loads((folder/'export/manifest.json').read_text())
        run = json.loads((folder/'run_manifest.json').read_text())
        summary = json.loads((folder/'summary.json').read_text())
        params = parameters(folder/'params.txt')
        if (export['n'] != n or export['length'] != 32 or export['frequency'] != .70
                or run.get('status') != 'finished' or run.get('exit_status') != 0
                or summary['trust_time'] != 2 or not summary['finite_diagnostics']
                or params.get('N_full') != str(n) or params.get('L_full') != '32'
                or params.get('max_level') != '0'
                or params.get('constraint_norms_interior_radius') != '8'
                or params.get('stop_time') != '2'
                or params.get('dt_multiplier') != '0.02'
                or params.get('amr.checkpoint_files_output') != '0'):
            raise ValueError('expected finished 96/128/192, omega=.70, L=32, r<8, t=2 triplet')
        # The first coarse pilot took one extra floating-point stop-boundary
        # step. All its observables are cropped to actual samples at t<=2.
        expected_steps = round(2/(.02*32/n))
        if params.get('max_steps') not in ({'-1', str(expected_steps)} if n == 96
                                           else {str(expected_steps)}):
            raise ValueError('unexpected step-count limit')
        comparable = {k:v for k,v in params.items() if k not in PATH_KEYS | {'N_full', 'max_steps'}}
        source = {k:export[k] for k in ('source_sha256', 'mass', 'winding', 'source_grid',
                    'ghosts', 'components', 'normalization', 'matter_model', 'perturbation')}
        core = json.loads((folder/'export/corridor.json').read_text())
        if (not core.get('accepted') or core.get('tolerance') != 1e-8
                or not core.get('maxima')
                or not all(np.isfinite(v) and 0 <= v <= 1e-8 for v in core['maxima'].values())):
            raise ValueError('uncertified Cartesian core')
        core_contract = {k:core[k] for k in ('radius', 'degree', 'comparison_degree',
                                            'tolerance', 'join_continuity')}
        identity = dict(params=comparable, source=source, binary=run['binary'], core=core_contract)
        if records and identity != records[0]['identity']:
            raise ValueError('triplet changes physics, gauge, boundary, source, core or binary')
        records.append(dict(folder=folder, n=n, identity=identity,
                            constraints=table(folder/'data/constraint_norms.dat'),
                            matter=table(folder/'data/complex_scalar_diagnostics.dat')))
    return records


def analyse(folders, times=TIMES):
    records = load_triplet(folders)
    h = [32/n for n in RESOLUTIONS]
    if any(t < 0 or t > 2 for t in times):
        raise ValueError('analysis must remain inside the common t<=2 trust window')
    constraints = {}
    for label, column in CONSTRAINTS.items():
        samples = np.array([at_times(r['constraints'], column, times) for r in records])
        constraints[label] = [dict(time=t, values=v.tolist(), pair_orders=constraint_orders(v, h))
                              for t, v in zip(times, samples.T)]
    observables = {}
    for column in OBSERVABLES:
        samples = np.array([at_times(r['matter'], column, times) for r in records])
        observables[column] = [dict(time=t, **richardson(v, h)) for t,v in zip(times, samples.T)]
    drift = np.array([np.array(at_times(r['matter'], 'Q_box', times))-r['matter']['Q_box'][0]
                      for r in records])
    observables['Q_box_minus_initial'] = [dict(time=t, **richardson(v, h))
                                         for t,v in zip(times, drift.T)]
    return dict(resolutions=list(RESOLUTIONS), spacings=h, times=list(times),
                scope='Unperturbed fixed-box convergence through t=2; stability not assessed',
                region='L0 only, fixed physical sphere r<8',
                constraints=constraints, observables=observables,
                expected_difference_factors={str(p):difference_factor(p, h) for p in (2,3,4)},
                archives=[str(r['folder']) for r in records],
                difference_floor=1e-9, order_bracket=[1e-6, 12],
                interpretation='Three-point asymptotic estimates; no assumed order and no stability certification')


def markdown_order_table(report):
    lines = ['| Constraint, r<8 | ' + ' | '.join(f't={t:g}' for t in report['times']) + ' |',
             '| --- | ' + ' | '.join('---' for _ in report['times']) + ' |']
    for name, rows in report['constraints'].items():
        cells = [' / '.join('unresolved' if p is None else f'{p:.2f}' for p in r['pair_orders']) for r in rows]
        lines.append('| '+name+' | '+' | '.join(cells)+' |')
    return '\n'.join(lines)+'\n\nEach cell: 96→128 / 128→192 measured order.\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', nargs=3, type=Path, help='96, 128, 192 completed archives, in that order')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = analyse(args.archives)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    args.out.with_suffix('.md').write_text(markdown_order_table(report))
    print(markdown_order_table(report))


if __name__ == '__main__':
    main()
