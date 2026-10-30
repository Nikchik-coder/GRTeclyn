"""A screen cannot masquerade as refinement; failed checks cannot export."""
import json
import sys
from types import SimpleNamespace
import numpy as np
import pytest
from grteclyn_wrapper.optimisation import resolution as r
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap


def fixture_state():
    return dict(**{k:np.ones((3,3)) for k in r.FIELDS}, sx=np.arange(3), sy=np.arange(3),
                map=ArctanMap(eta0=1.), sigma=2., xi_t=0., omega=.1, psim=-1.)


def test_resolution_requires_finite_consistent_successive_checks():
    rows = [dict(verdict='PASS', X=2.), dict(verdict='PASS', X=2.+1e-7)]
    assert r.consistent(rows)[0]
    for change in ({'verdict':'ABOVE_GATE'}, {'X':float('nan')}, {'X':2.01}):
        assert not r.consistent([rows[0], dict(rows[1], **change)])[0]
    assert not r.consistent(rows[:1])[0]
    assert r.refinement_grids(150,30) == [(150,30),(180,36),(210,42)]


def test_refinement_failure_preserves_existing_best(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "jax", SimpleNamespace(clear_caches=lambda: None))
    state = fixture_state()
    calls = []
    def solve(state, config, nx, ny, pin, d2, **kw):
        calls.append((nx,ny))
        assert kw['newton_tol'] == 1e-9
        if nx == 180:
            raise RuntimeError('Newton stalled')
        return state, dict(verdict='PASS', X=2., nx=nx, ny=ny)
    monkeypatch.setattr(r,'solve_trial',solve)
    monkeypatch.setattr(r,'save_trial',lambda *a: None)
    result, checked = r.check_candidate(state, {}, r.refinement_grids(150,30),
                                       ('R_e',2.), 1., tmp_path/'checks')
    assert not result['passed']
    assert calls == [(150,30),(180,36)]
    assert json.loads((tmp_path/'checks/result.json').read_text())['records'][-1]['verdict']=='FAILED'
    best = tmp_path/'best_clean.npz'
    best.write_bytes(b'existing best')
    with pytest.raises(ValueError, match='failed'):
        r.save_checked(best, checked, {}, {}, result)
    assert best.read_bytes() == b'existing best'


@pytest.mark.parametrize('method', ['screen','refine'])
def test_saved_fields_and_labels_describe_the_actual_check(tmp_path, method):
    state = fixture_state()
    cfg = dict(m=.3, q=[0,0,0], gamma=0., J=1.)
    row = dict(nx=2,ny=2,X=1.8,X_A=1.9,sigma=2.,verdict='PASS')
    result = dict(passed=True, method=method, records=[row,row], relative_bill_drift=0.)
    path = tmp_path/'best.npz'
    r.save_checked(path, state, cfg, dict(lam_eta0=0.,j0={},X=99.), result)
    with np.load(path) as z:
        meta=json.loads(str(z['meta']))
        assert meta['X']==1.8
        assert meta['resolution_validated'] == (method=='refine')
        assert meta['stability']=='not_assessed'
        assert 'lam_eta0' not in meta and 'j0' not in meta
        assert meta['nx']==z['F'].shape[0]-1
        np.testing.assert_array_equal(z['F'],state['F'])


def test_screen_does_not_call_newton_and_uses_original_polynomial(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "jax", SimpleNamespace(clear_caches=lambda: None))
    original = fixture_state()
    calls=[]
    def screen(state, config, nx, ny, pin, d2):
        assert state is original
        calls.append(nx)
        return dict(state),dict(verdict='PASS',X=2.,nx=nx,ny=ny)
    monkeypatch.setattr(r,'screen_trial',screen)
    monkeypatch.setattr(r,'solve_trial',lambda *a, **kw: pytest.fail('screen ran Newton'))
    monkeypatch.setattr(r,'save_trial',lambda *a: None)
    result,_=r.check_candidate(original,{},r.refinement_grids(150,30),('R_e',2.),1.,
                               tmp_path/'screen',method='screen')
    assert result['passed'] and result['method']=='screen'
    assert calls==[150,180,210]
