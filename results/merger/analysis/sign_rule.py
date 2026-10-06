#!/usr/bin/env python3
"""The sign rule, reduced to one table: separation change of the d = 12 pairs.

Two like-oriented drainhole throats released from rest PUSH apart; flipping
the field direction of one (wormhole_phi_sign_B = -1) turns the push into a
pull.  The scalar charge sets the size as well as the sign: with
|F_phi/F_grav| = Q = (a^2 + m^2)/m^2 = 5, the flipped pair's infall and the
like pair's escape are (Q+1) and (Q-1) in the same units, so

    |dsep_flip| / |dsep_rest| = (Q+1)/(Q-1) = 1.500,   time by time.

Measurement, following 03_two_throats/NOTES.md and the validated tool
grteclyn-wrapper/scripts/validation/apoint_repulsion.py (this script uses the
same centroid, box and split, and reproduces its accelerations exactly):
the pit position is the inverse-chi-weighted centroid of the cached chi_z
slice (frames/_slice_cache/chi_z/*.npz), +/-3 code units around the chi
minimum, throats split at x = 32 -- never throat_track.dat, whose 0.03
quantum is the whole early displacement.  Coordinates under-read while the
gauge settles, so the ratio is only quoted over t = 3.5 .. 10.5.

Reads the RUN TREE (the caches are not packed); writes the reduced table
into the pack, next to the group's NOTES.md:

    python results/merger/analysis/sign_rule.py \
        [--runs runs/wormhole_merger/03_two_throats] [--pack results/merger]

The figure is
``python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_sign_rule``,
which reads the table this writes and draws nothing the table does not hold.
"""
from __future__ import annotations

import argparse
import glob
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack_paths import group_dir  # noqa: E402

ARMS = (  # column name in the table -> run directory
    ("dsep_like", "ctrl_rest_d12"),   # sigma = +1, a = 2: the baseline push
    ("dsep_a1", "ctrl_rest_a1"),      # sigma = +1, a = 1: quarter the charge
    ("dsep_flip", "ctrl_flip_d12"),   # sigma = -1, a = 2: the pull
)
WINDOW = (3.5, 10.5)   # NOTES.md: nothing before t ~ 3 (gauge), 10.5 = flip's last slice
Q = 5.0                # |F_phi / F_grav| = (a^2 + m^2)/m^2 at a = 2, m = 1


def pit_centroid(arr, extent, xlo, xhi, box=3.0):
    """Inverse-chi-weighted centroid of the pit inside [xlo, xhi] -- the
    apoint_repulsion.py measurement, verbatim."""
    ny, nx = arr.shape
    x = np.linspace(extent[0], extent[1], nx)
    y = np.linspace(extent[2], extent[3], ny)
    X, Y = np.meshgrid(x, y)
    sel = (X >= xlo) & (X < xhi)
    a = np.where(sel, arr, np.inf)
    j, i = np.unravel_index(np.argmin(a), a.shape)
    win = sel & (np.abs(X - X[j, i]) <= box) & (np.abs(Y - Y[j, i]) <= box)
    w = np.where(win, 1.0 / np.clip(arr, 1e-12, None), 0.0)
    return float((w * X).sum() / w.sum())


def series(run_dir: str, split: float = 32.0) -> np.ndarray:
    """(t, separation) from every cached chi_z slice of one run."""
    rows = []
    for f in sorted(glob.glob(os.path.join(run_dir, "frames", "_slice_cache",
                                           "chi_z", "*.npz"))):
        d = np.load(f)
        arr, ext, t = d["arr"], d["extent"], float(d["time"])
        rows.append((t, pit_centroid(arr, ext, split, ext[1])
                     - pit_centroid(arr, ext, ext[0], split)))
    return np.array(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default="runs/wormhole_merger/03_two_throats")
    ap.add_argument("--pack", default="results/merger")
    a = ap.parse_args()

    ser = {}
    for col, run in ARMS:
        s = series(os.path.join(a.runs, run))
        if not len(s):
            raise SystemExit(f"no chi_z slice cache under {a.runs}/{run}")
        ser[col] = s
        print(f"  {run:<16} t = {s[0, 0]:g} .. {s[-1, 0]:g}   sep(0) = {s[0, 1]:.4f}"
              f"   dsep(end) = {s[-1, 1] - s[0, 1]:+.4f}")

    # One master clock (the like pair's), the others interpolated onto it
    # where they have data, NaN where they have ended.
    t = ser["dsep_like"][:, 0]
    cols = {}
    for col, _ in ARMS:
        s = ser[col]
        d = np.interp(t, s[:, 0], s[:, 1] - s[0, 1])
        d[t > s[-1, 0] + 1e-9] = np.nan
        cols[col] = d

    in_win = ((t >= WINDOW[0] - 1e-6) & (t <= WINDOW[1] + 1e-6)
              & np.isfinite(cols["dsep_flip"]))
    ratio = np.full(t.size, np.nan)
    ratio[in_win] = -cols["dsep_flip"][in_win] / cols["dsep_like"][in_win]
    r = ratio[in_win]
    print(f"  ratio |dsep_flip|/|dsep_like| over t = {WINDOW[0]} .. {WINDOW[1]}:"
          f"  {r.mean():.3f} +/- {r.std(ddof=1):.3f}  (n = {r.size},"
          f"  predicted (Q+1)/(Q-1) = {(Q + 1) / (Q - 1):.3f})")

    out = group_dir(pathlib.Path(a.pack), "03_two_throats") / "sign_rule_displacement.dat"
    with open(out, "w", encoding="utf-8") as f:
        f.write("# The sign rule at d = 12: separation change of three rest-released pairs.\n")
        f.write("# Inverse-chi-weighted pit centroids of the cached chi_z slices (box +/-3,\n")
        f.write("# split x = 32), the apoint_repulsion.py measurement; NOT throat_track.dat.\n")
        for col, run in ARMS:
            s = ser[col]
            f.write(f"# {col}: {run}, sep(0) = {s[0, 1]:.4f}, last slice t = {s[-1, 0]:g}\n")
        f.write(f"# ratio = -dsep_flip/dsep_like, only over t = {WINDOW[0]} .. {WINDOW[1]}"
                f" (gauge settles by t ~ 3):\n")
        f.write(f"#   {r.mean():.3f} +/- {r.std(ddof=1):.3f} over {r.size} slices;"
                f" predicted (Q+1)/(Q-1) = {(Q + 1) / (Q - 1):.3f} at Q = {Q:g}\n")
        f.write("# time  dsep_like  dsep_a1  dsep_flip  ratio\n")
        for i in range(t.size):
            f.write(f"  {t[i]:7.2f}  {cols['dsep_like'][i]:9.4f}  {cols['dsep_a1'][i]:9.4f}"
                    f"  {cols['dsep_flip'][i]:9.4f}  {ratio[i]:7.3f}\n")
    print(f"[sign-rule] wrote {out} ({t.size} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
