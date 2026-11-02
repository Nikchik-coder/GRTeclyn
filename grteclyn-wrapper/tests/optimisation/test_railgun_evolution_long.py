"""Time-extension identity checks, without starting a device or reading a cube."""
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from grteclyn_wrapper.optimisation.railgun import evolution_long as long_run
from grteclyn_wrapper.optimisation.railgun.evolution_convergence import parameters, PATH_KEYS


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[3]
    reference = tmp_path/'reference'
    shutil.copytree(repo/'results/railgun/studies/evolution-070-n192', reference)
    data = tmp_path/'export'; data.mkdir()
    for name in ('manifest.json', 'corridor.json', 'outcome.json'):
        shutil.copyfile(reference/'export'/name, data/name)
    binary = tmp_path/'test.ex'; binary.write_bytes(b'fixture binary')
    grid = data/'initial.gridinit'; grid.write_bytes(b'fixture grid')
    manifest = json.loads((reference/'run_manifest.json').read_text())
    manifest['binary']['sha256'] = long_run.digest(binary)
    (reference/'run_manifest.json').write_text(json.dumps(manifest))
    outcome = json.loads((reference/'export/outcome.json').read_text())
    outcome['gridinit_sha256'] = long_run.digest(grid)
    (reference/'export/outcome.json').write_text(json.dumps(outcome))
    (reference/'sha256sums.txt').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(reference)}\n'
        for p in sorted(reference.rglob('*')) if p.is_file() and p.name != 'sha256sums.txt'))
    def pilot(data, template, *, checkpoints):
        # The actual pilot validator has its own export/layout/certificate suite.
        # Here the tiny fixture isolates the long-run parameter-difference gate.
        template.write_text((reference/'params.txt').read_text())
    monkeypatch.setattr(long_run, 'prepare_pilot', pilot)
    return data, reference, tmp_path/'long.txt', binary


def test_duration_extension_preserves_all_physics_and_output_cadence(prepared):
    result = long_run.prepare(*prepared, checkpoints='off')
    changed = result['parameter_differences']
    assert changed.keys() <= PATH_KEYS | {'stop_time', 'max_steps'}
    assert changed['stop_time'] == ['2', '50']
    assert changed['max_steps'] == ['600', '15000']
    assert result['plot_interval'] == 25
    assert result['checkpoint_keep'] == 0
    assert long_run.prepare(*prepared, checkpoints='off') == result


def test_checkpoint_policy_is_explicit_and_retention_is_bounded(prepared):
    with pytest.raises(ValueError, match='explicit'):
        long_run.prepare(*prepared, checkpoints=None)
    result = long_run.prepare(*prepared, checkpoints='on')
    new = parameters(prepared[2])
    assert new['amr.checkpoint_files_output'] == '1'
    assert new['checkpoint_interval'] == '1500'
    assert new['checkpoint_keep'] == '3'
    assert result['checkpoint_interval']*(.02*32/192) == 5


def test_altered_initial_cube_or_binary_is_refused(prepared):
    data, _, template, binary = prepared
    (data/'initial.gridinit').write_bytes(b'changed')
    with pytest.raises(ValueError, match='initial cube'):
        long_run.prepare(*prepared, checkpoints='off')
    binary.write_bytes(b'changed')
    with pytest.raises(ValueError, match='frozen'):
        long_run.prepare(*prepared, checkpoints='off')
    assert not template.exists()


def test_existing_run_template_is_not_overwritten(prepared):
    long_run.prepare(*prepared, checkpoints='off')
    prepared[2].write_text('changed after review\n')
    with pytest.raises(ValueError, match='overwrite'):
        long_run.prepare(*prepared, checkpoints='off')


def test_changed_pilot_gauge_cannot_silently_change_the_long_run(prepared, monkeypatch):
    reference = prepared[1]
    def changed_pilot(data, template, *, checkpoints):
        template.write_text((reference/'params.txt').read_text().replace('eta = 1', 'eta = 2'))
    monkeypatch.setattr(long_run, 'prepare_pilot', changed_pilot)
    with pytest.raises(ValueError, match='physics'):
        long_run.prepare(*prepared, checkpoints='off')
