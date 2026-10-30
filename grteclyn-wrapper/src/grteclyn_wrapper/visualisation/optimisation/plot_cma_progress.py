#!/usr/bin/env python3
r"""Campaign M: CMA-ES exoticity against evaluation number.

Muted trial points show the search history; the blue step is the lowest
constraint-accepted X so far. A zoom of the final half of the search makes
late improvements visible without fitting an assumed convergence law.
Acceptance here refers only to the stored background-constraint gate,
not to physical stability or finer-grid validation.

Reads a search TSV from ``optimize_potential.py`` (row order is the
evaluation order).  Default: the packed D51 drainhole search.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_cma_progress
    ... plot_cma_progress --tsv <path>

Writes ``results/optimisation/figures/cma_progress_d51`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.lines as mlines  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import AutoMinorLocator, MultipleLocator  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[5]
PACKED = REPO / "results" / "optimisation" / "opt"
RUNS = REPO / "runs" / "optimisation" / "opt"
OUT = REPO / "results" / "optimisation" / "figures" / "cma_progress_d51"
DEFAULT_TSV = "fam_a_r1_0012_opt4s_150x30.tsv"
GATED = ("PASS", "FRONTIER")
TIGHT = dict(handlelength=1.6, handletextpad=0.4, columnspacing=0.8,
             borderpad=0.45)
# Blue is the optimisation accent; trial points remain neutral.
BLUE, INK, GREY = "#1f77b4", "#666666", "#cccccc"
# Initial and classical X live in the search log, not the TSV.
KNOWN = {
    "fam_a_r1_0012.json": dict(label="D51", x_v0=3.39986493, x_seed=1.72263,
                              q0=(2.4, 2.4, 0.0)),
    "fam_a_r1_0005.json": dict(label="D30", x_v0=4.37565222, x_seed=None,
                              q0=None),
    "fam_a_r1_0000.json": dict(label="D21", x_v0=4.64453314, x_seed=2.44332143,
                              q0=(0.0, 0.0, 0.0)),
}
# Same member JSON as D21; J = 0, so classical X and the kink start differ.
KNOWN_TSV = {
    "fam_a_r1_0000_opt4s_150x30_d0.tsv": dict(
        label="D0", x_v0=4.89835324, x_seed=2.51733602, q0=(0.0, 0.0, 0.0)),
}


def find_tsv(name: str) -> pathlib.Path:
    for root in (PACKED, RUNS):
        path = root / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"no search TSV {name} under {PACKED} or {RUNS}")


def load(path: pathlib.Path) -> tuple[str, list[dict]]:
    with open(path) as fh:
        rows = [{k: v for k, v in row.items()}
                for row in csv.DictReader(
                    (ln for ln in fh if not ln.startswith("#")),
                    delimiter="\t")]
    if not rows:
        raise ValueError(f"{path} has no evaluations")
    member = rows[0]["member"]
    out = []
    for i, row in enumerate(rows, 1):
        try:
            x = float(row["X"])
        except (TypeError, ValueError):
            x = math.nan
        out.append({"n": i, "X": x, "verdict": row.get("verdict", ""),
                    "m": row.get("mass", "")})
    return member, out


def running_best(rows: list[dict], verdicts: tuple[str, ...] | None):
    """Running min of finite X, optionally restricted to ``verdicts``.

    Returns (y at each eval, champion row or None).  y is nan until the
    first accepted point.
    """
    best, champ, ys = math.inf, None, []
    for row in rows:
        ok = math.isfinite(row["X"]) and (
            verdicts is None or row["verdict"] in verdicts)
        if ok and row["X"] < best:
            best, champ = row["X"], row
        ys.append(best if best < math.inf else math.nan)
    return np.asarray(ys, float), champ


def draw(rows, champ, y_best) -> object:
    style.prd(8.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.15), layout="constrained")
    n = np.array([r["n"] for r in rows], float)
    x = np.array([r["X"] for r in rows], float)
    above = np.array([r["verdict"] == "ABOVE-GATE" and math.isfinite(r["X"])
                      for r in rows])
    gated = np.array([r["verdict"] in GATED and math.isfinite(r["X"])
                      for r in rows])
    best = dict(color=BLUE, lw=1.35)

    def dots(color, ms):
        return dict(ls="none", marker="o", ms=ms, mfc=color, mec="none")

    def traces(axis):
        axis.plot(n[above], x[above], zorder=1, **dots(GREY, 1.7))
        axis.plot(n[gated], x[gated], zorder=2, **dots(INK, 1.9))
        axis.plot(n, y_best, ds="steps-post", zorder=3, **best)
        if champ is not None:
            axis.plot(champ["n"], champ["X"], ls="none", marker="s",
                      ms=4.0, mfc=BLUE, mec="white", mew=0.5, zorder=4)

    traces(ax)
    finite = x[above | gated]
    ylo, yhi = finite.min(), finite.max()
    pad = max(0.06 * (yhi - ylo), 0.005)
    end = 50.0 * math.ceil(n[-1] / 50.0)
    ax.set(xlim=(0, end), ylim=(ylo - pad, yhi + pad),
           xlabel=r"CMA-ES evaluation $n$")
    ax.set_ylabel(r"$X$", rotation=0, labelpad=6.0)
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))

    def key(fmt, label):
        return mlines.Line2D([], [], **fmt), label

    entries = [key(dots(INK, 2.4), "within gate"),
               key(dots(GREY, 2.4), "above gate"),
               key(best, "best so far")]
    style.legend_top(ax, entries, ncol=3, fontsize=7.2,
                     labelspacing=0.25, **TIGHT)

    # Use the empty upper-right region to resolve the late-search plateau.
    late = (n >= end / 2) & (above | gated)
    if np.any(late):
        zoom = ax.inset_axes([0.53, 0.47, 0.44, 0.43])
        traces(zoom)
        tail = np.concatenate((x[late], y_best[late]))
        tail = tail[np.isfinite(tail)]
        lo, hi = tail.min(), tail.max()
        padding = max(0.12 * (hi - lo), 0.002)
        zoom.set(xlim=(end / 2, end), ylim=(lo - padding, hi + padding))
        zoom.set_title("Late search", fontsize=7, pad=3)
        zoom.tick_params(axis="both", which="both", labelsize=6.5,
                         top=False, right=False)
        zoom.xaxis.set_major_locator(MultipleLocator(100))
        zoom.xaxis.set_minor_locator(AutoMinorLocator(2))
        zoom.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3))
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tsv", type=pathlib.Path, default=None,
                    help="search TSV (default: packed D51 CMA-ES)")
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--label", default=None)
    ap.add_argument("--x-v0", type=float, default=None,
                    help="classical V = 0 bill (summary only; omit to take the "
                         "member's known value)")
    ap.add_argument("--x-seed", type=float, default=None,
                    help="X of the initial potential; omit to take the "
                         "member's known start")
    args = ap.parse_args(argv)
    path = args.tsv or find_tsv(DEFAULT_TSV)
    if not path.is_file():
        path = find_tsv(path.name)
    member, rows = load(path)
    known = KNOWN_TSV.get(path.name) or KNOWN.get(member, {})
    label = args.label or known.get("label") or pathlib.Path(member).stem
    x_v0 = args.x_v0 if args.x_v0 is not None else known.get("x_v0")
    x_seed = args.x_seed if args.x_seed is not None else known.get("x_seed")
    if args.out == OUT and known.get("label"):
        args.out = OUT.with_name(f"cma_progress_{known['label'].lower()}")
    y_best, champ = running_best(rows, GATED)
    fig = draw(rows, champ, y_best)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    plt.close(fig)
    n_fail = sum(1 for r in rows if not math.isfinite(r["X"]))
    print(f"{label}: {len(rows)} evaluations, {n_fail} Newton-failed")
    if champ is not None:
        vs = []
        if x_seed is not None:
            vs.append(f"{100.0 * (champ['X'] / x_seed - 1.0):+.1f} % vs start")
        if x_v0 is not None:
            vs.append(f"{100.0 * (champ['X'] / x_v0 - 1.0):+.1f} % vs V = 0")
        extra = f" ({', '.join(vs)})" if vs else ""
        print(f"champion eval {champ['n']}: X {champ['X']:.8f}  "
              f"{champ['verdict']}{extra}")
    print(f"label audit: {'clean' if not problems else problems}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
