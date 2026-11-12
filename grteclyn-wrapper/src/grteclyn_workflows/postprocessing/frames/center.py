from __future__ import annotations

from typing import Sequence

import numpy as np

from ..config import _FRAME_BUFF_CAP, _FRAME_SAMPLES_PER_CELL


def _resolve_frame_physics_center(
    ds,
    axis: str,
    coord: float | None,
    zoom: float | None,
    center_xyz: Sequence[float] | None,
    corner: bool,
) -> list[float]:
    """Match visualize/__main__.py center logic; auto throat corner when unset."""
    mid_x = float((ds.domain_right_edge[0] + ds.domain_left_edge[0]) / 2.0)
    mid_y = float((ds.domain_right_edge[1] + ds.domain_left_edge[1]) / 2.0)
    mid_z = float((ds.domain_right_edge[2] + ds.domain_left_edge[2]) / 2.0)
    # Default to the DOMAIN MIDPOINT on every axis.  The old default left the
    # z component at 0.0, which is only correct for origin-centred domains:
    # on a [0, L] domain an axis-x/y slice then centres its window at z = 0
    # and the physics at z = L/2 is out of frame entirely -- this silently
    # ruined the queue-2e movies on 2026-09-14 (see README, defect 6).
    physics_center = [mid_x, mid_y, mid_z]

    if corner and zoom is not None:
        slice_plane_val = 0.0 if coord is None else float(coord)
        if center_xyz is not None:
            origin = np.array(center_xyz, dtype=float)
        else:
            origin = np.array(
                [mid_x - float(zoom) / 2.0, mid_y - float(zoom) / 2.0, slice_plane_val],
                dtype=float,
            )
        w = float(zoom)
        if axis == "z":
            physics_center = [origin[0] + w / 2.0, origin[1] + w / 2.0, slice_plane_val]
        elif axis == "y":
            physics_center = [origin[0] + w / 2.0, slice_plane_val, origin[2] + w / 2.0]
        elif axis == "x":
            physics_center = [slice_plane_val, origin[1] + w / 2.0, origin[2] + w / 2.0]
    elif center_xyz is not None:
        physics_center = [float(center_xyz[0]), float(center_xyz[1]), float(center_xyz[2])]

    if coord is not None:
        if axis == "z":
            physics_center[2] = float(coord)
        elif axis == "y":
            physics_center[1] = float(coord)
        elif axis == "x":
            physics_center[0] = float(coord)

    return physics_center


def _yt_slice_center(ds, axis: str, physics_center: Sequence[float]):
    """``physics_center`` as the centre handed to yt.SlicePlot: its plane moved off any cell face."""
    centre = [float(v) for v in physics_center]
    ai = {"x": 0, "y": 1, "z": 2}[axis]
    centre[ai] = _off_cell_face(ds, ai, centre[ai])
    return ds.arr(centre, "code_length")


def _off_cell_face(ds, axis: int, plane: float) -> float:
    """The slice plane, moved a millionth of the finest cell off a cell face it sits on.

    2026-10-17: yt's SlicePlot through a plane exactly on a cell face selects the
    cells on BOTH sides and its fixed-resolution buffer sums them, so every field
    was drawn 2x (the N 96 spinning runs: z = 32 is a face on every level there;
    measured 2.0000 against the plotfile).  Off the face, the cell above the plane
    is drawn (the one below it at the domain's upper edge).
    """
    dx = float(ds.index.get_smallest_dx().d)
    le = float(ds.domain_left_edge.d[axis])
    re = float(ds.domain_right_edge.d[axis])
    k = (float(plane) - le) / dx
    if abs(k - round(k)) > 1e-6:
        return float(plane)
    return float(plane) - 1e-6 * dx if plane >= re else float(plane) + 1e-6 * dx


def _frame_buff_size(ds, zoom: float | None) -> int:
    """Pixels across the FRB: ``_FRAME_SAMPLES_PER_CELL`` samples per simulation
    cell in the zoom window (capped at ``_FRAME_BUFF_CAP``)."""
    if zoom is None:
        zoom = float(ds.domain_width[0])
    le = np.array(ds.domain_left_edge.d, dtype=float)
    re = np.array(ds.domain_right_edge.d, dtype=float)
    dims = np.array(ds.domain_dimensions, dtype=float) * (2 ** int(ds.index.max_level))
    dx = (re - le) / np.maximum(dims, 1.0)
    cells = max(int(round(float(zoom) / min(dx[0], dx[1]))), 64)
    return int(min(max(cells * _FRAME_SAMPLES_PER_CELL, 256), _FRAME_BUFF_CAP))

