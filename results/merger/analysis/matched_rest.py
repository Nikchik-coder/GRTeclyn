#!/usr/bin/env python3
"""The rest pairs rerun on far-side-matched data: the sign rule and the force law, old against new.

Every old pair at rest (03_two_throats: ctrl_rest_d12/14/16/18, ctrl_flip_d12) started from the
superposition, whose mouths are 9-15 % larger than the isolated throat and whose mass leaves out
the interaction energy.  Each is rerun with its own params and only the data changed
(constraint_solve_puncture_mode = 3, name token csm): each mouth's far-side mass and charge are
the isolated drainhole's.  At t = 0 such a pair weighs

    M_ADM - 2m = sigma^2 [ +-(a^2 + m^2) - m^2 ] / d      (+ flipped, - like)

(results/merger/t0_matching/energy_scan.tsv), and the two readings of that energy give opposite
forces (Q = (a^2 + m^2)/m^2 = 5, in units of gravity's m^2/d^2):

    fixed charge    F = -dE/dd       flipped pushed apart (Q - 1), like pulled together (Q + 1)
    fixed potential (conductors)     flipped pulled together (Q + 1), like pushed apart (Q - 1)

so -dsep_flip/dsep_like is +(Q+1)/(Q-1) = 1.5 at fixed potential (what the superposed pairs did:
1.518 +/- 0.021) and -(Q-1)/(Q+1) = -0.67 at fixed charge.

Measurement: sign_rule.py's, with its pit_centroid imported: inverse-chi-weighted centroids of
the cached chi_z slices, box +/-3 around each chi minimum, throats split at the frame centre.
The ratio uses t = 3.5 .. 10.5 only (the gauge settles by t ~ 3); the force law is the
displacement at t = 11.5 (separation_ladder_2026-09-04.txt), fitted with A/(d + delta)^2.

Reads the RUN TREE (the caches are not packed); writes the reduced table into the pack:

    python results/merger/analysis/matched_rest.py [--runs runs/wormhole_merger] [--pack results/merger]
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
from sign_rule import pit_centroid  # noqa: E402

LIKE = {12: "ctrl_rest_d12_csm", 14: "ctrl_rest_d14_csm", 16: "ctrl_rest_d16_csm", 18: "ctrl_rest_d18_csm"}
FLIP = {12: "ctrl_flip_d12_csm"}
WINDOW = (3.5, 10.5)
T_LADDER = 11.5
# The superposed runs (separation_ladder_2026-09-04.txt; sign_rule_displacement.dat).
OLD_LADDER = {12: 0.4696, 14: 0.3699, 16: 0.2980, 18: 0.2438}
OLD_RATIO = (1.518, 0.021)
Q = 5.0


def find_run(runs: str, name: str) -> str | None:
    """The run directory, at the top of the run tree or filed in a group."""
    for pattern in (name, f"*/{name}", f"*/*/{name}"):
        hits = [p for p in glob.glob(os.path.join(runs, pattern)) if os.path.isdir(p)]
        if hits:
            return sorted(hits)[0]
    return None


def series(run_dir: str) -> np.ndarray:
    """(t, separation) from every cached chi_z slice, split at the frame centre."""
    rows = []
    for f in sorted(glob.glob(os.path.join(run_dir, "frames", "_slice_cache", "chi_z", "*.npz"))):
        d = np.load(f)
        arr, ext, t = d["arr"], d["extent"], float(d["time"])
        split = 0.5 * (ext[0] + ext[1])
        rows.append((t, pit_centroid(arr, ext, split, ext[1]) - pit_centroid(arr, ext, ext[0], split)))
    return np.array(rows)


def t0_solve(run_dir: str) -> dict[str, float]:
    """The t = 0 row of constraint_solve.dat (M_ADM, sigma, c, far side)."""
    path = os.path.join(run_dir, "data", "constraint_solve.dat")
    if not os.path.isfile(path):
        return {}
    head = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                head = line[1:].split()
            elif line.strip() and head:
                return dict(zip(head, (float(x) for x in line.split())))
    return {}


def at(s: np.ndarray, t0: float) -> float:
    """Displacement sep(t0) - sep(0), NaN before the run reaches t0."""
    if not len(s) or s[-1, 0] < t0 - 1e-9:
        return float("nan")
    return float(np.interp(t0, s[:, 0], s[:, 1]) - s[0, 1])


def offset_fit(ds: dict[int, float]) -> tuple[float, float]:
    """delta, A of dsep = A / (d + delta)^2, least squares over the rungs present."""
    d = np.array(sorted(ds), dtype=float)
    y = np.array([ds[k] for k in sorted(ds)])
    if d.size < 3:
        return float("nan"), float("nan")
    best = (np.inf, np.nan, np.nan)
    for delta in np.linspace(-5.0, 15.0, 20001):
        g = 1.0 / (d + delta) ** 2
        a = float((g * y).sum() / (g * g).sum())
        r = float(((y - a * g) ** 2).sum())
        if r < best[0]:
            best = (r, delta, a)
    return best[1], best[2]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default="runs/wormhole_merger")
    ap.add_argument("--pack", default="results/merger")
    ap.add_argument("--no-write", action="store_true", help="print only")
    a = ap.parse_args()

    ser, solve, names = {}, {}, {}
    for sign, arms in (("like", LIKE), ("flip", FLIP)):
        for d, name in arms.items():
            run_dir = find_run(a.runs, name)
            s = series(run_dir) if run_dir else np.empty((0, 2))
            if not len(s):
                print(f"  {name:<20} {'not in the run tree' if run_dir is None else 'no chi_z slice cache yet'}")
                continue
            ser[(sign, d)], solve[(sign, d)], names[(sign, d)] = s, t0_solve(run_dir), name
            sv = solve[(sign, d)]
            old = f"  old {OLD_LADDER[d]:+.4f}" if sign == "like" and d in OLD_LADDER else ""
            print(f"  {name:<20} t = 0 .. {s[-1, 0]:5.2f}  M_ADM(0) = {sv.get('M_ADM', np.nan):.5f}"
                  f"  sep(0) = {s[0, 1]:.4f}  dsep({T_LADDER}) = {at(s, T_LADDER):+.4f}{old}"
                  f"  dsep(end) = {s[-1, 1] - s[0, 1]:+.4f}")

    lines = []
    if ("like", 12) in ser and ("flip", 12) in ser:
        sl, sf = ser[("like", 12)], ser[("flip", 12)]
        t = sl[:, 0]
        like = sl[:, 1] - sl[0, 1]
        flip = np.interp(t, sf[:, 0], sf[:, 1] - sf[0, 1])
        flip[t > sf[-1, 0] + 1e-9] = np.nan
        win = (t >= WINDOW[0] - 1e-6) & (t <= WINDOW[1] + 1e-6) & np.isfinite(flip)
        r = -flip[win] / like[win]
        if r.size >= 2:
            lines.append(f"d = 12: -dsep_flip/dsep_like over t = {WINDOW[0]}..{min(WINDOW[1], t[win][-1]):g} = "
                         f"{r.mean():.3f} +/- {r.std(ddof=1):.3f} (n = {r.size}); superposed {OLD_RATIO[0]:.3f} +/- "
                         f"{OLD_RATIO[1]:.3f}; fixed potential {(Q + 1) / (Q - 1):.3f}, fixed charge {-(Q - 1) / (Q + 1):.3f}")
    ladder = {d: at(ser[("like", d)], T_LADDER) for d in LIKE if ("like", d) in ser}
    ladder = {d: v for d, v in ladder.items() if np.isfinite(v)}
    if ladder:
        lines.append("like pairs, dsep at t = 11.5: " + ", ".join(
            f"d = {d}: {v:+.4f} (old {OLD_LADDER[d]:+.4f}, x{v / OLD_LADDER[d]:.3f})" for d, v in sorted(ladder.items())))
        delta, amp = offset_fit(ladder)
        if np.isfinite(delta):
            dold, _ = offset_fit(OLD_LADDER)
            lines.append(f"force law A/(d + delta)^2 over d = {min(ladder)}..{max(ladder)}: delta = {delta:.2f}, "
                         f"A = {amp:.1f} (the superposed ladder, same fit: delta = {dold:.2f})")
    for line in lines:
        print("  " + line)

    if a.no_write or not ser:
        return 0
    out = group_dir(pathlib.Path(a.pack), "03_two_throats") / "matched_rest_displacement.dat"
    keys = [("like", d) for d in LIKE if ("like", d) in ser] + [("flip", d) for d in FLIP if ("flip", d) in ser]
    t_all = np.unique(np.concatenate([ser[k][:, 0] for k in keys]))
    with open(out, "w", encoding="utf-8") as f:
        f.write("# The rest pairs rerun on far-side-matched data (mode 3, 2026-09-28): separation change of each run.\n")
        f.write("# Inverse-chi-weighted pit centroids of the cached chi_z slices (box +/-3, split at the frame centre),\n")
        f.write("# sign_rule.py's measurement; NOT throat_track.dat.  The old superposed runs: sign_rule_displacement.dat,\n")
        f.write("# separation_ladder_2026-09-04.txt.\n")
        for k in keys:
            s, sv = ser[k], solve[k]
            f.write(f"# {names[k]}: M_ADM(0) = {sv.get('M_ADM', float('nan')):.5f}, sep(0) = {s[0, 1]:.4f},"
                    f" last slice t = {s[-1, 0]:g}\n")
        for line in lines:
            f.write(f"# {line}\n")
        f.write("# time  " + "  ".join(f"dsep_{k[0]}_d{k[1]}" for k in keys) + "\n")
        for ti in t_all:
            vals = []
            for k in keys:
                s = ser[k]
                j = np.where(np.isclose(s[:, 0], ti))[0]
                vals.append(s[j[0], 1] - s[0, 1] if j.size else np.nan)
            f.write(f"  {ti:7.2f}  " + "  ".join(f"{v:9.4f}" for v in vals) + "\n")
    print(f"[matched-rest] wrote {out} ({t_all.size} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
