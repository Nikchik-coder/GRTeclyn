#!/usr/bin/env python3
"""Pack a finished ring pilot, portable diagnostics and selected slice inputs.

Full plotfiles, Cartesian gridinit data, frames and caches stay in runs/scratch.
The accepted spectral source plus code reconstructs the large initial cube.
No live run, checkpoint or frame is removed by this packer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

import numpy as np

REPO = Path(__file__).resolve().parents[2]


def portable(text):
    text = text.replace(str(REPO) + '/', '')
    text = re.sub(r'/(?:home|workspace-[^/]+)/[^\s"\']*?GRTeclyn/', '', text)
    return text.replace('/tmp/grteclyn_scratch/', '<scratch>/')


def table(path):
    header = None
    for line in path.read_text().splitlines():
        if line.startswith('#'):
            header = line.lstrip('#').split()
        elif line.strip():
            break
    data = np.loadtxt(path, ndmin=2)
    if not header or len(header) != data.shape[1]:
        raise ValueError(f'bad diagnostic header: {path.name}')
    return dict(zip(header, data.T))


def pack(run, exported, name, *, job, trust=2.):
    run, exported = Path(run), Path(exported)
    manifest = json.loads((run/'run_manifest.json').read_text())
    if manifest.get('status') != 'finished' or manifest.get('exit_status') != 0:
        raise ValueError('only a finished, drained pilot can be packed')
    out = REPO/'results/railgun/studies'/name
    out.mkdir(exist_ok=False)
    for filename in ('run.log', 'consumer.log', 'params.txt', 'preflight.json',
                     'parameters_and_version.txt', 'run_manifest.json'):
        source = run/filename
        if source.exists():
            text = portable(source.read_text())
            if filename == 'run_manifest.json':
                record = json.loads(text)
                for key in ('node', 'node_label'):
                    if key in record:
                        record[key] = 'the second GPU node'
                text = json.dumps(record, indent=2) + '\n'
            (out/filename).write_text(text)
    for directory in ('data', 'small_data'):
        (out/directory).mkdir()
        for source in sorted((run/directory).glob('*.dat')):
            (out/directory/source.name).write_text(portable(source.read_text()))
    (out/'export').mkdir()
    for filename in ('manifest.json', 'outcome.json', 'corridor.json', 'progress.json'):
        (out/'export'/filename).write_text(portable((exported/filename).read_text()))
    log = REPO/'runs/capped_jobs'/job/'log'
    (out/'execution.log').write_text(portable(log.read_text()))
    n = json.loads((exported/'manifest.json').read_text())['n']
    final_step = round(trust/(.02*32/n))
    (out/'slices').mkdir()
    for field in ('scalar_activity', 'chi', 'lapse'):
        for step in (0, final_step):
            source = run/f'frames/_slice_cache/{field}_z/slice_{step:04d}.npz'
            with np.load(source, allow_pickle=False) as data:
                if float(data['time']) > trust + 1e-10:
                    raise ValueError('slice exceeds the trust window')
            shutil.copyfile(source, out/'slices'/f'{field}_{step:04d}.npz')
    figure = run/'preflight_frames/scalar_activity_z/frames/frame_z_0000.png'
    shutil.copyfile(figure, REPO/f'results/railgun/figures/ring070-n{n}-initial.png')
    series = table(run/'data/complex_scalar_diagnostics.dat')
    constraints = table(run/'data/constraint_norms.dat')
    mask = series['time'] <= trust + 1e-10
    if series['time'][mask][-1] < trust - 1e-6:
        raise ValueError('pilot did not reach its trust endpoint')
    summary = dict(pilot_completed=True, stability='not_assessed', n=n,
        trust_time=trust, recorded_end_time=float(series['time'][-1]),
        maximum_charge_relative_drift=float(np.max(abs(series['Q_box'][mask]/series['Q_box'][0]-1))),
        initial_Q=float(series['Q_box'][0]), final_Q=float(series['Q_box'][mask][-1]),
        initial_matter_J=float(series['Jz_matter_box'][0]), final_matter_J=float(series['Jz_matter_box'][mask][-1]),
        initial_peak_Phi_squared=float(series['max_abs_Phi_sq'][0]),
        final_peak_Phi_squared=float(series['max_abs_Phi_sq'][mask][-1]),
        maximum_m2_shape=float(np.max(np.hypot(series['m2_re'][mask], series['m2_im'][mask]))),
        finite_diagnostics=bool(all(np.isfinite(a).all() for a in series.values())),
        constraint_initial={key:float(value[0]) for key,value in constraints.items()},
        constraint_final={key:float(value[constraints['time']<=trust+1e-10][-1])
                          for key,value in constraints.items()},
        evidence='Unperturbed finite 3+1 pilot, full default frames and complex scalar parts; not a stability proof.')
    (out/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    (out/'README.md').write_text(
        '# Unperturbed scalar-ring evolution pilot\n\n'
        f'Cartesian N={n}, box 32, omega=0.70. Analysis uses t<=2 only.\n\n'
        'The spectral source is frequency-deep/frequency_01/accepted.npz.\n'
        'Export/core and binary/source hashes are retained. The large gridinit\n'
        'cube is reproducible with the exporter; it and all original frames\n'
        'remain in the run tree. Selected numerical slice inputs rebuild the\n'
        'figures without the cluster. No dynamical-stability claim.\n')
    (out/'sha256sums.txt').write_text(''.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(out)}\n'
        for path in sorted(out.rglob('*')) if path.is_file()))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--export', dest='exported', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--job', required=True)
    args = parser.parse_args()
    pack(args.run, args.exported, args.name, job=args.job)
