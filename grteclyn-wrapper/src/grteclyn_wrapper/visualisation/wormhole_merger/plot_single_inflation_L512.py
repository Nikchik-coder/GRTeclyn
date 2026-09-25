"""The kicked throat's inflation record in the causally disconnected box -- the F1b arm.

The sibling of ``plot_single_inflation_L128`` (the unkicked L = 128 t500 arm,
whose turn at t = 161 is the cube wall's reflection of the 1+log gauge wave,
GPU_PLAN 2026-09-25 06:30) for ``single_eps_m1e2_L512_ml5_t400``: the
eps = -1e-2 kicked throat in an L = 512 box, max_level 5 (finest dx 1/16, the
same physical refinement boxes as the L = 128 arm), the wall causally
disconnected from the neck to t ~ 340.  Reads the RUN TREE while the arm is
live (regenerate at will; ``--run`` takes the pack folder after landing).

WHAT THE PANELS SAY
(a) R_areal at the neck, two records that must agree: the dense INK line is
    the neck read off ``core_radial_profile.dat`` every step (chi_min per
    0.5-wide shell to r = 200; chi rises monotonically with r, so the shell's
    chi_min sits on its INNER edge and R = r_lo / sqrt(chi_min) is the areal
    radius there; the neck is the parabola-refined minimum over r_lo >= 0.5),
    the open circles are the consumer's x-ray stream (``areal_radius.dat``,
    one per plotfile, every 2 u).  The unkicked L = 128 arm rides beneath as
    a CONTEXT line (its record is flat to t = 66; it is a different seed,
    truncation noise, so it inflates 40 u later).  Stage lines: 10 % off the
    flat, and the coordinate neck leaving each refinement box (level 5 at
    |x| = 4, level 4 at |x| = 8, level 3 at |x| = 16, level 2 at |x| = 32).
(b) Shinkai-Hayward's test: R/R0 - 1 against the neck's proper time on a
    log axis, where their fit r/a = 1 + b4 exp(H (tau - b5)) is a straight
    line; that form fitted (H free) beside their massless value H a = 1.1 and
    the paper's linear mode converted to throat proper time (e-fold 5.13 t
    times the static throat lapse).
(c) the invariant record from the sidecar small_data/neck_horizons.dat
    (one x-ray per plotfile, from t = 88): the areal radii of the two
    trapping horizons bounding the anti-trapped throat region (theta_k = 0 on
    our side, solid; theta_l = 0 on the other side, dotted) and the neck with
    the conformal metric (squares), against the r/sqrt(chi) estimate (grey).
    Inside an inflating throat R is a time function and the neck is where the
    slice happens to be tangent to an R = const sphere -- slicing-dependent;
    the horizons are not.  THE r/sqrt(chi) RECORD IS A LOWER BOUND once the
    Gamma-driver shift has moved the grid (h22 = 1.45 at the neck at t = 90:
    10.08 for a true 12.17), the bias every areal_radius.dat of the campaign
    carries at late times (fixed in the consumer 2026-09-25 13:00).
(d) alpha at the neck (INK) and the global min alpha (MUTED), log scale.
(e) the arm's own L2 norms, H solid and M dashed, log scale.

SOURCES (the run tree; ``--run`` either layout):
``data/core_radial_profile.dat`` (time | chi_min x400 | absK_max x400 |
lapse_min x400 | n x400 | dx x400, shells centred 0.25 + 0.5 i),
``small_data/areal_radius.dat``, ``data/collapse_diagnostics.dat``,
``data/constraint_norms.dat``; the context arm from the pack,
``campaign/01_single_throat/seed/single_pureq_q1e2_L128_ml4_scalar_t500/``.

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
RUN = "runs/wormhole_merger/single_eps_m1e2_L512_ml5_t400"
CONTEXT_RUN = "seed/single_pureq_q1e2_L128_ml4_scalar_t500"
# The fixed refinement boxes' half-widths (tagging_L 256 at dx0 = 2: level l
# inside |x| < 256 * 2^-(l+1)), finest first.
BOXES = ((5, 4.0), (4, 8.0), (3, 16.0), (2, 32.0), (1, 64.0))
N_SHELLS = 400
SHELL_DR = 0.5


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


def neck_from_profile(path: pathlib.Path):
    """t, r_neck, R_neck, alpha_neck, |K|_neck from the radial profile.

    The shell's chi_min sits on its inner edge r_lo = 0.5 i (chi rises with
    r everywhere in the drainhole slice), so R(r_lo) = r_lo / sqrt(chi_min)
    is the areal radius there.  The neck is the minimum of R over r_lo >= 0.5,
    refined per step by a cubic spline of ln chi through the seven shells
    around the discrete minimum, evaluated on a 0.01-fine grid (the raw
    minimum jumps in 0.5-wide steps; a three-point parabola still leaves
    slope steps in d ln R/dt whenever the argmin shell moves).  The lapse
    and |K| are the same spline-interpolated shell profiles at the neck.
    """
    from scipy.interpolate import CubicSpline  # noqa: PLC0415

    d = _dedup(np.loadtxt(path))
    n = N_SHELLS
    t = d[:, 0]
    chi = d[:, 1:1 + n]
    absk = d[:, 1 + n:1 + 2 * n]
    lap = d[:, 1 + 2 * n:1 + 3 * n]
    r_lo = SHELL_DR * np.arange(n)
    valid = r_lo >= 0.5
    R = np.full_like(chi, np.inf)
    R[:, valid] = r_lo[None, valid] / np.sqrt(np.maximum(chi[:, valid], 1e-300))
    # Track the neck: the global minimum at t = 0, then the minimum within a
    # window around the previous step's neck.  A global argmin jumps to the
    # centre shells once the compactified far universe's chi plateau rises
    # (under-resolved there, R = r/sqrt(chi) is fiction and falls) -- the
    # artifact that took the t500 stream off its neck at t = 145 and this
    # finder at t = 62.2 (2026-09-25).
    j = np.empty(len(t), dtype=int)
    j[0] = int(np.argmin(R[0]))
    for i in range(1, len(t)):
        lo = max(1, int(0.6 * j[i - 1]))
        hi = min(n - 1, int(1.6 * j[i - 1]) + 3)
        j[i] = lo + int(np.argmin(R[i, lo:hi]))
    j = np.clip(j, 3, n - 4)
    r_neck = np.empty(len(t))
    R_neck = np.empty(len(t))
    a_neck = np.empty(len(t))
    k_neck = np.empty(len(t))
    for i in range(len(t)):
        sl = slice(max(1, j[i] - 3), j[i] + 4)   # never the r_lo = 0 shell (R = 0 there)
        rr = r_lo[sl]
        fine = np.arange(max(rr[0], 0.75), rr[-1] + 1e-9, 0.01)
        lnchi = CubicSpline(rr, np.log(np.maximum(chi[i, sl], 1e-300)))(fine)
        Rf = fine / np.exp(0.5 * lnchi)
        m = int(np.argmin(Rf))
        r_neck[i] = fine[m]
        R_neck[i] = Rf[m]
        a_neck[i] = CubicSpline(rr, lap[i, sl])(fine[m])
        k_neck[i] = CubicSpline(rr, absk[i, sl])(fine[m])
    return t, r_neck, R_neck, a_neck, k_neck


def _smooth(y: np.ndarray, w: int) -> np.ndarray:
    if w <= 1 or len(y) < w:
        return y
    k = np.ones(w) / w
    ys = np.convolve(y, k, mode="same")
    # the boxcar's edges: fall back to the raw value where the window is short
    h = w // 2
    ys[:h] = y[:h]
    ys[-h:] = y[-h:]
    return ys


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

    t, r_nk, R_nk, a_nk, k_nk = neck_from_profile(_src(run, "core_radial_profile.dat"))
    ar = _dedup(np.loadtxt(_src(run, "areal_radius.dat")))
    # the stream's argmin off the neck (onto the r = 0.5 cut, or the centre's
    # rising chi plateau) is the t500 artifact: keep the rows whose minimum
    # sits within a factor 1.6 of the previous row's radius
    keep = np.ones(len(ar), dtype=bool)
    for i in range(1, len(ar)):
        prev = ar[np.flatnonzero(keep[:i])[-1], 2]
        keep[i] = (ar[i, 2] > 0.6 * prev) and (ar[i, 2] < 1.6 * prev + 0.5)
    ar = ar[keep]
    cd = _dedup(np.loadtxt(_src(run, "collapse_diagnostics.dat")))
    # the invariant sidecar (neck_horizons_watch: the neck with the conformal
    # metric, R = r sqrt(h22/chi), and the two trapping horizons, one row per
    # plotfile from t = 88): columns time, x_neck, R_neck, R_neck_flat, h22,
    # alpha_neck, rate_neck, M_neck, phi_neck, x_hl, R_hl, alpha_hl, M_hl,
    # x_hk, R_hk, alpha_hk, M_hk
    nh = None
    nh_path = _src(run, "neck_horizons.dat")
    if nh_path.exists():
        try:
            nh = _dedup(np.atleast_2d(np.loadtxt(nh_path)))
            if len(nh) < 2:
                nh = None
        except Exception:
            nh = None
    cn = _dedup(np.loadtxt(_src(run, "constraint_norms.dat")))
    ctx = None
    if (ctx_dir / "areal_radius.dat").exists():
        ctx = _dedup(np.loadtxt(ctx_dir / "areal_radius.dat"))
        ctx = ctx[(ctx[:, 2] >= 1.0) | (ctx[:, 0] <= 10.0)]  # drop the r = 0.5-cut artifact rows

    t_end = float(t[-1])
    R0 = float(R_nk[0])
    dt = float(np.median(np.diff(t)))
    w = max(3, int(round(3.0 / dt)) | 1)  # three time units, odd
    lnR = np.log(R_nk)
    rate_t = _smooth(np.gradient(lnR, t), w)
    h = w // 2  # the boxcar's half-window: the rate is not drawn there
    tau = np.concatenate([[0.0], np.cumsum(0.5 * (a_nk[1:] + a_nk[:-1]) * np.diff(t))])
    rate_tau = rate_t / np.maximum(a_nk, 1e-12)

    # stage times
    dep = np.flatnonzero(R_nk > 1.1 * R0)
    t_dep = float(t[dep[0]]) if dep.size else None
    crossings = []
    for lev, half in BOXES:
        k = np.flatnonzero(r_nk >= half)
        if k.size:
            crossings.append((lev, half, float(t[k[0]])))
    i_pk = int(np.argmax(rate_t[:-h])) if len(t) > 2 * h else int(np.argmax(rate_t))
    rate_tau_end = float(rate_tau[-h - 1]) if len(t) > 2 * h else float(rate_tau[-1])
    gain = float(R_nk[-1] / R0)
    dbl = np.flatnonzero(R_nk >= 2.0 * R0)
    t_dbl = float(t[dbl[0]]) if dbl.size else None

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
    ymax = max(R_nk.max(), ar[:, 1].max())
    if nh is not None:
        ymax = max(ymax, nh[:, 2].max())
    if ctx is not None and (ctx[:, 0] <= xmax).any():
        ymax = max(ymax, ctx[ctx[:, 0] <= xmax, 1].max())
    ylo, yhi = 0.45 * R0, 1.4 * ymax   # every curve stays under 0.7: a caption band on top

    def fx(x):
        return x / xmax

    def fy(y):
        return (y - ylo) / (yhi - ylo)

    # ---- (a) the neck ------------------------------------------------------
    if ctx is not None:
        mc = ctx[:, 0] <= xmax
        axT.plot(ctx[mc, 0], ctx[mc, 1], color=style.CONTEXT, linewidth=1.0,
                 zorder=2, solid_capstyle="butt")
    axT.plot(t, R_nk, color=style.INK, linewidth=1.2, zorder=3)
    axT.plot(ar[:, 0], ar[:, 1], linestyle="none", marker="o", markersize=3.2,
             markerfacecolor="white", markeredgecolor=style.INK,
             markeredgewidth=0.9, zorder=4)
    if nh is not None:
        axT.plot(nh[:, 0], nh[:, 2], linestyle="none", marker="s", markersize=2.8,
                 color=style.INK, zorder=5)
    stage = []
    if t_dep is not None:
        stage.append((t_dep, f"$10\\,\\%$ off the flat, $t={t_dep:.0f}$"))
    for lev, half, tc in crossings:
        stage.append((tc, f"neck off level {lev} ($|x|={half:.0f}$), $t={tc:.0f}$"))
    for tc, _ in stage:
        # the stage lines stop under the caption band
        axT.axvline(tc, ymax=0.76, color=style.FAINT, linewidth=0.7, zorder=1)
    axT.set_xlim(0, xmax)
    axT.set_ylim(ylo, yhi)
    fig.canvas.draw()
    # the stage notes first (they belong to their lines), then the free
    # notes, each into the first slot that covers no curve, line or label:
    # a corner, or the middle of the widest gap between stage lines
    vx = [fx(tc) for tc, _ in stage]
    for tc, lab in stage:
        _place(axT, lab,
               _rows(fx(tc) - 0.006, "right", start=0.74, step=0.08)
               + _rows(fx(tc) + 0.008, "left", start=0.74, step=0.08)
               + _rows(fx(tc) - 0.006, "right", top=False, step=0.08)
               + _rows(fx(tc) + 0.008, "left", top=False, step=0.08),
               fontsize=6.5, color=style.MUTED)
    # the captions live in the band above the curves (which stay under 0.7
    # by the y-limits) and above the stage lines (which stop at 0.80)
    axT.text(0.06, 0.975, "kicked $\\epsilon=-10^{-2}$, $L=512$, level 5; wall causally "
             "disconnected to $t\\simeq340$",
             transform=axT.transAxes, fontsize=7, color=style.INK, ha="left", va="top")
    if ctx is not None:
        axT.text(0.06, 0.905, "grey: the unkicked $L=128$ arm (the t500 record; flat to $t=66$)",
                 transform=axT.transAxes, fontsize=6.5, color=style.CONTEXT, ha="left", va="top")
    axT.text(0.06, 0.845, "line, circles: $r/\\sqrt{\\chi}$, a lower bound once the grid has moved; "
             "squares: the neck with $h_{22}$",
             transform=axT.transAxes, fontsize=6.5, color=style.MUTED, ha="left", va="top")
    grow = f"$t={t_end:.0f}$: $\\times{gain:.2f}$ ($r/\\sqrt{{\\chi}}$)"
    if nh is not None:
        grow += f"\n$\\times{nh[-1, 2] / R0:.2f}$ ($h_{{22}}$, $t={nh[-1, 0]:.0f}$)"
    axT.text(0.985, 0.975, grow, transform=axT.transAxes, fontsize=6.5, color=style.INK,
             ha="right", va="top", multialignment="right")

    # ---- (b) Shinkai-Hayward in proper time --------------------------------
    # R/R0 - 1 against tau on a log axis: their fit r/a = 1 + b4 exp(H (tau - b5))
    # is a straight line there.  INK: the neck; MUTED dashed: that form fitted
    # (H free) over R/R0 - 1 > 0.1; CONTEXT: their massless value H a = 1.1
    # and the paper's linear mode (e-fold 5.13 t at the static throat lapse)
    # as slopes through the fit window's first point.
    y = R_nk / R0 - 1.0
    ms = y > 0.1
    H_fit = None
    if ms.sum() > 20:
        from scipy.optimize import curve_fit  # noqa: PLC0415
        (lnA, H_fit), _ = curve_fit(lambda x, la, hh: la + hh * x, tau[ms], np.log(y[ms]))
        i1 = int(np.flatnonzero(ms)[0])
        tt = tau[i1:]
        axs[0].plot(tt, np.exp(lnA + H_fit * tt), color=style.MUTED, linewidth=1.1,
                    linestyle=(0, (4, 2.5)), zorder=2)
        for hh, ls in ((1.1 / R0, "solid"), (1.0 / (5.13 * a_nk[0]), (0, (1.2, 1.8)))):
            axs[0].plot(tt, y[i1] * np.exp(hh * (tt - tau[i1])), color=style.CONTEXT,
                        linewidth=1.0, linestyle=ls, zorder=1)
    mv = y > 0.01
    axs[0].plot(tau[mv], y[mv], color=style.INK, linewidth=1.3, zorder=3)
    if nh is not None:
        axs[0].plot(np.interp(nh[:, 0], t, tau), nh[:, 2] / R0 - 1.0, linestyle="none",
                    marker="s", markersize=2.8, color=style.INK, zorder=5)
    axs[0].set_yscale("log")
    axs[0].set_xlim(tau[mv][0] - 0.5, tau[-1] + 0.5)
    axs[0].set_ylim(0.01, 30.0 * y[-1])
    fig.canvas.draw()
    if H_fit is not None:
        _place(axs[0], f"Shinkai--Hayward $1+A\\,e^{{H\\tau}}$ fitted (dashed):\n"
               f"$H R_0={H_fit * R0:.2f}$, e-fold ${1.0 / H_fit:.1f}\\,\\tau$\nsquares: the neck with $h_{{22}}$",
               [(0.04, 0.95, "left", "top"), (0.04, 0.5, "left", "center"), (0.96, 0.05, "right", "bottom")],
               fontsize=6.5, color=style.MUTED, multialignment="left")
        _place(axs[0], f"grey solid: SH massless, $Ha=1.1$\n"
               f"grey dotted: linear mode, $HR_0={R0 / (5.13 * a_nk[0]):.2f}$",
               [(0.96, 0.05, "right", "bottom"), (0.04, 0.78, "left", "top"), (0.04, 0.05, "left", "bottom")],
               fontsize=6.5, color=style.CONTEXT, multialignment="right")

    # ---- (c) the invariant record: the trapping horizons and the true neck ----
    # Inside an inflating throat both null expansions are positive, R is a
    # time function and the neck (min R on the slice) is slicing-dependent;
    # the theta_l = 0 and theta_k = 0 spheres bounding that region are not.
    vd = [t_dep / xmax] if t_dep is not None else []
    SLOTS = [(0.04, 0.95, "left", "top"), (0.96, 0.95, "right", "top")]
    for yy in np.arange(0.86, 0.29, -0.06):
        SLOTS += [(0.04, yy, "left", "top"), (0.96, yy, "right", "top")] + _gaps(vd, yy, "top")
    SLOTS += [(0.96, 0.05, "right", "bottom"), (0.04, 0.05, "left", "bottom")] + _gaps(vd, 0.05, "bottom")
    g_hk = g_nk = None
    if nh is not None:
        tn = nh[:, 0]
        axs[1].plot(tn, nh[:, 14], color=style.INK, linewidth=1.2, zorder=3)
        axs[1].plot(tn, nh[:, 10], color=style.INK, linewidth=1.0, linestyle=(0, (1.2, 1.8)), zorder=3)
        axs[1].plot(tn, nh[:, 2], linestyle="none", marker="s", markersize=2.8, color=style.INK, zorder=4)
        axs[1].plot(tn, nh[:, 3], color=style.MUTED, linewidth=1.0, linestyle=(0, (4, 2.5)), zorder=2)
        g_hk = np.polyfit(tn, np.log(nh[:, 14]), 1)[0]
        g_nk = np.polyfit(tn, np.log(nh[:, 2]), 1)[0]
        axs[1].set_xlim(tn[0] - 1.0, max(tn[-1] + 1.0, tn[0] + 10.0))
        axs[1].set_ylim(0.85 * nh[:, 3].min(), 1.45 * nh[:, 14].max())
        fig.canvas.draw()
        _place(axs[1], f"solid: horizon $\\theta_k=0$ (our side)\n$R$ {nh[0, 14]:.1f}$\\to${nh[-1, 14]:.1f}, "
               f"$d\\ln R/dt={g_hk:.4f}$\n$={g_hk / nh[:, 15].mean():.2f}$ per unit local $\\tau$",
               SLOTS, fontsize=6.5, color=style.INK, multialignment="left")
        _place(axs[1], f"dotted: horizon $\\theta_l=0$ (other side)\nsquares: neck with $h_{{22}}$, "
               f"$d\\ln R/dt={g_nk:.4f}$\ngrey: $r/\\sqrt{{\\chi}}$",
               SLOTS, fontsize=6.5, color=style.MUTED, multialignment="left")
    else:
        axs[1].text(0.5, 0.5, "no neck_horizons.dat yet", transform=axs[1].transAxes,
                    ha="center", va="center", fontsize=7, color=style.MUTED)
        axs[1].set_xlim(0, xmax)

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
           SLOTS[4:] + SLOTS[:4], fontsize=6.5, color=style.INK)

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
          f"{R_nk[-1]:.3f} (x{gain:.2f}), r_neck {r_nk[0]:.2f} -> {r_nk[-1]:.2f}, "
          f"stream {ar[0, 1]:.3f} -> {ar[-1, 1]:.3f} at t = {ar[-1, 0]:.0f}; "
          f"10 % off at t = {t_dep}, doubled at t = {t_dbl}, box crossings "
          f"{[(lev, tc) for lev, _, tc in crossings]}; rate peak {rate_t[i_pk]:.4f} "
          f"at t = {t[i_pk]:.1f}; d ln R/dtau now {rate_tau_end:.4f}; "
          f"alpha_neck {a_nk[-1]:.4f}, tau {tau[-1]:.2f}; sidecar rows {0 if nh is None else len(nh)}, "
          f"outer horizon dlnR/dt {g_hk}; SH fit H*R0 = "
          f"{(H_fit * R0) if H_fit is not None else float('nan'):.3f}; Ham end {cn[-1, 1]:.2e}")

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
