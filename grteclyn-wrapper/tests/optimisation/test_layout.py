"""The optimisation package's two dependency rules (decided 2026-10-28).

1. Nothing outside optimisation/ imports it.  develop, the public release
   line, ships the published packages without it, so one such import (say
   from analysis/spinning_wormhole) would break the release.  The package
   reads the published code, never the other way round.
2. optimisation/solver/ imports nothing from grteclyn_wrapper: the solver
   core stays physics-free and can be lifted out whole.
"""

from __future__ import annotations

import ast
import warnings
from pathlib import Path

WRAPPER = Path(__file__).resolve().parents[2]
SRC = WRAPPER / "src"
PKG = SRC / "grteclyn_wrapper" / "optimisation"
SCRIPTS = WRAPPER / "scripts"
OWN_SCRIPTS = SCRIPTS / "optimisation"


def _imports(path: Path) -> set[str]:
    """Every module name ``path`` imports, relative imports resolved
    against its package (files outside src/ have none)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(path.read_text(), str(path))
    package = (path.relative_to(SRC).with_suffix("").parts[:-1]
               if SRC in path.parents else ())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[: len(package) - node.level + 1]
                module = ".".join(base + ((node.module,) if node.module
                                          else ()))
            else:
                module = node.module
            names.add(module)
            # "from grteclyn_wrapper import optimisation" names it here
            names.update(f"{module}.{a.name}" for a in node.names)
    return names


def _within(name: str, package: str) -> bool:
    return name == package or name.startswith(package + ".")


def test_nothing_outside_imports_optimisation():
    outside = [p for p in sorted(SRC.rglob("*.py")) if PKG not in p.parents]
    outside += [p for p in sorted(SCRIPTS.rglob("*.py"))
                if OWN_SCRIPTS not in p.parents]
    offenders = [f"{p.relative_to(WRAPPER)} imports {name}"
                 for p in outside for name in sorted(_imports(p))
                 if _within(name, "grteclyn_wrapper.optimisation")]
    assert not offenders, "\n".join(offenders)


def test_solver_core_is_physics_free():
    offenders = [f"{p.relative_to(WRAPPER)} imports {name}"
                 for p in sorted((PKG / "solver").rglob("*.py"))
                 for name in sorted(_imports(p))
                 if _within(name, "grteclyn_wrapper")
                 and not _within(name, "grteclyn_wrapper.optimisation.solver")]
    assert not offenders, "\n".join(offenders)
