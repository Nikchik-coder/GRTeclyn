#!/usr/bin/env python3
r"""The width ladder: how the push of two like-signed throats at rest grows with their width.

Four like-signed pairs (sigma = +1, m = 1) released from rest at d = 12,
identical but for the throat width a = 1/1.5/2/3 (article Sec. V B).  Each
point is how far the pair has pushed itself apart by t = 11.5 -- the
force-law panel's quantity, and the a = 2 point is the same run as that
panel's d = 12 rung.  Against them: the point-charge law, whose net push
(Q - 1) m^2/d^2 is a^2/d^2 at m = 1, scaled through the a = 2 rung (grey,
dashed), and the power law A a^n fitted to the four rungs by least squares
in log-log (gold).  On the log-log axes each law is a straight line whose
slope is its exponent.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_width_ladder

WHY THIS PANEL (2026-10-05, the user: "create the required figure").  Sec.
V B's width sentence left the paper with the superposed campaign that
morning: its a-ladder was superposed, and the matched reruns
(ctrl_rest_a{1,15,3}_csm, 10-02) had never been reduced, because their chi_z
slice caches live only in the run tree.  ``results/merger/analysis/
matched_rest.py`` now reduces them into the packed
``campaign/03_two_throats/matched_rest_displacement.dat`` (dsep_like_a1 /
a15 / a3; a = 2 is dsep_like_d12): at t = 11.5, 0.1623 / 0.3250 / 0.4791 /
0.7583, n = 1.40 (1.21 at t = 8, 1.34 at t = 10; the superposed ladder gave
1.30 at t = 11).  The article draws it as panel (d) of the pair strip
(plot_pair_row); standalone it writes ``figures/03_two_throats/width_ladder``.

STYLE: plot_force_law's grammar -- ink points, the one gold accent for the
law the data pick, the rejected law in context grey, names on the lines.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "03_two_throats"
TABLE = "matched_rest_displacement.dat"
T_LADDER = 11.5
# Throat width -> its like pair's column; a = 2 is the force-law ladder's d = 12 rung.
RUNGS = {1.0: "dsep_like_a1", 1.5: "dsep_like_a15", 2.0: "dsep_like_d12", 3.0: "dsep_like_a3"}


def table(pack_root=PACK_ROOT) -> dict[str, np.ndarray]:
    """The matched rest-pair table, column by header name."""
    path = pathlib.Path(pack_root).expanduser() / "campaign" / GROUP / TABLE
    names = [ln[1:].split() for ln in path.read_text(encoding="utf-8").splitlines()
             if ln.startswith("# time")]
    if not names:
        raise SystemExit(f"{path}: no '# time ...' header")
    data = np.loadtxt(path, ndmin=2)
    return {n: data[:, i] for i, n in enumerate(names[-1])}


def ladder(pack_root=PACK_ROOT, t: float = T_LADDER) -> tuple[np.ndarray, np.ndarray]:
    """(a, delta d at t): each width's column interpolated at t -- the same
    arithmetic as the ledger's single_matched_aladder."""
    tab = table(pack_root)
    missing = [c for c in RUNGS.values() if c not in tab]
    if missing:
        raise SystemExit(f"{TABLE} has no {missing}: run results/merger/analysis/matched_rest.py "
                         "where the run tree is (the slice caches are not packed)")
    a = np.array(sorted(RUNGS))
    return a, np.array([np.interp(t, tab["time"], tab[RUNGS[w]]) for w in a])


def power_fit(a: np.ndarray, dd: np.ndarray) -> tuple[float, float]:
    """(A, n) of A a^n, least squares in log-log over the rungs -- the ledger's
    single_matched_width_exponent arithmetic."""
    n, ln_amp = np.polyfit(np.log(a), np.log(dd), 1)
    return float(np.exp(ln_amp)), float(n)


def figure_panel(ax, pack_root=PACK_ROOT, keys: bool = False) -> None:
    """The ladder drawn onto a SUPPLIED axis (style.prd already active; the
    caller owns the letter tag).  ``keys=True`` names the lines in a key above
    the frame (``style.legend_top``) instead of on the curves."""
    a, dd = ladder(pack_root)
    amp, n = power_fit(a, dd)
    two = dd[a == 2.0][0]
    ax.set_xscale("log")
    ax.set_yscale("log")
    s = np.geomspace(0.88, 3.5, 200)
    (h_two,) = ax.plot(s, two * (s / 2.0) ** 2, color=style.CONTEXT,
                       linestyle=(0, (4, 2.2)), linewidth=1.0, zorder=2)
    (h_fit,) = ax.plot(s, amp * s ** n, color=style.GOLD, linewidth=1.2, zorder=3)
    (h_dd,) = ax.plot(a, dd, linestyle="none", marker="o", ms=3.4, color=style.INK,
                      zorder=4)
    ax.set_xlim(0.88, 3.5)
    ax.set_ylim(0.12, 1.15)
    # Log axes would print powers of ten; the rungs and three doublings say more.
    plain = FuncFormatter(lambda v, _: f"{v:g}")
    ax.xaxis.set_major_locator(FixedLocator(sorted(RUNGS)))
    ax.yaxis.set_major_locator(FixedLocator([0.2, 0.4, 0.8]))
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(plain)
        axis.set_minor_locator(NullLocator())
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"$\delta d$ at $t=11.5$")
    if keys:
        style.legend_top(ax, [(h_dd, "measured"), (h_fit, rf"$a^{{{n:.1f}}}$"),
                              (h_two, r"$a^{2}$")], ncol=1, borderpad=0.35)
    else:
        # Names where the two laws have parted, past a = 2: gold below its
        # line, the grey rule above its own.
        ax.text(2.45, 0.86 * amp * 2.45 ** n, rf"$a^{{{n:.1f}}}$", fontsize=7.5,
                color=style.GOLD, ha="left", va="top")
        ax.text(2.3, 1.12 * two * (2.3 / 2.0) ** 2, r"$a^{2}$", fontsize=7.5,
                color=style.CONTEXT, ha="right", va="bottom")
    print(f"[width ladder] delta d at t = {T_LADDER}: "
          + ", ".join(f"a = {w:g}: {v:.4f}" for w, v in zip(a, dd))
          + f"; A a^n fit: A = {amp:.4f}, n = {n:.3f} (point charge: n = 2, "
          f"a^2 through a = 2 predicts {two * 2.25:.3f} at a = 3, measured {dd[-1]:.4f})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    style.prd(base=10.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.6), constrained_layout=True)
    figure_panel(ax, pack_root=args.pack_root)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "width_ladder.png")
    style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[width ladder] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
