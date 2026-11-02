"""Prepare the requested N=192, t=50 extension from the actual t=2 inputs.

The certified t=0 cube is reused because the earlier run wrote no checkpoint.
The original box, grid, physics, timestep and plot cadence are preserved.
Long-duration isolated-ring stability is not certified in this finite box.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .evolution import digest
from .evolution_convergence import parameters, PATH_KEYS, verify_archive
from .evolution_pilot import prepare as prepare_pilot


def prepare(data_directory, reference, template, binary, *, checkpoints):
    if checkpoints not in ('off', 'on'):
        raise ValueError('explicit checkpoints=off or on required')
    data_directory, reference, template, binary = map(Path,
        (data_directory, reference, template, binary))
    verify_archive(reference)
    manifest = json.loads((reference/'run_manifest.json').read_text())
    if digest(binary) != manifest['binary']['sha256']:
        raise ValueError('the frozen t=2 binary is required')
    exported = json.loads((data_directory/'manifest.json').read_text())
    archived = json.loads((reference/'export/manifest.json').read_text())
    outcome = json.loads((reference/'export/outcome.json').read_text())
    if (exported != archived or exported['n'] != 192
            or digest(data_directory/'initial.gridinit') != outcome['gridinit_sha256']):
        raise ValueError('the original certified N=192 initial cube is required')
    # Reuse every certificate/layout/hash check of the validated short pilot.
    with TemporaryDirectory(prefix='ring-long-contract-') as temporary:
        pilot = Path(temporary)/'pilot.txt'
        prepare_pilot(data_directory, pilot, checkpoints='off')
        expected = parameters(pilot)
    original = parameters(reference/'params.txt')
    changes = {key for key in expected.keys() | original.keys()
               if expected.get(key) != original.get(key)}
    if not changes <= PATH_KEYS:
        raise ValueError(f'archived pilot differs from certified physics: {sorted(changes)}')
    replacements = dict(output_path='"."',
        recipe_initial_data_file=f'"{(data_directory/"initial.gridinit").resolve()}"',
        **{'amr.plot_file':'"RingPlt"', 'amr.check_file':'"RingChk"'},
        stop_time='50', max_steps='15000')
    if checkpoints == 'on':
        replacements.update({'amr.checkpoint_files_output':'1',
                             'checkpoint_interval':'1500'})
    lines = []
    for line in (reference/'params.txt').read_text().splitlines():
        key = line.split('=', 1)[0].strip()
        if key in replacements:
            line = f'{key} = {replacements[key]}'
        lines.append(line)
    lines[0] = '# Unperturbed omega=0.70 ring, N=192, t<=50 in the original box.'
    if checkpoints == 'on':
        lines.append('checkpoint_keep = 3')
    text = '\n'.join(lines)+'\n'
    template.parent.mkdir(parents=True, exist_ok=True)
    if template.exists():
        if template.read_text() != text:
            raise ValueError('refusing to overwrite an existing run template')
    else:
        template.write_text(text)
    updated = parameters(template)
    differences = {key:[original.get(key), updated.get(key)]
                   for key in original.keys() | updated.keys()
                   if original.get(key) != updated.get(key)}
    return dict(n=192, length=32, stop_time=50, max_steps=15000,
                dt_multiplier=.02, plot_interval=25, checkpoints=checkpoints,
                checkpoint_interval=1500 if checkpoints == 'on' else -1,
                checkpoint_keep=3 if checkpoints == 'on' else 0,
                binary_sha256=manifest['binary']['sha256'],
                gridinit_sha256=outcome['gridinit_sha256'],
                parameter_differences=differences,
                start='Same certified t=0 data; no t=2 checkpoint exists',
                scope='Longer evolution in the original box; boundary effects possible; stability not certified')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--checkpoints', choices=['off', 'on'], required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.data_dir, args.reference, args.template, args.binary,
                             checkpoints=args.checkpoints), indent=2))


if __name__ == '__main__':
    main()
