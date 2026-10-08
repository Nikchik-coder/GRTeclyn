"""Where a run lives, by name: in the pack (results/merger) or in the run tree.

The pack is filed by physics, mirroring the run tree: campaign/<group>/<run>/,
or one level deeper where a group is split by question (01_single_throat/seed/,
04_binary_headon/csm/, 06_binary_flyby/verify_p025/, ...).  A run still on a
card sits at the top level until close-out files it.  Every analysis module
resolves a run through here, so none of them knows the layout:

    from grteclyn_wrapper.analysis.wormhole_merger.pack.paths import find_run, iter_runs
"""

from __future__ import annotations

import pathlib

# .../GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/analysis/wormhole_merger/pack
REPO = pathlib.Path(__file__).resolve().parents[6]
PACK_ROOT = REPO / "results" / "merger"
RUNS_ROOT = REPO / "runs" / "wormhole_merger"

CAMPAIGN = "campaign"
# Folders inside a run directory that are not runs themselves.
NOT_RUNS = {"movies", "frames", "part1", "horizon", "__pycache__"}
RUN_MARKERS = ("evolution_params.txt", "run_tail.log", "LOST.md", "launch_banner.txt")


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
        # campaign/00_archive holds untracked extracts of superseded runs.
        if d.name == "00_archive":
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
    # <run>.__keep is pack_results.sh's temporary copy of a run being repacked.
    if d.name.endswith(".__keep"):
        return False
    return any((d / f).exists() for f in RUN_MARKERS)


def find_run(root: pathlib.Path, name: str) -> pathlib.Path | None:
    """The packed directory of run <name>, wherever it is filed."""
    for _, d in iter_runs(root):
        if d.name == name:
            return d
    return None


def find_in_run_tree(root: pathlib.Path, name: str) -> pathlib.Path | None:
    """The directory of run <name> in the run tree: at the top level while it
    is on a card, else one or two levels down in its group."""
    for pattern in (name, f"*/{name}", f"*/*/{name}"):
        hits = sorted(p for p in pathlib.Path(root).glob(pattern) if p.is_dir())
        if hits:
            return hits[0]
    return None


def group_dir(root: pathlib.Path, group: str) -> pathlib.Path:
    """<root>/campaign/<group>, created if missing -- where a group's generated
    notes (INSTABILITY.md, BRANCHES.md, WAVE_GATES.md, ...) are written."""
    d = root / CAMPAIGN / group
    d.mkdir(parents=True, exist_ok=True)
    return d


def figure_dir(root: pathlib.Path, group: str) -> pathlib.Path:
    """<root>/figures/<group>, created if missing."""
    d = root / "figures" / group
    d.mkdir(parents=True, exist_ok=True)
    return d
