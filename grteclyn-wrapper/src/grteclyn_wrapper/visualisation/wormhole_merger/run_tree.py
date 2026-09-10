"""Where a run lives in runs/wormhole_merger, by name.

The campaign directory is filed by physics (2026-09-10): a run sits at the
top level while it is on a card and is moved into its group by
`scripts/campaigns/wormhole_merger/file_run.sh` once closed out
(01_single_throat, 03_two_throats, 04_binary_headon, 05_binary_spiral,
06_binary_flyby, 07_bbh_control, ...).  The shell side of the same rule is
`scripts/campaigns/wormhole_merger/lib/run_tree.sh`.

    from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_run
    d = find_run(runs_root, "merge_headon_flip_d8_v1_lvl5_t100_r02200")
"""

from __future__ import annotations

import pathlib

__all__ = ["find_run", "RUNS_ROOT"]

# …/GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger
_REPO = pathlib.Path(__file__).resolve().parents[5]
RUNS_ROOT = _REPO / "runs" / "wormhole_merger"


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
