#!/usr/bin/env python
"""The F(v_e) curve from the Job F1 measurement (working figure).

Reads results/optimisation/fcurve/f_curve.tsv and draws log10 F at a fixed
1 m throat against v_e, one series per family, the static anchors at
v_e = 0.  Campaign palette: ink and grey (the merger paper's gold and the
spinning paper's RGB belong to those papers).

Run (repo root):

    grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/analysis/quantum_budget/plot_f_curve.py
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="ascii") as fh:
        return [{k: (v if k in ("leg", "family") else float(v))
                 for k, v in row.items()}
                for row in csv.DictReader(fh, delimiter="\t")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tsv", default="results/optimisation/fcurve/f_curve.tsv")
    ap.add_argument("--out", default="results/optimisation/figures/f_curve.png")
    args = ap.parse_args()

    rows = read_rows(Path(args.tsv))
    fig, ax = plt.subplots(figsize=(5.2, 3.4), constrained_layout=True)
    series = {
        "a": dict(color="black", marker="o", ms=3.0, lw=0.0,
                  label="family (a), $\\gamma = -\\pi$"),
        "b": dict(color="0.55", marker="s", ms=3.0, lw=0.0,
                  label="family (b), $\\gamma = 0$"),
    }
    for fam, style in series.items():
        pts = sorted(((r["v_e"], r["log10_F_1m"]) for r in rows
                      if r["family"] == fam and r["leg"] != "static"))
        if pts:
            ax.plot(*zip(*pts), **style)
    for r in rows:
        if r["leg"] == "static":
            ax.plot([0.0], [r["log10_F_1m"]], marker="D", ms=5,
                    color=series[r["family"]]["color"], lw=0,
                    label=f"static anchor ({r['family']})")
    ax.set_xlabel("$v_e$ (throat equatorial speed)")
    ax.set_ylabel("$\\log_{10} F$ at $R_{\\rm eq} = 1\\,$m")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2,
              frameon=False, fontsize=8)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
