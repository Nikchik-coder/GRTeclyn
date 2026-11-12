"""Reading the campaign's data streams -- one loader per file shape.

Four modules were each parsing the Weyl4 files their own way, which is how
`plot_bbh_ringdown` came to read a column by its index and go on reading it
after the pack changed shape.  The shapes are:

``Weyl4_mode_<lm>.dat`` / ``weyl_extraction_mode_<lm>.dat``
    time, then (Re, Im) for one mode at each extraction sphere.  A header line
    ``#   r =   14.000000  14.000000  20.000000 ...`` names the spheres when it
    is present; when the pack thinned the file it sometimes is not, so the
    caller may pass the radii it expects.

``psi4_mode_l2_all.dat``
    time, then (Re, Im) for every m of l = 2 at every sphere, with the columns
    named in the header: ``Re_m-2(R=14)  Im_m-2(R=14) ... Re_m2(R=30)``.

Both are written while the run is alive, so the last line can be torn; both
loaders drop a short final row rather than raising.
"""

from __future__ import annotations

import pathlib
import re

import numpy as np

__all__ = ["load_l2_all", "load_mode", "read_rows"]


def read_rows(path: pathlib.Path, ncol: int) -> np.ndarray:
    """Numeric rows of at least ``ncol`` columns; comments and torn rows out."""
    rows = []
    with pathlib.Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < ncol:
                continue
            try:
                rows.append([float(x) for x in parts[:ncol]])
            except ValueError:
                continue
    if not rows:
        raise SystemExit(f"no numeric rows in {path}")
    return np.array(rows)


def load_mode(path, radii: list[float] | None = None):
    """``(t, {radius: complex mode integral})`` from a per-mode Weyl4 stream.

    The stream already folds the radius into the amplitude, so the values are
    r*psi4 and are directly comparable between spheres.
    """
    path = pathlib.Path(path)
    header = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            if "r =" in line:
                # `#   r =   14.000000  14.000000  20.000000 ...` -- one entry
                # per COLUMN, so the spheres are every other value.
                vals = [float(x) for x in re.findall(r"[\d.eE+-]+", line)]
                header = vals[::2]
                break
            if "R=" in line:
                # `# time  Re(R=10)  Im(R=10)  Re(R=14) ...` -- the consumer's
                # own naming, used by psi4_mode_l2m0.dat and friends.
                header = [float(x) for x in re.findall(r"Re\(R=([\d.eE+-]+)\)", line)]
                if header:
                    break
                header = None
    radii = header or radii
    if not radii:
        raise ValueError(f"no 'r =' header in {path} and no radii given")
    a = read_rows(path, 1 + 2 * len(radii))
    return a[:, 0], {r: a[:, 1 + 2 * i] + 1j * a[:, 2 + 2 * i] for i, r in enumerate(radii)}


def load_l2_all(path):
    """``(t, {(m, radius): complex})`` from ``psi4_mode_l2_all.dat``.

    The column names carry both m and the sphere, so nothing here depends on
    the order they happen to be written in.
    """
    path = pathlib.Path(path)
    names: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            if "Re_m" in line:
                names = line.lstrip("#").split()
                break

    if not names:
        raise ValueError(f"no column header in {path}")
    a = read_rows(path, len(names))
    out: dict[tuple[int, float], np.ndarray] = {}
    for i, nm in enumerate(names):
        # Two spellings in the wild: the consumer writes "Re_m0(R=14)", the
        # hand-stitched full-history file "Re_m0(R14)".
        m = re.fullmatch(r"Re_m(-?\d+)\(R=?([\d.]+)\)", nm)
        if m:
            out[(int(m.group(1)), float(m.group(2)))] = a[:, i] + 1j * a[:, i + 1]
    return a[:, 0], out
