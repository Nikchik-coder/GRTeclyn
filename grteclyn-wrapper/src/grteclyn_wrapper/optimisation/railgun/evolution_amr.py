"""Aligned initial-data cubes and matched templates for the ergoregion study.

Each AMR level receives a fresh sample of the same spectral solution. A fine
level never interpolates the coarse level's initial cube. All production
sampling and origin certification require CUDA; planning is CPU-only.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import time

import numpy as np

from .evolution import (COMPONENTS, algebraic_checks, digest, evolution_corridor,
                        grid_layout, grid_points, source_contract, state_evaluator)

DEFAULT_CONFIG = Path('research/railgun/studies/evolution_ergoregion_best.json')


def load_plan(config, n):
    cfg = json.loads(Path(config).read_text())
    contract = source_contract(cfg['source'])
    if contract['source_sha256'] != cfg['source_sha256']:
        raise ValueError('selected source hash changed')
    with np.load(cfg['source'],allow_pickle=False) as saved:
        frequency = float(saved['u'][-1])
    core = cfg['core']
    if (contract['mass'] != 1.0 or contract['winding'] != 1
            or not np.isfinite(cfg['frequency']) or abs(cfg['frequency']-frequency) > 1e-12
            or not np.isfinite(core['radius']) or core['radius'] <= 0
            or isinstance(core['degree'],bool) or int(core['degree']) != core['degree'] or core['degree'] < 3
            or core['comparison_degree'] != core['degree']+2 or core['tolerance'] != 1e-8):
        raise ValueError('source frequency, mass/winding and unchanged origin certificate limits required')
    if n not in cfg['base_N'] or cfg['checkpoints'] is not False:
        raise ValueError('approved base resolution and checkpoints OFF required')
    length, maximum = cfg['length'], cfg['max_level']
    radii, lengths = cfg['refinement_radii'], cfg['initial_cube_lengths']
    if (length != 64 or maximum != 6 or cfg['stop_time'] != 50
            or len(radii) != maximum or len(lengths) != maximum+1
            or lengths[0] != length or not 0 < radii[-1]
            or any(a <= b for a,b in zip([length/2]+radii, radii))):
        raise ValueError('L=64, six decreasing refinement radii and t=50 required')
    levels = []
    for level, side in enumerate(lengths):
        dx = length/(n*2**level)
        cells = round(side/dx)
        offset = (length-side)/(2*dx)
        if cells < 16 or cells % 8 or abs(cells*dx-side) > 1e-12 or abs(offset-round(offset)) > 1e-8:
            raise ValueError('nested cubes must align exactly with evolution cell centres')
        levels.append(dict(level=level, n=cells, length=side, dx=dx,
                           origin=(length-side)/2-4*dx,
                           bytes=(cells+8)**3*len(COMPONENTS)*8))
    return cfg, dict(**contract, base_n=n, world_length=length, max_level=maximum,
                     levels=levels, total_bytes=sum(p['bytes'] for p in levels),
                     finest_dx=levels[-1]['dx'], stop_time=50., checkpoints=False)


def export(config, out, n, *, batch=2048):
    cfg, plan = load_plan(config, n)
    from .geometry import RingGeometry
    from .workflow import load_state, write_json
    problem, state, _ = load_state(cfg['source'])
    jax = problem.jax
    if jax.devices()[0].platform != 'gpu':
        raise ValueError('production sampling and certification require CUDA')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    core = cfg['core']
    geometry = evolution_corridor(RingGeometry(problem, state),
                                  radius=core['radius'], degree=core['degree'])
    certificate = geometry.certify(tolerance=core['tolerance'])
    certificate.update(join_continuity='C6; degree-13 Bernstein step',
                       source_sha256=plan['source_sha256'])
    write_json(out/'corridor.json', certificate)
    if not certificate['accepted']:
        write_json(out/'outcome.json', dict(accepted=False, reason='origin_certificate'))
        raise ValueError('origin certificate rejected; no cube exported')
    manifest = dict(**plan, frequency=float(geometry.frequencies[0]),
        components=COMPONENTS, ghosts=4, batch=batch, core=core,
        matter_model='grtresna_complex_scalar', perturbation='none',
        normalization='Phi=chi_complex/sqrt(4*pi); Pi=+n^a partial_a Phi',
        commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        certificate_sha256=digest(out/'corridor.json'))
    write_json(out/'manifest.json', manifest)
    evaluate = state_evaluator(geometry.metric, lambda x: geometry.scalar(x,0), jax)
    files = []
    for level in plan['levels']:
        cells, side, dx, origin = (level[key] for key in ('n','length','dx','origin'))
        width = cells+8
        path = out/f'level_{level["level"]:02d}.gridinit'
        partial = path.with_suffix('.partial')
        header = ('GRTECLYN_GRID_INIT_V2\n'
            f'num_components {len(COMPONENTS)}\ncomponent_names {" ".join(COMPONENTS)}\n'
            f'nx_ny_nz {width} {width} {width}\n'
            f'dx {dx:.17e} {dx:.17e} {dx:.17e}\n'
            f'origin {origin:.17e} {origin:.17e} {origin:.17e}\nEND_HEADER\n')
        totals = np.zeros(2)
        maxima = dict(determinant_error=0., trace_A_error=0.)
        with partial.open('xb') as stream:
            stream.write(header.encode('ascii'))
            for start in range(0, width**3, batch):
                end = min(start+batch, width**3)
                points, indices = grid_points(cells, side, 4, start, end)
                padded = np.pad(points, ((0,batch-len(points)),(0,0)), mode='edge')
                values, densities = map(np.asarray, evaluate(jax.numpy.asarray(padded)))
                values, densities = values[:end-start], densities[:end-start]
                check = algebraic_checks(values)
                if not check['accepted']:
                    raise ValueError(f'CCZ4 algebraic checks failed on level {level["level"]}, cell {start}')
                for key in maxima:
                    maxima[key] = max(maxima[key], check[key])
                inside = np.all((indices>=4)&(indices<cells+4), axis=1)
                totals += densities[inside,:2].sum(axis=0)*dx**3
                stream.write(np.asarray(values,dtype='<f8').tobytes())
                if start == 0 or end == width**3 or start//batch % 128 == 0:
                    progress = dict(level=level['level'], cells=end, total=width**3,
                                    seconds=time.monotonic()-started)
                    write_json(out/'progress.json', progress)
                    print('[amr-export]', progress, flush=True)
        balance = abs(totals[1]+plan['winding']*totals[0])/max(abs(totals[0]),1e-30)
        if totals[0] <= 0 or balance > 1e-10:
            raise ValueError('charge/angular-momentum identity failed')
        partial.rename(path)
        files.append(dict(**level, file=path.name, sha256=digest(path),
                          charge=float(totals[0]), matter_J=float(totals[1]),
                          charge_J_error=float(balance), **maxima))
        write_json(out/'levels.json', files)
    outcome = dict(accepted=True, levels=files, source_sha256=plan['source_sha256'],
                   certificate_sha256=digest(out/'corridor.json'),
                   seconds=time.monotonic()-started, evolution_validated=False)
    write_json(out/'outcome.json', outcome)
    return outcome


def prepare(config, exported, template, n, *, checkpoints):
    if checkpoints != 'off':
        raise ValueError('checkpoints OFF required for this study')
    cfg, plan = load_plan(config,n)
    exported = Path(exported).resolve()
    manifest = json.loads((exported/'manifest.json').read_text())
    outcome = json.loads((exported/'outcome.json').read_text())
    certificate = json.loads((exported/'corridor.json').read_text())
    if (not outcome.get('accepted') or not certificate.get('accepted')
            or manifest['source_sha256'] != plan['source_sha256']
            or outcome['source_sha256'] != plan['source_sha256']
            or manifest['base_n'] != n or manifest['world_length'] != cfg['length']
            or manifest['max_level'] != cfg['max_level']
            or abs(manifest['frequency']-cfg['frequency']) > 1e-12
            or manifest['components'] != COMPONENTS or manifest['ghosts'] != 4
            or manifest['certificate_sha256'] != digest(exported/'corridor.json')
            or outcome['certificate_sha256'] != manifest['certificate_sha256']
            or certificate['radius'] != cfg['core']['radius']
            or certificate['degree'] != cfg['core']['degree']
            or certificate['comparison_degree'] != cfg['core']['comparison_degree']
            or certificate['tolerance'] != 1e-8
            or certificate['join_continuity'] != 'C6; degree-13 Bernstein step'
            or not certificate['maxima']
            or any(not np.isfinite(v) or v < 0 or v > 1e-8 for v in certificate['maxima'].values())
            or len(outcome['levels']) != 7):
        raise ValueError('certified, hash-matched source and AMR export required')
    files = []
    for expected, actual in zip(plan['levels'],outcome['levels']):
        path = exported/f'level_{expected["level"]:02d}.gridinit'
        layout = grid_layout(path)
        if (any(actual[key] != expected[key] for key in ('level','n','length','dx','origin'))
                or actual['sha256'] != digest(path)
                or layout['shape'] != [expected['n']+8]*3
                or layout['components'] != COMPONENTS
                or layout['spacing'] != [expected['dx']]*3
                or layout['origin'] != [expected['origin']]*3):
            raise ValueError('AMR initial-data level identity or alignment changed')
        files.append(str(path))
    # Preserve the established matter, gauge and CCZ4 settings verbatim.
    from .evolution_convergence import parameters
    reference = Path('results/railgun/studies/evolution-070-n128/params.txt')
    original = parameters(reference)
    replacements = dict(output_path='"."', **{
        'amr.plot_file':'"RingPlt"','amr.check_file':'"RingChk"',
        'recipe_initial_data_file':f'"{files[0]}"',
        'L_full':str(int(cfg['length'])), 'N_full':str(n),
        'center':'32 32 32','max_level':'6',
        'regrid_interval':'16 16 16 16 16 16',
        'stop_time':'50','max_steps':str(round(50/(.02*64/n))),
        'plot_interval':str(round(2/(.02*64/n))),
        'sigma':'0.4','constraint_norms_interior_radius':str(cfg['constraint_interior_radius'])})
    lines = ['# Strongest accepted ergoregion ring, aligned AMR, t<=50.']
    for line in reference.read_text().splitlines():
        if line.startswith('#'): continue
        key = line.split('=',1)[0].strip()
        lines.append(f'{key} = {replacements[key]}' if key in replacements else line)
    extras = {
        'recipe_initial_data_aligned':'1',
        'recipe_initial_data_level_files':' '.join(f'"{p}"' for p in files),
        'recipe_refinement_radii':' '.join(f'{r:g}' for r in cfg['refinement_radii']),
        'recipe_background_frequency':f'{cfg["frequency"]:.17g}',
        'constraint_norms_levels':'1','constraint_shells_dt':'2',
        'sponge_enabled':'1','sponge_inner_radius':'24','sponge_outer_radius':'32',
        'sponge_strength':'4','sponge_ramp_power':'4','sponge_center':'32 32 32',
        'sponge_drive_strength':'1','sommerfeld_relative_to_background':'1'}
    if any(key in original for key in extras):
        raise ValueError('reference now contains a new knob; review the parameter diff')
    lines.extend(f'{key} = {value}' for key,value in extras.items())
    text = '\n'.join(lines)+'\n'
    template = Path(template)
    template.parent.mkdir(parents=True,exist_ok=True)
    if template.exists() and template.read_text() != text:
        raise ValueError('refusing to overwrite an existing template')
    template.write_text(text)
    updated = parameters(template)
    changes = {key:[original.get(key),updated.get(key)]
               for key in sorted(original.keys()|updated.keys()) if original.get(key)!=updated.get(key)}
    return dict(**plan, template=str(template), parameter_differences=changes,
                original_parameter_sha256=digest(reference))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['plan','export','prepare'])
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--n',type=int,required=True)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--template',type=Path)
    parser.add_argument('--gpu',type=int)
    parser.add_argument('--checkpoints',choices=['off'])
    args = parser.parse_args()
    if args.action == 'plan':
        result = load_plan(args.config,args.n)[1]
    elif args.action == 'prepare':
        if not args.out or not args.template or not args.checkpoints:
            parser.error('prepare needs --out, --template and --checkpoints off')
        result = prepare(args.config,args.out,args.template,args.n,checkpoints=args.checkpoints)
    else:
        if args.gpu is None or args.gpu < 0 or not args.out:
            parser.error('export needs --gpu and --out')
        from ..solver.device import select_device
        select_device(args.gpu)
        result = export(args.config,args.out,args.n)
    print(json.dumps(result,indent=2))


if __name__ == '__main__': main()
