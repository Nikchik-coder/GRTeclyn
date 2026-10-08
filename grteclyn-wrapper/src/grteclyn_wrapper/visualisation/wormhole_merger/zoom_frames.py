#!/usr/bin/env python3
"""Redraw a run's cached slices zoomed about the window centre, into an episode
of its own -- the source of the upload videos' close-ups.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.zoom_frames \\
        EPISODE OUT --zoom 2 --fields K,lapse,chi,Weyl4_Re \\
        [--symlog Weyl4_Re:2] [--log chi] [--t-max T] [--scale-tmin T] [--scale-tmax T]

EPISODE is a run dir or a stitch dir (anything holding frames/_slice_cache).
The cached slice is already windowed (the run's frame window, e.g. 40 wide),
and the plotfiles are long gone, so a zoom is a crop: ``--zoom 2`` keeps the
central half in each direction at the cache's own pixels.  ``--zoom 1`` is a
plain redraw, for a series that only needs a different scale.

Every field gets ONE fixed scale measured over the cropped series (the live
renderer's per-slice rule, enveloped), so nothing cropped away sets the
colours.  K is linear, the standing convention; ``--symlog`` and
``--log`` name the fields drawn otherwise (FIELD:DECADES for symlog).

``--t-max`` is the trust window: later frames are not drawn.  ``--scale-tmin``
and ``--scale-tmax`` measure the scales only inside that time range -- for a
series whose initial-data junk, or whose final runaway (p = 0.90's K wall),
would otherwise set them; the frames outside it are still drawn and may
saturate.

Writes OUT/frames/<field>_z/frames/*.png, OUT/frames/zoom_zlims.json and
OUT/movies/movie_<field>_z.mp4.  The episode's own frames and cache are only
read.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames import slice_cache

REPO = pathlib.Path(__file__).resolve().parents[5]
MAKE_MOVIES = REPO / "grteclyn-wrapper" / "scripts" / "plot" / "make_movies.sh"
AXIS = "z"


def crop(arr: np.ndarray, extent: list[float], zoom: float) -> tuple[np.ndarray, list[float]]:
    """The central 1/zoom of a windowed slice, and its extent."""
    if zoom == 1:
        return arr, list(extent)
    ny, nx = arr.shape
    kx, ky = int(round(nx / zoom)), int(round(ny / zoom))
    i0, j0 = (nx - kx) // 2, (ny - ky) // 2
    x0, x1, y0, y1 = extent
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    return (arr[j0:j0 + ky, i0:i0 + kx],
            [x0 + i0 * dx, x0 + (i0 + kx) * dx, y0 + j0 * dy, y0 + (j0 + ky) * dy])


def series_limits(paths: list[str], field: str, zoom: float,
                  t_lo: float | None, t_hi: float | None) -> tuple[float, float] | None:
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames.zlim import (
        _auto_zlim_from_array,
    )
    lo = hi = None
    for p in paths:
        arr, extent, time, _ = slice_cache.load_slice(p)
        if (t_lo is not None and time < t_lo - 1e-9) or (t_hi is not None and time > t_hi + 1e-9):
            continue
        one = _auto_zlim_from_array(crop(arr, extent, zoom)[0], field)
        if one is None:
            continue
        lo = one[0] if lo is None else min(lo, one[0])
        hi = one[1] if hi is None else max(hi, one[1])
    return None if lo is None else (float(lo), float(hi))


def render_field(job: dict) -> tuple[str, int, list[float], str | None]:
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.config import (
        _field_frame_config,
    )
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames.slice import (
        draw_slice_png,
    )
    field, paths, zoom, norm, decades = (job[k] for k in ("field", "paths", "zoom", "norm", "decades"))
    limits = series_limits(paths, field, zoom, job["scale_tmin"], job["scale_tmax"])
    if limits is None:
        return field, 0, [], norm
    if norm == "log":
        limits = (max(limits[0], 1e-12), limits[1])
    linthresh = slice_cache.series_linthresh(limits, decades) if norm == "symlog" else None
    cfg = _field_frame_config(field)
    out_frames = str(job["out"] / "frames")
    for p in paths:
        arr, extent, time, coord_val = slice_cache.load_slice(p)
        sub, ext = crop(arr, extent, zoom)
        idx = int(slice_cache._SLICE_RE.search(p).group(1))
        draw_slice_png(sub, ext, field=field, cfg=cfg, axis=AXIS, coord_val=coord_val,
                       time=time, zlim=limits, frames_out_dir=out_frames, frame_idx=idx,
                       norm=norm, linthresh=linthresh)
    return field, len(paths), [limits[0], limits[1]], norm


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("out")
    ap.add_argument("--zoom", type=float, default=2.0)
    ap.add_argument("--fields", default="K,lapse,chi,Weyl4_Re")
    ap.add_argument("--symlog", default="Weyl4_Re:2", help="FIELD[:DECADES],... drawn symmetric-log")
    ap.add_argument("--log", default="", help="FIELD,... drawn on a log scale (positive fields)")
    ap.add_argument("--t-max", type=float, default=None)
    ap.add_argument("--scale-tmin", type=float, default=None)
    ap.add_argument("--scale-tmax", type=float, default=None)
    args = ap.parse_args(argv)

    ep = pathlib.Path(args.episode).resolve()
    frames_dir = ep if (ep / slice_cache.CACHE_DIR_NAME).is_dir() else ep / "frames"
    if not (frames_dir / slice_cache.CACHE_DIR_NAME).is_dir():
        raise SystemExit(f"no slice cache under {ep}")
    out = pathlib.Path(args.out).resolve()

    norms: dict[str, tuple[str, float]] = {}
    for item in filter(None, (s.strip() for s in args.symlog.split(","))):
        name, _, dec = item.partition(":")
        norms[name] = ("symlog", float(dec) if dec else slice_cache.DEFAULT_SYMLOG_DECADES)
    for name in filter(None, (s.strip() for s in args.log.split(","))):
        norms[name] = ("log", 0.0)

    jobs = []
    for field in filter(None, (s.strip() for s in args.fields.split(","))):
        paths = slice_cache.within_window(
            slice_cache.cached_series(str(frames_dir), field, AXIS), args.t_max)
        if not paths:
            raise SystemExit(f"{field}: nothing cached under {frames_dir}")
        for old in (out / "frames" / f"{field}_{AXIS}" / "frames").glob("*.png"):
            old.unlink()
        norm, decades = norms.get(field, (None, slice_cache.DEFAULT_SYMLOG_DECADES))
        jobs.append(dict(field=field, paths=paths, zoom=args.zoom, norm=norm, decades=decades,
                         scale_tmin=args.scale_tmin, scale_tmax=args.scale_tmax, out=out))

    used = {}
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        for field, n, limits, norm in pool.map(render_field, jobs):
            used[f"{field}_{AXIS}"] = limits
            print(f"[zoom] {field}: {n} frames, zoom {args.zoom:g}, "
                  f"{norm or 'linear'} {limits[0]:.4g} .. {limits[1]:.4g}" if limits else
                  f"[zoom] {field}: nothing drawn")
    (out / "frames").mkdir(parents=True, exist_ok=True)
    (out / "frames" / "zoom_zlims.json").write_text(json.dumps(
        {**used, "_zoom": args.zoom, "_t_max": args.t_max, "_scale_tmin": args.scale_tmin,
         "_scale_tmax": args.scale_tmax,
         "_source": str(frames_dir.relative_to(REPO)) if frames_dir.is_relative_to(REPO) else frames_dir.name}, indent=2, sort_keys=True))
    subprocess.run(["bash", str(MAKE_MOVIES), str(out)], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
