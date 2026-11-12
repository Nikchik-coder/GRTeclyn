import json

import numpy as np
import pytest

from grteclyn_wrapper.campaigns.stationary.ring_movies import completed, validate_cache


def test_waits_for_final_drain_and_rejects_short_run(tmp_path):
    manifest = tmp_path / 'run_manifest.json'
    manifest.write_text(json.dumps({'status': 'running'}))
    assert not completed(tmp_path, 50.)
    manifest.write_text(json.dumps({'status': 'finished', 'exit_status': 0, 't_end': 49.}))
    with pytest.raises(ValueError, match='end time'):
        completed(tmp_path, 50.)
    manifest.write_text(json.dumps({'status': 'failed', 'exit_status': 1, 't_end': 50.}))
    with pytest.raises(ValueError, match='failed'):
        completed(tmp_path, 50.)
    manifest.write_text(json.dumps({'status': 'finished', 'exit_status': 0, 't_end': 50.}))
    assert completed(tmp_path, 50.)


def cache_fixture(run):
    folder = run / 'frames/_slice_cache/phi_z'
    folder.mkdir(parents=True)
    for index in range(3):
        np.savez(folder / f'slice_{index:04d}.npz', time=index / 2., arr=np.ones((2, 2)))
    (run / 'data').mkdir()
    for name in ('complex_scalar_diagnostics', 'collapse_diagnostics', 'constraint_norms'):
        (run / 'data' / f'{name}.dat').write_text('# time value\n0 1\n0.5 1\n1 1\n')
    return folder


def test_missing_middle_slice_cannot_make_a_shortened_movie(tmp_path):
    folder = cache_fixture(tmp_path)
    assert validate_cache(tmp_path, ['phi'], 1., 2, 1) == 3
    (folder / 'slice_0001.npz').unlink()
    with pytest.raises(ValueError, match='incomplete slice cache'):
        validate_cache(tmp_path, ['phi'], 1., 2, 1)


def test_numeric_order_when_step_numbers_exceed_four_digits(tmp_path):
    folder = cache_fixture(tmp_path)
    for path in folder.glob('*.npz'):
        path.unlink()
    for index in range(0, 10001, 250):
        np.savez(folder / f'slice_{index:04d}.npz', time=index/10000., arr=np.ones((2, 2)))
    assert validate_cache(tmp_path, ['phi'], 1., 10000, 250) == 41


def test_rejects_wrong_time_or_nonfinite_diagnostics(tmp_path):
    folder = cache_fixture(tmp_path)
    np.savez(folder / 'slice_0001.npz', time=.6, arr=np.ones((2, 2)))
    with pytest.raises(ValueError, match='cached time'):
        validate_cache(tmp_path, ['phi'], 1., 2, 1)
    np.savez(folder / 'slice_0001.npz', time=.5, arr=np.ones((2, 2)))
    (tmp_path / 'data/constraint_norms.dat').write_text('# time value\n0 1\n1 nan\n')
    with pytest.raises(ValueError, match='invalid diagnostic'):
        validate_cache(tmp_path, ['phi'], 1., 2, 1)
