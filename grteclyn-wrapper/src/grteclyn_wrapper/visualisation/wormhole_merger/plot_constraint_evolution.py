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
          ``plot_single_inflation``).  Its key names the finest dx, not the
          level (2026-09-26, referee pass): level 5 of the L = 512 octant is
          dx = 1/16, the level-3 class of the L = 64/128 boxes, so "level 5"
          read finer than it is.  Read from the run's evolution_params.txt;
(e)       the head-on chain's H, drawn with the ladder grammar of its
          main-text page (2026-10-05: "this ladder can be
          represented here on the ham plot"): the used legs in ink across
          era rules at t = 35 / 50.8, levels named per era, leg 1's overrun
          in grey to its NaN at t = 38.845 (cross);
(f)       the d = 6 merger chain with its FULL ladder: the used legs
          (level 5 -> sigma -> chi floor -> level-4 settle) in ink across
          era rules at t = 25 / 30 / 35, and in grey every arm that failed
          -- leg 1's overrun to its hand stop (dot), the level-6 / level-7
          wall arms (dashed) and the sigma overrun, each ending in its
          death cross.  The deaths are single-cell h11 NaNs with the box
          norms clean to the last step, so the grey curves end mid-air at
          ordinary values: the crosses, not blow-ups, mark them;
(g)       the p = 0.60 plunge chain (2026-10-05: "add here p060"),
          same ladder grammar: the used legs (level 4: to 40, the restart to
          50, the chi-floor leg to 100) in ink across era rules at t = 40 /
          50, the min-chi 1e-8 extension in grey to its merged-core cell NaN
          at t = 55.52 (cross), the level-5 chi-floor check riding the
          merger clean to its t = 60 stop (grey dashed, dot), and the trust
          rule at t = 80 where the floored core's junk reaches the record.
          No MOTS ever converges on this plunge, so there is no gold clock;
(h)       the fly-by, p = 0.45, d = 12, L = 128, level 5 (2026-09-26, referee
          pass), drawn to the end of its record, t = 100, PAST its t = 70 gate
          (``plot_psi4_gallery.ARMS``: nothing is quoted from the fly-by after
          it) so the growth behind the gate shows -- both norms leave their
          floor at closest approach and H climbs three decades by t = 100.
          Rules: the mouths outgrow the per-mouth scan (t ~ 43,
          ``plot_momentum_orbits.scan_edge_time``, the ledger's
          clmFlybyScanEdgeTime) and the gate.  The needles at t = 9-24 are
          one-sample pulses during the approach, each gone within ~0.1 units
          (H to 0.16 in this dt = 0.05 stream; the run's every-step stream
          peaks at 1.6): transients, not the growth.  Their cause is not
          pinned down -- some level regrids on nearly every step, so timing
          cannot single one out, and most fall on no change of the grid
          layout the run log reports.

Two rows of four, one sub-grid each: the lone throat on top, (a)-(d); the
binaries below, (e)-(h) (2026-10-05: "second row make it 4 figures
same as first row").

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_constraint_evolution

Writes ``figures/00_code_health/constraint_evolution``.  The norms are the
code's base-grid box averages (Sec. III.C): they compare only within one box.

STYLE: the PRD frame; a key ABOVE every panel names each line and, in its
title, the run (``style.legend_top``); letter tags at the keys' left
(``style.tag_keys``); no text inside a frame.  Ink for H, grey dashes for M;
GOLD only for the horizon clock, as on the main figures; clocks without a
horizon are faint grey rules, named in the key.
"""

from __future__ import annotations

import argparse
import pathlib
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import (  # noqa: E402
    plot_headon_collapse as headon,
    plot_momentum_orbits as orbits,
    plot_psi4_gallery as gallery,
    plot_seed_branches,
    plot_single_collapse as collapse,
    plot_single_inflation_L512 as f4,
    plot_merger_chain as mc,
    style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "00_code_health"
DASH = (0, (4, 2.5))
DOT = (0, (1, 2))
RULE = (0, (4, 3))          # a faint dashed clock rule, as (e) and (f) draw them
KEY = dict(title_fontsize=6.5, alignment="left", handlelength=1.8)
# (g): the p = 0.60 plunge chain (the d6 wall on the d12 plunge, chi-floor
# cured; registry and trust_windows.tsv rows of 2026-10-03/05)
P60_GROUP = "06_binary_flyby"
P60_LEG1 = "merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm"
P60_EXT = "merge_orbit_flip_d12_p060_L128_lvl4_t100_lbf_csm_r04000"
P60_CHI = "merge_orbit_flip_d12_p060_L128_lvl4from50_chi1e4_t100_lbf_csm_r05000"
P60_LVL5 = "merge_orbit_flip_d12_p060_L128_lvl5from40_chi1e4_t060_lbf_csm_r04000"
P60_SEAM1 = 40.0      # leg 1's stop_time; the extension restarts from Chk04000
P60_SEAM2 = 50.0      # extension -> chi-floor leg (Chk05000)
P60_TRUST = 80.0      # trust_windows.tsv: the floored core's junk from ~80

# (h): the fly-by the text quotes (Sec. VII A) and the gallery's fly-by row
FLYBY_GROUP = "06_binary_flyby"
FLYBY = "merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm"
FLYBY_TRUST = 67.6    # trust_windows.tsv: sustained L2 Ham crossing of 2.5e-2
FLYBY_GATE_ROW = "clmEgwGateFortyFive"   # the wave gate: recomputed by that ledger row's extractor
FLYBY_READ = (0.0, 30.0, 40.0, 43.0, 50.0, 60.0, 70.0, 80.0, 100.0)   # printed
FLYBY_FLOOR = (30.0, 40.0)  # the floor the growth is measured against (median)


def _ledger_value(row_id: str) -> tuple[float, str]:
    """A claims-ledger row recomputed by its own extractor, so a rule drawn here
    moves with the row the caption quotes (manual rows: their printed num), and
    the text the paper prints for it (the key's label)."""
    import importlib.util
    import json
    path = pathlib.Path(PACK_ROOT).parents[1] / "research" / "merger" / "article" / "claims" / "claims.py"
    spec = importlib.util.spec_from_file_location("claims", path)
    claims = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(claims)
    row = next(r for r in claims.load() if r["id"] == row_id)
    if not row["extractor"]:
        return float(row["num"]), row["tex"]
    return float(claims.lib.EXTRACTORS[row["extractor"]](**json.loads(row["args"] or "{}"))), row["tex"]


def _h(ax, t, y, **kw):
    return ax.semilogy(t, y, **kw)[0]


def _rule(color, ls):
    return Line2D([], [], color=color, lw=0.7, ls=ls)


def _cross(color=style.INK, ms=5):
    # a marker-only handle bleeds half its marker past the handle box, so
    # the quarter-width keys pass ms=4 (label audit, 2026-10-05)
    return Line2D([], [], color=color, ls="none", marker="X", ms=ms,
                  mec="white", mew=0.8)


# (a)/(b): every seed amplitude at the HIGHEST level it was run at (
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
        # titles fit the quarter-width frame: a longer one runs past it
        ncol=1, title="lone throat; dash = kick sign", **KEY)
    style.legend_top(axM, [
        (Line2D([], [], lw=0.9, **ink), r"$|\varepsilon|=0.001$, level 3"),
        (Line2D([], [], lw=2.1, **ink), r"$|\varepsilon|=0.1$, level 3"),
        (_cross(), "death (NaN)")],
        # borderpad: a marker-only handle's extent is its line's span plus half
        # the marker, so the cross bleeds 2.5 pt left of a one-column key
        ncol=1, title="same arms;\nweight = kick size", borderpad=0.5, **KEY)


def pure_quadrupole(ax, pack) -> None:
    """(c): the pure-quadrupole arm, H and M, with its MOTS clock."""
    cn = np.loadtxt(pack / "campaign" / collapse.GROUP / collapse.ARM / "constraint_norms.dat")
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[:, 0], cn[:, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    ax.axvline(collapse.T_MOTS, color=style.GOLD, lw=0.7, ls=DOT, zorder=1)
    # post-trust norms kept, behind the arm's trust rule (validation B7, 2026-10-06)
    ax.axvline(collapse.T_TRUST, color=style.FAINT, lw=0.7, ls=DOT, zorder=1)
    ax.set_xlim(0, 100)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$"), (hM, r"$\mathcal{M}$"),
                          (_rule(style.GOLD, DOT), rf"MOTS, $t={collapse.T_MOTS:g}$"),
                          (_rule(style.FAINT, DOT), rf"trust window, $t={collapse.T_TRUST:g}$")],
                     ncol=1, title="pure quadrupole,\n" r"$\varepsilon_2=0.01$, level 4", **KEY)
    late = cn[cn[:, 0] >= collapse.T_TRUST]
    early = cn[cn[:, 0] <= collapse.T_TRUST]
    print(f"  (c) to the trust window: H max {early[:, 1].max():.2e}, M max {early[:, 2].max():.2e}")
    print(f"  (c) pure quadrupole: H {cn[0, 1]:.2e} -> {cn[-1, 1]:.2e}; "
          f"x{late[-1, 1] / late[0, 1]:.0f} over t = 60-{late[-1, 0]:.0f}")


def _param(run: pathlib.Path, key: str) -> float:
    """One numeric key of a packed run's evolution_params.txt (the reader the
    pre-csm plot_headon_collapse carried; local since its 09-30 rewrite)."""
    for ln in (run / "evolution_params.txt").read_text().splitlines():
        ln = ln.split("#", 1)[0].strip()
        if "=" in ln:
            k, v = ln.split("=", 1)
            if k.strip() == key:
                return float(v.strip().strip('"').split()[0])
    raise KeyError(key)


def _finest_dx(run: pathlib.Path) -> Fraction:
    """The finest cell of a packed run, from its evolution_params.txt: the full
    box's L / N over 2^max_level (the octant runs name the full box L_full /
    N_full; the refinement ratio is AMReX's default 2)."""
    try:
        L, N = _param(run, "L_full"), _param(run, "N_full")
    except KeyError:
        L, N = _param(run, "L"), _param(run, "N1")
    return Fraction(L / N / 2 ** int(_param(run, "max_level"))).limit_denominator(4096)


def inflation(ax, pack_root) -> None:
    """(d): F4 to its trust limit, as the inflation figure's old (i).  The key
    names its finest dx: level 5 of the L = 512 octant is the level-3 class."""
    run = f4.f4_dir(pack_root)
    cn = f4.record(run)["cn"]
    cn = cn[cn[:, 0] <= f4.T_WALL + 1e-9]
    mm = cn[:, 2] > 0
    dx = _finest_dx(run)
    L = _param(run, "L_full")
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[mm, 0], cn[mm, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    ax.set_xlim(0, f4.T_WALL)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$"), (hM, r"$\mathcal{M}$")], ncol=2,
                     title=(r"inflation, $\varepsilon=-0.01$," "\n" rf"$L={L:g}$ octant," "\n"
                            rf"finest $\Delta x={dx}$"),
                     **KEY)
    print(f"  (d) inflation F4 (L = {L:g} octant, finest dx = {dx}): H {cn[0, 1]:.2e} -> "
          f"{cn[-1, 1]:.2e} at t = {cn[-1, 0]:.0f}")


def _ladder_rules(ax, seams, t_mots):
    """The main-text pages' era grammar: faint rules at the restarts, the
    horizon clock in gold."""
    ax.axvline(t_mots, color=style.GOLD, lw=0.7, ls=DOT, zorder=1)
    for seam in seams:
        ax.axvline(seam, color=style.FAINT, lw=0.7, ls=RULE, zorder=1)


def _levels(ax, names, y=0.92):
    """Level names per era, at data x / axes y (the merger page's (a)/(d))."""
    for x, name in names:
        ax.text(x, y, name, transform=ax.get_xaxis_transform(), fontsize=7,
                ha="center", va="top", color=style.MUTED)


def headon_pair(ax, pack) -> None:
    """(e): the head-on chain's Hamiltonian norm drawn as its main-text page
    is: the used legs in ink across the era rules, levels named per era, and
    leg 1's overrun past its t = 35 checkpoint in grey to its NaN (cross)."""
    base = pack / "campaign" / headon.GROUP / headon.CHAIN
    c5 = headon._sorted(base / headon.LEG1 / "constraint_norms.dat")
    c6 = headon._sorted(base / headon.LEG2 / "constraint_norms.dat")
    c4 = headon._sorted(base / headon.LEG3 / "constraint_norms.dat")
    used = (headon._era(c5, -1.0, headon.T_SEAM1),
            headon._era(c6, headon.T_SEAM1, headon.T_SEAM2, headon.SETTLE),
            headon._era(c4, headon.T_SEAM2, 1e9, headon.SETTLE))
    for u in used:
        hU = _h(ax, u[:, 0], u[:, 1], color=style.INK, lw=1.1, zorder=3)
    over = c5[c5[:, 0] > headon.T_SEAM1 - 1e-9]          # runs on to the NaN
    hO = _h(ax, over[:, 0], over[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    ax.plot(over[-1, 0], over[-1, 1], "X", color=style.CONTEXT, ms=5,
            mec="white", mew=0.8, zorder=4)
    _ladder_rules(ax, (headon.T_SEAM1, headon.T_SEAM2), headon.T_MOTS)
    _levels(ax, ((9.0, "5"), (43.0, "6"), (75.0, "4")))
    ax.set_xlim(0, 100)
    # headroom: the level names sit in a clear band above the curve
    lo = min(float(u[:, 1].min()) for u in used)
    hi = max(float(u[:, 1].max()) for u in used)
    ax.set_ylim(0.85 * lo, 2.3 * hi)
    style.legend_top(ax, [(hU, "used legs, level 5-6-4"), (hO, "level-5 overrun"),
                          (_cross(style.CONTEXT), "death (NaN)"),
                          (_rule(style.GOLD, DOT), rf"MOTS, $t={headon.T_MOTS:g}$")],
                     ncol=1, title=r"head-on chain, $\mathcal{H}$", borderpad=0.5, **KEY)
    f = float(np.interp(headon.T_MOTS, c5[:, 0], c5[:, 1]))
    print(f"  (e) head-on: H at formation {f:.2e}; overrun dies {over[-1, 0]:g} "
          f"(H {over[-1, 1]:.2e}); leg ends {c5[-1, 0]:g}/{c6[-1, 0]:g}/{c4[-1, 0]:g}; "
          f"settle end H {c4[-1, 1]:.2e}")


def spiral_chain(ax, pack) -> None:
    """(f): the d = 6 merger chain with its full ladder: the used legs
    (level 5 -> sigma -> chi floor -> level-4 settle) in ink, and the wall
    arms of the merger page's (d) in grey with their death crosses."""
    base = pack / "campaign" / mc.GROUP / mc.CHAIN

    def load(name):
        return headon._sorted(base / name / "constraint_norms.dat")

    c1, cs, cc, c4 = load(mc.LEG1), load(mc.SIG), load(mc.CHI), load(mc.SETTLE)
    l6, l7 = load(mc.LVL6), load(mc.LVL7)
    used = (headon._era(c1, -1.0, mc.T_SEAM1),
            headon._era(cs, mc.T_SEAM1, mc.T_SEAM2, mc.SETTLE_CLIP),
            headon._era(cc, mc.T_SEAM2, mc.T_SEAM3, mc.SETTLE_CLIP),
            headon._era(c4, mc.T_SEAM3, 1e9, mc.SETTLE_CLIP))
    for u in used:
        hU = _h(ax, u[:, 0], u[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, used[-1][:, 0], used[-1][:, 2], color=style.CONTEXT, lw=0.9,
            ls=DOT, zorder=2)
    # the greys: leg 1's overrun to its hand stop (dot), the sigma arm's
    # overrun to its death, and the level-6/7 wall arms (dashed) -- crosses
    o1 = c1[c1[:, 0] > mc.T_SEAM1 - 1e-9]
    _h(ax, o1[:, 0], o1[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    ax.plot(o1[-1, 0], o1[-1, 1], "o", color=style.CONTEXT, ms=3.2, zorder=4)
    os_ = cs[cs[:, 0] > mc.T_SEAM2 - 1e-9]
    hO = _h(ax, os_[:, 0], os_[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    ax.plot(os_[-1, 0], os_[-1, 1], "X", color=style.CONTEXT, ms=5,
            mec="white", mew=0.8, zorder=4)
    for w in (l6, l7):
        hW = _h(ax, w[:, 0], w[:, 1], color=style.CONTEXT, lw=0.9,
                ls=(0, (3, 1.6)), zorder=2)
        ax.plot(w[-1, 0], w[-1, 1], "X", color=style.CONTEXT, ms=5,
                mec="white", mew=0.8, zorder=4)
    _ladder_rules(ax, (mc.T_SEAM1, mc.T_SEAM2, mc.T_SEAM3), mc.T_MOTS)
    _levels(ax, ((18.0, "5"), (70.0, "4")))
    ax.set_xlim(0, 100)
    style.legend_top(ax, [(hU, "used legs, level 5-4"),
                          (hW, "level-6, 7 walls"),
                          (hO, r"$\sigma$ arm, overruns"),
                          (hM, r"$\mathcal{M}$, settle leg"),
                          (_rule(style.GOLD, DOT), rf"MOTS, $t={mc.T_MOTS:g}$")],
                     ncol=1, title=r"merger chain, $d=6$, $\mathcal{H}$", **KEY)
    print(f"  (f) d6 chain: leg ends {c1[-1, 0]:g}/{cs[-1, 0]:g}/{cc[-1, 0]:g}/{c4[-1, 0]:g}; "
          f"H at contact {float(np.interp(mc.T_MOTS, c1[:, 0], c1[:, 1])):.2e}, "
          f"settle end H {c4[-1, 1]:.2e} M {c4[-1, 2]:.2e}")
    for nm, w in (("lvl6", l6), ("lvl7", l7), ("sigma", cs)):
        print(f"      {nm}: dies {w[-1, 0]:g}, H start {w[0, 1]:.2e} -> last step {w[-1, 1]:.2e}")


def p060_chain(ax, pack) -> None:
    """(g): the p = 0.60 plunge chain's Hamiltonian norm with its ladder: the
    used legs in ink, the 1e-8 extension's death and the level-5 check in
    grey, the trust rule where the floored core's junk reaches the record."""
    base = pack / "campaign" / P60_GROUP

    def load(name):
        return headon._sorted(base / name / "constraint_norms.dat")

    c1, ce, cc, c5 = load(P60_LEG1), load(P60_EXT), load(P60_CHI), load(P60_LVL5)
    used = (headon._era(c1, -1.0, P60_SEAM1),
            headon._era(ce, P60_SEAM1, P60_SEAM2, mc.SETTLE_CLIP),
            headon._era(cc, P60_SEAM2, 1e9, mc.SETTLE_CLIP))
    for u in used:
        hU = _h(ax, u[:, 0], u[:, 1], color=style.INK, lw=1.1, zorder=3)
    oe = ce[ce[:, 0] > P60_SEAM2 - 1e-9]                 # runs on to the NaN
    hO = _h(ax, oe[:, 0], oe[:, 1], color=style.CONTEXT, lw=0.9, zorder=2)
    ax.plot(oe[-1, 0], oe[-1, 1], "X", color=style.CONTEXT, ms=5,
            mec="white", mew=0.8, zorder=4)
    h5 = _h(ax, c5[:, 0], c5[:, 1], color=style.CONTEXT, lw=0.9,
            ls=(0, (3, 1.6)), zorder=2)
    ax.plot(c5[-1, 0], c5[-1, 1], "o", color=style.CONTEXT, ms=3.2, zorder=4)
    for seam in (P60_SEAM1, P60_SEAM2):
        ax.axvline(seam, color=style.FAINT, lw=0.7, ls=RULE, zorder=1)
    ax.axvline(P60_TRUST, color=style.FAINT, lw=0.7, ls=DOT, zorder=1)
    _levels(ax, ((66.0, "level 4"),))
    ax.set_xlim(0, 100)
    style.legend_top(ax, [(hU, "used legs"),
                          (h5, "level-5 check"),
                          (hO, "floor-free overrun"),
                          (_rule(style.FAINT, DOT), rf"trust window, $t={P60_TRUST:g}$")],
                     ncol=1, title="plunge, $p=0.60$, $\\mathcal{H}$;\n"
                     r"$\chi$ floor from $t=50$", **KEY)
    print(f"  (g) p060 chain: leg ends {c1[-1, 0]:g}/{ce[-1, 0]:g}/{cc[-1, 0]:g}; "
          f"overrun dies {oe[-1, 0]:g} (H {oe[-1, 1]:.2e}); lvl5 check end "
          f"{c5[-1, 0]:g} (H {c5[-1, 1]:.2e}); chi leg H at trust "
          f"{float(np.interp(P60_TRUST, cc[:, 0], cc[:, 1])):.2e}, end {cc[-1, 1]:.2e}")


def flyby(ax, pack) -> None:
    """(h): the p = 0.45 scatterer's H and M to t = 100, with its two clocks."""
    cn = headon._sorted(pack / "campaign" / FLYBY_GROUP / FLYBY / "constraint_norms.dat")
    hH = _h(ax, cn[:, 0], cn[:, 1], color=style.INK, lw=1.1, zorder=3)
    hM = _h(ax, cn[:, 0], cn[:, 2], color=style.MUTED, lw=1.1, ls=DASH, zorder=3)
    ax.axvline(FLYBY_TRUST, color=style.FAINT, lw=0.7, ls=RULE, zorder=1)
    gate, gate_tex = _ledger_value(FLYBY_GATE_ROW)
    ax.axvline(gate, color=style.FAINT, lw=0.7, ls=DOT, zorder=1)
    ax.set_xlim(0, 100)
    style.legend_top(ax, [(hH, r"$\mathcal{H}$"), (hM, r"$\mathcal{M}$"),
                          (_rule(style.FAINT, RULE), rf"trust window, $t={FLYBY_TRUST:g}$"),
                          (_rule(style.FAINT, DOT), rf"wave gate, $t={gate_tex}$")],
                     ncol=1, title=r"fly-by, $p=0.45$, level 4", **KEY)
    t = cn[:, 0]
    quiet = (t >= 10.0) & (t <= 40.0)
    for col, nm in ((1, "H"), (2, "M")):
        floor = float(np.median(cn[quiet, col]))
        print(f"  (g) {nm}: quiet median {floor:.2e}; at trust {float(np.interp(FLYBY_TRUST, t, cn[:, col])):.2e}; "
              f"end {cn[-1, col]:.2e} (x{cn[-1, col] / floor:.0f})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 4.9), constrained_layout=True)
    # One sub-grid per row, the lone throat on top and the binaries below: on
    # one shared grid the rows' column edges (4 against 3) would not line up,
    # and constrained layout, one margin per column, collapses the axes.
    gs = fig.add_gridspec(2, 1)
    top, bottom = gs[0].subgridspec(1, 4), gs[1].subgridspec(1, 4)
    axs = ([fig.add_subplot(top[0, i]) for i in range(4)]
           + [fig.add_subplot(bottom[0, i]) for i in range(4)])
    print("[constraint evolution]")
    seed_scan(axs[0], axs[1], pack)
    pure_quadrupole(axs[2], pack)
    inflation(axs[3], args.pack_root)
    headon_pair(axs[4], pack)
    spiral_chain(axs[5], pack)
    p060_chain(axs[6], pack)
    flyby(axs[7], pack)
    for k, ax in enumerate(axs):
        ax.set_xlabel(r"$t$")
        ax.set_ylabel({0: r"$L^2\,\mathcal{H}$", 1: r"$L^2\,\mathcal{M}$",
                       4: r"$L^2\,\mathcal{H}$", 6: r"$L^2\,\mathcal{H}$"}.get(
                          k, r"$L^2$ norms"))
    style.tag_keys(fig, axs, [f"({c})" for c in "abcdefgh"], row="last")

    hits = style.label_audit(fig)
    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "constraint_evolution.png")
    png = style.save(fig, out)
    print(f"[constraint evolution] wrote {png} (+pdf); label audit: {len(hits)} hit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
