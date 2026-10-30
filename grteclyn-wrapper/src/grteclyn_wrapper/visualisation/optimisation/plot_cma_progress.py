#!/usr/bin/env python3
r"""Campaign M: CMA-ES exoticity against evaluation number.

One panel at the spinning paper's column width and layout (its
instability figure: 3.4 in, key above in two columns, one axis in two
units) and colours (C0 red / C2 blue / ink / grey).
Grey dots have an unused-constraint residual (E19 or $E_c$) above
$10^{-6}$; they can sit below the accepted minimum and still not
count.  The dashed blue curve is an exponential fit through that
cloud, its formula in the key.
Red dots have residual $\le 10^{-6}$; the ink step is the lowest
accepted $X$ so far; the square marks that minimum.  A faint rule
is $X$ of the starting potential (the pure kink $q = 0$, or an
earlier scan's best clean point).  The frame is the
CMA window (classical $\mathcal{V} = 0$ sits well above it).  The right
edge relabels $X$ as $X/X_{\mathcal{V}=0} - 1$, the paper's $\Delta X$.

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
# Spinning-paper C0 / ink / grey (plot_spin_trends RGB[0], not the
# merger GOLD accent).
C0, C2, INK, GREY = "#d62728", "#1f77b4", "#1a1a18", "#c8c6c0"
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


def above_trend(n: np.ndarray, x: np.ndarray):
    """Exponential floor a + b exp(-c n) through the ABOVE-GATE cloud."""
    if n.size < 8:
        return None
    from scipy.optimize import curve_fit

    def f(t, a, b, c):
        return a + b * np.exp(-np.abs(c) * t)

    try:
        popt, _ = curve_fit(
            f, n, x, p0=(float(np.min(x)), 0.3, 0.02),
            bounds=([0.5, -2.0, 0.0], [3.0, 2.0, 1.0]), maxfev=8000)
    except (RuntimeError, ValueError):
        return None
    return f, popt


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


def draw(rows, champ, y_best, *, x_seed, x_v0, q0) -> object:
    style.prd(8.0)
    # the printed column width, so the 8 pt type prints at 8 pt
    fig, ax = plt.subplots(figsize=(3.4, 2.3), layout="constrained")
    n = np.array([r["n"] for r in rows], float)
    x = np.array([r["X"] for r in rows], float)
    above = np.array([r["verdict"] == "ABOVE-GATE" and math.isfinite(r["X"])
                      for r in rows])
    gated = np.array([r["verdict"] in GATED and math.isfinite(r["X"])
                      for r in rows])
    rule = dict(color=style.FAINT, lw=0.6)
    fit = dict(color=C2, lw=1.0, ls=(0, (3.0, 1.6)))
    best = dict(color=INK, lw=1.2)
    square = dict(ls="none", marker="s", ms=4.8, mfc=C0, mec=INK, mew=0.6)

    def dots(color, ms):
        return dict(ls="none", marker="o", ms=ms, mfc=color, mec="none")

    if x_seed is not None:
        ax.axhline(x_seed, zorder=0, **rule)
    ax.plot(n[above], x[above], zorder=2, clip_on=False, **dots(GREY, 1.6))
    trend = above_trend(n[above], x[above]) if np.any(above) else None
    if trend is not None:
        f, popt = trend
        tt = np.linspace(n[0], n[-1], 400)
        ax.plot(tt, f(tt, *popt), zorder=3, **fit)
    ax.plot(n[gated], x[gated], zorder=4, clip_on=False, **dots(C0, 2.6))
    ax.plot(n, y_best, ds="steps-post", zorder=3, **best)
    if champ is not None:
        ax.plot(champ["n"], champ["X"], zorder=5, clip_on=False, **square)
    finite = x[np.isfinite(x)]
    ylo = finite.min()
    yhi = finite.max()
    if x_seed is not None:
        ylo, yhi = min(ylo, x_seed), max(yhi, x_seed)
    pad = 0.06 * (yhi - ylo)
    # the search budget's round end, so every search shares the x ticks
    ax.set(xlim=(0.0, 50.0 * math.ceil(n[-1] / 50.0)),
           ylim=(ylo - pad, yhi + pad), xlabel=r"CMA-ES evaluation $n$")
    ax.set_ylabel(r"$X$", rotation=0, labelpad=6.0)
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    if x_v0 is not None:
        # the same scale relabelled against the massless phantom on the
        # right edge, which is that axis's alone
        ax.tick_params(axis="y", which="both", right=False)
        right = ax.secondary_yaxis(
            "right", functions=(lambda y: 100.0 * (y / x_v0 - 1.0),
                                lambda d: x_v0 * (1.0 + d / 100.0)))
        right.set_ylabel(r"$X/X_{\mathcal{V}=0}-1$ [%]")
        right.minorticks_on()

    def key(fmt, label):
        return mlines.Line2D([], [], **fmt), label

    # read row by row: the markers on the left, the lines on the right
    entries = [key(dots(GREY, 1.8), "rejected")]
    if trend is not None:
        a, b, c = popt
        entries.append(key(fit, rf"fit, ${a:.2f}+{b:.2f}\,e^{{-n/{1.0 / c:.0f}}}$"))
    entries += [key(dots(C0, 2.6), "accepted"), key(best, "lowest accepted")]
    if champ is not None:
        entries.append(key(square, rf"minimum, $X={champ['X']:.3f}$"))
    if x_seed is not None:
        start = ("start" if q0 is None else r"start, $q_i=0$" if not any(q0)
                 else r"start, $q=(%g,%g,%g)$" % tuple(q0))
        entries.append(key(rule, start))
    style.legend_top(ax, entries, ncol=2, labelspacing=0.45, **TIGHT)
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tsv", type=pathlib.Path, default=None,
                    help="search TSV (default: packed D51 CMA-ES)")
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--label", default=None)
    ap.add_argument("--x-v0", type=float, default=None,
                    help="classical V = 0 bill (drawn; omit to take the "
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
    q0 = known.get("q0")
    if args.out == OUT and known.get("label"):
        args.out = OUT.with_name(f"cma_progress_{known['label'].lower()}")
    y_best, champ = running_best(rows, GATED)
    if champ is None:
        y_best, champ = running_best(rows, None)
    fig = draw(rows, champ, y_best, x_seed=x_seed, x_v0=x_v0, q0=q0)
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
