#!/usr/bin/env python3
r"""Separation and throat monitors of one binary arm: does it merge or fly by?

Two panels on one time axis: the tracked separation of the two throats above,
and each throat's own monitor -- the minimum chi in its half-space -- below.
The closest approach is marked, because whether the arm merges or misses is the
one thing the figure exists to say.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_separation \
        --run merge_orbit_flip_d12_p045_t200 --group 06_binary_flyby \
        --name p045_flyby_separation

WHY TWO PANELS AND NOT TWO AXES

The figure this replaces put the separation and min chi on a shared frame with
a second y-axis on the right.  Two scales in one frame make the crossing point
of the curves look like an event; it is an artefact of where the two axes were
put, and moving either one moves it.  Here they are stacked instead, sharing
only the time axis, which is the only thing they genuinely share.

The throat monitor is a compactified-origin quantity and gauge-dependent; it
says whether the well is deepening or relaxing, not what the throat's areal
radius is doing.  That is written on the panel, not left to be inferred.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    figure_dir, find_packed,
)

STREAM = "binary_throat_diagnostics.dat"
# columns of binary_throat_diagnostics.dat, after time
COL = dict(sep=0, xA=1, yA=2, zA=3, chiA=4, lapseA=5,
           xB=6, yB=7, zB=8, chiB=9, lapseB=10)


def read_stream(path: pathlib.Path):
    rows = [ln.split() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]
    if not rows:
        raise SystemExit(f"no rows in {path}")
    a = np.array([[float(x) for x in r] for r in rows])
    return a[:, 0], a[:, 1:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="run name, resolved in the pack")
    ap.add_argument("--group", default="06_binary_flyby")
    ap.add_argument("--name", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--t-max", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    t, c = read_stream(find_packed(args.run, args.pack_root) / STREAM)
    if args.t_max is not None:
        keep = t <= args.t_max
        t, c = t[keep], c[keep]
    sep = c[:, COL["sep"]]
    i_min = int(np.argmin(sep))

    style.paper(base=10.0)
    fig, (ax_s, ax_c) = plt.subplots(2, 1, figsize=(7.4, 5.2), sharex=True,
                                     constrained_layout=True,
                                     height_ratios=(1.25, 1.0))

    ax_s.plot(t, sep, **style.series(0, lw=1.5))
    ax_s.plot(t[i_min], sep[i_min], marker="o", ms=5, color=style.BURGUNDY,
              mec=style.GROUND, mew=0.9, zorder=5)
    ax_s.annotate(rf"closest approach ${sep[i_min]:.2f}$ at $t={t[i_min]:.1f}$",
                  (t[i_min], sep[i_min]), xytext=(10, 10), textcoords="offset points",
                  fontsize=8.5, color=style.BURGUNDY, va="bottom", ha="left")
    ax_s.set_ylabel(r"$d$")
    ax_s.set_title("(a) tracked separation of the two throats", loc="left")

    ax_c.semilogy(t, c[:, COL["chiA"]], label="throat A", **style.series(0, lw=1.3))
    chiB = c[:, COL["chiB"]]
    if np.all(np.isfinite(chiB)) and chiB[0] < 1.0:
        ax_c.semilogy(t, chiB, label="throat B", **style.series(1, lw=1.3))
        ax_c.legend(loc="lower right", ncols=2)
    for ax in (ax_s, ax_c):
        ax.axvline(t[i_min], color=style.FAINT, ls=(0, (2, 3)), lw=0.8, zorder=1)
    ax_c.set_ylabel(r"$\min\chi$")
    ax_c.set_xlabel(r"$t$")
    ax_c.set_title("(b) each throat's own monitor — the minimum $\\chi$ in its half-space "
                   "(gauge-dependent, not an areal radius)", loc="left", fontsize=9)

    if args.title:
        fig.suptitle(args.title)

    stem = args.name or f"{args.run}_separation"
    out = pathlib.Path(args.out) if args.out else figure_dir(args.group, args.pack_root)
    png = style.save(fig, (out / f"{stem}.png") if out.is_dir() else out)
    print(f"[separation] wrote {png} (+pdf); closest approach {sep[i_min]:.3f} "
          f"at t = {t[i_min]:.2f}, stream to t = {t[-1]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
