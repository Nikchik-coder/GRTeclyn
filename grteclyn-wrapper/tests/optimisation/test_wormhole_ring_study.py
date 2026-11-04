"""Variable-spin mixed-field dispatch and independently matched controls."""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from test_fixed_area_study import ellis
from grteclyn_wrapper.optimisation import study, study_parameters, study_report
from grteclyn_wrapper.optimisation.commands.optimize_potential import build_parser


@pytest.mark.parametrize('free_spin', [False, True])
@pytest.mark.parametrize('winding', [None, -1, 0, 1])
def test_parameter_layout_keeps_spin_mass_and_amplitude_distinct(free_spin, winding):
    c = dict(m=.3, q=[1., 2., 3.], J=.05, matter_mass=2., amplitude=.03)
    x = study_parameters.encode(c, free_spin=free_spin, winding=winding, radius=4.)
    expected = [.3, 1., 2., 3.]
    if free_spin:
        expected.append(.05)
    if winding is not None:
        expected.extend([np.log(8.), np.log(.03)])
    np.testing.assert_allclose(x, expected)
    result = study_parameters.decode(x, dict(J=.05), free_spin=free_spin,
                                     winding=winding, radius=4.)
    assert result['J'] == .05
    if winding is not None:
        assert result['matter_mass'] == pytest.approx(2.)
        assert result['amplitude'] == pytest.approx(.03)
        assert result['winding_k'] == winding


@pytest.mark.parametrize('free_spin', [False, True])
@pytest.mark.parametrize('control_pass', [False, True])
@pytest.mark.parametrize('endpoint_changed', [False, True])
def test_ring_workflow_resolves_seed_and_matches_potential_and_spin(
        monkeypatch, tmp_path, free_spin, control_pass, endpoint_changed):
    import scipy.optimize
    base = ellis(8, 4)
    basecfg = dict(m=0., q=[0., 0., 0.], gamma=0., J=.05)
    seed = ellis(8, 4, sigma=2.)
    seed['Z'] = .03 * (1-seed['sx'][:, None]**2) * np.ones((1, 5))
    seed['frequency'] = .7
    if endpoint_changed:
        seed['psim'] *= 1.01
    seedcfg = dict(basecfg, m=.3, matter='winding', winding_k=1,
                   matter_mass=1., amplitude=.03, J=0.)
    source = tmp_path/'seed.npz'
    study.save_trial(source, seed, seedcfg, {}, ('R_e', 2.))
    config = tmp_path/'study.toml'
    config.write_text('tidal_factors=[4.0]\nwindings=[-1]\nenergy_budgets=[1.0]\n'
                      'rescale_matter_seeds=true\nmatter_candidate_seeds=['
                      +json.dumps(str(source))+']\n')
    def row(c):
        # This controlled example improves over V=0 but loses to the same
        # potential without the ring. The report must distinguish them.
        control_x = 3. if endpoint_changed else 1.
        x = (3. if c['amplitude'] == .03 else 2.) if c.get('matter') else (control_x if c['m'] else 4.)
        return dict(verdict='PASS', nx=8, ny=4, X=x, X_A=x, X_full=x,
                    R_A=1., tidal_peak=1.)
    def state(c):
        return seed if c.get('matter') else base
    checks = []
    def check(s, c, grids, pin, *a, **kw):
        checks.append(c.copy())
        assert pin == ('minimal_area', pytest.approx(4*np.pi))
        assert kw['perturb_seed']
        passed = control_pass or c.get('matter') or c['m'] == 0.
        return dict(passed=bool(passed), method='refine', records=[row(c)],
                    relative_bill_drift=0.), state(c)
    solves = []
    def solve(s, c, *a, **kw):
        if not solves:
            assert c['winding_k'] == -1 and c['J'] == .05
            assert c['m'] == pytest.approx(.6)
            assert c['matter_mass'] == pytest.approx(2.)
            assert s['sigma'] == pytest.approx(1.)
            assert s['frequency'] == pytest.approx(1.4)
        solves.append(c.copy())
        return state(c), row(c)
    monkeypatch.setattr(study, 'massless_state', lambda *a: (base, basecfg))
    monkeypatch.setattr(study, 'source_manifest', lambda *a: {})
    monkeypatch.setattr(study, 'find_surface', lambda *a: np.zeros(5))
    monkeypatch.setattr(study, 'check_candidate', check)
    monkeypatch.setattr(study, 'solve_trial', solve)
    monkeypatch.setattr(study, 'validate', lambda s, c, r, **kw: r)
    monkeypatch.setattr(study, 'release_solver', lambda: None)
    monkeypatch.setattr(study_report, 'plot_comparison', lambda *a: None)
    def minimize(objective, x0, **kw):
        assert len(x0) == 6 + free_spin
        lo, hi = np.asarray(kw['bounds']).T
        offset = 4 + free_spin
        assert lo[offset] == pytest.approx(np.log(.5))
        assert hi[offset+1] == pytest.approx(np.log(.5))
        values = [.4, .1, .2, .3]
        if free_spin:
            assert hi[4] == .4
            values.append(.2)
        values.extend([np.log(3.), np.log(.04)])
        objective(np.asarray(values))
    monkeypatch.setattr(scipy.optimize, 'minimize', minimize)
    extra = ['--free-J', '--J-min', '0', '--J-max', '.4', '--J-step', '.025'] if free_spin else []
    args = build_parser().parse_args(['unused.json', '--study-config', str(config),
        '--study-case', 'boson-k-1-t4-e1', '--nx', '8', '--ny', '4',
        '--out', str(tmp_path/'out'), '--maxfev', '1', *extra])
    assert study.run(args, error=lambda msg: pytest.fail(msg)) == 0
    data = json.loads((tmp_path/'out/boson-k-1-t4-e1/outcome.json').read_text())
    # The ring-free control must match the selected candidate's potential.
    winner = next(c for c in checks[1:] if c.get('matter'))
    control = checks[-1]
    assert not control.get('matter')
    for key in ('J', 'm', 'q', 'gamma'):
        assert control[key] == winner[key]
    assert solves[1]['matter_mass'] == pytest.approx(3.)
    assert solves[1]['amplitude'] == pytest.approx(.04)
    assert solves[1]['J'] == (.2 if free_spin else .05)
    assert data['winner_J'] == (.2 if free_spin else .05)
    assert data['validated_fractional_improvement'] == .5
    gain = 1/3 if endpoint_changed else -1.
    assert data['ring_control_fractional_change'] == (pytest.approx(gain) if control_pass else None)
    assert data['validated_ring_control_improvement'] == (
        pytest.approx(1/3) if control_pass and endpoint_changed else None)
    assert data['ring_control_same_potential'] == (control_pass and not endpoint_changed)
    assert data['validated_ring_only_improvement'] is None
    assert data['stability'] == 'not_assessed'


def test_ordinary_energy_never_cancels_phantom_objective():
    from grteclyn_wrapper.optimisation.study_diagnostics import volume_budgets
    s = ellis(24, 10)
    before = volume_budgets(s, {})
    s['Z'] = .1*(1-s['sx'][:, None]**2)**3*np.ones((1, 11))
    s['frequency'] = .7
    after = volume_budgets(s, dict(matter='winding', matter_mass=1., winding_k=-1))
    assert after['E_b'] > 0 and after['J_b'] > 0
    assert after['X_full'] == before['X_full']


def test_prepared_cases_preview_without_gpu_or_output(tmp_path):
    root = Path(__file__).resolve().parents[3]
    config = study.load_config(root/'research/optimisation/studies/wormhole_ring.toml')
    assert set(study.cases(config)) == {'potential-t4', 'boson-k-1-t4-e1'}
    for source in config['matter_candidate_seeds']:
        assert (root/source).is_file()
    for case in ('potential', 'ring-fixed', 'ring-spin'):
        run = subprocess.run(['bash', 'research/optimisation/studies/run_wormhole_ring.sh',
                              case, '999999', str(tmp_path/'out')], cwd=root,
                             capture_output=True, text=True, check=True)
        assert '--mem 160 --timeout 14400' in run.stdout
        assert ('--free-J' in run.stdout) == (case == 'ring-spin')
    assert not (tmp_path/'out').exists()
