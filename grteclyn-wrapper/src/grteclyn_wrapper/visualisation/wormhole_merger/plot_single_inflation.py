#!/usr/bin/env python3
r"""The inflating throat, on one page (the paper's Fig. single_inflation): F4 only.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_inflation

F4 is ``campaign/01_single_throat/seed/single_eps_m1e2_L512_ml5_oct_t400`` in the
pack: eps = -1e-2, L = 512, max_level 5, on an octant, the neck's areal radius in
the FULL metric.  Every panel stops at T_WALL = 218, F4's trust limit (also in
results/merger/trust_windows.tsv): the paper shows the quotable record only.  No
level-4 data (2026-09-26, the user): those arms' radii are r / sqrt(chi), a lower
bound once the grid has moved.  The arm's method -- the record's cut, the onset
fit, Shinkai-Hayward's window and fit, the theta_k track -- is imported from
``plot_single_inflation_L512``, as the claims ledger imports it.

(a) the neck's areal radius; gold, the onset fit R0 (1 + A e^(t/T)), solid over
    its window and dashed on (extrapolated); shaded, the Shinkai-Hayward window
    (faint gold) and, after it, the slower growth in t once 1+log freezes the
    neck's clock (grey).
(b) Shinkai-Hayward's test: R/R0 - 1 against the neck's proper time, their
    1 + A e^(H tau) fitted over the window (shaded), their massless H a = 1.1 and
    the linear mode drawn from the window's start.
(c) the trapping horizons bounding the anti-trapped throat: theta_k = 0 (gold,
    to its first jump at t = 212) and theta_l = 0 on the neck (gold dotted).
(d) the lapse at the neck and, dashed, min alpha on the finest box; (e) max |K|
    and (f) min chi on the finest box.  collapse_diagnostics.dat reduces over the
    FINEST LEVEL only (BinaryWormholeLevel.cpp, state_fine): the level-5 box about
    the origin, the far side's compactified infinity, which the neck leaves at
    t = 44.  So these are the core's values, labelled so: max |K| there is not the
    global maximum (the shell profiles reach |K| 0.14 at r ~ 39 by t = 200).
(g), (h) chi and alpha per shell of core_radial_profile.dat, r <= 60 (the neck
    migrates from x = 1.6 to 38), t = 0-200 every 40 u, a grey ramp, light =
    early.  Not t = 218: there the r = 20 shell's lapse sits on the code's floor
    (1e-10), a one-shell spike.  F4's L2 constraint norms, once panel (i) here,
    are panel (d) of the appendix's code-health figure
    (``plot_constraint_evolution``, 2026-09-26).

Writes ``figures/01_single_throat/single_throat_inflation``.

STYLE: the PRD frame; a key ABOVE every panel names each line
(``style.legend_top``), letter tags at the keys' left (``style.tag_keys``), no
text inside a frame, an end dot on a record that stops inside its frame.  GOLD
only for the fits, the Shinkai-Hayward window and the horizons; the rest ink and
grey.  ``style.label_audit`` is printed.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import plot_single_inflation_L512 as f4  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "01_single_throat"
SNAPS = (0.0, 40.0, 80.0, 120.0, 160.0, 200.0)   # shell profiles, light = early
RAMP = (style.FAINT, "#8f8b81", "#6f6c64", "#54524c", "#37352f", style.INK)
R_SHELL = 60.0                                    # the neck reaches x = 38 by t = 218
DASH = (0, (4, 2.5))
DOT = (0, (1.2, 1.8))


def _patch(shade: dict) -> Patch:
    """A key handle for an axvspan drawn with ``shade``."""
    return Patch(**{k: v for k, v in shade.items() if k != "zorder"})


def _plain_log(ax, ticks) -> None:
    """Plain-number major ticks on a log axis that spans under two decades."""
    lo, hi = ax.get_ylim()
    ax.yaxis.set_major_locator(FixedLocator([v for v in ticks if lo <= v <= hi]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(NullFormatter())


def _shells(path: pathlib.Path, times, fields=("chi_min", "lapse_min")):
    """Radii and, per field, one profile row per requested time from
    core_radial_profile.dat (~200 MB: only the wanted rows are parsed)."""
    with open(path) as fh:
        names: list[str] = []
        for line in fh:
            if not line.startswith("#"):
                break
            names = line.lstrip("#").split()
    idx = {f: [i for i, nm in enumerate(names) if nm.startswith(f + "_r")] for f in fields}
    r = np.array([float(names[i].split("_r")[-1]) for i in idx[fields[0]]])
    rows: dict[float, np.ndarray] = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            tt = float(line.split(maxsplit=1)[0])
            for w in times:
                if w not in rows and abs(tt - w) < 0.03:
                    rows[w] = np.array(line.split(), dtype=float)
            if len(rows) == len(times):
                break
    return r, {f: {w: v[idx[f]] for w, v in rows.items()} for f in fields}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run = f4.f4_dir(args.pack_root)

    # ---- F4, to its trust limit --------------------------------------------
    # T_WALL (218) is F4's trust limit, also held per run in
    # results/merger/trust_windows.tsv (closeout.sh cuts the movies there)
    rec = f4.record(run)
    T = f4.T_WALL
    nh, cd, cn = (a[a[:, 0] <= T + 1e-9] for a in (rec["nh"], rec["cd"], rec["cn"]))
    # cn stays read: the console line below quotes H at both ends
    t, R, a_nk, R_hl, R_hk = nh[:, 0], nh[:, 2], nh[:, 5], nh[:, 10], nh[:, 14]
    on = f4.onset_fit(t, R)
    sh = f4.sh_fit(t, R, a_nk)
    kk, jumped = f4.theta_k_track(R_hk)
    r_sh, prof = _shells(run / "core_radial_profile.dat", SNAPS)
    R0 = on["R0"]

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 5.6), constrained_layout=True)
    # the strip over a row of four panels and a row of three
    # One sub-grid per row: on a shared 12-column grid the rows' column edges
    # (3/6/9 against 4/8) do not line up, and constrained layout, which keeps
    # one margin per column, collapsed the axes to zero.
    gs = fig.add_gridspec(3, 1, height_ratios=[1.15, 1.0, 1.0])
    axT = fig.add_subplot(gs[0])
    row2, row3 = gs[1].subgridspec(1, 4), gs[2].subgridspec(1, 3)
    axs = ([fig.add_subplot(row2[0, i]) for i in range(4)]
           + [fig.add_subplot(row3[0, i]) for i in range(3)])
    aSH, aHZ, aLap, aK, aChi, aChiR, aLapR = axs
    for ax in (axT, aHZ, aLap, aK, aChi):
        ax.set_xlim(0, T)          # the frame ends where the quoted record ends
        ax.set_xlabel(r"$t$")

    # ---- (a) the neck, its onset, and where Shinkai-Hayward holds -----------
    axT.axvspan(sh["t0"], sh["t1"], **f4.SH_SHADE)
    axT.axvspan(sh["t1"], T, **f4.SLOW_SHADE)
    neck = axT.plot(t, R, color=style.INK, linewidth=1.4, zorder=4)[0]
    axT.set_ylim(3.0, R.max() + 0.08 * (R.max() - 3.0))
    tf = np.linspace(on["t0"], on["t1"], 60)
    fit = axT.plot(tf, R0 * (1.0 + on["A"] * np.exp(tf / on["T"])), color=style.GOLD,
                   linewidth=1.9, zorder=5, solid_capstyle="butt")[0]
    t_top = on["T"] * np.log((axT.get_ylim()[1] / R0 - 1.0) / on["A"])
    te = np.linspace(on["t1"], t_top, 80)
    ext = axT.plot(te, R0 * (1.0 + on["A"] * np.exp(te / on["T"])), color=style.GOLD,
                   linewidth=1.3, linestyle=DASH, zorder=5)[0]
    axT.set_ylabel(r"$R_{\rm areal}$")
    style.legend_top(axT, [
        (neck, rf"neck, full metric (quoted to $t={t[-1]:.0f}$)"),
        (fit, rf"fit $R_0(1+Ae^{{t/T}})$, $T={on['T']:.1f}$, $t={on['t0']:.0f}$–${on['t1']:.0f}$"),
        (ext, "fit, extrapolated"),
        (_patch(f4.SH_SHADE), rf"Shinkai–Hayward rate ($t={sh['t0']:.0f}$–${sh['t1']:.0f}$)"),
        (_patch(f4.SLOW_SHADE), r"slower in $t$: $1{+}\log$ freezes the neck's clock")], ncol=3)

    # ---- (b) Shinkai-Hayward in the neck's proper time ---------------------
    y, tau = sh["y"], sh["tau"]
    mv = y > 0.01
    aSH.axvspan(sh["tau0"], sh["tau1"], **f4.SH_SHADE)
    keyB = [(aSH.plot(tau[mv], y[mv], color=style.INK, linewidth=1.3, zorder=3)[0], "neck")]
    i0 = int(np.flatnonzero(sh["mask"])[0])
    tt = tau[i0:]
    yf = np.exp(sh["lnA"] + sh["H"] * tt)
    keyB.append((aSH.plot(tt, yf, color=style.GOLD, linewidth=1.3, linestyle=DASH,
                          zorder=4)[0], rf"fit, $HR_0={sh['H'] * R0:.2f}$"))
    ytop = max(float(y[mv].max()), float(yf.max()))
    for hh, ls, lab in ((1.1 / R0, "solid", r"SH, $Ha=1.1$"),
                        (sh["H_linear"], DOT, rf"linear, $HR_0={sh['H_linear'] * R0:.2f}$")):
        yy = y[i0] * np.exp(hh * (tt - tau[i0]))
        ytop = max(ytop, float(yy.max()))
        keyB.append((aSH.plot(tt, yy, color=style.CONTEXT, linewidth=1.0, linestyle=ls,
                              zorder=2)[0], lab))
    keyB.append((_patch(f4.SH_SHADE), "SH window"))
    aSH.set_yscale("log")
    aSH.set_xlim(tau[mv][0] - 0.5, tau[-1])
    aSH.set_ylim(0.01, 1.8 * ytop)
    aSH.set_xlabel(r"$\tau$ (neck)")
    aSH.set_ylabel(r"$R/R_0-1$")
    style.legend_top(aSH, keyB, ncol=1, handlelength=1.6)

    # ---- (c) the horizons bounding the anti-trapped throat -----------------
    fl = np.isfinite(R_hl)
    t_hk = float(t[kk[-1]])
    keyC = [(aHZ.plot(t[kk], R_hk[kk], color=style.GOLD, linewidth=1.4, zorder=3)[0],
             rf"$\theta_k=0$, to $t={t_hk:.0f}$")]
    if jumped:
        aHZ.plot(t[kk[-1]], R_hk[kk[-1]], linestyle="none", marker="o", markersize=2.8,
                 color=style.GOLD, zorder=3)
    keyC.append((aHZ.plot(t[fl], R_hl[fl], color=style.GOLD, linewidth=1.3, linestyle=DOT,
                          zorder=4)[0], r"$\theta_l=0$"))
    keyC.append((aHZ.plot(t, R, color=style.INK, linewidth=1.2, zorder=2)[0], "neck"))
    aHZ.set_yscale("log")
    aHZ.set_ylim(0.85 * np.nanmin(np.r_[R, R_hl[fl], R_hk[kk]]),
                 1.35 * np.nanmax(np.r_[R, R_hl[fl], R_hk[kk]]))
    _plain_log(aHZ, (2, 5, 10, 20, 50, 100, 200))
    aHZ.set_ylabel(r"$R_{\rm areal}$")
    style.legend_top(aHZ, keyC, ncol=1, handlelength=1.6)

    # ---- (d) the lapse; (e) max|K| and (f) min chi on the finest box --------
    keyD = [(aLap.plot(t, a_nk, color=style.INK, linewidth=1.2, zorder=3)[0],
             r"$\alpha$ at the neck"),
            (aLap.plot(cd[:, 0], cd[:, 1], color=style.MUTED, linewidth=1.0, linestyle=DASH,
                       zorder=2)[0], r"$\min\alpha$, finest box")]
    aLap.set_yscale("log")
    aLap.set_ylabel(r"$\alpha$")
    style.legend_top(aLap, keyD, ncol=1)
    style.legend_top(aK, [(aK.plot(cd[:, 0], cd[:, 3], color=style.INK, linewidth=1.1,
                                   zorder=3)[0], r"$\max|K|$, finest box")], ncol=1)
    aK.set_ylabel(r"$|K|$")
    style.legend_top(aChi, [(aChi.plot(cd[:, 0], cd[:, 2], color=style.INK, linewidth=1.1,
                                       zorder=3)[0], r"$\min\chi$, the origin")], ncol=1)
    aChi.set_yscale("log")
    aChi.set_ylabel(r"$\chi$")

    # ---- (g)/(h) chi and the lapse per shell, light = early ------------------
    m = r_sh <= R_SHELL
    for ax, field, lab in ((aChiR, "chi_min", r"$\chi$ per shell"),
                           (aLapR, "lapse_min", r"$\alpha$ per shell")):
        snaps = [(ax.plot(r_sh[m], prof[field][ts][m], color=c, linewidth=1.0, zorder=3)[0],
                  f"{ts:g}") for c, ts in zip(RAMP, SNAPS) if ts in prof[field]]
        ax.set_yscale("log")
        ax.set_xlim(0, R_SHELL)
        ax.set_xlabel(r"$r$")
        ax.set_ylabel(lab)
        style.legend_top(ax, snaps, ncol=3, title=r"$t=$", title_fontsize=6.5,
                         alignment="left", handlelength=1.2)

    fig.align_ylabels([axT, aSH, aChiR])
    style.tag_keys(fig, [axT] + axs, [f"({c})" for c in "abcdefgh"], row="last")

    grow = np.diff(R)
    print(f"[single-inflation] F4 to t = {t[-1]:.0f}: neck R {R0:.3f} -> {R[-1]:.3f} "
          f"(x{R[-1] / R0:.3f}), rising at {int((grow > 0).sum())} of {grow.size} steps; "
          f"onset fit t = {on['t0']:.0f}-{on['t1']:.0f}: T = {on['T']:.3f}; extrapolated to "
          f"t = {t_top:.1f}")
    print(f"[single-inflation] SH window t = {sh['t0']:.0f}-{sh['t1']:.0f} (tau "
          f"{sh['tau0']:.2f}-{sh['tau1']:.2f}), local H R0 "
          f"{np.nanmin(sh['local'][sh['mask']]):.3f}-{np.nanmax(sh['local'][sh['mask']]):.3f}; "
          f"fit H R0 = {sh['H'] * R0:.4f}; linear mode {sh['H_linear'] * R0:.3f}; proper time "
          f"from t = {sh['t1']:.0f} to {t[-1]:.0f}: {tau[-1] - sh['tau1']:.2f}")
    print(f"[single-inflation] theta_k to t = {t_hk:.0f} at R = {R_hk[kk[-1]]:.2f}; theta_l "
          f"- neck at t = {t[-1]:.0f}: {R_hl[-1] - R[-1]:+.3f}; alpha_neck {a_nk[0]:.3f} -> "
          f"{a_nk[-1]:.4f}; global min alpha {cd[-1, 1]:.2e}; min chi {cd[0, 2]:.2e} -> {cd[-1, 2]:.2e}; "
          f"L2 H {cn[0, 1]:.2e} -> {cn[-1, 1]:.2e}")
    hits = style.label_audit(fig)
    print(f"[single-inflation] label audit: {len(hits)} overlaps")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation.png")
    png = style.save(fig, out)
    print(f"[single-inflation] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
