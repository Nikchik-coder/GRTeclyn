"""Physical remapping, prediction, finite budgets and independent sign gates."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
from grteclyn_wrapper.optimisation.railgun.ergoregion_scan import (
    convergence_checks, preflight, remap_arrays, secant_guess)

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'results/railgun/studies/frequency-deep/frequency_01/accepted.npz'
CONFIG = ROOT/'research/railgun/studies/ergoregion_amplitude.json'


def test_radial_remap_preserves_physical_values_and_endpoints():
    old_s, _ = lobatto(20)
    old_y, _ = lobatto(6)
    new_s, _ = lobatto(24)
    new_y, _ = lobatto(8)
    field = lambda s, y: (1+s[:, None])*(1-s[:, None])**2*(2+y[None, :]**2)
    arrays = {'q0': field(old_s, old_y)}
    actual = remap_arrays(arrays, old_s, old_y, 5., new_s, new_y, 2.5)['q0']
    mapped_s = (2.5*(1+new_s)-5*(1-new_s))/(2.5*(1+new_s)+5*(1-new_s))
    np.testing.assert_allclose(actual, field(mapped_s, new_y), atol=2e-14)
    assert np.max(abs(actual-field(new_s, new_y))) > .1
    np.testing.assert_allclose(actual[[0, -1]], 0., atol=2e-14)
    identity = remap_arrays(arrays, old_s, old_y, 5., old_s, old_y, 5.)
    np.testing.assert_allclose(identity['q0'], arrays['q0'], atol=2e-14)


def test_secant_predicts_every_variable_with_unequal_pin_steps():
    slope = np.array([2., -3., .1, .25])  # includes the solved frequency
    previous = np.array([1., 4., .2, .7])
    current = previous+.03*slope
    guess = secant_guess(current, previous, .19, .13, .1)
    np.testing.assert_allclose(guess, previous+.09*slope)
    with pytest.raises(ValueError):
        secant_guess(current, previous, .19, .1, .1)
    with pytest.raises(ValueError):
        secant_guess(current, previous[:-1], .19, .13, .1)


def test_plan_measures_scalar_peak_instead_of_reusing_the_tail_pin():
    config = json.loads(CONFIG.read_text())
    plan = preflight(SOURCE, config)
    assert 1. < plan['anchor_radius'] < 1.4
    assert .30 < plan['initial_pin'] < .32
    assert plan['amplitudes'][-1]/plan['initial_pin'] == pytest.approx(1.06**8)
    assert plan['max_solves'] == 27
    assert not plan['numerical_execution']
    for key, value in [('max_solves', 30), ('equation_tol', 1e-7), ('length', 3.),
                       ('amplitude_factors', [1.06**i for i in range(10)])]:
        changed = deepcopy(config)
        changed[key] = value
        with pytest.raises(ValueError):
            preflight(SOURCE, changed)


def test_plan_refuses_a_different_source(tmp_path):
    path = tmp_path/'state.npz'
    path.write_bytes(SOURCE.read_bytes()+b'changed')
    with pytest.raises(ValueError, match='hash'):
        preflight(path, json.loads(CONFIG.read_text()))


def test_ergoregion_needs_three_passing_grids_and_a_resolved_positive_sign():
    rows = [dict(verdict='PASS', lapse_min=.2, gtt_max=.01,
                 shift_norm_over_lapse_max=1.1) for _ in range(3)]
    assert convergence_checks(rows, [.7]*3)['ergoregion_resolved']
    rows[0]['gtt_max'] = -.001
    assert not convergence_checks(rows, [.7]*3)['ergoregion_resolved']
    rows[0]['gtt_max'] = .01
    rows[1]['verdict'] = 'REJECT'
    assert not convergence_checks(rows, [.7]*3)['passed']
    rows[1]['verdict'] = 'PASS'
    for row in rows:
        row['gtt_max'] = 1e-10
    assert not convergence_checks(rows, [.7]*3)['ergoregion_resolved']
    assert not convergence_checks(rows, [.7, .7, 1.01])['passed']
    assert not convergence_checks(rows, [.7, .7, .7001])['passed']
    assert not convergence_checks(rows, [.7, .7, np.nan])['passed']
    assert not convergence_checks(rows[:2], [.7]*2)['passed']


@pytest.mark.parametrize('extra_passes', [False, True])
def test_additional_acceptance_runs_before_any_accepted_file(tmp_path, monkeypatch, extra_passes):
    from grteclyn_wrapper.optimisation.railgun import workflow, problem, diagnostics
    from grteclyn_wrapper.optimisation.solver import newton as newton_module
    class FakeProblem:
        def __init__(self, *args, **kwargs):
            self.jax = SimpleNamespace(devices=lambda: [SimpleNamespace(platform='cpu', device_kind='test')],
                                       __version__='test', config=SimpleNamespace(jax_enable_x64=True))
            self.residual = self.jacobian = None
        def seed(self):
            return np.array([1.])
        def transfer(self, *args, **kwargs):
            return self.seed()
    saved = []
    monkeypatch.setattr(problem, 'RingProblem', FakeProblem)
    monkeypatch.setattr(newton_module, 'newton', lambda *a, **k: (np.array([1.]), {'converged': True}))
    monkeypatch.setattr(diagnostics, 'validate', lambda *a, **k: dict(verdict='PASS', reasons=[]))
    monkeypatch.setattr(diagnostics, 'converged_records', lambda *a, **k: (True, 0.))
    monkeypatch.setattr(workflow, 'save_state', lambda path, *a, **k: saved.append((path.name, k)))
    result = workflow.run_study(dict(fields=[], require_gpu=False), tmp_path/'study',
                                acceptance_check=lambda rows: dict(passed=extra_passes))
    assert result['accepted'] == extra_passes
    assert ('accepted.npz' in [name for name, _ in saved]) == extra_passes


def test_gpu_repin_frees_frequency_and_preserves_the_initial_geometry():
    from grteclyn_wrapper.optimisation.railgun.workflow import load_state
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    config = json.loads(CONFIG.read_text())
    plan = preflight(SOURCE, config)
    old, u, _ = load_state(SOURCE)
    assert old.jax.devices()[0].platform == 'gpu'
    field = ScalarField(**dict(plan['metadata']['fields'][0], amplitude=plan['initial_pin'],
                               anchor_radius=plan['anchor_radius']))
    p = RingProblem([field], nx=128, ny=16, length=2.5)
    arrays, frequencies = old.unpack(u)
    mapped = remap_arrays(arrays, old.s, old.y, old.length, p.s, p.y, p.length)
    value = p.pack(mapped, frequencies)
    residual = np.asarray(p.residual(value))
    assert abs(residual[-1]) < 1e-8
    changed = value.copy()
    changed[-1] += .01
    assert float(p.residual(changed)[-1]) == pytest.approx(residual[-1], abs=1e-14)
    assert np.max(abs(np.asarray(p.residual(changed))[:-1]-residual[:-1])) > 1e-5
    assert p.frequency_targets == (None,)
