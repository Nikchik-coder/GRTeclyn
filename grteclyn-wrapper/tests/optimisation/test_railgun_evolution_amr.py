"""No-CUDA contracts for independently sampled, aligned AMR initial data."""
import json
from pathlib import Path

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun import evolution_amr as amr
from grteclyn_wrapper.optimisation.railgun.evolution_convergence import parameters


@pytest.mark.parametrize('n', [96, 128, 192])
def test_all_imported_levels_align_to_global_evolution_cells(n):
    cfg, plan = amr.load_plan(amr.DEFAULT_CONFIG, n)
    assert plan['checkpoints'] is False and plan['max_level'] == 6
    for level in plan['levels']:
        dx = level['dx']
        offset = round(level['origin']/dx)
        # Local first/last non-ghost cell are exact global cell centres.
        for cell in (4, level['n']+3):
            exported = level['origin']+(cell+.5)*dx
            assert exported == pytest.approx((offset+cell+.5)*dx, abs=1e-13)
        assert level['n']*dx == pytest.approx(level['length'])
    assert plan['finest_dx'] == pytest.approx(64/(64*n))
    assert cfg['refinement_radii'][-1] > .166


def export_fixture(tmp_path, monkeypatch, n):
    """Sparse payloads exercise headers without creating gigabytes of data.

    Payload hashing itself is already tested by evolution.py's digest tests;
    here grid files hash only their headers, while certificates hash normally.
    """
    original_digest = amr.digest
    def digest(path):
        import hashlib
        path = Path(path)
        if path.suffix != '.gridinit':
            return original_digest(path)
        with path.open('rb') as stream:
            return hashlib.sha256(stream.read(1000)).hexdigest()
    monkeypatch.setattr(amr, 'digest', digest)
    cfg, plan = amr.load_plan(amr.DEFAULT_CONFIG, n)
    out = tmp_path/f'export-{n}'
    out.mkdir()
    certificate = dict(accepted=True, **cfg['core'],
        join_continuity='C6; degree-13 Bernstein step', maxima={'einstein_max':1e-10})
    (out/'corridor.json').write_text(json.dumps(certificate))
    manifest = dict(**plan, frequency=cfg['frequency'], components=amr.COMPONENTS,
                    ghosts=4, certificate_sha256=digest(out/'corridor.json'))
    levels = []
    for level in plan['levels']:
        path = out/f'level_{level["level"]:02d}.gridinit'
        width = level['n']+8
        header = ('GRTECLYN_GRID_INIT_V2\n'
            f'num_components 29\ncomponent_names {" ".join(amr.COMPONENTS)}\n'
            f'nx_ny_nz {width} {width} {width}\n'
            f'dx {level["dx"]:.17e} {level["dx"]:.17e} {level["dx"]:.17e}\n'
            f'origin {level["origin"]:.17e} {level["origin"]:.17e} {level["origin"]:.17e}\nEND_HEADER\n').encode()
        with path.open('wb') as stream:
            stream.write(header)
            stream.truncate(len(header)+level['bytes'])
        levels.append(dict(**level, file=path.name, sha256=digest(path)))
    outcome = dict(accepted=True, source_sha256=plan['source_sha256'], levels=levels,
                   certificate_sha256=manifest['certificate_sha256'])
    for name, value in [('manifest',manifest),('outcome',outcome)]:
        (out/f'{name}.json').write_text(json.dumps(value))
    return out


def test_three_templates_share_physics_boundaries_and_refinement(tmp_path, monkeypatch):
    records = []
    for n in (96, 128, 192):
        out = export_fixture(tmp_path, monkeypatch, n)
        template = tmp_path/f'n{n}.txt'
        amr.prepare(amr.DEFAULT_CONFIG, out, template, n, checkpoints='off')
        record = parameters(template)
        assert record['L_full'] == '64' and record['max_level'] == '6'
        assert record['amr.checkpoint_files_output'] == '0'
        assert record['checkpoint_interval'] == '-1'
        assert record['sigma'] == '0.4'
        assert record['sponge_inner_radius'] == '24' and record['sponge_outer_radius'] == '32'
        assert record['sommerfeld_relative_to_background'] == '1'
        assert float(record['recipe_background_frequency']) == pytest.approx(.7081422911154203)
        assert float(record['dt_multiplier'])*64/n*int(record['plot_interval']) == pytest.approx(2.)
        records.append(record)
    differences = {key for key in records[0] if len({record[key] for record in records}) != 1}
    assert differences == {'N_full','recipe_initial_data_file','recipe_initial_data_level_files',
                           'max_steps','plot_interval'}


def test_short_pilot_changes_only_duration_and_step_count(tmp_path, monkeypatch):
    out = export_fixture(tmp_path, monkeypatch, 96)
    long_template = tmp_path/'long.txt'
    amr.prepare(amr.DEFAULT_CONFIG, out, long_template, 96, checkpoints='off')
    cfg = json.loads(amr.DEFAULT_CONFIG.read_text())
    cfg['stop_time'] = 2.
    short_config = tmp_path/'short.json'
    short_config.write_text(json.dumps(cfg))
    short_template = tmp_path/'short.txt'
    amr.prepare(short_config, out, short_template, 96, checkpoints='off')
    before, after = parameters(long_template), parameters(short_template)
    assert {key for key in before if before[key] != after[key]} == {'stop_time', 'max_steps'}
    assert float(after['stop_time']) == 2.
    assert int(after['max_steps'])*float(after['dt_multiplier'])*64/96 == pytest.approx(2.)
    assert amr.load_plan(short_config, 96)[1]['stop_time'] == 2.


@pytest.mark.parametrize('stop', [0, -2, 1, 51, float('nan')])
def test_refuses_unreviewed_duration(tmp_path, stop):
    cfg = json.loads(amr.DEFAULT_CONFIG.read_text())
    cfg['stop_time'] = stop
    config = tmp_path/'changed.json'
    config.write_text(json.dumps(cfg))
    with pytest.raises(ValueError, match='t=2 or t=50'):
        amr.load_plan(config, 96)


@pytest.mark.parametrize('damage', ['certificate', 'source', 'grid', 'checkpoints'])
def test_rejects_changed_certificate_source_grid_or_checkpoint_policy(tmp_path, monkeypatch, damage):
    out = export_fixture(tmp_path, monkeypatch, 96)
    if damage == 'certificate':
        path = out/'corridor.json'
        value = json.loads(path.read_text()); value['maxima']['einstein_max'] = 2e-8
        path.write_text(json.dumps(value))
    elif damage == 'source':
        path = out/'manifest.json'
        value = json.loads(path.read_text()); value['source_sha256'] = '0'*64
        path.write_text(json.dumps(value))
    elif damage == 'grid':
        with (out/'level_06.gridinit').open('r+b') as stream:
            stream.write(b'CORRUPTED')
    with pytest.raises(ValueError):
        amr.prepare(amr.DEFAULT_CONFIG, out, tmp_path/'params.txt', 96,
                    checkpoints='on' if damage == 'checkpoints' else 'off')
