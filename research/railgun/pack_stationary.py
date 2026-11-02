#!/usr/bin/env python3
"""Archive a completed stationary study; keep original runs unchanged."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from pack_evolution import portable

REPO = Path(__file__).resolve().parents[2]


def portable_text(text):
    return re.sub(r'hostname="[^"]*"', 'hostname="two-GPU node"', portable(text))


def pack(run, name, job, report):
    run = Path(run)
    job = REPO/'runs/capped_jobs'/job
    if not re.fullmatch(r'[a-z0-9-]+', name):
        raise ValueError('archive name must be a simple study name')
    if not (job/'exit_code').exists() or int((job/'exit_code').read_text()) not in (0, 2):
        raise ValueError('only completed jobs with exit 0 or 2 can be archived')
    if not (run/'outcome.json').is_file():
        raise ValueError('completed outcome required')
    files = sorted(p for p in run.rglob('*') if p.is_file())
    if any(p.is_symlink() for p in run.rglob('*')):
        raise ValueError('symlinks are not copied into an archive')
    if sum(p.stat().st_size for p in files) > 100*1024**2:
        raise ValueError('review studies above 100 MiB separately')
    out = REPO/'results/railgun/studies'/name
    out.mkdir(exist_ok=False)
    original = {}
    for source in files:
        relative = source.relative_to(run)
        destination = out/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        original[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
        if source.suffix == '.npz':
            shutil.copy2(source, destination)
        else:
            destination.write_text(portable_text(source.read_text()))
    (out/'execution.log').write_text(portable_text((job/'log').read_text()))
    shutil.copy2(job/'exit_code', out/'exit_code.txt')
    if report:
        (out/'regressions.xml').write_text(portable_text(Path(report).read_text()))
    (out/'archive.json').write_text(json.dumps(dict(original_files_sha256=original,
        portability='NPZ files copied byte for byte; text paths made repository relative.',
        source=portable(str(run))), indent=2)+'\n')
    (out/'README.md').write_text('# Stationary ring study\n\n'
        'The original run is preserved. Outcome and grid reports distinguish\n'
        'accepted fields, provisional searches and rejected attempts. Full\n'
        'Newton histories, independent checks and execution evidence are retained.\n'
        'NPZ contents are unchanged; only text paths are made portable.\n')
    (out/'sha256sums.txt').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n'
        for p in sorted(out.rglob('*')) if p.is_file()))
    print(f'Archived {name}: {len(files)} original files, {sum(p.stat().st_size for p in files)} bytes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--job', required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    pack(args.run, args.name, args.job, args.report)
