"""Physical remapping, prediction, finite budgets and independent sign gates."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from grteclyn_stationary.numerics.spectral import lobatto
from grteclyn_stationary.railgun.ergoregion_scan import (
    common_metric_samples, convergence_checks, preflight, remap_arrays, secant_guess)

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'results/railgun/studies/frequency-deep/frequency_01/accepted.npz'
CONFIG = ROOT/'grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_amplitude.json'


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


def test_common_point_extrema_remove_grid_position_error(tmp_path):
    results, raw_minima = [], []
    for nx, ny in [(16, 6), (24, 8), (32, 10)]:
        s, _ = lobatto(nx)
        y, _ = lobatto(ny)
        f = -1+(s[:, None]-.137)**2+.2*(y[None, :]+.4)**2
        arrays = [f]+[np.zeros_like(f) for _ in range(4)]
        meta = dict(schema=1, model='canonical_regular_centre', nx=nx, ny=ny,
                    length=2.5, fields=[{}], validated=False)
        path = tmp_path/f'{nx}.npz'
        np.savez(path, metadata=json.dumps(meta), u=np.r_[np.array(arrays).ravel(), .7])
        sample = common_metric_samples(path)
        results.append(dict(verdict='PASS', **sample))
        raw_minima.append(float(np.exp(f.min()/2)))
    assert np.ptp(raw_minima) > 1e-5
    checks = convergence_checks(results, [.7]*3)
    assert checks['passed']
    assert max(checks['drifts'].values()) < 1e-13
    assert not checks['ergoregion_resolved']


def test_bootstrap_reuse_preserves_three_spent_solves_and_refuses_promoted_evidence(tmp_path):
    from grteclyn_stationary.railgun.ergoregion_scan import bootstrap_preflight
    config = json.loads(CONFIG.read_text())
    plan = preflight(SOURCE, config)
    previous = tmp_path/'previous'
    target = previous/'amplitude_00'
    target.mkdir(parents=True)
    def write(path, value):
        path.write_text(json.dumps(value))
    write(previous/'manifest.json', dict(config=config))
    write(previous/'outcome.json', dict(solves=3, records=[dict(index=0, accepted=False)]))
    write(target/'manifest.json', dict(config=config))
    original = json.loads((SOURCE.parent/'grid_160x20.json').read_text())
    with np.load(SOURCE) as data:
        meta = json.loads(str(data['metadata']))
        old_arrays = data['u'][:-1].reshape(5, 161, 21)
    old_s, _ = lobatto(160)
    old_y, _ = lobatto(20)
    rows = []
    for nx, ny in config['grids']:
        s, _ = lobatto(nx)
        y, _ = lobatto(ny)
        arrays = remap_arrays(dict(enumerate(old_arrays)), old_s, old_y, 5., s, y, 2.5)
        changed = dict(meta, nx=nx, ny=ny, length=2.5, validated=False,
                       fields=[dict(meta['fields'][0], amplitude=plan['initial_pin'],
                                    anchor_radius=plan['anchor_radius'])])
        changed.pop('frequency_targets')
        np.savez(target/f'grid_{nx}x{ny}.npz', metadata=json.dumps(changed),
                 u=np.r_[np.array(list(arrays.values())).ravel(), .7])
        row = dict(grid=[nx, ny], verdict='PASS', newton=dict(converged=True, newton_steps=[1., 1.]),
                   M_ADM_estimate=original['M_ADM_estimate'], J_volume=original['J_volume'])
        rows.append(row)
        write(target/f'grid_{nx}x{ny}.json', row)
    study = dict(accepted=False, reasons=['additional_acceptance'], records=rows)
    write(target/'outcome.json', study)
    reuse = bootstrap_preflight(previous, SOURCE, config, plan)
    assert reuse['solves_spent'] == 3
    assert reuse['solves_remaining'] == 24
    assert reuse['checks']['passed']
    assert len(reuse['hashes']) == 10
    study['accepted'] = True
    write(target/'outcome.json', study)
    with pytest.raises(ValueError, match='stopped'):
        bootstrap_preflight(previous, SOURCE, config, plan)


@pytest.mark.parametrize('extra_passes', [False, True])
def test_additional_acceptance_runs_before_any_accepted_file(tmp_path, monkeypatch, extra_passes):
    from grteclyn_stationary.railgun import workflow, problem, diagnostics
    from grteclyn_stationary.numerics import newton as newton_module
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


def test_gpu_repin_frees_frequency_and_preserves_the_initial_geometry(cuda_device):
    from grteclyn_stationary.railgun.workflow import load_state
    from grteclyn_stationary.railgun.problem import RingProblem
    from grteclyn_stationary.railgun.model import ScalarField
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
