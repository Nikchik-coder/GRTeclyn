"""Frames of a symmetry-reduced run, mirrored into the full plane.

With ``--reflect`` the simulated domain holds only the part of the frame
window on the positive side of each reflective plane.  The frame is drawn from
that part and mirrored across the reflective in-plane axes, so an octant run's
frame looks exactly like the full-box run's with the same ``--frames-zoom``
(the FULL window width) -- throat in the middle, same colour scale.  Every
frame field is a scalar or a diagonal component (even parity); an odd-parity
field is refused rather than mirrored with the wrong sign.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import yt

from ..extraction.symmetry import ODD_PARITY_FIELDS, reflect_axes
from ..fields import _field_key, _register_derived_fields
from .center import _frame_buff_size

_AXIS = {"x": 0, "y": 1, "z": 2}
# yt's image axes for a slice normal to each axis: (horizontal, vertical).
_IMAGE_AXES = {0: (1, 2), 1: (2, 0), 2: (0, 1)}


def mirror_plan(axis: str, reflect: Sequence[str] | None) -> tuple[bool, bool]:
    """(mirror horizontally, mirror vertically) for a slice normal to ``axis``."""
    h_ax, v_ax = _IMAGE_AXES[_AXIS[axis]]
    r = set(reflect_axes(reflect))
    return (h_ax in r, v_ax in r)


def mirrored_window(
    ds,
    field: str,
    axis: str,
    coord: float | None,
    zoom: float | None,
    center_xyz: Sequence[float] | None,
    reflect: Sequence[str] | None,
) -> tuple[np.ndarray, list[float], float] | None:
    """(array indexed [v, h], extent (h_lo, h_hi, v_lo, v_hi), slice coordinate)
    of the full-plane frame, or None when no in-plane axis is reflective.

    ``center_xyz`` is the physics centre on the reflective planes (the launch
    passes the params' centre); ``zoom`` is the full window width.
    """
    mh, mv = mirror_plan(axis, reflect)
    if not (mh or mv):
        return None
    if field in ODD_PARITY_FIELDS:
        raise ValueError(f"{field} has odd parity across a reflective plane; not mirrored")
    ai = _AXIS[axis]
    h_ax, v_ax = _IMAGE_AXES[ai]
    le = np.asarray(ds.domain_left_edge.d, dtype=float)
    c = np.asarray(center_xyz, dtype=float) if center_xyz is not None else le.copy()
    width = float(zoom) if zoom is not None else 2.0 * float(ds.domain_width.d[h_ax])
    half = width / 2.0
    h_lo, h_hi = (c[h_ax], c[h_ax] + half) if mh else (c[h_ax] - half, c[h_ax] + half)
    v_lo, v_hi = (c[v_ax], c[v_ax] + half) if mv else (c[v_ax] - half, c[v_ax] + half)
    plane = float(coord) if coord is not None else float(c[ai])

    _register_derived_fields(ds, field)
    plot_field = _field_key(ds, field)
    # The full window's pixel count, halved on each mirrored axis: the mirrored
    # frame has the same pixels, at the same centres, as a full-box frame of
    # this width -- so frames and slice caches compare one to one.
    n_full = _frame_buff_size(ds, width)
    n_h = n_full // 2 if mh else n_full
    n_v = n_full // 2 if mv else n_full
    centre3 = [0.0, 0.0, 0.0]
    centre3[ai] = plane
    centre3[h_ax] = 0.5 * (h_lo + h_hi)
    centre3[v_ax] = 0.5 * (v_lo + v_hi)
    slc = yt.SlicePlot(ds, axis, plot_field, center=ds.arr(centre3, "code_length"),
                       buff_size=(n_h, n_v))
    slc.set_width(((h_hi - h_lo, "code_length"), (v_hi - v_lo, "code_length")))
    q = np.asarray(slc.frb[plot_field], dtype=float)
    if q.shape == (n_h, n_v) and n_h != n_v:
        q = q.T
    if mh:
        q = np.hstack([q[:, ::-1], q])
    if mv:
        q = np.vstack([q[::-1, :], q])
    extent = [c[h_ax] - half, c[h_ax] + half, c[v_ax] - half, c[v_ax] + half]
    return q, extent, plane
