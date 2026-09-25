#!/usr/bin/env python3
r"""The force law of two like-signed throats at rest: how the push falls with d.

Four like-signed pairs (sigma = +1, a = 2, m = 1) released from rest,
identical but for the gap d = 12/14/16/18 (article Sec. V B).  Each point is
how far the pair has pushed itself apart by the common time t = 11.5 -- the
growth of the separation, delta d, the same quantity the sign-rule panel
draws against time.  Against it: inverse-square in the coordinate separation,
scaled through the d = 12 rung (grey, dashed), and the offset law
A/(d + delta)^2 fitted on d = 12-16 alone (gold), whose value at d = 18 was a
blind prediction (drawn dotted past d = 16).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_force_law

WHY THIS PANEL (2026-09-25, the user's read of Sec. V B: "what are those
numbers, I don't get it -- there should be a figure").  The text quoted the
four displacements and the two predictions with nothing to look at; the
sign-rule panel shows only the d = 12 pairs.  This is the ladder itself.

Reads ``campaign/03_two_throats/separation_ladder_2026-09-04.txt`` (RESULT
table: inverse-chi-weighted pit centroids from the chi_z slice caches, which
are gone -- the table is the record, and the claims ledger reads the same
rows, extract_single._dladder).  Standalone it writes
``figures/03_two_throats/force_law``; the article draws it as panel (c) of the
pair strip (plot_pair_row).

STYLE: the sign-rule grammar -- ink points, the one gold accent for the model
the data pick, the rejected law in context grey, names on the curves.
"""

from __future__ import annotations

import argparse
import pathlib
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "03_two_throats"
LADDER = "separation_ladder_2026-09-04.txt"
FIT_RUNGS = (12.0, 14.0, 16.0)


def ladder(pack_root=PACK_ROOT) -> tuple[np.ndarray, np.ndarray]:
    """(d, delta d at t = 11.5) from the RESULT table."""
    path = pathlib.Path(pack_root).expanduser() / "campaign" / GROUP / LADDER
    block = path.read_text(encoding="utf-8").split("RESULT", 1)[1]
    rows = []
    for line in block.splitlines():
        p = line.split()
        if len(p) >= 3 and re.fullmatch(r"\d+", p[0]) and re.fullmatch(r"\d+\.\d+", p[2]):
            rows.append((float(p[0]), float(p[2])))
        elif rows and not p:
            break
    d, dd = np.array(rows).T
    return d, dd


def offset_fit(d: np.ndarray, dd: np.ndarray) -> tuple[float, float]:
    """(A, delta) of A/(d + delta)^2, least squares on FIT_RUNGS -- the
    ledger's clmOffsetPrediction arithmetic."""
    from scipy.optimize import curve_fit
    m = np.isin(d, FIT_RUNGS)
    (amp, delta), _ = curve_fit(lambda s, A, dl: A / (s + dl) ** 2, d[m], dd[m],
                                p0=(100.0, 3.0))
    return float(amp), float(delta)


def figure_panel(ax, pack_root=PACK_ROOT) -> None:
    """The ladder drawn onto a SUPPLIED axis (style.prd already active; the
    caller owns the letter tag)."""
    d, dd = ladder(pack_root)
    amp, delta = offset_fit(d, dd)
    s = np.linspace(11.6, 18.8, 200)
    inv = dd[d == 12.0][0] * (12.0 / s) ** 2
    ax.plot(s, inv, color=style.CONTEXT, linestyle=(0, (4, 2.2)), linewidth=1.0, zorder=2)
    # Solid over the rungs it was fitted on, dotted where it predicts.
    fit = s <= max(FIT_RUNGS)
    ax.plot(s[fit], amp / (s[fit] + delta) ** 2, color=style.GOLD, linewidth=1.2, zorder=3)
    ax.plot(s[~fit], amp / (s[~fit] + delta) ** 2, color=style.GOLD, linewidth=1.2,
            linestyle=(0, (1.2, 1.5)), zorder=3)
    ax.plot(d, dd, linestyle="none", marker="o", ms=3.4, color=style.INK, zorder=4)
    ax.set_xlim(11, 19)
    ax.set_xticks([12, 14, 16, 18])
    ax.set_ylim(0.18, 0.53)
    ax.set_xlabel(r"$d$")
    ax.set_ylabel(r"$\delta d$ at $t=11.5$")
    # Names on the two laws, where they have parted: gold above the points,
    # the grey rule below them.
    ax.text(15.1, amp / (15.1 + delta) ** 2 + 0.03, r"$(d{+}\delta)^{-2}$",
            fontsize=7.5, color=style.GOLD, ha="left", va="bottom")
    ax.text(16.9, dd[d == 12.0][0] * (12.0 / 16.9) ** 2 - 0.025, r"$d^{-2}$",
            fontsize=7.5, color=style.CONTEXT, ha="right", va="top")
    print(f"[force law] delta d = {dict(zip(d, dd))}; offset fit on {FIT_RUNGS}: "
          f"A = {amp:.1f}, delta = {delta:.2f}, predicts {amp / (18 + delta) ** 2:.3f} "
          f"at d = 18 (inverse square {dd[d == 12.0][0] * (12 / 18) ** 2:.3f}, "
          f"measured {dd[d == 18.0][0]:.4f})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    style.prd(base=10.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.6), constrained_layout=True)
    figure_panel(ax, pack_root=args.pack_root)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "force_law.png")
    style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[force law] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
