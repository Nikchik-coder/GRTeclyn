#!/usr/bin/env python3
"""Convergence orders of a Bondi resolution set's constraint norms.

Reads ``data/constraint_norms.dat`` of each member (an episode dir, or a packed
cell holding ``constraint_norms.dat``) and prints, at the requested times, the
order between consecutive members, p = ln(e1/e2) / ln(N2/N1), for

  Ham int / Mom int   cols 18-19, r <= 24 inside the sponge (binary 8d0771d4 on)
  Ham amr / Mom amr   cols 12-13, all cells but the 4-cell boundary layer.

Each time is read off the last row at or before it, so "0" is the first row,
t = dt.  With --reference (one packed cell per member, same order) it also
prints how far the members' existing columns sit from the reference rows at
the same times: a rerun on a newer binary reproduces its old run when they
agree to rounding.

Usage:
  constraint_orders.py <member> <member> [<member> ...] [--times 0 5 10 15 20]
      [--reference <packed cell> ...]
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

COLUMNS = {  # name -> 0-based column (time is column 0)
    "L2_Ham": 1, "L2_Mom": 2, "L2_Ham_amr": 11, "L2_Mom_amr": 12,
    "Linf_Ham_amr": 15, "L2_Ham_int": 17, "L2_Mom_int": 18,
}
ROWS = (("Ham int", "L2_Ham_int"), ("Mom int", "L2_Mom_int"),
        ("Ham amr", "L2_Ham_amr"), ("Mom amr", "L2_Mom_amr"))


def norms_file(member: Path) -> Path:
    for cand in (member / "data" / "constraint_norms.dat", member / "constraint_norms.dat"):
        if cand.is_file():
            return cand
    raise SystemExit(f"no constraint_norms.dat under {member}")


def load(member: Path) -> np.ndarray:
    rows = []
    for line in norms_file(member).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            rows.append([float(v) for v in line.split()])
    width = max(len(r) for r in rows)
    out = np.full((len(rows), width), np.nan)
    for i, r in enumerate(rows):
        out[i, :len(r)] = r
    return out


def resolution(member: Path) -> int:
    """N from the member's params (episode) or launch record (packed cell)."""
    for name in ("params.txt", "evolution_params.txt"):
        p = member / name
        if p.is_file():
            for line in p.read_text().splitlines():
                key, _, value = line.partition("=")
                if key.strip() == "N_full":
                    return int(float(value.split()[0]))
    raise SystemExit(f"no N_full in {member}")


def row_at(table: np.ndarray, t: float) -> np.ndarray:
    i = np.searchsorted(table[:, 0], t + 1e-9, side="right") - 1
    return table[max(i, 0)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("members", nargs="+", type=Path)
    ap.add_argument("--times", nargs="+", type=float, default=[0, 5, 10, 15, 20])
    ap.add_argument("--reference", nargs="+", type=Path, default=None)
    args = ap.parse_args()

    members = sorted(((resolution(m), m, load(m)) for m in args.members),
                     key=lambda x: x[0])
    ns = [n for n, _, _ in members]
    print("orders " + " / ".join(f"N {a}->{b}" for a, b in zip(ns[:-1], ns[1:])))
    print(f"{'':10s}" + "".join(f"{'t ' + format(t, 'g'):>18s}" for t in args.times))
    for label, col in ROWS:
        c = COLUMNS[col]
        cells = []
        for t in args.times:
            vals = [row_at(tab, t)[c] if c < tab.shape[1] else np.nan
                    for _, _, tab in members]
            parts = []
            for (n1, n2), (e1, e2) in zip(zip(ns[:-1], ns[1:]), zip(vals[:-1], vals[1:])):
                ok = np.isfinite(e1) and np.isfinite(e2) and e1 > 0 and e2 > 0
                parts.append(f"{math.log(e1 / e2) / math.log(n2 / n1):.1f}" if ok else "-")
            cells.append(" / ".join(parts))
        print(f"{label:10s}" + "".join(f"{s:>18s}" for s in cells))

    print("\nnorms (first member to last)")
    for label, col in ROWS:
        c = COLUMNS[col]
        for t in args.times:
            vals = [row_at(tab, t)[c] if c < tab.shape[1] else np.nan
                    for _, _, tab in members]
            print(f"  {label:8s} t {t:5g}: " + "  ".join(f"{v:.4e}" for v in vals))

    if args.reference:
        if len(args.reference) != len(args.members):
            raise SystemExit("--reference needs one packed cell per member")
        refs = sorted(((resolution(r), load(r)) for r in args.reference), key=lambda x: x[0])
        print("\nreproduction: max |new/ref - 1| over the reference rows at t <= "
              f"{max(args.times):g}")
        for (n, _, tab), (nr, ref) in zip(members, refs):
            if n != nr:
                raise SystemExit(f"reference N {nr} does not match member N {n}")
            ref = ref[ref[:, 0] <= max(args.times) + 1e-9]
            idx = np.searchsorted(tab[:, 0], ref[:, 0] - 1e-9)
            idx = np.clip(idx, 0, len(tab) - 1)
            same_t = np.abs(tab[idx, 0] - ref[:, 0]) < 1e-9
            out = []
            for col in ("L2_Ham", "L2_Mom", "L2_Ham_amr", "L2_Mom_amr", "Linf_Ham_amr"):
                c = COLUMNS[col]
                rel = np.abs(tab[idx[same_t], c] / ref[same_t, c] - 1.0)
                out.append(f"{col} {np.nanmax(rel):.1e}")
            print(f"  N {n} ({int(same_t.sum())} rows): " + ", ".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
