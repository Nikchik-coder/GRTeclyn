"""Dry seed budgets preserve discrete winding, parity and source provenance."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from grteclyn_wrapper.optimisation.railgun.branch_seeds import preflight

ROOT=Path(__file__).resolve().parents[3]


def test_six_bound_modes_are_homotopy_starts_not_final_backgrounds():
    cfg=json.loads((ROOT/'research/railgun/studies/branch_seeds.json').read_text())
    source=ROOT/'results/railgun/studies/ring-validated/accepted.npz'
    plan=preflight(source,cfg)
    assert plan['max_eigenproblems']==6 and not plan['numerical_execution']
    assert [b['field']['parity'] for b in cfg['branches']]==['even','even','odd']
    for key,value in [('max_eigenproblems',8),('outer_candidates',[-12,-16])]:
        altered=dict(cfg,**{key:value})
        with pytest.raises(ValueError):preflight(source,altered)
    altered=deepcopy(cfg);altered['branches'][0]['field']['winding']=1.5
    with pytest.raises(ValueError):preflight(source,altered)
    altered=deepcopy(cfg);altered['source_sha256']='0'*64
    with pytest.raises(ValueError):preflight(source,altered)
