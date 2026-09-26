#!/usr/bin/env python3
r"""Code health on one page: the constraint record of every run the paper draws.

The appendix figure "Code health and constraint evolution" (2026-09-26, the
user: "for fig 1 2 4 6 9 extract the measurement plots, the ones that validate
the results are correct, and move them to the single plot in appendix that
covers the constraints for all of them; keep the physical observables").  Each
panel is the constraint panel its main-text figure used to carry, drawn from
the same streams by the same rules, so the main figures now show physics only:

(a), (b)  the lone throat's L2 Hamiltonian / momentum norms, every seed
          amplitude at the highest level it was run at (was Fig. 1(d),(e), the
          level-3 scan only);
(c)       the pure-quadrupole collapse (was Fig. 2(g), ``plot_single_collapse``);
(d)       the inflating throat F4 to its trust limit (was Fig. 4(i),
          ``plot_single_inflation``);
(e)       the head-on: scout, level-5 arm, down-step (was Fig. 6(e),
          ``plot_headon_collapse``);
(f)       the production spiral's level-5 leg and the level-3 leg over their
          shared window (was Fig. 9(d), ``plot_spiral_collapse``, there on a
          normalised log scale against max|K|; here the norms themselves).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_constraint_evolution

Writes ``figures/00_code_health/constraint_evolution``.  The norms are the
code's base-grid box averages (Sec. III.C): they compare only within one box.

STYLE: the PRD frame; a key ABOVE every panel names each line and, in its
title, the run (``style.legend_top``); letter tags at the keys' left
(``style.tag_keys``); no text inside a frame.  Ink for H, grey dashes for M;
GOLD only for the horizon clock, as on the main figures.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import (  # noqa: E402
    plot_headon_collapse as headon,
    plot_seed_branches,
    plot_single_collapse as collapse,
    plot_single_inflation_L512 as f4,
    plot_spiral_collapse as spiral,
    style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "00_code_health"
DASH = (0, (4, 2.5))
DOT = (0, (1, 2))
KEY = dict(title_fontsize=6.5, alignment="left", handlelength=1.8)


def _h(ax, t, y, **kw):
    return ax.semilogy(t, y, **kw)[0]


def _rule(color, ls):
    return Line2D([], [], color=color, lw=0.7, ls=ls)


def _cross(color=style.INK):
    return Line2D([], [], color=color, ls="none", marker="X", ms=5,
                  mec="white", mew=0.8)


# (a)/(b): every seed amplitude at the HIGHEST level it was run at (the user,
# 2026-09-26: "max level available should be shown").  At L = 64 that is level
# 4 for the unkicked throat and the +-0.01 pair -- +0.01 was stopped by hand at
# t = 13.5 (registry), so it ends in a dot, not a cross -- and level 3 for
# +-0.001 and +-0.1, which were never run at level 4.  (Level 5 exists only for
# -0.01, on L = 512: panel (d).)  The grammar is Fig. 1(c)'s: dash = sign of the
# kick, weight = its size, grey = no kick, cross = death by NaN.
SEED_ARMS = (   # (pack path under 01_single_throat, kick, level)
    ("hold/single_hold_ml4_t100", None, 4),
    ("seed/single_eps_m1e2_ml4_t100", "-0.01", 4),
    ("seed/single_eps_p1e2_ml4_t060", "+0.01", 4),
    ("seed/single_eps_m1e3_t100", "-0.001", 3),
    ("seed/single_eps_p1e3_t100", "+0.001", 3),
    ("seed/single_eps_m1e1_t100", "-0.1", 3),
    ("seed/single_eps_p1e1_t100", "+0.1", 3),
)


def seed_scan(axH, axM, pack) -> None:
    """(a)/(b): L2 H and M of the seed arms, each at its highest level."""
    base = pack / "campaign" / "01_single_throat"
    for rel, kick, level in SEED_ARMS:
        d = base / rel
        a = plot_seed_branches._norms(d)
        if a is None:
            print(f"  {rel}: no constraint_norms, skipped"); continue
        a = a[np.isfinite(a[:, 1]) & np.isfinite(a[:, 2])]
        dead = plot_seed_branches.died(d)
        if dead:
            a = plot_seed_branches._cut_overflow(a)   # the overflow step is not a reading
        if kick is None:
            st = dict(color=style.CONTEXT, lw=0.9, ls=(0, ()))
        else:
            size = abs(float(kick))
            st = dict(color=style.INK, lw=2.1 if size >= 5e-2 else (1.5 if size >= 5e-3 else 0.9),
                      ls=DASH if kick.startswith("+") else (0, ()))
        for ax, col in ((axH, 1), (axM, 2)):
            ax.semilogy(a[:, 0], a[:, col], zorder=2 if kick is None else 3, **st)
            if dead:
                ax.plot(a[-1, 0], a[-1, col], "X", color=st["color"], ms=5, mec="white",
                        mew=0.8, zorder=4)
            elif a[-1, 0] < 99.0:                     # stopped by hand, not dead
                ax.plot(a[-1, 0], a[-1, col], "o", color=st["color"], ms=3.2, zorder=4)
        print(f"  {kick or 'no kick':>7s} level {level}  t = 0-{a[-1, 0]:6.2f}  H(0) = {a[0, 1]:.2e}  "
              f"M(0.5) = {np.interp(0.5, a[:, 0], a[:, 2]):.2e}  H_end = {a[-1, 1]:.2e}"
              + ("  NaN" if dead else ""))
    for ax in (axH, axM):
        ax.set_xlim(0, 100)
    ink = dict(color=style.INK)
    style.legend_top(axH, [
        (Line2D([], [], lw=1.5, **ink), r"$\varepsilon=-0.01$, level 4"),
        (Line2D([], [], lw=1.5, ls=DASH, **ink), r"$\varepsilon=+0.01$, level 4"),
        (Line2D([], [], color=style.CONTEXT, lw=0.9), "no kick, level 4"),
        (Line2D([], [], color=style.INK, ls="none", marker="o", ms=3.2), "stopped by hand")],
        ncol=1, title="lone throat; dash = sign of the kick", **KEY)
    style.legend_top(axM, [
        (Line2D([], [], lw=0.9, **ink), r"$|\varepsilon|=0.001$, level 3"),
        (Line2D([], [], lw=2.1, **ink), r"$|\varepsilon|=0.1$, level 3"),
        (_cross(), "death (NaN)")],
        # borderpad: a marker-only handle's extent is its line's span plus half
        # the marker, so the cross bleeds 2.5 pt left of a one-column key
        ncol=1, title="same arms; weight = kick size", borderpad=0.5, **KEY)


def pure_quadrupole(ax, pack) -> None:
    """(c): the pure-quadrupole arm, H and M, with its MOTS clock."""
    cn = np.loadtxt(pack / "campaign" / collapse.GROUP / collapse.ARM / "constraint_norms.dat")
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[:, 0], cn[:, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    ax.axvline(collapse.T_MOTS, color=style.GOLD, lw=0.7, ls=DOT, zorder=1)
    ax.set_xlim(0, 100)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$"), (hM, r"$\mathcal{M}$"),
                          (_rule(style.GOLD, DOT), rf"MOTS, $t={collapse.T_MOTS:g}$")],
                     ncol=2, title=r"pure quadrupole, $\varepsilon_2=0.01$, level 4", **KEY)
    late = cn[cn[:, 0] >= 60.0]
    print(f"  (c) pure quadrupole: H {cn[0, 1]:.2e} -> {cn[-1, 1]:.2e}; "
          f"x{late[-1, 1] / late[0, 1]:.0f} over t = 60-{late[-1, 0]:.0f}")


def inflation(ax, pack_root) -> None:
    """(d): F4 to its trust limit, as the inflation figure's old (i)."""
    cn = f4.record(f4.f4_dir(pack_root))["cn"]
    cn = cn[cn[:, 0] <= f4.T_WALL + 1e-9]
    mm = cn[:, 2] > 0
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[mm, 0], cn[mm, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    ax.set_xlim(0, f4.T_WALL)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$"), (hM, r"$\mathcal{M}$")], ncol=2,
                     title=r"inflation, $\varepsilon=-0.01$, level 5, $L=512$",
                     **KEY)
    print(f"  (d) inflation F4: H {cn[0, 1]:.2e} -> {cn[-1, 1]:.2e} at t = {cn[-1, 0]:.0f}")


def headon_pair(ax, pack) -> None:
    """(e): the head-on's Hamiltonian norm on its three arms."""
    base = pack / "campaign" / headon.GROUP
    cs = headon._sorted(base / headon.SCOUT / "constraint_norms.dat")
    c5 = headon._sorted(base / headon.ARM / "constraint_norms.dat")
    c3 = headon._clipped(base / headon.DOWN / "constraint_norms.dat")
    h5 = _h(ax, c5[:, 0], c5[:, 1], color=style.INK, lw=1.1, zorder=3)
    hs = _h(ax, cs[:, 0], cs[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    h3 = _h(ax, c3[:, 0], c3[:, 1], color=style.MUTED, lw=0.9, ls=DASH, zorder=2)
    ax.axvline(headon.T_MOTS, color=style.GOLD, lw=0.7, ls=DOT, zorder=1)
    ax.axvline(headon.T_WALL, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.set_ylim(2.5e-4, 3e-2)
    ax.set_xlim(-1.5, float(c5[-1, 0]) + 1.5)
    style.legend_top(ax, [(h5, "level 5"), (hs, "level-3 scout"), (h3, "level-3 down-step"),
                          (_rule(style.GOLD, DOT), rf"MOTS, $t={headon.T_MOTS:g}$"),
                          (_rule(style.FAINT, (0, (4, 3))), "scout dies")],
                     ncol=2, title=r"head-on, $\mathcal{H}$", **KEY)
    f = float(np.interp(headon.T_MOTS, c5[:, 0], c5[:, 1]))
    print(f"  (e) head-on level 5: H at formation {f:.2e}, max after {c5[c5[:, 0] > 30, 1].max():.2e}, "
          f"end {c5[-1, 1]:.2e}; scout at its wall {cs[-1, 1]:.2e}")


def spiral_chain(ax, pack) -> None:
    """(f): the spiral's level-5 leg to the wall, the level-3 leg where they overlap."""
    camp = pack / "campaign" / spiral.GROUP
    arm = camp / spiral.ARM
    d = spiral._sorted(arm / "collapse_diagnostics.dat")
    d = d[d[:, 0] >= d[0, 0] + spiral.SETTLE]
    t0, t_end = float(d[0, 0]), float(d[-1, 0])
    # the chi-floor clock as the spiral figure reads it, off the radial profile
    pt, _, blk = spiral._read_profile(arm / "core_radial_profile.dat.gz")
    t_floor = float(pt[np.argmax(np.nanmin(blk["chi"], axis=1) <= spiral.CHI_FLOOR * 1.01)])
    cn = spiral._sorted(arm / "constraint_norms.dat")
    cn = cn[cn[:, 0] >= t0]
    t_trans = float(cn[int(np.argmax(cn[:, 2])), 0])
    c3 = spiral._sorted(camp / spiral.LEVEL3 / "constraint_norms.dat")
    c3 = c3[(c3[:, 0] >= t0) & (c3[:, 0] <= t_end)]
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[:, 0], cn[:, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    g3 = _h(ax, c3[:, 0], c3[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    _h(ax, c3[:, 0], c3[:, 2], color=style.CONTEXT, lw=0.9, ls=DASH, zorder=2)
    ax.plot(cn[-1, 0], cn[-1, 1], "X", color=style.INK, ms=5, mec="white", mew=0.8, zorder=4)
    ax.axvline(t_trans, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.axvline(t_floor, color=style.FAINT, lw=0.7, ls=DOT, zorder=1)
    ax.set_xlim(t0 - 0.6, t_end + 0.6)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$, level 5"), (hM, r"$\mathcal{M}$, level 5"),
                          (g3, "level-3 leg"), (_cross(), "death (NaN)"),
                          (_rule(style.FAINT, (0, (4, 3))), "merger transient"),
                          (_rule(style.FAINT, DOT), r"$\chi$ on its floor")],
                     ncol=2, title=r"spiral, $p=0.12$", **KEY)
    H5, M5 = np.interp(c3[:, 0], cn[:, 0], cn[:, 1]), np.interp(c3[:, 0], cn[:, 0], cn[:, 2])
    print(f"  (f) spiral: t = {t0:.1f}-{t_end:.2f}; transient t = {t_trans:.2f} "
          f"(H {cn[:, 1].max():.2e}, M {cn[:, 2].max():.2e}); chi floor t = {t_floor:.2f}; "
          f"H at the wall {cn[-1, 1]:.2e} (start {cn[0, 1]:.2e}); level-3 overlap median "
          f"|dH|/H {np.median(abs(c3[:, 1] - H5) / H5) * 100:.1f}%, "
          f"|dM|/M {np.median(abs(c3[:, 2] - M5) / M5) * 100:.1f}%")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 4.9), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    axs = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(6)]
    print("[constraint evolution]")
    seed_scan(axs[0], axs[1], pack)
    pure_quadrupole(axs[2], pack)
    inflation(axs[3], args.pack_root)
    headon_pair(axs[4], pack)
    spiral_chain(axs[5], pack)
    for k, ax in enumerate(axs):
        ax.set_xlabel(r"$t$")
        ax.set_ylabel({0: r"$L^2\,\mathcal{H}$", 1: r"$L^2\,\mathcal{M}$",
                       4: r"$L^2\,\mathcal{H}$"}.get(k, r"$L^2$ norms"))
    style.tag_keys(fig, axs, [f"({c})" for c in "abcdef"], row="last")

    hits = style.label_audit(fig)
    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "constraint_evolution.png")
    png = style.save(fig, out)
    print(f"[constraint evolution] wrote {png} (+pdf); label audit: {len(hits)} hit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
