#!/usr/bin/env python3
"""Overlay one Weyl4 mode of several runs at every extraction sphere, and
tabulate every pairwise difference -- the seam check for restarted runs.

Usage:
  python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_modes \\
      [--runs-root DIR] [--source data|pack] [--mode 20] [--radii 10 14 18] \\
      [--restart T] [--speed 0.94] [--windows 45:60 60:80 80:100] \\
      [--peak-ref RUN] [--title STR] [--out FILE] RUN[=LABEL] [RUN[=LABEL] ...]

  The FIRST run is the subject: drawn thick and on top, its extrema annotated.
  --source data  reads <runs-root>/<run>/data/Weyl4_mode_<mode>.dat, the every-
                 step stream the code writes while it runs (default);
  --source pack  reads <repo>/results/merger/campaign/<run>/Weyl4_mode_<mode>.dat
                 (thinned to dt = 0.05, what git keeps).
  --radii        extraction spheres, in the column order of the file (time, then
                 Re/Im per sphere); a 'r = ...' header, when present, overrides.
  --restart T    the seam: a black dotted line at T and a red dotted line at
                 T + R/speed on each panel (earliest arrival of anything the
                 restart changed, at --speed c).
  --windows      time windows for the pairwise table (lo:hi; 'end' allowed).
  --peak-ref     the run whose peak |r psi4| after the junk band (t > R + 8)
                 normalises the table (default: the first run).

Plotted quantity: Re(r * psi4) of the mode, the file holding raw psi4.
Comparisons are time-aligned on rounded times (np.intersect1d), never by row.

Example (2026-09-10, the head-on down-step against the level-5 arm it came from):
  python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_modes --restart 35 \\
      merge_headon_flip_d8_v1_lvl3down_t100_r03500="level-3 down-step from t = 35" \\
      merge_headon_flip_d8_v1_lvl5_t100_r02200="level-5 arm from t = 22" \\
      merge_headon_flip_d8_v1c_latefreeze_t100="V1c late-freeze, never restarted"
"""

from __future__ import annotations

import argparse
import itertools
import pathlib
import re

import matplotlib
import numpy as np

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_run

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

# …/GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger
REPO = pathlib.Path(__file__).resolve().parents[5]
JUNK_BAND = (-4.0, 8.0)   # initial-data junk from the mouths reaches sphere R in t = R-4 .. R+8


def load_mode(path: pathlib.Path, radii: list[float]) -> tuple[np.ndarray, list[float]]:
    """Return (rows, radii).  Rows: time, Re, Im per sphere.  Tolerates a header
    and a torn last line (the file may still be written)."""
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                if "r =" in line:
                    vals = [float(x) for x in re.findall(r"[\d.eE+-]+", line)]
                    radii = vals[::2]
                continue
            p = line.split()
            if len(p) < 1 + 2 * len(radii):
                continue
            try:
                rows.append([float(x) for x in p[: 1 + 2 * len(radii)]])
            except ValueError:
                continue
    if not rows:
        raise SystemExit(f"no rows in {path}")
    return np.array(rows), radii


def aligned(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ta, tb = np.round(a[:, 0], 3), np.round(b[:, 0], 3)
    t, ia, ib = np.intersect1d(ta, tb, return_indices=True)
    return t, a[ia], b[ib]


def parse_window(s: str, t_end: float) -> tuple[float, float]:
    lo, hi = s.split(":")
    return float(lo), (t_end if hi == "end" else float(hi))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-root", default=str(REPO / "runs" / "wormhole_merger"))
    ap.add_argument("--pack-root", default=str(REPO / "results" / "merger" / "campaign"))
    ap.add_argument("--source", choices=["data", "pack"], default="data")
    ap.add_argument("--mode", default="20", help="lm of the mode file, e.g. 20, 22, 2-2")
    ap.add_argument("--radii", type=float, nargs="+", default=[10.0, 14.0, 18.0])
    ap.add_argument("--restart", type=float, default=None, help="seam time to mark")
    ap.add_argument("--speed", type=float, default=0.94, help="signal speed for the arrival line")
    ap.add_argument("--windows", nargs="+", default=["45:60", "60:80", "80:end", "45:end"])
    ap.add_argument("--peak-ref", default=None)
    ap.add_argument("--annotate-after", type=float, default=None,
                    help="annotate the subject's extrema after this time (default: restart, else R+8)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--out", default=None, help="figure path (default: <subject>/frames/psi4_<mode>_compare.png)")
    ap.add_argument("runs", nargs="+", metavar="RUN[=LABEL]")
    args = ap.parse_args(argv)

    names, labels = [], {}
    for item in args.runs:
        name, _, label = item.partition("=")
        name = name.rstrip("/")
        names.append(name)
        labels[name] = label or name
    root = pathlib.Path(args.runs_root if args.source == "data" else args.pack_root).expanduser().resolve()
    data, radii = {}, list(args.radii)
    run_dirs = {n: find_run(root, n) for n in names}   # by name, wherever filed
    for n in names:
        p = run_dirs[n] / ("data" if args.source == "data" else "") / f"Weyl4_mode_{args.mode}.dat"
        data[n], radii = load_mode(p, radii)
    subject = names[0]
    ref = args.peak_ref or subject
    t_end = min(data[n][-1, 0] for n in names)   # common end of the overlap
    for n in names:
        print(f"{labels[n]:<52s} t = {data[n][0, 0]:.2f} .. {data[n][-1, 0]:.2f}")

    # ---- figure ----------------------------------------------------------
    style.paper(base=10.0)
    # "20" -> "2,0", "2-2" -> "2,-2": the superscript is (l, m), and printing it
    # as a bare pair of digits reads as the number twenty.
    mode_lm = f"{args.mode[0]},{args.mode[1:]}"
    # The subject is slot 0 (ink, solid) and is drawn last, on top; the arms it
    # is compared with follow in the fixed order.
    kws = style.family(len(names), lw=None)
    fig, axs = plt.subplots(len(radii), 1, figsize=(8.6, 2.5 * len(radii)), sharex=True, squeeze=False)
    axs = axs[:, 0]
    t_max = max(data[n][-1, 0] for n in names)
    for k, R in enumerate(radii):
        ax, col = axs[k], 1 + 2 * k
        ax.axvspan(R + JUNK_BAND[0], R + JUNK_BAND[1], color=style.GRID, lw=0, zorder=0)
        for j, n in reversed(list(enumerate(names))):     # subject drawn last, on top
            d = data[n]
            ax.plot(d[:, 0], R * d[:, col], zorder=3 if j == 0 else 2, **kws[j])
        if args.restart is not None:
            ax.axvline(args.restart, color=style.MUTED, ls=(0, (1, 2)), lw=0.9)
            ax.axvline(args.restart + R / args.speed, color=style.BURGUNDY, ls=(0, (1, 2)), lw=0.9)
        # the subject's extrema after the junk band (or the restart)
        after = args.annotate_after if args.annotate_after is not None else (
            args.restart if args.restart is not None else R + JUNK_BAND[1])
        d = data[subject]
        m = d[:, 0] > after
        # Smooth over ~2 code units, not over a fixed 15 samples: from t ~ 85
        # these arms carry a grid-scale wobble of period ~1.5, which a 15-sample
        # (0.75-unit) window leaves untouched, so every wobble crest counted as
        # a swing and the labels landed on top of each other.
        tt = d[m, 0]
        win = max(3, int(round(2.0 / max(np.median(np.diff(tt)), 1e-9))) | 1)
        yy = np.convolve(R * d[m, col], np.ones(win) / win, mode="same")
        # Label the swings, but only the ones worth a label.  The late grid-scale
        # wobble turns every third sample into an extremum, and labelling those
        # printed five overlapping strings on top of each other; require a real
        # amplitude AND a gap set by the span drawn, not a fixed six units.
        gap = max(8.0, 0.12 * (tt[-1] - tt[0])) if len(tt) else 8.0
        big = 0.30 * np.max(np.abs(yy)) if len(yy) else 0.0
        last = -1e9
        for i in range(20, len(yy) - 20):
            if (yy[i] - yy[i - 1]) * (yy[i + 1] - yy[i]) < 0 and abs(yy[i]) > big \
                    and tt[i] - last > gap and tt[i] < tt[-1] - 1.5:
                last = tt[i]
                ax.annotate(f"${yy[i]:+.2f}$ at $t={tt[i]:.0f}$", (tt[i], yy[i]),
                            xytext=(0, -15 if yy[i] > 0 else 9), textcoords="offset points",
                            ha="center", fontsize=8, color=style.MUTED)
        ax.set_ylabel(rf"$r\,\mathrm{{Re}}\,\Psi_4^{{{mode_lm}}}$" "\n" rf"$R={R:g}$")
        ax.set_xlim(0, np.ceil(t_max / 5) * 5 + 1)
        ax.margins(y=0.25)
    # Legend in RUN order -- the curves are drawn back to front so the subject
    # ends on top, and left to itself the key comes out upside down, naming the
    # least important arm first.
    handles = [plt.Line2D([], [], **kws[j]) for j in range(len(names))]
    axs[0].legend(handles, [labels[n] for n in names], loc="upper left")
    axs[-1].set_xlabel(r"$t$")
    title = args.title or (rf"$r\,\mathrm{{Re}}\,\Psi_4^{{{mode_lm}}}$ at "
                           f"$R={' / '.join(f'{R:g}' for R in radii)}$"
                           f"   —   {labels[subject]}")
    fig.suptitle(title, y=0.995)
    sub = "grey band: initial-data junk from the mouths"
    if args.restart is not None:
        sub += (f";  dotted: the restart at $t={args.restart:g}$;  red dotted: the earliest "
                f"arrival of anything it changed, at ${args.speed:g}\\,c$")
    axs[0].set_title(sub, fontsize=8.5, color=style.MUTED, pad=4, loc="left")
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    out = pathlib.Path(args.out).expanduser() if args.out else \
        run_dirs[subject] / "frames" / f"psi4_{args.mode}_compare.png"
    print("wrote", style.save(fig, out))

    # ---- pairwise table ----------------------------------------------------
    if len(names) < 2:
        return 0
    pairs = list(itertools.combinations(range(len(names)), 2))
    wins = [parse_window(w, t_end) for w in args.windows]
    print(f"\nmax |diff| of Re r.psi4 ({mode_lm}), % of the peak of '{labels[ref]}' after the junk band")
    print("runs: " + "  ".join(f"[{j}] {labels[n]}" for j, n in enumerate(names)))
    print(f"{'window':>13s}  R  " + "  ".join(f"[{a}]-[{b}]" for a, b in pairs) + "   peak")
    for k, R in enumerate(radii):
        col = 1 + 2 * k
        dr = data[ref]
        peak = np.max(np.abs(R * dr[dr[:, 0] > R + JUNK_BAND[1], col]))
        for lo, hi in wins:
            cells = []
            for a, b in pairs:
                t, A, B = aligned(data[names[a]], data[names[b]])
                m = (t >= lo) & (t <= hi)
                cells.append("    n/a" if m.sum() < 5 else
                             f"{100 * np.max(np.abs(R * (A[m, col] - B[m, col]))) / peak:7.2f}")
            print(f"{lo:6.1f}-{hi:6.1f} {R:2g}  " + "  ".join(cells) + f"   {peak:.3f}")
    print("\nmax |Re r.psi4| per window, per run:")
    for k, R in enumerate(radii):
        col = 1 + 2 * k
        for lo, hi in wins:
            amps = []
            for n in names:
                d = data[n]
                m = (d[:, 0] >= lo) & (d[:, 0] <= hi)
                amps.append("   n/a" if m.sum() < 5 else f"{np.max(np.abs(R * d[m, col])):.4f}")
            print(f"R = {R:2g} {lo:6.1f}-{hi:6.1f}  " + " / ".join(amps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
