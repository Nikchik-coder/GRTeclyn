#!/usr/bin/env python3
r"""The refinement ladder of the p = 0.12 spiral: the wall does not move.

The article's Fig. for sec:spiral:wall.  Every arm restarts the p = 0.12,
d = 12 orbital merger from the SAME t = 50 checkpoint and raises max_level;
every one dies on an h11 NaN.  The gains saturate: +1.03, +2.51, +0.53,
+0.06 units per doubling in the plain family -- sixteen times the resolution
buys 4.13 units and never reaches the merger's end -- and the half-time-step
control gains +0.36 on its own level-5 twin, most of the size of the
level 5 -> 6 spatial gain, so the top of the ladder is saturation evidence,
not a converged limit.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_ladder

Reads ``campaign/05_binary_spiral/refinement_ladder.dat`` (level, cell,
family, dt_mult, t_death, run -- built from the run logs; the plain and
damped families are different physical treatments and are never averaged).
The FAINT reference line is the paper chain's escape hatch, drawn for scale:
restarted three times EARLIER (t = 36) on a doubled base grid, the level-5
production arm still dies, at t = 60.445 (Fig. spiral_collapse).

STYLE: seed-branches grammar, single column (3.4 x 2.6); families named in
place; no accent -- there is no horizon instrument on this figure, and no
horizon at any death.
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
    PACK_ROOT, figure_dir,
)

GROUP = "05_binary_spiral"
T_PAPER_ARM = 60.445    # v2 L = 128 level-5 arm from t = 36 (its README)


def _read_ladder(path: pathlib.Path):
    rows = []
    for ln in path.read_text().splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        lvl, _cell, fam, dt, t_death, run = s.split()
        rows.append((int(lvl), fam, float(dt), float(t_death), run))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    rows = _read_ladder(pack / "campaign" / GROUP / "refinement_ladder.dat")

    plain = sorted((r[0], r[3]) for r in rows if r[1] == "plain" and r[2] == 0.02)
    damped = sorted((r[0], r[3]) for r in rows if r[1] == "damped")
    half = [(r[0], r[3]) for r in rows if r[2] == 0.01]

    print("[spiral ladder] plain:", ", ".join(f"L{l} {t:.2f}" for l, t in plain))
    print("[spiral ladder] damped:", ", ".join(f"L{l} {t:.2f}" for l, t in damped))
    gains = [plain[i + 1][1] - plain[i][1] for i in range(len(plain) - 1)]
    print("[spiral ladder] plain gains per doubling:",
          ", ".join(f"{g:+.2f}" for g in gains),
          f"; halfstep vs its twin {half[0][1] - dict(plain)[half[0][0]]:+.2f}"
          if half else "")

    style.prd(base=10.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.65), constrained_layout=True)

    lp, tp = zip(*plain)
    ld, td = zip(*damped)
    ax.plot(lp, tp, color=style.INK, lw=1.1, marker="o", ms=4.0,
            mfc=style.INK, mec=style.INK, zorder=4)
    ax.plot(ld, td, color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)), marker="o",
            ms=3.6, mfc=style.GROUND, mec=style.MUTED, zorder=3)
    if half:
        ax.plot([half[0][0]], [half[0][1]], ls="none", marker="D", ms=4.0,
                mfc=style.GROUND, mec=style.INK, mew=1.0, zorder=5)
        ax.annotate(r"$\mathrm{d}t/2$", (half[0][0], half[0][1]),
                    xytext=(4.62, half[0][1] + 0.02), fontsize=7.5,
                    color=style.INK, va="center", ha="right")

    for i, g in enumerate(gains):
        ax.text(0.5 * (lp[i] + lp[i + 1]), 0.5 * (tp[i] + tp[i + 1]) + 0.42,
                f"$+{g:.2f}$", fontsize=7, ha="center", va="bottom",
                color=style.MUTED)

    ax.axhline(T_PAPER_ARM, color=style.FAINT, lw=0.8, zorder=1)
    ax.text(6.95, T_PAPER_ARM - 0.25, "restart at $t=36$, base grid doubled",
            fontsize=7, ha="right", va="top", color=style.MUTED)

    ax.text(6.9, 55.55, "no matter device", fontsize=7.5, ha="right",
            va="top", color=style.INK)
    ax.text(3.55, 54.35, "damped core", fontsize=7.5, ha="left", va="bottom",
            color=style.MUTED)

    ax.set_xlim(2.65, 7.35)
    ax.set_ylim(51.3, 61.6)
    ax.set_xticks([3, 4, 5, 6, 7])
    ax.set_xlabel(r"max level $\ell$ (cell $0.5/2^{\ell}$)")
    ax.set_ylabel(r"$t$ of the $h_{11}$ NaN")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "spiral_refinement_ladder.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[spiral ladder] wrote {png} (+pdf); "
          f"{len(plain)} plain + {len(damped)} damped rungs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
