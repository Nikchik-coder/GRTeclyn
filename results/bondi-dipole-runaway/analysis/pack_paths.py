"""Where a packed run lives: ``campaign/<NN_group>/<run>``.

Since 2026-10-23 the pack files each run under the question it answers, in the
same groups as ``runs/bondi/``.  Readers find a run by its name alone, so a run
can change group without any of them changing.
"""

from __future__ import annotations

import pathlib


def runs(camp: pathlib.Path) -> list[pathlib.Path]:
    """Every packed run directory, sorted by run name."""
    return sorted((d for d in pathlib.Path(camp).glob("[0-9][0-9]_*/*") if d.is_dir()),
                  key=lambda d: d.name)


def run_dir(camp: pathlib.Path, name: str) -> pathlib.Path:
    """The directory of the packed run ``name``; ``camp/name`` if no group holds it."""
    hits = sorted(pathlib.Path(camp).glob(f"[0-9][0-9]_*/{name}"))
    return hits[0] if hits else pathlib.Path(camp) / name
