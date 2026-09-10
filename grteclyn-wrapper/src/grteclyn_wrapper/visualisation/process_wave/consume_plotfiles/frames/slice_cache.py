"""Keep the 2-D slices, not the plotfiles, so a movie can be rescaled later.

THE PROBLEM.  Frames are rendered as plotfiles arrive and the plotfiles are
deleted immediately -- they are far too large to keep.  So the renderer can
never know how large a field will grow later in the run, and both of its
choices are wrong for a paper movie: rescaling every frame makes the colourbar
and its tick labels move in every frame, and locking the scale from the first
plotfile puts late-time features off the end of it.

THE FIX.  The thing the renderer actually draws is a single 2-D slice, and it is
already in memory when the frame is drawn.  A slice is around ten thousand times
smaller than the plotfile it came from -- at N = 512 that is a ~1 MB array out of
a ~30 GB plotfile -- so it can be kept for the whole run at negligible cost.
Afterwards the envelope over every cached slice gives the one scale that clips
nothing, and every frame is redrawn against it.

Rough cost: ``N * N * 4`` bytes per field per frame before compression, and these
fields are smooth, so ``savez_compressed`` typically takes a large bite out of
that.  For N = 512, 19 fields and 500 frames the raw figure is about 5 GB;
cache only the fields you actually want movies of if that matters.

Only the native (uniform covering grid) render path caches.  AMR levels go
through yt's fixed-resolution buffer instead and are not cached yet.
"""

from __future__ import annotations

import json
import os
import re
from typing import Iterable, Sequence

import numpy as np

#: Slices live beside the frames, under a name that cannot collide with a
#: ``<field>_<axis>`` frame directory.
CACHE_DIR_NAME = "_slice_cache"

_SLICE_RE = re.compile(r"slice_(\d+)\.npz$")


def _series_dir(frames_out_dir: str, field: str, axis: str) -> str:
    return os.path.join(frames_out_dir, CACHE_DIR_NAME, f"{field}_{axis}")


def cache_slice(
    frames_out_dir: str,
    field: str,
    axis: str,
    frame_idx: int,
    arr: np.ndarray,
    extent: Sequence[float],
    *,
    time: float,
    coord_val: float,
) -> str:
    """Store one slice, with everything needed to redraw its frame."""
    out_dir = _series_dir(frames_out_dir, field, axis)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"slice_{frame_idx:04d}.npz")
    np.savez_compressed(
        path,
        arr=np.asarray(arr, dtype=np.float32),
        extent=np.asarray(extent, dtype=np.float64),
        time=np.float64(time),
        coord_val=np.float64(coord_val),
    )
    return path


def cached_series(frames_out_dir: str, field: str, axis: str) -> list[str]:
    """Cached slices for one field/axis, in frame order."""
    out_dir = _series_dir(frames_out_dir, field, axis)
    if not os.path.isdir(out_dir):
        return []
    found = [
        os.path.join(out_dir, n) for n in os.listdir(out_dir) if _SLICE_RE.search(n)
    ]
    return sorted(found, key=lambda p: int(_SLICE_RE.search(p).group(1)))


def cached_fields(frames_out_dir: str) -> list[tuple[str, str]]:
    """Every ``(field, axis)`` pair with cached slices."""
    root = os.path.join(frames_out_dir, CACHE_DIR_NAME)
    if not os.path.isdir(root):
        return []
    pairs = []
    for name in sorted(os.listdir(root)):
        if not os.path.isdir(os.path.join(root, name)) or "_" not in name:
            continue
        field, _, axis = name.rpartition("_")
        if field and axis:
            pairs.append((field, axis))
    return pairs


def load_slice(path: str) -> tuple[np.ndarray, list[float], float, float]:
    with np.load(path) as data:
        return (
            np.asarray(data["arr"], dtype=np.float64),
            [float(v) for v in data["extent"]],
            float(data["time"]),
            float(data["coord_val"]),
        )


def series_zlim(paths: Iterable[str], field: str) -> tuple[float, float] | None:
    """The scale that clips nothing across a whole cached series.

    Each slice is asked for the limits it would have chosen on its own -- the
    same rule the live renderer uses -- and the envelope of those is taken.  So
    no frame is scaled worse than it would have been per-frame, and the scale is
    the same in all of them.
    """
    from .zlim import _auto_zlim_from_array

    lo = hi = None
    for path in paths:
        try:
            arr, _, _, _ = load_slice(path)
        except (OSError, ValueError):
            continue
        one = _auto_zlim_from_array(arr, field)
        if one is None:
            continue
        lo = one[0] if lo is None else min(lo, one[0])
        hi = one[1] if hi is None else max(hi, one[1])
    if lo is None or hi is None:
        return None
    return (float(lo), float(hi))


#: Decades of dynamic range a symmetric-log frame shows below its peak.  Two is
#: about what a reader can still get values off a colourbar for; beyond three
#: the quiet end is the field's own numerical noise floor, drawn large.
DEFAULT_SYMLOG_DECADES = 2.0


def series_linthresh(
    zlim: Sequence[float], decades: float = DEFAULT_SYMLOG_DECADES
) -> float | None:
    """Where a symmetric-log scale should stop being linear.

    Fixed at ``decades`` below the series peak, so the log part always spans a
    known, readable range.

    It is tempting to measure this from the data instead -- the quietest frame's
    own auto-limit -- but that latches onto a degenerate frame and produces a
    picture of noise.  Measured 2026-09-10 on the head-on stitch: K is exactly
    zero at t = 0 (momentarily-static initial data), so the measured rule
    returned the 5e-6 floor, 15000x below the peak, and every frame after the
    merger came out uniformly saturated.
    """
    span = max(abs(float(zlim[0])), abs(float(zlim[1])))
    if span <= 0.0 or decades <= 0.0:
        return None
    return span / (10.0 ** decades)


def rerender_series(
    frames_out_dir: str,
    field: str,
    axis: str,
    *,
    zlim: Sequence[float] | None = None,
    corner: bool = False,
    verbose: bool = False,
    norm: str | None = None,
    linthresh: float | None = None,
    decades: float = DEFAULT_SYMLOG_DECADES,
) -> tuple[int, tuple[float, float] | None]:
    """Redraw every frame of one series against a single fixed scale.

    Returns ``(frames_written, zlim_used)``.  With ``zlim`` given, that scale is
    used; otherwise it is measured from the cache.
    """
    from ..config import _field_frame_config
    from .slice import draw_slice_png

    paths = cached_series(frames_out_dir, field, axis)
    if not paths:
        return (0, None)

    limits = tuple(zlim) if zlim is not None else series_zlim(paths, field)
    if limits is None:
        return (0, None)
    if norm == "symlog" and linthresh is None:
        linthresh = series_linthresh(limits, decades)

    cfg = _field_frame_config(field)
    written = 0
    for path in paths:
        idx = int(_SLICE_RE.search(path).group(1))
        try:
            arr, extent, time, coord_val = load_slice(path)
        except (OSError, ValueError) as exc:
            print(f"WARNING: rerender skipped {os.path.basename(path)}: {exc}")
            continue
        draw_slice_png(
            arr, extent,
            field=field, cfg=cfg, axis=axis,
            coord_val=coord_val, time=time, zlim=limits,
            frames_out_dir=frames_out_dir, frame_idx=idx,
            corner=corner, verbose=verbose, note=" (cached)",
            norm=norm, linthresh=linthresh,
        )
        written += 1
    return (written, (float(limits[0]), float(limits[1])))


def rerender_all(
    frames_out_dir: str,
    *,
    corner: bool = False,
    verbose: bool = False,
    norms: dict[str, str] | None = None,
    decades: float = DEFAULT_SYMLOG_DECADES,
    field_decades: dict[str, float] | None = None,
    only: Iterable[str] | None = None,
) -> dict[str, list[float]]:
    """Redraw every cached series, each against its own fixed scale.

    ``norms`` maps a field name to a colour normalisation ("symlog", "log") for
    that field only; every field left out keeps the linear default.  A key of
    ``"*"`` applies to every field that has no entry of its own.
    ``field_decades`` overrides the symlog range for named fields -- fields do
    not all want the same one: on the head-on stitch K and the scalar want two
    decades, while Weyl4 at two decades is mostly the coarse grid's own noise
    and reads better at 1.5.  ``only`` restricts the redraw to named fields.
    """
    used: dict[str, list[float]] = {}
    norms = norms or {}
    field_decades = field_decades or {}
    only = set(only) if only else None
    for field, axis in cached_fields(frames_out_dir):
        if only is not None and field not in only:
            continue
        norm = norms.get(field, norms.get("*"))
        written, limits = rerender_series(
            frames_out_dir, field, axis, corner=corner, verbose=verbose,
            norm=norm, decades=field_decades.get(field, decades),
        )
        if not written or limits is None:
            print(f"[rerender] {field}_{axis}: nothing cached, skipped")
            continue
        used[f"{field}_{axis}"] = [limits[0], limits[1]]
        dec = field_decades.get(field, decades)
        how = f" [{norm}, {dec:g} decades]" if norm == "symlog" else (f" [{norm}]" if norm else "")
        print(
            f"[rerender] {field}_{axis}: {written} frame(s) at a fixed "
            f"{limits[0]:.6g} .. {limits[1]:.6g}{how}"
        )
    if used:
        record = os.path.join(frames_out_dir, CACHE_DIR_NAME, "rerender_zlims.json")
        try:
            with open(record, "w", encoding="utf-8") as fh:
                json.dump(used, fh, indent=2, sort_keys=True)
        except OSError as exc:
            print(f"WARNING: could not write {record}: {exc}")
    return used
