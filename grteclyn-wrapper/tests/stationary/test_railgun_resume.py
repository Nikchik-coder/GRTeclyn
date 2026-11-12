"""A memory interruption may resume only its still-unstarted final solve."""
import copy
import json

import numpy as np
import pytest

from grteclyn_stationary.railgun.workflow import interrupted_prefix


def fixture(tmp_path):
    config = dict(grids=[[8,4],[12,6],[16,8]],discretisation='regular',equation_tol=1e-8)
    (tmp_path/'manifest.json').write_text(json.dumps(dict(config=config)))
    interruption = dict(completed_grids=config['grids'][:2],unfinished_grid=config['grids'][2],
                        unfinished_grid_updates=0)
    (tmp_path/'interruption.json').write_text(json.dumps(interruption))
    for nx,ny in config['grids'][:2]:
        name = tmp_path/f'grid_{nx}x{ny}'
        name.with_suffix('.json').write_text(json.dumps(dict(grid=[nx,ny],verdict='PASS',
            reasons=[],newton=dict(converged=True))))
        np.savez(name.with_suffix('.npz'),metadata=json.dumps(dict(nx=nx,ny=ny,
            solver_discretisation='regular')),u=np.ones(10))
    return config


def test_only_two_passed_grids_are_reused_with_file_hashes(tmp_path):
    cfg = fixture(tmp_path)
    records,hashes,_ = interrupted_prefix(cfg,tmp_path)
    assert [r['grid'] for r in records] == cfg['grids'][:2]
    assert len(hashes) == 4 and all(len(value)==64 for value in hashes.values())


@pytest.mark.parametrize('damage',['config','rejected','updates','third_state','nonfinite','metadata'])
def test_resume_refuses_changed_or_completed_evidence(tmp_path,damage):
    cfg = fixture(tmp_path)
    if damage == 'config':
        cfg = copy.deepcopy(cfg);cfg['equation_tol'] = 1e-7
    elif damage == 'rejected':
        path=tmp_path/'grid_12x6.json';value=json.loads(path.read_text())
        value['verdict']='REJECT';path.write_text(json.dumps(value))
    elif damage == 'updates':
        path=tmp_path/'interruption.json';value=json.loads(path.read_text())
        value['unfinished_grid_updates']=1;path.write_text(json.dumps(value))
    elif damage == 'third_state':
        (tmp_path/'grid_16x8.npz').touch()
    else:
        path=tmp_path/'grid_12x6.npz'
        np.savez(path,metadata=json.dumps(dict(nx=12,ny=6,
            solver_discretisation='wrong' if damage=='metadata' else 'regular')),
            u=np.array([np.nan if damage=='nonfinite' else 1.]))
    with pytest.raises(ValueError):
        interrupted_prefix(cfg,tmp_path)
