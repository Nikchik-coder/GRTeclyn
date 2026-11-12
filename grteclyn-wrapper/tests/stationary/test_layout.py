"""Enforce portable solver and application dependency boundaries."""
import ast
import importlib.util
from pathlib import Path

WRAPPER = Path(__file__).resolve().parents[2]
SOURCE = WRAPPER / 'packages/stationary/src'
STATIONARY = SOURCE / 'grteclyn_stationary'
NUMERICS = STATIONARY / 'numerics'


def imports(path, root=SOURCE):
    relative = path.relative_to(root).with_suffix('')
    package = '.'.join(relative.parts[:-1])
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = (importlib.util.resolve_name('.' * node.level + (node.module or ''), package)
                      if node.level else node.module)
            yield module
            yield from (f'{module}.{alias.name}' for alias in node.names)


def within(name, package):
    return name == package or name.startswith(package + '.')


def test_numerics_has_no_physics_or_campaign_dependencies():
    assert {p.stem for p in NUMERICS.glob('*.py')} >= {'newton', 'jacobian', 'device', 'spectral'}
    offenders = [(p.name, name) for p in NUMERICS.rglob('*.py') for name in imports(p)
                 if within(name, 'grteclyn_stationary')
                 and not within(name, 'grteclyn_stationary.numerics')]
    assert not offenders


def test_spinning_model_depends_only_on_numerics_and_its_own_model():
    paths = list((STATIONARY / 'spinning_wormhole').glob('*.py'))
    assert paths
    allowed = ('grteclyn_stationary.numerics', 'grteclyn_stationary.spinning_wormhole')
    offenders = [(p.name, name) for p in paths for name in imports(p)
                 if within(name, 'grteclyn_stationary') and not any(within(name, a) for a in allowed)]
    assert not offenders


def test_complete_solver_has_no_wrapper_dependency():
    offenders = [(str(p.relative_to(STATIONARY)), name)
                 for p in STATIONARY.rglob('*.py') for name in imports(p)
                 if within(name, 'grteclyn_workflows')]
    assert not offenders


def test_active_code_does_not_import_retired_packages():
    forbidden = ('grteclyn_workflows.optimisation', 'grteclyn_workflows.analysis.spinning_wormhole',
                 'grteclyn_workflows.rl', 'grteclyn_workflows.stationary', 'grteclyn_workflows.numerics')
    offenders = []
    for root in (WRAPPER/'src', WRAPPER/'scripts', SOURCE):
        for p in root.rglob('*.py'):
            for name in imports(p, root):
                if any(within(name, f) for f in forbidden):
                    offenders.append((str(p.relative_to(WRAPPER)), name))
    assert not offenders
