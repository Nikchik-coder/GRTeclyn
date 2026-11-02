"""Search budgets, failure ranking, automatic walks and central-redshift control."""
from copy import deepcopy
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.ergoregion_cma import (
    BudgetExhausted, Search, SolveBudget, bounded_cma, clean, next_log_lapse,
    predictor, preflight, score)

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT/'research/railgun/studies/ergoregion_cma.json'


def test_failed_trials_cannot_outrank_valid_trials_or_nan():
    passing = score(dict(verdict='PASS', independent=True), dict(shift_norm_over_lapse_max=1.1))
    for residual in (0., 1e-12, 1e9, np.nan, None):
        failed = dict(verdict='REJECT', newton=dict(res_scaled_inf=residual))
        assert np.isfinite(score(failed))
        assert passing < score(failed, dict(shift_norm_over_lapse_max=1e10))
    assert score(dict(verdict='PASS'), dict(shift_norm_over_lapse_max=np.nan)) >= 2
    assert score(dict(verdict='PASS', independent=False), dict(shift_norm_over_lapse_max=100.)) >= 2


def test_separate_budgets_never_allow_an_extra_solve():
    budget = SolveBudget(2, 3)
    budget.take(); budget.take()
    with pytest.raises(BudgetExhausted):
        budget.take()
    assert budget.search_used == 2
    for _ in range(3):
        budget.take(refinement=True)
    with pytest.raises(BudgetExhausted):
        budget.take(refinement=True)
    assert budget.refinement_used == 3


def test_targets_walk_in_both_directions_and_predictor_is_bounded():
    assert next_log_lapse(-1., -2., .04) == pytest.approx(-1.04)
    assert next_log_lapse(-1., -.9, .04) == pytest.approx(-.96)
    assert next_log_lapse(-1., -1.02, .04) == pytest.approx(-1.02)
    current, old = np.array([1., .7]), np.array([.8, .72])
    np.testing.assert_allclose(predictor(current, old, -1.08, -1.04, -1.), 2*current-old)
    np.testing.assert_allclose(predictor(current, old, -2., -1.04, -1.), current+2*(current-old))
    np.testing.assert_array_equal(predictor(current, old, -2., -1., -1.), current)


@pytest.mark.parametrize('limit', [5, 8])
def test_real_cma_keeps_bounds_and_partial_population_budget(limit, monkeypatch, tmp_path):
    monkeypatch.setenv('MPLCONFIGDIR', str(tmp_path))
    config = json.loads(CONFIG.read_text())
    config['max_evaluations'] = limit
    tried = []
    def objective(x):
        tried.append(x)
        return 3. if len(tried) <= 2 else (x-.20)**2
    stopped = bounded_cma(config, objective, lambda:False)
    assert len(tried) == limit
    assert stopped['evaluations_started'] == limit
    assert all(.14 <= value <= .41 for value in tried)


def test_cma_stops_immediately_on_a_validated_target_or_solve_budget(monkeypatch, tmp_path):
    monkeypatch.setenv('MPLCONFIGDIR', str(tmp_path))
    config = json.loads(CONFIG.read_text())
    count = []
    def objective(x):
        count.append(x)
        return .4
    result = bounded_cma(config, objective, lambda:len(count) == 1)
    assert len(count) == 1 and result['reason'] == 'validated_ergoregion'
    def exhausted(x):
        raise BudgetExhausted()
    assert bounded_cma(config, exhausted, lambda:False)['reason'] == 'search_solve_budget'


def test_failed_step_is_bisected_automatically_without_reusing_its_fields():
    search = Search.__new__(Search)
    search.config = dict(max_log_lapse_step=.04, max_splits_per_evaluation=4)
    initial = dict(log=-1., path='initial')
    search.pool = [initial]
    calls = []
    def solve(target, seed, *, independent):
        calls.append((target, seed['path'], independent))
        passed = len(calls) != 1
        row = dict(log=target, path=f'candidate{len(calls)}', row=dict(verdict='PASS' if passed else 'REJECT'))
        if passed:
            search.pool.append(row)
        return row
    search.solve = solve
    target = -1.04
    result = search.evaluate(math.exp(target))
    assert result['row']['verdict'] == 'PASS'
    assert calls[1][0] == pytest.approx(-1.02)
    assert all(seed != 'candidate1' for _, seed, _ in calls)
    assert calls[-1][2]


def test_config_refuses_unapproved_extra_work_or_relaxed_equations():
    config = json.loads(CONFIG.read_text())
    for key, value in [('max_search_solves', 81), ('max_evaluations', 33),
                       ('equation_tol', 1e-7), ('central_lapse_bounds', [.01, .41])]:
        altered = deepcopy(config)
        altered[key] = value
        with pytest.raises(ValueError, match='bounded'):
            preflight('/nonexistent', altered)


def test_clean_preserves_failed_diagnostics_as_json_null():
    value = clean(dict(a=np.float64(np.nan), b=np.array([1., np.inf]), passed=np.bool_(True)))
    assert json.loads(json.dumps(value, allow_nan=False)) == dict(a=None, b=[1., None], passed=True)


def test_provisional_ergoregion_cannot_be_promoted_after_failed_refinement(tmp_path, monkeypatch):
    from grteclyn_wrapper.optimisation.railgun import workflow
    search = Search.__new__(Search)
    search.config = json.loads(CONFIG.read_text())
    search.plan = dict(metadata=dict(fields=[]))
    search.directory, search.source = tmp_path, tmp_path/'source.npz'
    search.budget = SolveBudget(80, 9)
    search.floor = .001
    search.finalists, search.found = [], False
    search.progress = lambda:None
    monkeypatch.setattr(workflow, 'run_study', lambda *a, **k: dict(accepted=False,
                        records=[{}, {}, {}], additional_acceptance=dict(ergoregion_resolved=True)))
    search.refine(dict(log=math.log(.2), path='provisional.npz'))
    assert not search.found
    assert not (tmp_path/'accepted_ergoregion.npz').exists()
    assert search.budget.refinement_used == 3
    assert search.finalists[0]['accepted'] is False


@pytest.mark.parametrize('lapse', [0., 1., -1., np.nan])
def test_invalid_central_targets_are_rejected_before_jax_startup(lapse):
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    with pytest.raises(ValueError, match='central lapse'):
        RingProblem([ScalarField()], central_lapse=lapse)


def test_gpu_central_border_frees_both_frequency_and_amplitude(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    from grteclyn_wrapper.optimisation.railgun.workflow import save_state, load_state
    p = RingProblem([ScalarField()], nx=12, ny=4, central_lapse=.4)
    assert p.jax.devices()[0].platform == 'gpu'
    value = p.seed()
    residual = np.asarray(p.residual(value))
    changed = value.copy()
    changed[-1] += .01
    changed[4*p.n:5*p.n] *= 1.1
    assert float(p.residual(changed)[-1]) == pytest.approx(residual[-1], abs=1e-14)
    arrays, frequencies = p.unpack(value)
    arrays['f'][-1] += .1
    assert float(p.residual(p.pack(arrays, frequencies))[-1])-residual[-1] == pytest.approx(.1)
    path = tmp_path/'central.npz'
    save_state(path, p, value)
    other, restored, meta = load_state(path)
    assert other.central_lapse == .4 and not meta['validated']
    assert 'measured_amplitude_pins' in meta
    np.testing.assert_array_equal(restored, value)
    with pytest.raises(ValueError):
        RingProblem([ScalarField()], central_lapse=.4, frequency_targets=[.7])


def test_gpu_central_control_recovers_the_known_physical_ring():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state
    from grteclyn_wrapper.optimisation.railgun.ergoregion_scan import remap_arrays
    from grteclyn_wrapper.optimisation.railgun.diagnostics import validate
    from grteclyn_wrapper.optimisation.solver.newton import newton
    old, value, _ = load_state(ROOT/'results/railgun/studies/frequency-deep/frequency_01/accepted.npz')
    assert old.jax.devices()[0].platform == 'gpu'
    arrays, frequencies = old.unpack(value)
    central = float(np.exp(arrays['f'][-1].mean()/2))
    p = RingProblem(old.fields, nx=128, ny=16, length=2.5, central_lapse=central)
    mapped = remap_arrays(arrays, old.s, old.y, old.length, p.s, p.y, p.length)
    guess = p.transfer(p, p.pack(mapped, frequencies), perturb=1e-5)
    u, info = newton(p.residual, p.jacobian, guess, tol=1e-14, min_updates=2,
                     max_iter=30, chord_ratio=0.)
    record = validate(p, u, info)
    assert record['verdict'] == 'PASS', record['reasons']
    assert float(u[-1]) == pytest.approx(.70, abs=1e-10)
    assert record['M_ADM_estimate'] == pytest.approx(1.2610721027861238, rel=1e-6)
