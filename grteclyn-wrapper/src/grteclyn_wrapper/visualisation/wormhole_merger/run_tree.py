"""Where a run lives in runs/wormhole_merger, by name.

The campaign directory is filed by physics (2026-09-10): a run sits at the
top level while it is on a card and is moved into its group by
`scripts/campaigns/wormhole_merger/file_run.sh` once closed out
(01_single_throat, 03_two_throats, 04_binary_headon, 05_binary_spiral,
06_binary_flyby, 07_bbh_control, ...).  The shell side of the same rule is
`scripts/campaigns/wormhole_merger/lib/run_tree.sh`.

The packed copy under `results/merger/campaign/` is filed to the same shape, so
the same resolver serves both trees:

    from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_run, find_packed
    d = find_run(runs_root, "merge_headon_flip_d8_v1_lvl5_t100_r02200")
    d = find_packed("merge_twin_p012_plain_t100")      # in the pack

Never hard-code either path: a run is refiled by question as the campaign grows
and only the name survives.
"""

from __future__ import annotations

import pathlib
import re

__all__ = ["boosted_adm_mass", "pair_mass", "figure_dir", "find_packed", "find_run", "iter_packed",
           "PACK_ROOT", "REPO", "RUNS_ROOT"]

# …/GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger
REPO = _REPO = pathlib.Path(__file__).resolve().parents[5]
RUNS_ROOT = _REPO / "runs" / "wormhole_merger"
PACK_ROOT = _REPO / "results" / "merger"


def find_run(root: pathlib.Path | str, name: str) -> pathlib.Path:
    """The run directory called <name>: at the top level, or one or two
    levels down inside an NN_* group.  Raises FileNotFoundError."""
    root = pathlib.Path(root).expanduser().resolve()
    name = pathlib.Path(name.rstrip("/")).name
    top = root / name
    if top.is_dir():
        return top
    for pattern in (f"[0-9][0-9]_*/{name}", f"[0-9][0-9]_*/*/{name}"):
        for d in sorted(root.glob(pattern)):
            if d.is_dir():
                return d
    raise FileNotFoundError(f"no run called {name!r} under {root}")


def find_packed(name: str, pack_root: pathlib.Path | str | None = None) -> pathlib.Path:
    """The packed directory of run <name> under <pack_root>/campaign.

    The pack is filed by physics exactly like the run tree, so this is
    `find_run` pointed at `campaign/`.  Raises FileNotFoundError.
    """
    root = pathlib.Path(pack_root or PACK_ROOT).expanduser().resolve()
    camp = root if root.name == "campaign" else root / "campaign"
    return find_run(camp, name)


def figure_dir(group: str, pack_root: pathlib.Path | str | None = None) -> pathlib.Path:
    """<pack>/figures/<group>, created if missing -- where a figure belongs."""
    d = pathlib.Path(pack_root or PACK_ROOT).expanduser() / "figures" / group
    d.mkdir(parents=True, exist_ok=True)
    return d


def iter_packed(pack_root: pathlib.Path | str | None = None):
    """Every packed run, as ``(group, path)``.

    The pack is ``campaign/<group>/[<sub>/]<run>``, with a run still on a card
    sitting at the top level until close-out files it; ``group`` is "" for that
    case and "05_binary_spiral/p012" for a run two levels down.
    """
    root = pathlib.Path(pack_root or PACK_ROOT).expanduser()
    camp = root if root.name == "campaign" else root / "campaign"
    if not camp.is_dir():
        return
    marks = ("evolution_params.txt", "run_tail.log", "LOST.md", "launch_banner.txt")
    skip = {"movies", "frames", "part1", "horizon", "__pycache__"}

    def is_run(d):
        return any((d / m).exists() for m in marks)

    for d in sorted(camp.iterdir()):
        if not d.is_dir():
            continue
        if is_run(d):
            yield "", d
            continue
        for e in sorted(d.iterdir()):
            if not e.is_dir() or e.name in skip:
                continue
            if is_run(e):
                yield d.name, e
            else:
                for f in sorted(e.iterdir()):
                    if f.is_dir() and is_run(f):
                        yield f"{d.name}/{e.name}", f


def boosted_adm_mass(name: str, pack_root: pathlib.Path | str | None = None) -> float:
    """The ADM mass of an exact-boost pair (momentum model 1), by run name.

    The solve's face estimate leaves out each throat's kinetic energy; the
    corrected value is the ``M_ADM_boost`` column of
    ``<pack>/analysis/boosted_adm_mass.tsv`` (grteclyn_wrapper.analysis.
    wormhole_merger.two_throats.boosted_adm_mass).  Raises KeyError for a run
    the table lacks.
    """
    root = pathlib.Path(pack_root or PACK_ROOT).expanduser()
    table = root / "analysis" / "boosted_adm_mass.tsv"
    key = pathlib.Path(name.rstrip("/")).name
    cols = None
    for line in table.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        if cols is None:
            cols = f
            continue
        if pathlib.Path(f[0]).name == key:
            return float(f[cols.index("M_ADM_boost")])
    raise KeyError(f"{key!r} is not in {table}")


# The three d = 12 exact-boost pairs whose t = 0 mass was MEASURED (MASS-t0,
# 2026-10-06): every run of a family shares its parent's solve.
_T0_FAMILY = re.compile(r"merge_orbit_flip_d12_p0(25|45|60)_L128_")


def pair_mass(name: str, pack_root: pathlib.Path | str | None = None) -> float:
    """The mass an exact-boost pair's energies are quoted per, by run name.

    The measured t = 0 ADM mass (the full surface integral, ``M_ADM_t0`` of
    ``<pack>/analysis/t0_adm_mass.tsv``) for the d = 12 pairs at p = 0.25 /
    0.45 / 0.60, any run of the family (restart legs, twins, SERIES); else
    ``boosted_adm_mass``.  The prescription reads 2.4-3.2 % below the
    measurement where both exist.
    """
    root = pathlib.Path(pack_root or PACK_ROOT).expanduser()
    key = pathlib.Path(name.rstrip("/")).name
    hit = _T0_FAMILY.search(key)
    if hit:
        table = root / "analysis" / "t0_adm_mass.tsv"
        cols = None
        for line in table.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            f = line.split("\t")
            if cols is None:
                cols = f
                continue
            if f"_p0{hit.group(1)}_" in f[0]:
                return float(f[cols.index("M_ADM_t0")])
        raise KeyError(f"{key!r}: its family p0{hit.group(1)} is not in {table}")
    return boosted_adm_mass(name, pack_root)
