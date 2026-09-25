"""The kicked throat's inflation record in the causally disconnected box -- the F4 arm.

The sibling of ``plot_single_inflation_L128`` (the unkicked L = 128 t500 arm,
whose turn at t = 161 is the cube wall's reflection of the 1+log gauge wave,
GPU_PLAN 2026-09-25 06:30) for ``single_eps_m1e2_L512_ml5_oct_t400``: the
eps = -1e-2 kicked throat in an L = 512 box, max_level 5 (finest dx 1/16), 1+log
slicing, the wall causally disconnected from the neck to t ~ 340, evolved on
the octant [0, 256]^3 with mirror planes x = y = z = 0 (F1b's physics; F1b
itself was wiped 2026-09-25).  Reads the RUN TREE while the arm is live
(regenerate at will; ``--run`` takes the pack folder after landing).

EVERY RADIUS IS THE PROPER AREAL RADIUS, R = r (h22 h33)^(1/4) / sqrt(chi): the
area of the coordinate sphere through the neck with the full conformal
metric.  The flat estimate r / sqrt(chi), which every earlier page of the
campaign drew, is a lower bound once the Gamma-driver shift has moved the
grid (h22 = 1.35 at the neck by t = 64) and is kept only as the dashed
reference line.

WHAT THE PANELS SAY
(a) R at the neck against t: the consumer's ``--neck-horizons`` record (the
    minimum of R on the +x ray, tracked from the previous plotfile, one per
    plotfile, every 2 u), with r / sqrt(chi) at the same neck dashed and the
    unkicked L = 128 arm beneath as a CONTEXT line (its t500 record has only
    r / sqrt(chi); a different seed, truncation noise, so it inflates 40 u
    later).  Stage lines: R = 1.1 R0, and the coordinate neck leaving
    each refinement box (the faces read off the plotfile headers, not the
    nominal tag half-widths: the boxes are the tagged cube around the tracked
    chi pit, rounded up by the error buffer and the blocking factor).
(b) Shinkai-Hayward's test: R/R0 - 1 against the neck's proper time on a
    log axis, where their fit r/a = 1 + b4 exp(H (tau - b5)) is a straight
    line; that form fitted (H free) over the onset only (the neck's lapse
    above half its t = 0 value) and drawn on, beside their massless value
    H a = 1.1 and the paper's linear mode converted to throat proper time
    (e-fold 5.13 t times the static throat lapse); the late local rate is
    quoted separately, since 1+log freezes the clock at the neck.
(c) the invariant record: the areal radii of the two trapping horizons
    bounding the anti-trapped throat region (theta_k = 0 on our side, solid;
    theta_l = 0 on the other side, dotted), the neck (squares) and its
    r / sqrt(chi) estimate (dashed).  Inside an inflating throat R is a time
    function and the neck is where the slice happens to be tangent to an
    R = const sphere -- slicing-dependent; the horizons are not.  A static
    throat is its own degenerate double horizon, so both start ON the neck.
    Rates over the last 10 u, per unit t and per unit local proper time.
(d) alpha at the neck (INK) and the global min alpha (MUTED), log scale.
(e) the arm's own L2 norms, H solid and M dashed, log scale.

SOURCES (the run tree; ``--run`` either layout):
``small_data/neck_horizons.dat`` (time | x_neck | R_neck | R_neck_flat |
h22_neck | alpha_neck | rate_neck | M_MS_neck | phi_neck | x_hl | R_hl |
alpha_hl | M_hl | x_hk | R_hk | alpha_hk | M_hk), ``data/collapse_diagnostics.dat``,
``data/constraint_norms.dat``; the context arm from the pack,
``campaign/01_single_throat/seed/single_pureq_q1e2_L128_ml4_scalar_t500/``.
Not ``areal_radius.dat``: it is the GLOBAL minimum along the ray beyond
r = 0.5, which falls onto the compactified other end's chi plateau from t = 60
(R 8.98 at r = 0.53 at t = 64, while the neck is at x = 9.8, R 10.90).

STYLE: house (style.prd); INK = the live arm, CONTEXT = the L = 128 arm,
letter tags above the frames; labels placed off the drawn curves and checked
by ``style.label_audit`` (printed, not fatal: the run is live and the
picture moves).
"""

from __future__ import annotations

import argparse
import os
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT,
    REPO,
    figure_dir,
)

GROUP = "01_single_throat"
RUN = "runs/wormhole_merger/single_eps_m1e2_L512_ml5_oct_t400"
CONTEXT_RUN = "seed/single_pureq_q1e2_L128_ml4_scalar_t500"
# The refinement boxes' outer faces along each axis, finest first, from the
# plotfile headers (F3 at t = 46, F4 at t = 66): tagging_L 256 tags
# |x - c| < 256 * 2^-(l+1) about the tracked chi pit c, and the error buffer
# and the blocking factor round each box up.  Level 5 reaches x = 5 until the
# pit has drifted to c = 0.88 (t ~ 66, long after the neck left it), then 6.
BOXES = ((5, 5.0), (4, 10.0), (3, 20.0), (2, 40.0), (1, 80.0))
# the window of the late rates quoted in (c)
RATE_WINDOW = 10.0


def _dedup(a: np.ndarray) -> np.ndarray:
    """First row per time (the streams re-log a step on restarts)."""
    _, idx = np.unique(a[:, 0], return_index=True)
    return a[idx]


def _src(run: pathlib.Path, name: str) -> pathlib.Path:
    for sub in ("", "small_data", "data"):
        p = run / sub / name
        if p.exists():
            return p
    return run / name


def _first_crossing(t: np.ndarray, y: np.ndarray, level: float) -> float | None:
    """The time y first reaches ``level``, linear between the samples."""
    k = np.flatnonzero(y >= level)
    if not k.size:
        return None
    k = int(k[0])
    if k == 0:
        return float(t[0])
    w = (level - y[k - 1]) / (y[k] - y[k - 1])
    return float(t[k - 1] + w * (t[k] - t[k - 1]))


def _late_rate(t: np.ndarray, R: np.ndarray) -> float | None:
    """d ln R / dt fitted over the last RATE_WINDOW time units."""
    m = (t >= t[-1] - RATE_WINDOW) & np.isfinite(R) & (R > 0)
    if m.sum() < 3:
        return None
    return float(np.polyfit(t[m], np.log(R[m]), 1)[0])


def _dense(ax, px_step: float = 3.0) -> np.ndarray:
    """Every drawn line of ``ax`` densified to ``px_step`` pixels, in axes
    fraction, each line in ITS OWN transform (an axvline is blended)."""
    inv = ax.transAxes.inverted()
    chunks = []
    for line in ax.lines:
        xy = line.get_xydata()
        if xy is None or len(xy) < 2 or not line.get_visible():
            continue
        disp = line.get_transform().transform(np.asarray(xy, dtype=float))
        disp = disp[np.isfinite(disp).all(axis=1)]
        if len(disp) < 2:
            continue
        if line.get_linestyle() in ("None", "none", " ", ""):
            chunks.append(disp)          # markers only
            continue
        seg = np.hypot(*(disp[1:] - disp[:-1]).T)
        for a, b, L in zip(disp[:-1], disp[1:], seg):
            chunks.append(np.linspace(a, b, max(2, int(L / px_step))))
    if not chunks:
        return np.empty((0, 2))
    pts = inv.transform(np.vstack(chunks))
    return pts[np.isfinite(pts).all(axis=1)]


def _place(ax, text: str, candidates, *, pad: float = 0.008, **kw):
    """Put ``text`` at the first of ``candidates`` -- (x, y, ha, va) in axes
    fraction -- whose box covers no drawn sample and no placed label; if
    none is clean, the least-covered one.  Returns the Text."""
    fig = ax.figure
    inv = ax.transAxes.inverted()
    pts = _dense(ax)
    boxes = style._text_boxes(ax)
    best, best_n = None, None
    for x, y, ha, va in candidates:
        txt = ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, **kw)
        fig.canvas.draw()
        box = txt.get_window_extent().transformed(inv)
        n = style._covered(pts, box, pad)
        for b in boxes:
            if box.x0 < b.x1 + pad and box.x1 > b.x0 - pad and box.y0 < b.y1 + pad and box.y1 > b.y0 - pad:
                n += 1000                 # on another label
        if box.x0 < -0.002 or box.x1 > 1.002 or box.y0 < -0.002 or box.y1 > 1.002:
            n += 500                      # spills out of the frame
        if os.environ.get("WHM_PLACE_DEBUG"):
            print(f"[place] {text.splitlines()[0][:30]!r} at ({x:.2f},{y:.2f},{ha},{va}): n={n} box=({box.x0:.2f},{box.y0:.2f})-({box.x1:.2f},{box.y1:.2f})")
        if best is None or n < best_n:
            if best is not None:
                best.remove()
            best, best_n = txt, n
        else:
            txt.remove()
        if n == 0:
            break
    return best


def _rows(x: float, ha: str, top: bool = True, n: int = 5, step: float = 0.1,
          start: float = 0.965):
    """Candidate anchors stacked down from ``start`` (or up from the bottom)."""
    if top:
        return [(x, start - step * k, ha, "top") for k in range(n)]
    return [(x, 0.035 + step * k, ha, "bottom") for k in range(n)]


def _gaps(edges, y: float, va: str):
    """Centre-aligned anchors in the gaps between vertical stage lines (axes
    fraction ``edges``, 0 and 1 included), widest gap first."""
    e = sorted(set([0.0, 1.0] + [float(v) for v in edges]))
    gaps = sorted(zip(e[:-1], e[1:]), key=lambda g: g[0] - g[1])
    return [(0.5 * (a + b), y, "center", va) for a, b in gaps]


CORNERS = [(0.04, 0.95, "left", "top"), (0.96, 0.95, "right", "top"),
           (0.96, 0.05, "right", "bottom"), (0.04, 0.05, "left", "bottom"),
           (0.04, 0.5, "left", "center"), (0.96, 0.5, "right", "center")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--run", default=RUN,
                    help="the run's folder (run tree or pack); a relative path "
                         "resolves against the repo root")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()
    run = pathlib.Path(args.run).expanduser()
    if not run.is_absolute():
        run = REPO / run
    ctx_dir = pack / "campaign" / GROUP / CONTEXT_RUN

    # the neck and the horizons, one x-ray per plotfile (NECK_HORIZONS_HEADER)
    nh = _dedup(np.atleast_2d(np.loadtxt(_src(run, "neck_horizons.dat"))))
    if len(nh) < 2:
        raise SystemExit(f"[single-inflation-L512] {run}: fewer than two neck_horizons rows")
    t = nh[:, 0]
    x_nk, R_nk, R_fl, a_nk = nh[:, 1], nh[:, 2], nh[:, 3], nh[:, 5]
    R_hl, R_hk, a_hk = nh[:, 10], nh[:, 14], nh[:, 15]
    cd = _dedup(np.loadtxt(_src(run, "collapse_diagnostics.dat")))
    cn = _dedup(np.loadtxt(_src(run, "constraint_norms.dat")))
    ctx = None
    if (ctx_dir / "areal_radius.dat").exists():
        ctx = _dedup(np.loadtxt(ctx_dir / "areal_radius.dat"))
        ctx = ctx[(ctx[:, 2] >= 1.0) | (ctx[:, 0] <= 10.0)]  # drop the r = 0.5-cut artifact rows

    t_end = float(t[-1])
    R0 = float(R_nk[0])
    rate_t = np.gradient(np.log(R_nk), t)
    tau = np.concatenate([[0.0], np.cumsum(0.5 * (a_nk[1:] + a_nk[:-1]) * np.diff(t))])
    rate_tau = rate_t / np.maximum(a_nk, 1e-12)

    # stage times
    t_dep = _first_crossing(t, R_nk, 1.1 * R0)
    crossings = []
    for lev, face in BOXES:
        tc = _first_crossing(t, x_nk, face)
        if tc is not None:
            crossings.append((lev, face, tc))
    i_pk = int(np.argmax(rate_t))
    gain = float(R_nk[-1] / R0)
    gain_fl = float(R_fl[-1] / R0)
    t_dbl = _first_crossing(t, R_nk, 2.0 * R0)

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 6.0), constrained_layout=True)
    gs = fig.add_gridspec(3, 6, height_ratios=[1.15, 1.0, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1, 0:3]), fig.add_subplot(gs[1, 3:6]),
           fig.add_subplot(gs[2, 0:3]), fig.add_subplot(gs[2, 3:6])]
    # every axis label and letter tag first: constrained layout resizes the
    # axes for them, and a note placed before that lands somewhere else
    axT.set_xlabel(r"$t$")
    axT.set_ylabel(r"$R_{\rm areal}$")
    axT.text(0.012, 0.93, "(a)", transform=axT.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    for k, (ax, xl, yl) in enumerate(zip(axs, (r"$\tau$ (proper time at the neck)", r"$t$", r"$t$", r"$t$"),
                                         (r"$R/R_0-1$", r"$R$: horizons, neck", r"$\alpha$", r"$L_2$ norms"))):
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.text(0.0, 1.03, f"({'bcde'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    xmax = 5.0 * np.ceil((1.15 * t_end + 2.0) / 5.0)   # a right margin for the live note
    ymax = float(R_nk.max())
    if ctx is not None and (ctx[:, 0] <= xmax).any():
        ymax = max(ymax, ctx[ctx[:, 0] <= xmax, 1].max())
    ylo = 0.45 * R0

    def fx(x):
        return x / xmax

    # ---- (a) the neck ------------------------------------------------------
    if ctx is not None:
        mc = ctx[:, 0] <= xmax
        axT.plot(ctx[mc, 0], ctx[mc, 1], color=style.CONTEXT, linewidth=1.0,
                 zorder=2, solid_capstyle="butt")
    axT.plot(t, R_fl, color=style.MUTED, linewidth=1.0, linestyle=(0, (4, 2.5)), zorder=3)
    axT.plot(t, R_nk, color=style.INK, linewidth=1.2, marker="s", markersize=2.4, zorder=4)
    axT.set_xlim(0, xmax)
    fig.canvas.draw()
    # the captions first, stacked from the top, each under the previous one's
    # measured box (the roots and superscripts make the lines tall); the
    # band's lowest edge then sets the y-limits (every curve stays under it)
    # and where the stage lines stop
    inv = axT.transAxes.inverted()
    captions = [("kicked $\\epsilon=-10^{-2}$, $L=512$ on an octant, level 5, 1+log; "
                 "wall causally disconnected to $t\\simeq340$", dict(fontsize=7, color=style.INK))]
    if ctx is not None:
        captions.append(("grey: the unkicked $L=128$ arm (the t500 record, $r/\\sqrt{\\chi}$ only; "
                         "flat to $t=66$)", dict(fontsize=6.5, color=style.CONTEXT)))
    captions.append(("line, squares: the neck, $R=r\\,(h_{22}h_{33})^{1/4}/\\sqrt{\\chi}$; "
                     "dashed: $r/\\sqrt{\\chi}$, a lower bound once the grid has moved",
                     dict(fontsize=6.5, color=style.MUTED)))
    band = 0.975
    for text, kw in captions:
        txt = axT.text(0.06, band, text, transform=axT.transAxes, ha="left", va="top", **kw)
        fig.canvas.draw()
        band = txt.get_window_extent().transformed(inv).y0 - 0.012
    grow = (f"$t={t_end:.0f}$: $\\times{gain:.2f}$ (full metric)\n"
            f"$\\times{gain_fl:.2f}$ ($r/\\sqrt{{\\chi}}$)")
    axT.text(0.985, 0.975, grow, transform=axT.transAxes, fontsize=6.5, color=style.INK,
             ha="right", va="top", multialignment="right")
    axT.set_ylim(ylo, ylo + (ymax - ylo) / (band - 0.06))
    stage = []
    if t_dep is not None:
        stage.append((t_dep, f"$10\\,\\%$ above $R_0$, $t={t_dep:.0f}$"))
    for lev, face, tc in crossings:
        stage.append((tc, f"neck off level {lev} ($|x|={face:.0f}$), $t={tc:.0f}$"))
    for tc, _ in stage:
        # the stage lines stop under the caption band
        axT.axvline(tc, ymax=band - 0.015, color=style.FAINT, linewidth=0.7, zorder=1)
    fig.canvas.draw()
    # the stage notes (they belong to their lines), each into the first slot
    # beside its line that covers no curve, line or label
    for tc, lab in stage:
        _place(axT, lab,
               _rows(fx(tc) - 0.006, "right", start=band - 0.03, step=0.08)
               + _rows(fx(tc) + 0.008, "left", start=band - 0.03, step=0.08)
               + _rows(fx(tc) - 0.006, "right", top=False, step=0.08)
               + _rows(fx(tc) + 0.008, "left", top=False, step=0.08),
               fontsize=6.5, color=style.MUTED)

    # ---- (b) Shinkai-Hayward in proper time --------------------------------
    # R/R0 - 1 against tau on a log axis: their fit r/a = 1 + b4 exp(H (tau - b5))
    # is a straight line there.  INK: the neck; MUTED dashed: that form fitted
    # (H free) over the ONSET only -- R/R0 - 1 > 0.1 while the neck's lapse is
    # above half its t = 0 value -- and drawn on to the end, so the late
    # departure shows as the neck falling under it; the faint line marks where
    # the clock goes (1+log freezes the lapse at the neck, and tau = int alpha
    # dt at a slicing-dependent neck stops being a clock the comparison can
    # trust).  A single fit over everything averaged the two regimes (local
    # H R0 1.2 early, 0.7 by t = 80) into SH's 1.1.  CONTEXT: their massless
    # value H a = 1.1 and the paper's linear mode (e-fold 5.13 t at the static
    # throat lapse) as slopes through the fit window's first point.
    y = R_nk / R0 - 1.0
    clock = a_nk >= 0.5 * a_nk[0]
    ms = (y > 0.1) & clock
    H_fit = H_late = tau_clock = None
    if ms.sum() >= 4:
        from scipy.optimize import curve_fit  # noqa: PLC0415
        (lnA, H_fit), _ = curve_fit(lambda x, la, hh: la + hh * x, tau[ms], np.log(y[ms]))
        i1 = int(np.flatnonzero(ms)[0])
        tt = tau[i1:]
        axs[0].plot(tt, np.exp(lnA + H_fit * tt), color=style.MUTED, linewidth=1.1,
                    linestyle=(0, (4, 2.5)), zorder=2)
        for hh, ls in ((1.1 / R0, "solid"), (1.0 / (5.13 * a_nk[0]), (0, (1.2, 1.8)))):
            axs[0].plot(tt, y[i1] * np.exp(hh * (tt - tau[i1])), color=style.CONTEXT,
                        linewidth=1.0, linestyle=ls, zorder=1)
        if not clock.all():
            tau_clock = float(tau[np.flatnonzero(~clock)[0]])
            axs[0].axvline(tau_clock, ymin=0.3, color=style.FAINT, linewidth=0.7, zorder=1)  # clear of the bottom notes
        late = ~clock & (y > 0.1)
        if late.sum() >= 5:
            H_late = float(np.polyfit(tau[late][-5:], np.log(y[late][-5:]), 1)[0])
    mv = y > 0.01
    axs[0].plot(tau[mv], y[mv], color=style.INK, linewidth=1.3, zorder=3)
    axs[0].set_yscale("log")
    axs[0].set_xlim(tau[mv][0] - 0.5, tau[-1] + 0.5)
    axs[0].set_ylim(0.01, 30.0 * y[-1])
    fig.canvas.draw()
    if H_fit is not None:
        note = (f"Shinkai--Hayward $1+A\\,e^{{H\\tau}}$ fitted over the onset\n"
                f"($\\alpha_{{\\rm neck}}>\\alpha_0/2$, dashed): $H R_0={H_fit * R0:.2f}$, "
                f"e-fold ${1.0 / H_fit:.1f}\\,\\tau$")
        if H_late is not None:
            note += f"\nlater, lapse freezing: local $H R_0={H_late * R0:.2f}$"
        _place(axs[0], note,
               [(0.04, 0.95, "left", "top"), (0.04, 0.5, "left", "center"), (0.96, 0.05, "right", "bottom")],
               fontsize=6.5, color=style.MUTED, multialignment="left")
        _place(axs[0], f"grey solid: SH massless, $Ha=1.1$\n"
               f"grey dotted: linear mode, $HR_0={R0 / (5.13 * a_nk[0]):.2f}$",
               [(0.96, 0.05, "right", "bottom"), (0.04, 0.78, "left", "top"), (0.04, 0.05, "left", "bottom")],
               fontsize=6.5, color=style.CONTEXT, multialignment="right")

    # ---- (c) the invariant record: the trapping horizons and the neck ------
    # Inside an inflating throat both null expansions are positive, R is a
    # time function and the neck (min R on the slice) is slicing-dependent;
    # the theta_l = 0 and theta_k = 0 spheres bounding that region are not.
    vd = [t_dep / xmax] if t_dep is not None else []
    SLOTS = [(0.04, 0.95, "left", "top"), (0.96, 0.95, "right", "top")]
    for yy in np.arange(0.86, 0.29, -0.06):
        SLOTS += [(0.04, yy, "left", "top"), (0.96, yy, "right", "top")] + _gaps(vd, yy, "top")
    SLOTS += [(0.96, 0.05, "right", "bottom"), (0.04, 0.05, "left", "bottom")] + _gaps(vd, 0.05, "bottom")
    fk, fl = np.isfinite(R_hk), np.isfinite(R_hl)
    axs[1].plot(t[fk], R_hk[fk], color=style.INK, linewidth=1.2, zorder=3)
    axs[1].plot(t[fl], R_hl[fl], color=style.INK, linewidth=1.0, linestyle=(0, (1.2, 1.8)), zorder=3)
    axs[1].plot(t, R_nk, linestyle="none", marker="s", markersize=2.4, color=style.INK, zorder=4)
    axs[1].plot(t, R_fl, color=style.MUTED, linewidth=1.0, linestyle=(0, (4, 2.5)), zorder=2)
    g_hk = _late_rate(t[fk], R_hk[fk])
    g_nk = _late_rate(t, R_nk)
    late = t >= t_end - RATE_WINDOW
    a_hk_late = float(np.nanmean(a_hk[late & fk])) if (late & fk).any() else float("nan")
    axs[1].set_xlim(0, xmax)
    # the curves stay under ~0.55: the two notes need the top band
    axs[1].set_ylim(0.85 * np.nanmin(R_fl), 1.9 * np.nanmax(np.r_[R_hk[fk], R_nk]))
    fig.canvas.draw()
    hk_note = f"solid: horizon $\\theta_k=0$ (our side)\n$R$ {R_hk[fk][0]:.1f}$\\to${R_hk[fk][-1]:.1f}"
    if g_hk is not None:
        hk_note += (f", $d\\ln R/dt={g_hk:.4f}$\n$={g_hk / a_hk_late:.2f}$ per unit local $\\tau$ "
                    f"(last {RATE_WINDOW:.0f} u)")
    _place(axs[1], hk_note, SLOTS, fontsize=6.5, color=style.INK, multialignment="left")
    nk_note = "dotted: horizon $\\theta_l=0$ (other side)\nsquares: the neck"
    if g_nk is not None:
        nk_note += f", $d\\ln R/dt={g_nk:.4f}$"
    nk_note += "\ndashed: $r/\\sqrt{\\chi}$"
    _place(axs[1], nk_note, SLOTS, fontsize=6.5, color=style.MUTED, multialignment="left")

    # ---- (d) the lapse at the neck and the global minimum -----------------
    axs[2].plot(t, a_nk, color=style.INK, linewidth=1.1, zorder=3)
    axs[2].plot(cd[:, 0], cd[:, 1], color=style.MUTED, linewidth=1.0,
                linestyle=(0, (4, 2.5)), zorder=2)
    axs[2].set_yscale("log")
    axs[2].set_xlim(0, xmax)
    axs[2].set_ylim(0.5 * min(a_nk.min(), cd[:, 1].min()), 4.0 * max(a_nk.max(), cd[:, 1].max()))
    fig.canvas.draw()
    _place(axs[2], f"$\\alpha$ at the neck: ${a_nk[0]:.2f}\\to{a_nk[-1]:.3f}$",
           SLOTS, fontsize=6.5, color=style.INK)
    _place(axs[2], "$\\min\\alpha$ over the box (dashed)",
           SLOTS, fontsize=6.5, color=style.MUTED)
    _place(axs[2], f"$\\tau_{{\\rm neck}}={tau[-1]:.1f}$ at $t={t_end:.0f}$",
           [s for s in SLOTS if s[2] == "right"] + SLOTS, fontsize=6.5, color=style.INK)

    # ---- (e) the arm's own constraints ------------------------------------
    if t_dep is not None:
        axs[3].axvline(t_dep, ymax=0.85, color=style.FAINT, linewidth=0.7, zorder=1)
    axs[3].plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    mm = cn[:, 2] > 0
    axs[3].plot(cn[mm, 0], cn[mm, 2], color=style.MUTED, linewidth=1.1,
                linestyle=(0, (4, 2.5)), zorder=3)
    axs[3].set_yscale("log")
    axs[3].set_xlim(0, xmax)
    lo = max(1e-8, 0.3 * cn[mm, 2].min())
    axs[3].set_ylim(lo, 40.0 * cn[:, 1].max())
    fig.canvas.draw()
    _place(axs[3], f"$\\mathcal{{H}}$: ${cn[0, 1]:.1e}\\to{cn[-1, 1]:.1e}$".replace("e-0", "e-"),
           SLOTS, fontsize=6.5, color=style.INK)
    _place(axs[3], "$\\mathcal{M}$ (dashed)",
           SLOTS, fontsize=6.5, color=style.MUTED)

    print(f"[single-inflation-L512] live to t = {t_end:.2f}: neck R {R0:.3f} -> "
          f"{R_nk[-1]:.3f} (x{gain:.2f}; r/sqrt(chi) x{gain_fl:.2f}), x_neck {x_nk[0]:.2f} -> "
          f"{x_nk[-1]:.2f}; 10 % off at t = {t_dep}, doubled at t = {t_dbl}, box crossings "
          f"{[(lev, round(tc, 1)) for lev, _, tc in crossings]}; rate peak {rate_t[i_pk]:.4f} "
          f"at t = {t[i_pk]:.1f}; d ln R/dtau now {rate_tau[-1]:.4f}; "
          f"alpha_neck {a_nk[-1]:.4f}, tau {tau[-1]:.2f}; outer horizon R {R_hk[fk][-1]:.2f}, "
          f"late dlnR/dt {g_hk}; SH fit (onset) H*R0 = "
          f"{(H_fit * R0) if H_fit is not None else float('nan'):.3f}, late local "
          f"{(H_late * R0) if H_late is not None else float('nan'):.3f}, clock gone at tau "
          f"{tau_clock}; Ham end {cn[-1, 1]:.2e}")

    hits = style.label_audit(fig)
    if hits:
        print("[single-inflation-L512] label audit:", *hits, sep="\n  ")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation_L512.png")
    png = style.save(fig, out)
    print(f"[single-inflation-L512] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
