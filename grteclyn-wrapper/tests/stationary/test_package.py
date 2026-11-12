"""The wheel owns its commands and configuration, independent of source paths."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import sysconfig

import pytest

WRAPPER = Path(__file__).resolve().parents[2]
PROJECT = WRAPPER / 'packages/stationary'
PACKAGE = PROJECT / 'src/grteclyn_stationary'
ENTRY_POINTS = sorted(f'{group}.{p.stem}'
                      for group in ('commands', 'checks', 'derivations')
                      for p in (PACKAGE / group).glob('*.py') if p.stem != '__init__')


@pytest.fixture(scope='module')
def installed(tmp_path_factory):
    directory = tmp_path_factory.mktemp('stationary-wheel')
    build = subprocess.run([sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel',
                            '-d', str(directory)], cwd=PROJECT, text=True, capture_output=True)
    assert build.returncode == 0, build.stderr
    wheel, = directory.glob('*.whl')
    target = directory / 'installed'
    install = subprocess.run(['uv', 'pip', 'install', '--python', sys.executable,
                              '--no-deps', '--offline', '--target', str(target), str(wheel)],
                             env=dict(os.environ, UV_CACHE_DIR=str(directory/'cache')),
                             text=True, capture_output=True)
    assert install.returncode == 0, install.stderr
    # -S prevents the editable source installation's .pth file being processed.
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(target), sysconfig.get_path('purelib')]),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', JAX_PLATFORMS='cpu')
    env.pop('GRTECLYN_ROOT', None)
    return directory, target, env


@pytest.mark.parametrize('entry', ENTRY_POINTS)
def test_installed_help_and_import_do_not_start_jax(installed, entry):
    directory, target, env = installed
    module = f'grteclyn_stationary.{entry}'
    code = '''
import importlib, importlib.abc, pathlib, runpy, sys
class NoJax(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'jax', 'grteclyn_workflows', 'yt', 'h5py'}:
            raise AssertionError(f'help/import attempted to import {fullname}')
sys.meta_path.insert(0, NoJax())
module = importlib.import_module(sys.argv[1])
assert pathlib.Path(module.__file__).is_relative_to(pathlib.Path(sys.argv[2]))
try:
    module.main(['--help'])
except SystemExit as result:
    assert result.code == 0
else:
    raise AssertionError('help did not exit before computation')
'''
    result = subprocess.run([sys.executable, '-S', '-c', code, module, str(target)],
                            cwd=directory, env=env, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert 'usage:' in result.stdout.lower()
    result = subprocess.run([sys.executable, '-S', '-m', module, '--help'], cwd=directory,
                            env=env, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_installed_pipeline_resource_and_dry_run(installed):
    directory, target, env = installed
    build = subprocess.run([sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel',
                            '-d', str(directory/'wrapper-wheel')], cwd=WRAPPER,
                           text=True, capture_output=True)
    assert build.returncode == 0, build.stderr
    wheel, = (directory/'wrapper-wheel').glob('*.whl')
    import zipfile
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(directory/'wrapper')
    env = dict(env, PYTHONPATH=str(directory/'wrapper') + os.pathsep + env['PYTHONPATH'])
    code = '''
import importlib.util
from grteclyn_workflows.campaigns.stationary.pipeline import load
cfg, stages = load()
assert len(stages) == len(cfg['stage']) > 0
for stage in stages.values():
    assert 'script' not in stage
    assert importlib.util.find_spec(stage['module']) is not None
'''
    result = subprocess.run([sys.executable, '-S', '-c', code], cwd=directory,
                            env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    # A synthetic checkout exercises root resolution without touching any job.
    checkout = directory/'checkout'
    marker = checkout/'Examples/RadialRecipe/params.txt'
    marker.parent.mkdir(parents=True)
    marker.touch()
    env = dict(env, GRTECLYN_ROOT=str(checkout))
    result = subprocess.run([sys.executable, '-S', '-m',
                             'grteclyn_workflows.campaigns.stationary.pipeline', 'run',
                             'first-v-0003-150', '--dry-run'], cwd=directory,
                            env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert str(checkout) in result.stdout
    assert '-m grteclyn_stationary.commands.first_matter_solve' in result.stdout
    assert not (checkout/'runs').exists()


def test_python_310_syntax_and_no_obsolete_script_directory():
    for path in [*PACKAGE.rglob('*.py'), *(PACKAGE/'numerics').glob('*.py')]:
        ast.parse(path.read_text(), filename=str(path), feature_version=(3, 10))
    assert not (WRAPPER/'scripts/optimisation').exists()


def test_installed_models_and_retired_namespaces(installed):
    directory, target, env = installed
    code = '''
import importlib, importlib.abc, importlib.util, sys
class NoJax(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'jax', 'grteclyn_workflows', 'yt', 'h5py'}:
            raise AssertionError('model import attempted to initialise JAX')
sys.meta_path.insert(0, NoJax())
for module in ('numerics.newton', 'numerics.jacobian', 'numerics.spectral',
               'spinning_wormhole.solution', 'railgun.problem', 'matter.equations',
               'profiles.boson_star_ode', 'profiles.qball_ode', 'profiles.qball_torus'):
    importlib.import_module('grteclyn_stationary.' + module)
assert not any(n == 'grteclyn_workflows' or n.startswith('grteclyn_workflows.') for n in sys.modules)
from grteclyn_stationary.provenance import source_revision
assert source_revision() is None
'''
    result = subprocess.run([sys.executable, '-S', '-c', code], cwd=directory,
                            env=env, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_installed_solver_recovers_exact_background_without_wrapper(installed):
    directory, target, env = installed
    code = '''
import importlib.abc, sys
class NoWrapper(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'grteclyn_workflows', 'yt', 'h5py'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, NoWrapper())
import numpy as np
from grteclyn_stationary.spinning_wormhole.equations import CollocationProblem
from grteclyn_stationary.numerics.newton import newton
p = CollocationProblem(eta0=2., gamma=0., nx=8, ny=4, prescribe=('omega_inf', 0.))
shape = (p.nx + 1, p.ny + 1)
perturbation = .02 * np.cos(.5 * np.pi * p.sx[:, None])**2 * np.ones(shape)
u, info = newton(p.residual, p.jacobian, p.pack(perturbation, np.zeros(shape)))
assert info['converged'], info
F, W = p.fields(u)
np.testing.assert_allclose(F - p.f_bg, 0., atol=1e-13)
np.testing.assert_allclose(W, 0., atol=1e-13)
np.testing.assert_allclose(p.solve_N(F, W), 0., atol=1e-13)
'''
    result = subprocess.run([sys.executable, '-S', '-c', code], cwd=directory,
                            env=env, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('args', [[], ['optimize'], ['validate'], ['rings']])
def test_installed_command_dispatcher_help(installed, args):
    directory, target, env = installed
    result = subprocess.run([sys.executable, '-S', '-m', 'grteclyn_stationary', *args, '--help'],
                            cwd=directory, env=env, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert 'usage:' in result.stdout.lower()
