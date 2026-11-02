"""Wait for a completed ring evolution, then render movies on the CPU.

Original frames and slice caches are never modified. The completed manifest
and the complete cache cadence are required before any redraw starts.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np

from .evolution_convergence import table


def completed(run: Path, end: float) -> bool:
    manifest = json.loads((run / 'run_manifest.json').read_text())
    if manifest['status'] == 'running':
        return False
    if manifest['status'] != 'finished' or manifest.get('exit_status') != 0:
        raise ValueError('evolution failed; movies were not started')
    if manifest.get('t_end') is None or abs(manifest['t_end'] - end) > 1e-7:
        raise ValueError('evolution did not reach the requested end time')
    return True


def validate_cache(run: Path, fields: list[str], end: float,
                   steps: int, cadence: int) -> int:
    expected = list(range(0, steps + 1, cadence))
    for field in fields:
        paths = sorted((run / 'frames/_slice_cache' / f'{field}_z').glob('slice_*.npz'))
        indices = [int(p.stem.split('_')[-1]) for p in paths]
        if indices != expected:
            raise ValueError(f'incomplete slice cache for {field}: {len(paths)} frames')
        for index, path in zip(expected, paths):
            with np.load(path) as data:
                if abs(float(data['time']) - end * index / steps) > 1e-7:
                    raise ValueError(f'wrong cached time in {path.name}')
                values = data['arr']
                if np.isinf(values).any() or not np.isfinite(values).any():
                    raise ValueError(f'invalid cached values in {field}/{path.name}')
    for name in ('complex_scalar_diagnostics', 'collapse_diagnostics', 'constraint_norms'):
        diagnostic = table(run / 'data' / f'{name}.dat')
        if abs(diagnostic['time'][-1] - end) > 1e-7:
            raise ValueError(f'incomplete diagnostics: {name}')
    return len(expected)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run', type=Path)
    ap.add_argument('--end', type=float, default=50.)
    ap.add_argument('--steps', type=int, default=15000)
    ap.add_argument('--cadence', type=int, default=25)
    ap.add_argument('--wait-seconds', type=int, default=10800)
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[5]
    run = args.run.resolve()
    # ffmpeg inherits this affinity as well as the numerical thread limits.
    available = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, available[:2])
    deadline = time.monotonic() + args.wait_seconds
    print('[movies] waiting for evolution and final consumer drain', flush=True)
    while not completed(run, args.end):
        if time.monotonic() >= deadline:
            raise TimeoutError('evolution did not finish within the movie wait budget')
        time.sleep(30)
    fields = [line.strip() for line in
              (repo / 'grteclyn-wrapper/scripts/campaigns/railgun/frames_default.txt')
              .read_text().splitlines() if line.strip() and not line.startswith('#')]
    count = validate_cache(run, fields, args.end, args.steps, args.cadence)
    render = run / 'movie_render'
    render.mkdir(exist_ok=True)
    print(f'[movies] complete cache: {count} frames x {len(fields)} fields', flush=True)
    subprocess.run([
        sys.executable, str(repo / 'grteclyn-wrapper/scripts/plot/rerender_frames.py'),
        str(run / 'frames'), '--out', str(render / 'frames'), '--t-max', str(args.end),
        '--symlog', 'phi,Pi,phi_lump0,Pi_lump0,chi_minus_1,shift1,shift2,shift3,'
        'Weyl4_Re:1.5,Weyl4_Im:1.5', '--skip', '', '--movies',
    ], check=True)
    destination = run / 'movies'
    destination.mkdir(exist_ok=True)
    records = {}
    from PIL import Image, ImageOps, ImageDraw
    for field in fields:
        name = f'movie_{field}_z.mp4'
        source = render / 'movies' / name
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,nb_frames,duration',
            '-of', 'json', str(source),
        ], text=True))['streams'][0]
        if not count <= int(probe['nb_frames']) <= count + 2:
            raise ValueError(f'wrong encoded frame count: {name}')
        if abs(float(probe['duration']) - count / 10.) > .3:
            raise ValueError(f'wrong movie duration: {name}')
        temporary = destination / f'.{name}.tmp'
        shutil.copy2(source, temporary)
        temporary.replace(destination / name)
        records[name] = probe
        # Three consecutive frames from the actual MP4, for colourbar QA.
        if field in ('scalar_activity', 'phi', 'shift1', 'lapse'):
            qa = render / 'qa' / field
            qa.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                'ffmpeg', '-y', '-loglevel', 'error', '-ss', str(count / 20.),
                '-i', str(source), '-frames:v', '3', str(qa / '%02d.png'),
            ], check=True)
            images = [Image.open(p).convert('RGB') for p in sorted(qa.glob('*.png'))]
            width, height = images[0].size
            sheet = Image.new('RGB', (3 * width, height + 32), 'white')
            ImageDraw.Draw(sheet).text((10, 8), f'{field}: consecutive decoded movie frames', fill='black')
            for index, image in enumerate(images):
                sheet.paste(ImageOps.pad(image, (width, height)), (index * width, 32))
            sheet.save(render / 'qa' / f'{field}-consecutive.png')
    report = {'stage': 'encoded; contact sheets await visual review',
              'time_range': [0., args.end], 'cached_frames_per_field': count,
              'fixed_colour_scales': True, 'original_frames_preserved': True,
              'scope': 'Exploratory finite-box evolution; no isolated-ring stability claim.',
              'movies': records}
    (destination / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'[movies] finished: {len(records)} movies; QA sheets in movie_render/qa', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
