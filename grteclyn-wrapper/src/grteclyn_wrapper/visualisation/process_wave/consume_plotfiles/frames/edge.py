"""Blank the box-edge strip of the Weyl4 frames (the consumer's ``--frames-blank-edge``).

Weyl4 is built from second derivatives.  In the outermost two base-grid cells
its 4th-order stencil reaches beyond the box, into ghost cells that are
first-order extrapolated copies of the edge, so the values there are not data.
On the spinning 0.9c (2026-10-17) that strip read 2.4e-4 against 5.5e-7 one
cell further in, from t = 0 on, and set the Weyl4 colour scale.

``blank_edge`` sets the strip to NaN: the frame draws it blank, the colour-scale
rules skip it (they keep finite values only), and the slice cache stores what
the frame shows, so a redraw from the cache is blank there too.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

#: The fields whose edge strip is blanked: the Weyl4 family.
EDGE_BLANK_PREFIX = "Weyl4"


def blanks_edge(field: str) -> bool:
    """Whether ``--frames-blank-edge`` applies to ``field``."""
    return field.startswith(EDGE_BLANK_PREFIX)


def plane_axes(axis: str) -> tuple[int, int]:
    """(horizontal, vertical) dataset axes of a slice normal to ``axis``, in
    yt's order (x-normal: y, z; y-normal: z, x; z-normal: x, y)."""
    return {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[axis]


def edge_widths(ds, axis: str, cells: int) -> tuple[float, float]:
    """``cells`` base-grid cells in code units along the slice's two axes."""
    le = np.asarray(ds.domain_left_edge.d, dtype=float)
    re = np.asarray(ds.domain_right_edge.d, dtype=float)
    dx0 = (re - le) / np.asarray(ds.domain_dimensions, dtype=float)
    h_ax, v_ax = plane_axes(axis)
    return float(cells * dx0[h_ax]), float(cells * dx0[v_ax])


def domain_bounds(ds, axis: str) -> tuple[float, float, float, float]:
    """The box in the slice plane, as (h_lo, h_hi, v_lo, v_hi)."""
    le = np.asarray(ds.domain_left_edge.d, dtype=float)
    re = np.asarray(ds.domain_right_edge.d, dtype=float)
    h_ax, v_ax = plane_axes(axis)
    return float(le[h_ax]), float(re[h_ax]), float(le[v_ax]), float(re[v_ax])


def blank_edge(
    arr: np.ndarray,
    extent: Sequence[float],
    domain: Sequence[float],
    widths: Sequence[float],
) -> None:
    """Set to NaN, in place, every pixel of ``arr`` (indexed [v, h], covering
    ``extent`` = (h_lo, h_hi, v_lo, v_hi)) whose centre lies within ``widths``
    (h, v) of the box ``domain`` = (h_lo, h_hi, v_lo, v_hi)."""
    ny, nx = arr.shape
    h = extent[0] + (np.arange(nx) + 0.5) * (extent[1] - extent[0]) / nx
    v = extent[2] + (np.arange(ny) + 0.5) * (extent[3] - extent[2]) / ny
    h_edge = (h < domain[0] + widths[0]) | (h > domain[1] - widths[0])
    v_edge = (v < domain[2] + widths[1]) | (v > domain[3] - widths[1])
    arr[v_edge[:, None] | h_edge[None, :]] = np.nan
