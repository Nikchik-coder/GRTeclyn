"""The renamed workflow wheel works outside the checkout's source tree."""
from pathlib import Path
import os
import subprocess
import sys
import sysconfig
import zipfile

import pytest

PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def wheel_install(tmp_path_factory):
    directory = tmp_path_factory.mktemp('workflows-wheel')
    target = directory / 'installed'
    for project in (PROJECT, PROJECT / 'packages/stationary'):
        result = subprocess.run(
            [sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel', '-d', str(directory)],
            cwd=project, capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
    for wheel in directory.glob('*.whl'):
        with zipfile.ZipFile(wheel) as archive:
            assert not any(n.startswith('grteclyn_wrapper/') for n in archive.namelist())
            assert not any(n.endswith(('.png', '.pdf', '.eps')) for n in archive.namelist())
            archive.extractall(target)
    # -S prevents editable-install .pth files from supplying source modules.
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(target), sysconfig.get_path('purelib')]),
               GRTECLYN_ROOT=str(PROJECT.parent), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='')
    return directory, target, env


def test_installed_workflow_ownership_and_console_entry(wheel_install):
    directory, target, env = wheel_install
    code = '''
import importlib, importlib.metadata, importlib.util, pathlib, sys
root = pathlib.Path(sys.argv[1])
assert importlib.util.find_spec('grteclyn_wrapper') is None
import grteclyn_workflows.diagnostics
assert not any(n.startswith('grteclyn_workflows.search') for n in sys.modules)
for name in ('evolution.runner', 'diagnostics', 'search.scoring',
             'search.scoring.incremental', 'postprocessing', 'plotting.waveforms.plot_extracted_psi4'):
    module = importlib.import_module('grteclyn_workflows.' + name)
    assert pathlib.Path(module.__file__).is_relative_to(root)
entry, = importlib.metadata.distribution('grteclyn-workflows').entry_points
assert entry.name == 'grteclyn-workflows'
assert callable(entry.load())
'''
    result = subprocess.run([sys.executable, '-S', '-c', code, str(target)],
                            cwd=directory, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('module', [
    'grteclyn_workflows', 'grteclyn_workflows.postprocessing',
    'grteclyn_workflows.plotting.constraints',
    'grteclyn_workflows.plotting.waveforms.plot_extracted_psi4',
])
def test_installed_commands(wheel_install, module):
    directory, _, env = wheel_install
    result = subprocess.run([sys.executable, '-S', '-m', module, '--help'], cwd=directory,
                            env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert 'usage:' in result.stdout.lower()


def test_installed_plotter_writes_default_output_outside_source(wheel_install):
    directory, target, env = wheel_install
    checkout = directory / 'plot-checkout'
    marker = checkout / 'Examples/RadialRecipe/params.txt'
    marker.parent.mkdir(parents=True)
    marker.touch()
    data = directory / 'constraints.dat'
    data.write_text('0 0.01 0.02\n1 0.005 0.01\n2 0.0025 0.005\n')
    result = subprocess.run(
        [sys.executable, '-S', '-m', 'grteclyn_workflows.plotting.constraints', str(data)],
        cwd=directory, env=dict(env, GRTECLYN_ROOT=str(checkout), MPLBACKEND='Agg'),
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    for suffix in ('png', 'pdf', 'eps'):
        output = checkout / 'runs/plots' / f'constraints_plot.{suffix}'
        assert output.stat().st_size > 100
    assert not list(target.rglob('*.png'))
