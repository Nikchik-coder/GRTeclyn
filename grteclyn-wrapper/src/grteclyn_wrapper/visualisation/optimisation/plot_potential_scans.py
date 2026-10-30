#!/usr/bin/env python3
r"""Parameter coverage and progress of the fixed-R_e, fixed-J CMA-ES searches.

Rows separate the drainhole and symmetric families. The first two columns
project the four potential parameters into (q1, q2) and (mass, q3); colour
encodes recorded evaluation order. Every logged proposal is shown, including
failed solves. Diamonds mark each run's lowest finite X within the stored
background-constraint ceiling (PASS or FRONTIER, max(E19, E_c) <= 1e-6).
The last column tracks that running minimum relative to the first qualifying
candidate in the same run. These are search diagnostics, not stability or
finer-grid clearance. No response surface is interpolated between proposals.

Only tracked data are read. The explicit input list selects the latest
completed fixed-size, fixed-spin run for each model as of 2026-10-30;
area/free-spin experiments and stationary extension trials are separate.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_potential_scans
"""

from __future__ import annotations

import argparse
import csv
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from grteclyn_wrapper.visualisation.wormhole_merger import style

REPO = pathlib.Path(__file__).resolve().parents[5]
OPT = REPO / "results" / "optimisation" / "opt"
OUT = REPO / "results" / "optimisation" / "figures" / "potential_scans"
# Explicit provenance: no glob can silently substitute an older search.
SEARCHES = (
    ("Drainhole", "D0", "fam_a_r1_0000_opt4s_150x30_d0.tsv"),
    ("Drainhole", "D21", "fam_a_r1_0000_opt4s_150x30_kink.tsv"),
    ("Drainhole", "D30", "fam_a_r1_0005_opt4s_kink_150x30.tsv"),
    ("Drainhole", "D51", "fam_a_r1_0012_opt4s_150x30.tsv"),
    ("Drainhole", "D80", "fam_a_r1_0023_opt4s_kink_150x30.tsv"),
    ("Drainhole", "D90", "fam_a_r1_0031_opt4s_kink_150x30.tsv"),
    ("Symmetric", "S0", "fam_b_0000_opt4s_kink_150x30_s0.tsv"),
    ("Symmetric", "S27", "fam_b_0003_opt4s_150x30.tsv"),
    ("Symmetric", "S50", "fam_b_0012_opt4s_150x30.tsv"),
    ("Symmetric", "S85", "fam_b_0025_opt4s_150x30.tsv"),
)
PARAMS = ("mass", "q1", "q2", "q3")
GATED = ("PASS", "FRONTIER")
# Line style remains an independent channel when printed in greyscale.
CURVES = (
    ("#292929", "-"), ("#1f77b4", "-"), ("#79b9dd", "--"),
    ("#4c667b", ":"), ("#777777", "-."), ("#35566e", (0, (5, 2, 1, 2))),
)


def load_search(family, label, name):
    with (OPT / name).open() as fh:
        rows = list(csv.DictReader((s for s in fh if not s.startswith("#")),
                                   delimiter="\t"))
    if not rows:
        raise ValueError(f"{name}: empty search trace")
    params = np.array([[float(r[k]) for k in PARAMS] for r in rows])
    x = np.array([float(r["X"]) for r in rows])
    keep = np.array([r["verdict"] in GATED for r in rows]) & np.isfinite(x)
    if not keep.any():
        raise ValueError(f"{name}: no candidate within the search gate")
    # Read the recorded categories, and check their numerical meaning too.
    monitors = np.array([[float(r[k]) for k in ("E19", "E_c")] for r in rows])
    if not np.all(np.isfinite(monitors[keep])) or np.any(monitors[keep] > 1.001e-6):
        raise ValueError(f"{name}: stored acceptance disagrees with constraints")
    best = np.minimum.accumulate(np.where(keep, x, np.inf))
    best[~np.isfinite(best)] = np.nan
    first = np.flatnonzero(keep)[0]
    champion = int(np.argmin(np.where(keep, x, np.inf)))
    return dict(family=family, label=label, source=name, params=params,
                n=np.arange(1, len(rows) + 1), x=x, keep=keep,
                best=best, relative=best / x[first], champion=champion)


def draw(searches):
    style.prd(8.0)
    fig = plt.figure(figsize=(7.05, 3.85), layout="constrained")
    grid = fig.add_gridspec(2, 4, width_ratios=(1, 1, 1.15, 0.055))
    axes = np.array([[fig.add_subplot(grid[i, j]) for j in range(3)]
                     for i in range(2)])
    cax = fig.add_subplot(grid[:, 3])
    cmap = ListedColormap(plt.get_cmap("Blues")(np.linspace(0.22, 0.95, 256)))
    norm = Normalize(1, 400)
    progress_floor = 0.05 * np.floor(min(np.nanmin(s["relative"])
                                        for s in searches) / 0.05) - 0.025
    diamond = dict(marker="D", ls="none", ms=4.0, mfc="white",
                   mec="#222222", mew=0.7, zorder=5)
    for row, family in enumerate(("Drainhole", "Symmetric")):
        group = [s for s in searches if s["family"] == family]
        # Sort by evaluation so late proposals are visible across all runs.
        params = np.concatenate([s["params"] for s in group])
        n = np.concatenate([s["n"] for s in group])
        order = np.argsort(n, kind="stable")
        for col, (ix, iy) in enumerate(((1, 2), (0, 3))):
            ax = axes[row, col]
            xy = params[order][:, [ix, iy]]
            finite = np.isfinite(xy).all(axis=1)
            ax.scatter(*xy[finite].T, c=n[order][finite], norm=norm, cmap=cmap,
                       s=4.2, linewidths=0, alpha=0.65, rasterized=True)
            for s in group:
                point = s["params"][s["champion"]]
                ax.plot(point[ix], point[iy], **diamond)
            ax.set_xlabel((r"$q_1$", r"$m$")[col])
            ax.set_ylabel((r"$q_2$", r"$q_3$ (symlog)")[col], labelpad=2)
            ax.xaxis.set_major_locator(MaxNLocator(4))
            ax.yaxis.set_major_locator(MaxNLocator(4))
            ax.margins(0.07)
            # D51 explores much larger q3 than the other runs; show every
            # proposal on a declared symmetric-log scale, with a linear core.
            if col == 1:
                ax.set_yscale("symlog", linthresh=1.0, linscale=0.7)
                ax.set_yticks([-4, -1, 0, 1, 4, 16] if row == 0
                             else [-4, -1, 0, 1, 4])
                ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.set_title(f"({chr(97 + row * 3 + col)}) {family}",
                         loc="left", fontsize=8, pad=5)
        ax = axes[row, 2]
        entries = []
        for s, (colour, dash) in zip(group, CURVES):
            ln, = ax.plot(s["n"], s["relative"], drawstyle="steps-post",
                          color=colour, ls=dash, lw=1.1)
            entries.append((ln, s["label"]))
        ax.set(xlim=(0, 400), ylim=(progress_floor, 1.025),
               xlabel="Recorded evaluation", ylabel=r"$X_{\rm best}/X_{\rm first}$")
        ax.set_xticks([0, 200, 400])
        ax.set_yticks([0.6, 0.8, 1.0])
        style.legend_top(ax, entries, ncol=3, fontsize=6.8,
                         handlelength=1.5, handletextpad=0.3, columnspacing=0.7,
                         labelspacing=0.25, borderpad=0.2)
    colourbar = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
    colourbar.set_label("Recorded evaluation", labelpad=5)
    colourbar.set_ticks([1, 100, 200, 300, 400])
    fig.legend([Line2D([], [], ls="none", marker="o", ms=3,
                       mfc="#6baed6", mec="none"), Line2D([], [], **diamond)],
               ["recorded proposal", r"lowest $X$ below constraint threshold"],
               loc="outside upper center", ncol=2, frameon=False, fontsize=7.5,
               handlelength=1.0, columnspacing=2)
    style.tag_keys(fig, axes[:, 2], ["(c)", "(f)"], fontsize=8)
    return fig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    args = ap.parse_args(argv)
    searches = [load_search(*spec) for spec in SEARCHES]
    fig = draw(searches)
    problems = style.label_audit(fig)
    output = style.save(fig, args.out)
    plt.close(fig)
    for s in searches:
        k = s["champion"]
        print(f"{s['label']}: {len(s['n'])} recorded, {s['keep'].sum()} within gate; "
              f"best X={s['x'][k]:.8f} at record {s['n'][k]}")
    print(f"label audit: {'clean' if not problems else problems}")
    print(f"wrote {output}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
