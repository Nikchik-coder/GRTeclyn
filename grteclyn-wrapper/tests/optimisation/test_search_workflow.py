"""Exercise the full search with deterministic solves and optimiser proposals."""
import csv
import json
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto


@pytest.mark.parametrize('key', ['e19', 'e_c'])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_monitors_have_finite_rejection_penalty(command, key, value):
    from grteclyn_wrapper.optimisation.search import objective
    assert objective.monitor_overflow(dict(e19=1e-9, e_c=1e-9) | {key: value}) == 10.


@pytest.fixture
def search(command, invoke, monkeypatch, tmp_path):
    cli = command('optimize_potential')
    from grteclyn_wrapper.optimisation.search import driver, evaluation, continuation
    m = driver
    def patch(name, value):
        for module in (driver, evaluation, continuation):
            if hasattr(module, name):
                monkeypatch.setattr(module, name, value)
    trace = SimpleNamespace(solves=[], checks=[], scores=[], proposals=None,
                            refine_pass=True, screen_pass=True, fail_mass=None, monitor=0.,
                            proposal_monitor=0., checked_offset=0.)
    shape = (5, 3)
    radial = ArctanMap(eta0=1.)
    sol = SimpleNamespace(meta={'prescribed': {'J': 1.}}, observables={'D': 1/np.pi},
                          eta0=1., gamma=0., radial_map=radial, nx=4, ny=2, omega_inf=.1,
                          eval_grid=lambda *a: np.zeros(shape))
    monkeypatch.setattr(m.Solution, 'load', lambda path: sol)
    patch('select_device', lambda *a: None)
    patch('tail_ratio', lambda *a, **kw: 0.)
    monkeypatch.setitem(sys.modules, 'jax', SimpleNamespace(clear_caches=lambda: None))
    th = dict(R_e=2., R_A=3., R_pol=2., area_throat=36*np.pi, eta_throat=0., sigma=1., xi_t=0.)
    patch('throat', lambda *a: th)
    class Problem:
        def __init__(self, **kw):
            self.kw = kw
            self.eta0 = 1.
            self.map = radial
            self.sx, self.Dx = lobatto(4)
            self.sy, _ = lobatto(2)
            self.f_bg = self.q = self.psi_prof = np.zeros(shape)
            self.h_i = np.ones((3, 1))
            potential = kw.get('potential')
            self.mass = 0. if potential is None else float(np.sqrt(potential(-1.).coeffs[2]))
        def pack(self, *a, **kw):
            return dict(marker=float(a[0][0, 0]))
        def residual(self, u):
            return u
        def jacobian(self, u):
            return u
        def fields(self, u):
            return (np.full(shape, u['marker']), np.full(shape, .1), np.zeros(shape),
                    np.ones(shape), np.full(shape, -1.))
        def unpack(self, u):
            return (.1, -1.)
        def throat(self, u):
            return th
        def diagnostics(self, u):
            return dict(E19=np.full((3, 3), trace.monitor), E_c=np.full((3, 3), trace.monitor))
    def newton(residual, jac, u, **kw):
        p = residual.__self__
        trace.solves.append((p.mass, p.kw['prescribe'][1], u['marker']))
        if trace.fail_mass is not None and np.isclose(p.mass, trace.fail_mass):
            raise RuntimeError('controlled Newton failure')
        return dict(marker=p.mass), dict(converged=True, res_scaled_inf=0., iters=1)
    patch('MatterCollocationProblem', Problem)
    patch('newton', newton)
    def exotic(*a):
        marker = float(a[5][0, 0])
        return dict(X=3.-marker, X_A=5.-marker, R_e=2., R_A=3., R_pol=2.)
    patch('exotic_x', exotic)
    def check(state, config, grids, pin, d2, directory, **kw):
        method = kw['method']
        trace.checks.append(method)
        row = dict(nx=4, ny=2, X=3.-config['m']+trace.checked_offset, X_A=5.-config['m']+trace.checked_offset, R_e=2., R_A=3.,
                   R_pol=2., E19=0., E_c=0., verdict='PASS')
        return dict(passed=trace.screen_pass if method == 'screen' else trace.refine_pass, method=method,
                    records=[row, row], relative_bill_drift=0.), state
    patch('check_candidate', check)
    def evaluate(objective, x0):
        trace.monitor = trace.proposal_monitor
        for x in trace.proposals or [x0]:
            trace.scores.append(objective(np.asarray(x)))
    def minimize(objective, x0, **kw):
        trace.simplex = kw['options']['initial_simplex']
        evaluate(objective, x0)
        return SimpleNamespace(message='controlled stop')
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize, 'minimize', minimize)
    class CMA:
        def __init__(self, x0, sigma, options):
            self.x0, self.done = x0, False
            trace.cma_options = options
        def stop(self):
            return {'test': True} if self.done else {}
        def ask(self):
            trace.monitor = trace.proposal_monitor
            return trace.proposals or [self.x0]
        def tell(self, xs, scores):
            trace.scores.extend(scores)
            self.done = True
    monkeypatch.setitem(sys.modules, 'cma', SimpleNamespace(CMAEvolutionStrategy=CMA))
    def run(*args):
        return invoke(cli, 'synthetic.json', '--out', tmp_path/'search.tsv', *args)
    trace.run, trace.out, trace.module = run, tmp_path, m
    return trace


@pytest.mark.parametrize('engine', ['nm', 'cma'])
@pytest.mark.parametrize('wide', [False, True])
def test_engines_fields_metadata_and_score(search, engine, wide):
    args = ['--engine', engine]
    if wide:
        args += ['--free-J', '--pin', 'area', '--J-max', '2']
    assert search.run(*args) == 0
    assert search.scores == pytest.approx([4.7 if wide else 2.7])
    assert search.checks == ['screen', 'refine']
    with np.load(search.out/'search_best_clean.npz') as z:
        meta = json.loads(str(z['meta']))
        assert meta['resolution_validated'] is True
        assert meta['stability'] == 'not_assessed'
        np.testing.assert_allclose(z['F'], .3)
    with np.load(search.out/'search_e0001.npz') as z:
        meta = json.loads(str(z['meta']))
        assert meta['resolution_validated'] is False
        assert meta['pin'] == ('area' if wide else 'R_e')
        assert set(['F','W','N','B','PSI','sx','sy','meta']) == set(z.files)
    with (search.out/'search.tsv').open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(rows) == 1 and rows[0]['verdict'] == 'PASS'
    assert ('X_A' in rows[0]) == wide
    if engine == 'nm':
        assert search.simplex.shape == ((6, 5) if wide else (5, 4))
    else:
        assert len(search.cma_options['bounds'][0]) == (5 if wide else 4)


@pytest.mark.parametrize('flags', [[], ['--no-save'], ['--no-save-accepted'], ['--refine-best', 'each']])
def test_refinement_failure_and_save_policy(search, flags):
    search.refine_pass = False
    assert search.run(*flags) == 2
    assert not (search.out/'search_best_clean.npz').exists()
    assert (search.out/'search_best_screened.npz').exists() == ('--no-save' not in flags)
    assert (search.out/'search_e0001.npz').exists() == (not any(f in flags for f in ['--no-save', '--no-save-accepted']))


def test_bounds_failures_and_nearest_seed(search):
    search.proposals = [[.4,0,0,0], [.8,0,0,0], [.79,0,0,0], [5.,0,0,0], [.9,0,0,0]]
    search.fail_mass = .9
    assert search.run() == 0
    assert search.scores[-2:] == [1010., 1010.]
    assert not any(np.isclose(m, 5.) for m,j,s in search.solves)
    assert next(seed for m,j,seed in search.solves if np.isclose(m,.79)) == pytest.approx(.8)


def test_walk_failure_is_bounded(search):
    search.fail_mass = .1
    assert search.run() == 1
    assert len(search.solves) < 25
    assert not search.scores


@pytest.mark.parametrize('extra', [['--stability'], ['--x0', '.3,0,0,0,1'], ['--x0', '5,0,0,0']])
def test_invalid_options_do_not_solve(search, extra):
    with pytest.raises(SystemExit) as exc:
        search.run(*extra)
    assert exc.value.code == 2
    assert not search.solves


def test_existing_output_is_not_overwritten(search):
    path = search.out/'search.tsv'
    path.write_text('existing data')
    with pytest.raises(SystemExit):
        search.run()
    assert path.read_text() == 'existing data'
    assert not search.solves


@pytest.mark.parametrize('monitor,score,verdict', [
    (5e-9, 2.8, 'FRONTIER'),
    (1e-5, 1000+np.log10(1e-5*np.pi**2/1e-6), 'ABOVE-GATE'),
    (float('nan'), 1010., 'FAILED'),
    (float('inf'), 1010., 'FAILED'),
])
def test_constraint_outcomes_and_penalties(search, monitor, score, verdict):
    search.proposal_monitor = monitor
    assert search.run() == 2
    assert search.scores == pytest.approx([score])
    with (search.out/'search.tsv').open() as f:
        row, = csv.DictReader(f, delimiter='\t')
    assert row['verdict'] == verdict
    assert not search.checks
    assert not (search.out/'search_best_clean.npz').exists()


@pytest.mark.parametrize('proposal,options', [
    ([.3,9.,0.,0.], []), ([.3,-1.5,0.,0.], []),
    ([.3,0.,0.,0.,3.], ['--free-J','--J-max','2']),
])
def test_shape_positivity_and_j_bounds_reject_before_solving(search, proposal, options):
    search.proposals = [proposal]
    assert search.run(*options) == 2
    assert search.scores == [1010.]
    with (search.out/'search.tsv').open() as f:
        assert list(csv.DictReader(f, delimiter='\t')) == []


def test_failed_screen_is_not_a_validated_best(search):
    search.screen_pass = False
    assert search.run() == 2
    assert search.scores == [1001.]
    assert search.checks == ['screen']
    assert not (search.out/'search_best_screened.npz').exists()
    assert not (search.out/'search_best_clean.npz').exists()


def test_checked_bill_controls_score(search):
    search.checked_offset = .2
    assert search.run('--refine-best', 'each') == 0
    assert search.scores == pytest.approx([2.9])
    assert search.checks == ['screen','refine']


def test_no_save_still_requires_successful_refinement(search):
    assert search.run('--no-save') == 0
    assert search.checks == ['screen','refine']
    assert not list(search.out.glob('*.npz'))
    assert (search.out/'search.tsv').exists()


def test_existing_best_is_not_overwritten(search):
    best = search.out/'search_best_clean.npz'
    best.write_bytes(b'existing best')
    with pytest.raises(SystemExit):
        search.run()
    assert best.read_bytes() == b'existing best'
    assert not search.solves
