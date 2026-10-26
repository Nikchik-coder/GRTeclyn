#!/usr/bin/env python3
"""Repair the outermost cell layer of a solved pair's metric (chi, lapse).

Gridinits converted with a target origin before 2026-10-22
(grtresna/io/chombo.py, _target_span_slice) painted each face's outermost layer
from a solve cell outside the evolution box: the nearest-cell fallback mapped
outside cells onto the edge, and the last one painted won.  chi and the lapse
step there by up to 3e-4 on five of the six faces; the matter, repainted
analytically, is clean.  The step is a source of constraint violation that
grows with resolution.

The solve's HDF5 is deleted after conversion, so the right values are gone.
This sets that layer from the interior by cubic extrapolation along the face
normal (error ~ dx^4 times the fourth derivative), face by face, so edges and
corners take already-repaired neighbours.  Every other cell and component is
copied unchanged.

Usage:
  repair_face_layer.py <source episode dir> <output episode dir>
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analysis" / "bondi_dipole"))
from t0_constraints import open_gridinit  # noqa: E402

FIELDS = ("chi", "lapse")
COPIED = ("initial_data.matter.json", "metadata.json", "lapse_patch.json")


def face_planes(shape: tuple[int, int, int]):
    """(name, axis, outer index, inward step) for the six faces; axes (z, y, x)."""
    nz, ny, nx = shape
    return [("x-", 2, 0, 1), ("x+", 2, nx - 1, -1), ("y-", 1, 0, 1),
            ("y+", 1, ny - 1, -1), ("z-", 0, 0, 1), ("z+", 0, nz - 1, -1)]


def plane(arr: np.ndarray, axis: int, index: int) -> tuple:
    sl = [slice(None)] * 3
    sl[axis] = index
    return tuple(sl)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    src, out = args.source.resolve(), args.output.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")

    (out / "grtresna").mkdir(parents=True)
    for name in COPIED:
        if (src / name).is_file():
            shutil.copy2(src / name, out / name)
    for item in (src / "grtresna").iterdir():
        if item.is_file():
            shutil.copy2(item, out / "grtresna" / item.name)

    names, data, dx, origin = open_gridinit(src / "initial_data.gridinit")
    dst = out / "initial_data.gridinit"
    shutil.copyfile(src / "initial_data.gridinit", dst)
    fixed = np.memmap(dst, dtype=np.float64, mode="r+", offset=data.offset, shape=data.shape)
    record = {"source": str(src), "fields": {}}
    for field in FIELDS:
        c = names.index(field)
        f = np.array(data[..., c])
        steps = {}
        for face, axis, i0, step in face_planes(f.shape):
            p = [f[plane(f, axis, i0 + step * k)] for k in range(1, 5)]
            new = 4.0 * p[0] - 6.0 * p[1] + 4.0 * p[2] - p[3]
            steps[face] = float(np.max(np.abs(f[plane(f, axis, i0)] - new)))
            f[plane(f, axis, i0)] = new
        fixed[..., c] = f
        record["fields"][field] = steps
    fixed.flush()
    del fixed
    check = np.memmap(dst, dtype=np.float64, mode="r", offset=data.offset, shape=data.shape)
    others = [c for c, n in enumerate(names) if n not in FIELDS]
    record["other_components_identical"] = all(
        np.array_equal(np.asarray(check[kz][..., others]), np.asarray(data[kz][..., others]))
        for kz in range(data.shape[0]))
    (out / "face_repair.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{out.parent.name} N {data.shape[2]}: other components identical: "
          f"{record['other_components_identical']}")
    for field, steps in record["fields"].items():
        print(f"  {field}: outer-layer change per face " +
              " ".join(f"{k} {v:.1e}" for k, v in steps.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
