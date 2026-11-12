"""Recovery must retain the selected ring and its existing origin limits."""
import json
from pathlib import Path

import pytest

from grteclyn_stationary.railgun.smooth_origin_recovery import plan


CONFIG = Path('grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_origin_recovery_372.json')


def test_recovery_preserves_the_372_source_and_evolution_origin_check():
    proposed = plan(CONFIG)
    cfg = proposed['config']
    target = json.loads(Path(cfg['evolution_config']).read_text())
    assert cfg['source_sha256'] == target['source_sha256']
    assert cfg['core'] == dict(radius=.08,degree=12,tolerance=1e-8)
    assert cfg['grids'] == [[224,28],[256,32],[288,36]]
    assert proposed['max_solves'] == 3 and proposed['checkpoints'] is False
    assert proposed['numerical_execution'] is False
    assert proposed['canonical_equations_checked']
    assert proposed['all_interior_rows_retained']
    assert proposed['physical_origin_checked']


@pytest.mark.parametrize('damage',['source','radius','equation_tol'])
def test_recovery_refuses_source_substitution_or_changed_limits(tmp_path,damage):
    cfg = json.loads(CONFIG.read_text())
    if damage == 'source':
        cfg['evolution_config'] = 'grteclyn-wrapper/scripts/campaigns/railgun/configs/evolution_ergoregion_best.json'
    elif damage == 'radius':
        cfg['core']['radius'] = .04
    else:
        cfg['equation_tol'] = 1e-7
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError):
        plan(path)
