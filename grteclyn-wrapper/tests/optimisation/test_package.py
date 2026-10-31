"""The wheel owns its commands and configuration, independent of source paths."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import sysconfig

import pytest

WRAPPER = Path(__file__).resolve().parents[2]
PACKAGE = WRAPPER / 'src/grteclyn_wrapper/optimisation'
ENTRY_POINTS = sorted(f'{group}.{p.stem}'
                      for group in ('commands', 'checks', 'derivations')
                      for p in (PACKAGE / group).glob('*.py') if p.stem != '__init__')


@pytest.fixture(scope='module')
def installed(tmp_path_factory):
    directory = tmp_path_factory.mktemp('optimisation-wheel')
    build = subprocess.run([sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel',
                            '-d', str(directory)], cwd=WRAPPER, text=True, capture_output=True)
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
    module = f'grteclyn_wrapper.optimisation.{entry}'
    code = '''
import importlib, importlib.abc, pathlib, runpy, sys
class NoJax(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname == 'jax' or fullname.startswith('jax.'):
            raise AssertionError('help/import attempted to initialise JAX')
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
    code = '''
import importlib.util
from grteclyn_wrapper.optimisation.commands.pipeline import load
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
                             'grteclyn_wrapper.optimisation.commands.pipeline', 'run',
                             'first-v-0003-150', '--dry-run'], cwd=directory,
                            env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert str(checkout) in result.stdout
    assert '-m grteclyn_wrapper.optimisation.commands.first_matter_solve' in result.stdout
    assert not (checkout/'runs').exists()


def test_python_310_syntax_and_no_obsolete_script_directory():
    for path in PACKAGE.rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path), feature_version=(3, 10))
    assert not (WRAPPER/'scripts/optimisation').exists()
