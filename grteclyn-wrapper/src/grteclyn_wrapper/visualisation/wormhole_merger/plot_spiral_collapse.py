#!/usr/bin/env python3
r"""The spiral merger's collapse, as a top-of-page strip: history, horizon, core.

The paper's p = 0.12 collapse figure.  The production spiral is one history in
three legs -- level 3 from t = 0, level 5 restarted at t = 36 (death at the
wall, t = 60.445), and the frozen-core leg restarted at t = 57 that carries the
exterior to t = 100 -- and the figure draws that history, not the schedule.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_collapse

Reads, all under ``campaign/05_binary_spiral/p012_paper/``:

* ``v2_spiral_d12_p012_L128_SERIES/binary_throat_diagnostics.dat`` -- the glued
  three-leg record; the pit separation is drawn from its UNFROZEN legs only
  (t <= 60.44), because the third leg's pits sit inside the frozen core.
* ``v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600/`` -- ``collapse_diagnostics.dat``
  (columns min_lapse, min_chi, max_abs_K, ..., NO header on a restart),
  ``constraint_norms.dat``, ``core_radial_profile.dat.gz`` (time + 128 shells x
  {chi_min, absK_max, lapse_min, n, dx}, dr = 0.03125), and the two oriented
  marginal-surface scans ``horizon_oriented_scan_t55-57.txt`` / ``_t58-60.txt``.
* ``v2_spiral_d12_p012_L128_lvl5_t100_freeze_r05700/evolution_params.txt`` --
  when the freeze was armed and how far the fill reaches (the shaded era).

PANELS

(a) The pits' coordinate separation over the whole history, t = 0-100, on a
    log axis so the late approach is legible: the two chi pits -- each
    wormhole's compactified far side -- are 0.31 apart at t = 57, 20 finest
    cells, and are drawn pale once chi sits on its floor (t = 58.4), where the
    half-space minima are floored cells rather than resolved pits.  Shaded:
    the frozen-core era.  Nothing is drawn there from inside the fill: a
    global minimum inside a frozen region is not physics.
(b) Areal radii on a broken time axis, t = 54.5-61 | 97.5-100.5: the common
    MOTS of the shape-free flow finder (FLOW_MOTS, REMNANT_MOTS; gold), and
    the common neck -- the areal minimum of coordinate spheres about the pits'
    midpoint, which enclose both far sides -- from the two oriented scans
    (ink; open level 3, filled level 5, which agree to 0.2 %).  Nothing from
    inside the fill: the remnant's neck sits in the frozen core.
    Rules: one initial throat, R_star, and the radius of the two throats'
    summed area, sqrt(2) R_star.
(c) Core extrema on one log axis: min chi, min lapse, max|K|, max|phi|, max|Pi|.
    (Until 2026-09-26 a panel (d) set the constraint norms against max|K| on a
    normalised log scale; the norms, with the level-3 leg, are now panel (f) of
    the appendix's code-health figure, ``plot_constraint_evolution``, and
    max|K| joined the other extrema here.)
(d) The |K| spike (radius of the radial maximum, from the first time it stands
    2x above the background) and its |K| > 0.2 edge, against the neck's
    coordinate radius from the scans.

WHAT THE FIGURE HAS TO GET RIGHT

*The horizon columns of the in-code stream are not drawn.*  Its theta_common
goes negative at t = 30.77 with the naive +r orientation, a signal once quoted
as a common horizon and withdrawn (GPU_PLAN, 2026-09-15).  The horizon
instruments here are the orientation-corrected offline scan (the neck) and the
shape-free flow finder (the MOTS).

*The restart-settle rows are masked, not smoothed.*  For its first steps a
restart reduces over an incomplete hierarchy and reports coarse-grid extrema:
five rows of the glued separation stream spike to 7.5 just after t = 36, and
the first collapse-diagnostics rows do the same.  Both are clipped a tenth of a
unit past their restart.

*The peak-radius track starts where the peak is real.*  Before t = 49.09 the
radial |K| profile is flat (at t = 45 the "peak" is 0.078 against a 0.066
background), so an argmax there is noise.

STYLE (2026-09-24, the reviewer: "why does this picture span the whole page?"):
a 7.05 x 4.3 strip for the top of a page, included at 0.80 textwidth like every
two-column figure -- four panels where the float page had ten; the radial
snapshots and the separate lapse / chi / scalar panels went.  style.prd frame,
letter tags above the frames, every series named in place, no key.  Monochrome
ink plus the one accent: GOLD is the horizon -- the flow finder's common MOTS --
and nothing else; the neck (a minimal sphere, not a horizon) is ink.
"""

from __future__ import annotations

import argparse
import gzip
import math
import pathlib
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "05_binary_spiral"
ARM = "p012_paper/v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600"
SERIES = "p012_paper/v2_spiral_d12_p012_L128_SERIES"
FREEZE = "p012_paper/v2_spiral_d12_p012_L128_lvl5_t100_freeze_r05700"
LEVEL3 = "p012_paper/v2_spiral_d12_p012_L128_lvl3_t050"

# BinaryWormholeLevel's writer, in order -- no header on a restart.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

CHI_FLOOR = 1e-8       # the evolution's clamp on chi
EDGE_K = 0.2           # |K| defining the disturbance's outer edge
SETTLE = 0.1           # time clipped after a restart (incomplete hierarchy)
HANDOVER = 36.0        # level 3 -> 5 in the glued series (its README)

# The common MOTS of the shape-free flow finder (grteclyn-wrapper/scripts/
# validation/ah_flow_finder.py) on the surviving death-window slices:
# (t, areal R, on the production chain?).  t = 55-57 from the production
# chain's level-5 slices (t = 55: outer seed, lmax 8); t = 59 from the arm
# evolved at level 5 from t = 0 (inner + outer seeds, R = 4.72 +- 0.01).
# Source: GPU_PLAN, "R0 VERDICT (2026-09-21)" and its slice-hunt bullets;
# ledger rows clmSpiralFlowRadius*.
FLOW_MOTS = ((55.0, 4.83, True), (56.0, 4.80, True), (57.0, 4.77, True),
             (59.0, 4.72, False))
# The remnant on the frozen-core leg's live exterior (fill r <= 1.9, inside the
# surface, whose h >= 2.33): R ~ 4.15 on each of t = 98/99/100, M_MS 2.083 ->
# 2.079 -> 2.075.  Same source; ledger clmSpiralRemnantRadius (t = 97 corrupt).
REMNANT_MOTS = ((98.0, 4.15), (99.0, 4.15), (100.0, 4.15))


def _sorted(path: pathlib.Path) -> np.ndarray:
    d = np.loadtxt(path)
    return d[np.argsort(d[:, 0])]


def _params(path: pathlib.Path) -> dict[str, str]:
    out = {}
    for ln in path.read_text().splitlines():
        ln = ln.split("#", 1)[0].strip()
        if "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _r_star(a: float, m: float) -> float:
    """Areal radius of the static drainhole's minimal surface (Sec. II):
    r_t = (m + sqrt(m^2 + a^2)) / 2, R = e^{-u(r_t)} sqrt(a^2 + m^2)."""
    rt = 0.5 * (m + math.hypot(m, a))
    x = (rt - a * a / (4 * rt)) / a
    u = (m / a) * (math.atan(x) - math.pi / 2)
    return math.exp(-u) * math.hypot(a, m)


def _read_profile(path: pathlib.Path):
    with gzip.open(path, "rt") as fh:
        names = fh.readline().split()[1:]     # drop the leading '#'
        prof = np.loadtxt(fh)
    nsh = (len(names) - 1) // 5               # blocks: chi, |K|, lapse, n, dx
    rr = np.array([float(n.rsplit("_r", 1)[1]) for n in names[1:1 + nsh]])
    t = prof[:, 0]
    blk = {}
    for i, name in enumerate(("chi", "K", "lapse")):
        y = prof[:, 1 + i * nsh:1 + (i + 1) * nsh].copy()
        y[np.abs(y) > 1e29] = np.nan          # shells the fine mask never covered
        blk[name] = y
    return t, rr, blk


def _read_scans(paths) -> list[tuple[float, int, float, float]]:
    """(t, level, neck coordinate r, neck areal R) per scan block.

    A block can report several 'areal-radius minimum (throat)' lines -- grid
    noise at small r fakes minima with R in the hundreds -- so the neck is the
    minimum with the SMALLEST areal radius.
    """
    head = re.compile(r"BinaryWormholePlt\d+\s+t=([\d.]+)\s+.*level=(\d)")
    line = re.compile(r"areal-radius minimum \(throat\) at r = ([\d.]+): R = ([\d.]+)")
    out, cur = [], None
    for path in paths:
        for ln in pathlib.Path(path).read_text().splitlines():
            m = head.search(ln)
            if m:
                if cur and cur[2] is not None:
                    out.append(cur)
                cur = [float(m.group(1)), int(m.group(2)), None, None]
                continue
            m = line.search(ln)
            if m and cur is not None:
                r, R = float(m.group(1)), float(m.group(2))
                if cur[3] is None or R < cur[3]:
                    cur[2], cur[3] = r, R
        if cur and cur[2] is not None:
            out.append(cur)
            cur = None
    return [tuple(c) for c in out]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    camp = pack / "campaign" / GROUP
    arm = camp / ARM

    d = _sorted(arm / "collapse_diagnostics.dat")
    d = d[d[:, 0] >= d[0, 0] + SETTLE]
    t = d[:, 0]
    col = {n: d[:, i + 1] for i, n in enumerate(COLS)}
    cn = _sorted(arm / "constraint_norms.dat")
    cn = cn[cn[:, 0] >= t[0]]
    t_end = float(t[-1])

    # The unfrozen legs of the glued series only: leg 3 (t > t_end) is frozen.
    b = _sorted(camp / SERIES / "binary_throat_diagnostics.dat")
    b = b[(b[:, 0] <= t_end) & ~((b[:, 0] > HANDOVER) & (b[:, 0] < HANDOVER + 4 * SETTLE))]
    ts, sep = b[:, 0], b[:, 1]

    fz = _params(camp / FREEZE / "evolution_params.txt")
    t_freeze = float(fz["core_fill_from_time"])
    r_fill = float(fz["core_fill_radius_start"])
    t_last = float(_sorted(camp / FREEZE / "collapse_diagnostics.dat")[-1, 0])
    r_star = _r_star(float(fz["wormhole_throat_radius_A"]),
                     float(fz["wormhole_drainhole_mass_A"]))

    pt, rr, blk = _read_profile(arm / "core_radial_profile.dat.gz")
    dr = float(rr[1] - rr[0])
    scans = _read_scans([arm / "horizon_oriented_scan_t55-57.txt",
                         arm / "horizon_oriented_scan_t58-60.txt"])

    # ---- derived events, printed for the caption --------------------------
    i_fl = int(np.argmax(np.nanmin(blk["chi"], axis=1) <= CHI_FLOOR * 1.01))
    t_floor = float(pt[i_fl])
    i_tr = int(np.argmax(cn[:, 2]))
    t_trans = float(cn[i_tr, 0])

    K = blk["K"]
    pk = np.nanargmax(np.where(np.isnan(K), -np.inf, K), axis=1)
    vpk = K[np.arange(len(pt)), pk]
    bg = K[:, int(0.4 / dr)]
    real = vpk > 2.0 * bg
    t_spike = float(pt[np.argmax(real & (pt > 45.0))])
    edge = np.array([rr[np.where(K[k] > EDGE_K)[0].max()]
                     if (K[k] > EDGE_K).any() else np.nan for k in range(len(pt))])
    i_wide = int(np.nanargmax(edge))

    def logc(a, v):
        a, v = np.log10(np.maximum(a, 1e-300)), np.log10(np.maximum(v, 1e-300))
        return float(np.corrcoef(a, v)[0, 1])

    m40 = t >= 40.0
    hh = np.interp(t, cn[:, 0], cn[:, 1])
    mm = np.interp(t, cn[:, 0], cn[:, 2])
    corr_h, corr_m = logc(col["max_abs_K"][m40], hh[m40]), logc(col["max_abs_K"][m40], mm[m40])
    abs_phi = np.maximum(np.abs(col["min_phi"]), np.abs(col["max_phi"]))
    abs_pi = np.maximum(np.abs(col["min_Pi"]), np.abs(col["max_Pi"]))
    sep_at = {tv: float(np.interp(tv, ts, sep)) for tv in (50.0, 55.0, 57.0, t_floor)}

    print(f"[spiral collapse] window t = {t[0]:.2f}-{t_end:.2f}; "
          f"transient peak t = {t_trans:.2f} (H {cn[:,1].max():.2e}, M {cn[:,2].max():.2e}); "
          f"chi on {CHI_FLOOR:g} floor from t = {t_floor:.2f}; "
          f"min lapse {col['min_lapse'].min():.2e}; max|K| peak {col['max_abs_K'].max():.2f}; "
          f"max|phi| {abs_phi.max():.2f}, max|Pi| {abs_pi.max():.2f}")
    print(f"  spike real from t = {t_spike:.2f}; edge widest {np.nanmax(edge):.3f} "
          f"at t = {pt[i_wide]:.2f}; corr after t=40: K-H {corr_h:+.2f}, K-M {corr_m:+.2f}")
    print("  pit separation " + ", ".join(f"{v:.3f} at t = {k:.2f}" for k, v in sep_at.items())
          + f"; {sep[-1]:.3f} at t = {ts[-1]:.2f}")
    print(f"  freeze armed t = {t_freeze:g}, fill r <= {r_fill:g}, frozen leg to t = {t_last:.2f}; "
          f"R_star = {r_star:.4f}, sqrt(2) R_star = {math.sqrt(2) * r_star:.3f}")
    for tv, lv, r0, R0 in scans:
        print(f"  scan t = {tv:.0f} level {lv}: neck r = {r0:.3f}, R = {R0:.3f}")

    # ---- the strip -----------------------------------------------------------
    style.prd(base=10.0)
    W, H = 7.05, 4.3
    fig = plt.figure(figsize=(W, H))

    def box(x0, y0, w, h, **kw):
        return fig.add_axes([x0 / W, y0 / H, w / W, h / H], **kw)

    top_y, top_h = 2.52, 1.50
    bot_y, bot_h = 0.44, 1.46
    axA = box(0.56, top_y, 3.92, top_h)
    axB1 = box(5.18, top_y, 1.28, top_h)
    axB2 = box(6.52, top_y, 0.42, top_h, sharey=axB1)
    # the two bottom panels share the width three used to (4.62 = 3 x 1.74 + 0.59
    # less the gap), so the core's five extrema get the room they need
    xw, gap = 2.905, 0.59
    axC = box(0.56, bot_y, xw, bot_h)
    axE = box(0.56 + xw + gap, bot_y, xw, bot_h)

    def tag(ax, letter):
        ax.text(0.0, 1.045, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    def rules(ax, trans=True, floor=True):
        if trans:
            ax.axvline(t_trans, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
        if floor:
            ax.axvline(t_floor, color=style.FAINT, lw=0.7, ls=(0, (1, 2)), zorder=1)

    shade = dict(color=style.GRID, lw=0, zorder=0)

    # (a) the whole history ----------------------------------------------------
    live = ts <= t_floor
    axA.axvspan(t_freeze, t_last + 1.0, **shade)
    axA.semilogy(ts[live], sep[live], color=style.INK, lw=1.2, zorder=3)
    axA.semilogy(ts[~live], sep[~live], color=style.CONTEXT, lw=1.0, zorder=3)
    axA.plot([ts[-1]], [sep[-1]], ls="none", marker="x", ms=5, mew=1.3,
             color=style.INK, zorder=4)
    axA.axvline(HANDOVER, color=style.FAINT, lw=0.7, zorder=1)
    axA.axvline(t_trans, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
    axA.set_xlim(-1.5, t_last + 1.0)
    axA.set_ylim(0.075, 22)
    axA.set_ylabel(r"pit separation $d$")
    axA.set_xlabel(r"$t$")
    axA.text(1.5, 0.62, r"separation of the two $\chi$ pits", fontsize=8,
             ha="left", va="top", color=style.INK)
    # Where the flow finder has a common MOTS on the record: the same slices
    # as (b), open for the arm evolved at level 5 from t = 0.
    rug = 15.0
    for tv, _, own in FLOW_MOTS:
        axA.plot(tv, rug, ls="none", marker="D", ms=3.0, mec=style.GOLD, mew=0.9,
                 mfc=style.GOLD if own else style.GROUND, zorder=5)
    for tv, _ in REMNANT_MOTS:
        axA.plot(tv, rug, ls="none", marker="D", ms=3.0, mec=style.GOLD, mew=0.9,
                 mfc=style.GOLD, zorder=5)
    axA.text(61.8, rug, "common MOTS", fontsize=7.5, ha="left", va="center",
             color=style.GOLD)
    axA.text(HANDOVER - 0.8, 0.10, "level\n3 $\\to$ 5", fontsize=7.5, ha="right",
             va="bottom", color=style.MUTED, linespacing=1.15)
    axA.text(t_trans + 0.8, 5.0, "merger\ntransient", fontsize=7.5, ha="left",
             va="center", color=style.MUTED, linespacing=1.15)
    axA.text(ts[-1] + 1.2, sep[-1] * 0.95, "wall", fontsize=7.5, ha="left",
             va="center", color=style.INK)
    axA.text(0.5 * (t_freeze + t_last) + 3.0, 5.0,
             f"core frozen ($r\\leq{r_fill:g}$)\nfrom $t={t_freeze:g}$;\n"
             f"live exterior to $t={t_last:.0f}$",
             fontsize=7.5, ha="center", va="center", color=style.MUTED,
             linespacing=1.25)
    tag(axA, "a")

    # (b) areal radii: birth window | remnant ----------------------------------
    axB2.axvspan(96.0, 102.0, **shade)
    for ax in (axB1, axB2):
        ax.axhline(r_star, color=style.MUTED, lw=0.8, ls=(0, (1, 2)), zorder=1)
        ax.axhline(math.sqrt(2) * r_star, color=style.MUTED, lw=0.8,
                   ls=(0, (1, 2)), zorder=1)
    for lv, mfc in ((3, style.GROUND), (5, style.INK)):
        pts = [(tv, R0) for tv, l, r0, R0 in scans if l == lv]
        if pts:
            xs, ys = zip(*pts)
            axB1.plot(xs, ys, ls="none", marker="o", ms=3.6, mfc=mfc,
                      mec=style.INK, mew=1.0, zorder=5)
    for tv, Rv, own in FLOW_MOTS:
        axB1.plot(tv, Rv, ls="none", marker="D", ms=3.8,
                  mfc=style.GOLD if own else style.GROUND, mec=style.GOLD,
                  mew=1.1, zorder=6)
    for tv, Rv in REMNANT_MOTS:
        axB2.plot(tv, Rv, ls="none", marker="D", ms=3.8, mfc=style.GOLD,
                  mec=style.GOLD, mew=1.1, zorder=6)
    axB1.set_xlim(54.4, 60.9)
    axB2.set_xlim(97.4, 100.6)
    axB1.set_ylim(3.72, 5.86)
    axB1.set_xticks([55, 57, 59])
    axB2.set_xticks([98, 100])
    axB1.spines["right"].set_visible(False)
    axB2.spines["left"].set_visible(False)
    axB1.tick_params(axis="y", which="both", right=False)
    axB2.tick_params(axis="y", which="both", left=False, right=True, labelleft=False)
    brk = dict(marker=[(-1, -2.2), (1, 2.2)], markersize=6, linestyle="none",
               color=style.INK, mec=style.INK, mew=0.8, clip_on=False)
    axB1.plot([1, 1], [0, 1], transform=axB1.transAxes, **brk)
    axB2.plot([0, 0], [0, 1], transform=axB2.transAxes, **brk)
    axB1.set_ylabel(r"areal radius $R$")
    fig.text((5.18 + 6.94) / 2 / W, (top_y - 0.27) / H, r"$t$", ha="center",
             va="center", fontsize=10, color=style.INK)
    axB1.text(54.7, 5.07, "common MOTS", fontsize=7.0, ha="left", va="bottom",
              color=style.GOLD)
    # Open circles level 3, filled level 5 (the caption says so): the two
    # agree to 0.2 %, so the level-3 ring hides under the level-5 disc.
    axB1.text(56.85, 4.085, "common neck", fontsize=7.0, ha="left", va="bottom",
              color=style.INK)
    axB2.text(99.0, 4.33, "remnant", fontsize=7.0, ha="center", va="bottom",
              color=style.INK)
    style.edge_label(axB2, r_star, r"$R_\star$", fontsize=7.5)
    style.edge_label(axB2, math.sqrt(2) * r_star, r"$\sqrt{2}R_\star$", fontsize=7.5)
    tag(axB1, "b")

    # (c) core extrema ---------------------------------------------------------
    axC.semilogy(t, col["min_chi"], color=style.INK, lw=1.1)
    axC.semilogy(t, col["min_lapse"], color=style.INK, lw=1.1, ls=(0, (5, 2)))
    axC.semilogy(t, abs_phi, color=style.MUTED, lw=1.0, ls=(0, (1.2, 1.6)))
    axC.semilogy(t, abs_pi, color=style.MUTED, lw=1.0)
    axC.semilogy(t, col["max_abs_K"], color=style.INK, lw=1.3, ls=(0, (5, 1.6, 1, 1.6)))
    axC.axhline(CHI_FLOOR, color=style.FAINT, lw=0.7, ls=(0, (1, 2)))
    axC.set_ylim(3e-9, 150)
    axC.set_yticks([1e-8, 1e-6, 1e-4, 1e-2, 1])
    axC.set_ylabel("core extrema")
    axC.text(37.0, 2.2e-5, r"$\min\chi$", fontsize=7.5, ha="left", va="bottom",
             color=style.INK)
    axC.text(46.0, 5.5e-3, r"$\min\alpha$", fontsize=7.5, ha="left", va="bottom",
             color=style.INK)
    axC.text(43.5, 1.35, r"$\max|\phi|$", fontsize=7.5, ha="left", va="bottom",
             color=style.MUTED)
    axC.text(55.2, 7.0, r"$\max|\Pi|$", fontsize=7.5, ha="right", va="bottom",
             color=style.MUTED)
    axC.text(44.0, CHI_FLOOR * 1.6, "floor", fontsize=7.0, ha="left",
             va="bottom", color=style.MUTED)
    # Under its own climb, in the empty two decades above min alpha.
    axC.annotate(r"$\max|K|$", (51.0, float(np.interp(51.0, t, col["max_abs_K"]))),
                 xytext=(0, -4), textcoords="offset points", fontsize=7.5,
                 ha="center", va="top", color=style.INK)

    for ax in (axC,):
        rules(ax)
        ax.set_xlim(t[0] - 0.6, t_end + 0.6)
        ax.set_xlabel(r"$t$")

    # (e) the wall rides the neck ---------------------------------------------
    ok = real & (pt >= t_spike)
    axE.plot(pt[ok], rr[pk[ok]], color=style.INK, lw=1.1)
    axE.plot(pt, edge, color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    r_scan = {}
    for tv, lv, r0, R0 in scans:          # level 5 wins where both scanned
        if tv not in r_scan or lv > r_scan[tv][0]:
            r_scan[tv] = (lv, r0, R0)
    t_sc = sorted(r_scan)
    axE.plot(t_sc, [r_scan[tv][1] for tv in t_sc], ls="none", marker="o",
             ms=3.6, mfc=style.INK, mec=style.INK, mew=1.0, zorder=5)
    rules(axE, trans=False)
    axE.set_xlim(48.4, t_end + 0.7)
    axE.set_ylim(0.55, 1.55)
    axE.set_xlabel(r"$t$")
    axE.set_ylabel(r"coordinate radius $r$")
    axE.text(49.0, 1.42, "edge, $|K|>0.2$", fontsize=7.5, ha="left",
             va="bottom", color=style.MUTED)
    axE.text(50.0, 1.05, r"peak of $|K|$", fontsize=7.5, ha="left",
             va="top", color=style.INK)
    axE.text(56.3, 0.855, "neck", fontsize=7.5, ha="center",
             va="top", color=style.INK)

    for ax, letter in ((axC, "c"), (axE, "d")):
        tag(ax, letter)

    hits = style.label_audit(fig)
    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "p012_collapse_diagnostics.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[spiral collapse] wrote {png} (+pdf); 4 panels, {len(scans)} scan rows; "
          f"label audit: {len(hits)} hit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
