#!/usr/bin/env python3
r"""Campaign M: CMA-ES exoticity against evaluation number.

One panel, spinning-paper colours (C0 red / C2 blue / ink / grey).
Grey dots have an unused-constraint residual (E19 or $E_c$) above
$10^{-6}$; they can sit below the accepted minimum and still not
count.  The blue curve is an exponential fit through that cloud.
Red dots have residual $\le 10^{-6}$; the ink step is the lowest
accepted $X$ so far; the square marks that minimum.  A dashed rule
is $X$ of the starting potential (the pure kink $q = 0$, or an
earlier scan's best clean point).  The frame is the
CMA window (classical $V = 0$ sits well above it).  The right
axis is $(X_{\rm cl} - X)/X_{\rm cl}$ relative to that bill.

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
C0, C2, INK, GREY, SEED = "#d62728", "#1f77b4", "#1a1a18", "#c8c6c0", "#8a8a86"
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
    fig, ax = plt.subplots(figsize=(3.55, 2.35), layout="constrained")
    n = np.array([r["n"] for r in rows], float)
    x = np.array([r["X"] for r in rows], float)
    above = np.array([r["verdict"] == "ABOVE-GATE" and math.isfinite(r["X"])
                      for r in rows])
    gated = np.array([r["verdict"] in GATED and math.isfinite(r["X"])
                      for r in rows])
    ax.plot(n[above], x[above], ls="none", marker="o", ms=1.6,
            mfc=GREY, mec="none", zorder=2, clip_on=False)
    trend = above_trend(n[above], x[above]) if np.any(above) else None
    if trend is not None:
        f, popt = trend
        tt = np.linspace(n[0], n[-1], 400)
        ax.plot(tt, f(tt, *popt), color=C2, lw=1.3, zorder=3)
    ax.plot(n[gated], x[gated], ls="none", marker="o", ms=2.6,
            mfc=C0, mec="none", zorder=4, clip_on=False)
    ax.plot(n, y_best, color=INK, lw=1.25, ds="steps-post", zorder=3)
    if x_seed is not None:
        ax.axhline(x_seed, color=SEED, lw=0.8, ls=(0, (3.0, 1.6)),
                   zorder=1)
    if champ is not None:
        ax.plot(champ["n"], champ["X"], ls="none", marker="s", ms=5.5,
                mfc=C0, mec=INK, mew=0.4, zorder=5, clip_on=False)
    finite = x[np.isfinite(x)]
    ylo = finite.min()
    yhi = finite.max()
    if x_seed is not None:
        ylo, yhi = min(ylo, x_seed), max(yhi, x_seed)
    pad = 0.06 * (yhi - ylo)
    ax.set(xlim=(0.0, float(n[-1]) + 0.5), ylim=(ylo - pad, yhi + pad),
           xlabel="CMA-ES evaluation",
           ylabel=r"$X = |{\rm VIQ}|/R_e$")
    if x_v0 is not None:
        ax.tick_params(axis="y", which="both", right=False)
        ax2 = ax.twinx()
        y0, y1 = ax.get_ylim()
        ax2.set_ylim(100.0 * (1.0 - y0 / x_v0), 100.0 * (1.0 - y1 / x_v0))
        ax2.set_ylabel(
            rf"$(X_{{\rm cl}} - X)/X_{{\rm cl}}$ [%], "
            rf"$V = 0$, $X_{{\rm cl}} = {x_v0:.2f}$")
        ax2.minorticks_on()
    entries = [
        (mlines.Line2D([], [], ls="none", marker="o", ms=1.8,
                       mfc=GREY, mec="none"), "rejected"),
        (mlines.Line2D([], [], ls="none", marker="o", ms=2.6,
                       mfc=C0, mec="none"), "accepted"),
        (mlines.Line2D([], [], color=C2, lw=1.3), "fit") if trend is not None
        else None,
        (mlines.Line2D([], [], color=INK, lw=1.25), "lowest accepted"),
    ]
    if champ is not None:
        entries.append(
            (mlines.Line2D([], [], ls="none", marker="s", ms=5.5,
                           mfc=C0, mec=INK, mew=0.4),
             f"minimum, $X={champ['X']:.3f}$"))
    if x_seed is not None:
        qlab = (r"$q=(%g,%g,%g)$" % tuple(q0) if q0 is not None
                else r"starting $X$")
        entries.append(
            (mlines.Line2D([], [], color=SEED, lw=0.8,
                           ls=(0, (3.0, 1.6))), qlab))
    entries = [e for e in entries if e is not None]
    style.legend_top(ax, entries, ncol=3, **TIGHT)
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
