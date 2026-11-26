"""The lower-dragging candidate keeps the approved evolution configuration."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from grteclyn_stationary.railgun.certify_ergoregion_core import plan
from grteclyn_stationary.railgun.evolution_amr import DEFAULT_CONFIG

CONFIG = Path('grteclyn-wrapper/scripts/campaigns/railgun/configs/evolution_ergoregion_372.json')


def test_selected_candidate_has_three_passing_grids_and_a_resolved_ergoregion():
    cfg, contract = plan(CONFIG)
    source = Path(cfg['source'])
    outcome = json.loads((source.parent/'outcome.json').read_text())
    assert outcome['accepted']
    assert [row['grid'] for row in outcome['records']] == [[160,20],[192,24],[224,28]]
    assert all(row['verdict'] == 'PASS' and row['gtt_max'] > 0 for row in outcome['records'])
    assert contract['source_sha256'] == 'dea15224bb7e97be5a1d8528a828886b6ba3e4cbf3c8cae66d88abc8cf4207cd'
    assert cfg['frequency'] == pytest.approx(.6741001877002323,abs=1e-15)


def test_substitution_preserves_box_resolution_boundary_and_checkpoint_choices():
    old = json.loads(DEFAULT_CONFIG.read_text())
    new, _ = plan(CONFIG)
    changes = {key for key in old if old[key] != new[key]}
    assert changes == {'source','source_sha256','frequency','selection','core','approval'}
    assert new['length'] == 64 and new['max_level'] == 6
    assert new['base_N'] == [96,128,192] and new['checkpoints'] is False
    assert new['core']['tolerance'] == old['core']['tolerance'] == 1e-8


@pytest.mark.parametrize('damage',['frequency','tolerance','comparison_degree'])
def test_certificate_plan_refuses_stale_phase_or_changed_limits(tmp_path,damage):
    cfg = json.loads(CONFIG.read_text())
    if damage == 'frequency': cfg['frequency'] += .01
    elif damage == 'tolerance': cfg['core']['tolerance'] = 1e-7
    else: cfg['core']['comparison_degree'] += 1
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError):
        plan(path)


def test_dry_run_never_initializes_a_jax_backend():
    env = dict(os.environ,JAX_PLATFORMS='invalid_backend')
    result = subprocess.run([sys.executable,'-m',
        'grteclyn_stationary.railgun.certify_ergoregion_core',
        '--config',str(CONFIG),'--dry-run'],env=env,text=True,capture_output=True)
    assert result.returncode == 0,result.stderr
    assert json.loads(result.stdout)['numerical_execution'] is False


@pytest.mark.parametrize('query_failure',[False,True])
def test_launch_refuses_busy_or_unreadable_card_before_preparing_data(tmp_path,query_failure):
    fake = tmp_path/'nvidia-smi'
    fake.write_text('#!/bin/sh\n'+('exit 1\n' if query_failure else
        'case "$*" in\n*query-gpu=uuid*) echo GPU-test;;\n*) echo "GPU-test, 123";;\nesac\n'))
    fake.chmod(0o755)
    result = subprocess.run(['bash',
        'grteclyn-wrapper/scripts/campaigns/railgun/launch_ergoregion.sh',
        '--data-dir',str(tmp_path/'missing'), '--name','must-not-start',
        '--n','96','--gpu','0','--binary','missing','--checkpoints','off'],
        env=dict(os.environ,PATH=str(tmp_path)+os.pathsep+os.environ['PATH']),
        text=True,capture_output=True)
    assert result.returncode != 0
    assert 'Traceback' not in result.stderr
    if not query_failure:
        assert 'occupied; nothing started' in result.stderr
