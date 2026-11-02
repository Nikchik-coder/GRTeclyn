"""Manufactured orders, diagnostic alignment and study-identity regressions."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.evolution_convergence import (
    analyse, at_times, constraint_orders, difference_factor, load_triplet,
    markdown_order_table, richardson,
)


@pytest.mark.parametrize('order', [2., 3.4, 4., 6.])
def test_generalized_richardson_recovers_order_and_continuum_with_unequal_ratios(order):
    h = 32/np.array([96., 128., 192.])
    for coefficient in (-.8, .8):
        values = 1.234+coefficient*h**order
        result = richardson(values, h, difference_floor=0)
        assert result['status'] == 'fitted'
        assert result['order'] == pytest.approx(order, abs=1e-8)
        assert result['continuum'] == pytest.approx(1.234, abs=1e-12)
        assert result['estimated_fine_error'] == pytest.approx(abs(coefficient*h[-1]**order))
    np.testing.assert_allclose(constraint_orders(h**order, h), [order, order])
    assert difference_factor(4, h) == pytest.approx(2.692307692307692)


def test_unresolved_oscillatory_and_divergent_triplets_are_not_given_an_order():
    h = [1/3, 1/4, 1/6]
    assert richardson([1., 1.+1e-11, 1.+2e-11], h)['status'] == 'unresolved_differences'
    assert richardson([1., 2., 1.5], h)['status'] == 'nonmonotone'
    assert richardson(np.array(h)**-2, h)['status'] == 'outside_positive_order_bracket'
    with pytest.raises(ValueError, match='decreasing'):
        richardson([1, 2, 3], h[::-1])
    with pytest.raises(ValueError, match='finite'):
        richardson([1, np.nan, 3], h)


def test_matched_times_require_real_samples_and_never_interpolate():
    data = {'time':np.array([0., .5, 1.]), 'value':np.array([2., 3., 5.])}
    assert at_times(data, 'value', [0., 1.]) == [2., 5.]
    with pytest.raises(ValueError, match='sample'):
        at_times(data, 'value', [.25])


def checksum(folder):
    (folder/'sha256sums.txt').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(folder)}\n'
        for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'sha256sums.txt'))


@pytest.fixture
def triplet(tmp_path):
    # Start from the actual archived physics contract, then replace diagnostics
    # by a labelled manufactured h^4 signal in temporary directories only.
    repo = Path(__file__).resolve().parents[3]
    reference = repo/'results/railgun/studies/evolution-070-n128'
    folders = []
    times = np.array([0., .5, 1., 1.5, 2.])
    for n in (96, 128, 192):
        out = tmp_path/str(n); (out/'data').mkdir(parents=True); (out/'export').mkdir()
        for name in ('export/manifest.json', 'export/corridor.json', 'run_manifest.json', 'summary.json'):
            data = json.loads((reference/name).read_text())
            if name == 'export/manifest.json': data['n'] = n
            (out/name).write_text(json.dumps(data))
        text = (reference/'params.txt').read_text().replace('N_full = 128', f'N_full = {n}')
        text = text.replace('max_steps = 400', f'max_steps = {round(2/(.02*32/n))}')
        (out/'params.txt').write_text(text)
        h = 32/n
        np.savetxt(out/'data/constraint_norms.dat', np.array([times, (1+times)*h**4,
                                                          (2+times)*h**3]).T,
                   header='time L2_Ham_int L2_Mom_int')
        np.savetxt(out/'data/complex_scalar_diagnostics.dat',
                   np.array([times, 1+times*h**4, -1+(1+times)*h**4,
                             2+(1+times)*h**4]).T,
                   header='time Q_box Jz_matter_box integral_abs_Phi_sq')
        checksum(out); folders.append(out)
    return folders


def test_end_to_end_order_report_and_honest_t0_floor(triplet):
    report = analyse(triplet)
    assert report['region'].startswith('L0')
    np.testing.assert_allclose(report['constraints']['Ham L0'][2]['pair_orders'], [4, 4])
    np.testing.assert_allclose(report['constraints']['Mom L0'][2]['pair_orders'], [3, 3])
    assert report['observables']['Q_box'][0]['status'] == 'unresolved_differences'
    assert report['observables']['Q_box'][3]['order'] == pytest.approx(4)
    assert report['observables']['Q_box'][3]['continuum'] == pytest.approx(1)
    assert '4.00 / 4.00' in markdown_order_table(report)
    with pytest.raises(ValueError, match='three'):
        analyse(triplet[:2])
    with pytest.raises(ValueError, match='trust'):
        analyse(triplet, times=[3.])


def test_corruption_or_changed_gauge_or_binary_blocks_comparison(triplet):
    folder = triplet[-1]; path = folder/'params.txt'; original = path.read_text()
    path.write_text(original.replace('eta = 1', 'eta = 2'))
    with pytest.raises(ValueError, match='checksum'):
        load_triplet(triplet)
    checksum(folder)
    with pytest.raises(ValueError, match='triplet changes'):
        load_triplet(triplet)
    path.write_text(original)
    manifest = json.loads((folder/'run_manifest.json').read_text())
    manifest['binary']['sha256'] = 'different'
    (folder/'run_manifest.json').write_text(json.dumps(manifest)); checksum(folder)
    with pytest.raises(ValueError, match='triplet changes'):
        load_triplet(triplet)


def test_third_grid_preparation_changes_only_resolution_knobs(tmp_path, monkeypatch):
    from grteclyn_wrapper.optimisation.railgun import evolution_pilot as pilot
    from grteclyn_wrapper.optimisation.railgun.evolution import COMPONENTS
    repo = Path(__file__).resolve().parents[3]
    reference = repo/'results/railgun/studies/evolution-070-n128'
    manifest = json.loads((reference/'export/manifest.json').read_text()); manifest['n'] = 192
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    (tmp_path/'outcome.json').write_text(json.dumps({'accepted':True, 'gridinit_sha256':'test'}))
    (tmp_path/'corridor.json').write_text((reference/'export/corridor.json').read_text())
    monkeypatch.setattr(pilot, 'digest', lambda p:'test')
    monkeypatch.setattr(pilot, 'grid_layout', lambda p:dict(components=COMPONENTS,
        shape=[200]*3, spacing=[32/192]*3, origin=[-4*32/192]*3))
    plan = pilot.prepare(tmp_path, tmp_path/'params.txt', checkpoints='off')
    assert plan['n'] == 192 and plan['max_steps'] == 600
    from grteclyn_wrapper.optimisation.railgun.evolution_convergence import parameters, PATH_KEYS
    old = parameters(reference/'params.txt'); new = parameters(tmp_path/'params.txt')
    assert {k for k in old.keys()|new.keys() if old.get(k) != new.get(k)} <= (
        PATH_KEYS | {'N_full', 'max_steps'})
