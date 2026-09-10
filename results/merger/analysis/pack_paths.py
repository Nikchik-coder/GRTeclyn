"""Where a run's packed streams live in results/merger, by name.

Since 2026-09-10 the pack is filed by physics, mirroring the run tree:
campaign/<group>/<run>/ with the groups 01_single_throat, 03_two_throats,
04_binary_headon (its one-step placement probes one level deeper, under
placement/), 05_binary_spiral (its freeze programme one level deeper, under
merger_fix/), 06_binary_flyby, 07_bbh_control.  Every analysis script resolves
a run through here, so none of them knows the layout.

    from pack_paths import find_run, iter_runs, group_of
"""

from __future__ import annotations

import pathlib

CAMPAIGN = "campaign"
# Folders inside a run directory that are not runs themselves.
NOT_RUNS = {"movies", "frames", "part1", "horizon", "__pycache__"}


def iter_runs(root: pathlib.Path):
    """Every packed run directory under <root>/campaign, deepest shape
    campaign/<group>/<sub>/<run>; yields (group, path), group = '' for an
    unfiled run at the top level (a live run packed before close-out)."""
    camp = root / CAMPAIGN
    if not camp.is_dir():
        return
    for d in sorted(camp.iterdir()):
        if not d.is_dir():
            continue
        if _is_run(d):
            yield "", d
            continue
        for e in sorted(d.iterdir()):
            if not e.is_dir() or e.name in NOT_RUNS:
                continue
            if _is_run(e):
                yield d.name, e
            else:
                for f in sorted(e.iterdir()):
                    if f.is_dir() and _is_run(f):
                        yield f"{d.name}/{e.name}", f


def _is_run(d: pathlib.Path) -> bool:
    return any((d / f).exists() for f in ("evolution_params.txt", "run_tail.log", "LOST.md", "launch_banner.txt"))


def find_run(root: pathlib.Path, name: str) -> pathlib.Path | None:
    """The packed directory of run <name>, wherever it is filed."""
    for _, d in iter_runs(root):
        if d.name == name:
            return d
    return None


def group_of(root: pathlib.Path, path: pathlib.Path) -> str:
    """'05_binary_spiral' for campaign/05_binary_spiral/<run>."""
    rel = path.resolve().relative_to((root / CAMPAIGN).resolve())
    return rel.parts[0] if len(rel.parts) > 1 else ""


def group_dir(root: pathlib.Path, group: str) -> pathlib.Path:
    """<root>/campaign/<group>, created if missing -- where a group's generated
    notes (INSTABILITY.md, BRANCHES.md, PLACEMENT_CURVE.md, ...) are written."""
    d = root / CAMPAIGN / group
    d.mkdir(parents=True, exist_ok=True)
    return d


def figure_dir(root: pathlib.Path, group: str) -> pathlib.Path:
    """<root>/figures/<group>, created if missing."""
    d = root / "figures" / group
    d.mkdir(parents=True, exist_ok=True)
    return d
