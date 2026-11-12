"""The finer reference changes resolution without changing the physical ring."""
import json

import pytest

from grteclyn_stationary.railgun.evolution_source_refinement import DEFAULT_CONFIG, plan


def test_refinement_retains_source_and_has_only_three_bounded_solves():
    proposed = plan()
    assert proposed['max_solves'] == 3
    assert proposed['config']['grids'] == [[224,28],[256,32],[288,36]]
    assert proposed['checkpoints'] is False
    assert proposed['numerical_execution'] is False
    assert max(proposed['jacobian_GiB']) < 24


@pytest.mark.parametrize('key,value', [('central_lapse',.08),('equation_tol',1e-7),
                                     ('require_nodeless',False),('max_solves',4)])
def test_changed_physics_tolerance_or_budget_is_rejected(tmp_path,key,value):
    cfg = json.loads(DEFAULT_CONFIG.read_text())
    cfg[key] = value
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError):
        plan(path)
