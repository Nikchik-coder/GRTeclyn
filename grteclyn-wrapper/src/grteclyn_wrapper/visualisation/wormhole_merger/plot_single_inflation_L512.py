"""The kicked throat's inflation record in the L = 512 box -- the F4 arm.

``single_eps_m1e2_L512_ml5_oct_t400``: the eps = -1e-2 kicked throat, max_level
5 (finest dx 1/16), 1+log slicing, evolved on the octant [0, 256]^3 with mirror
planes x = y = z = 0.  The evolution died at t = 392.36 on a NaN in h11 on
level 2.  The constraint norms' runaway is detected, the neck row it already
reaches (t = 392) is dropped, and every stream ends at t_end = 390.

Every radius is the proper areal radius R = r (h22 h33)^(1/4) / sqrt(chi) of
the coordinate sphere through the neck; r / sqrt(chi) is its flat lower bound.

(a) R at the neck against t, with r / sqrt(chi), the unkicked L = 128 arm as
    context, the exponential onset fit R0 (1 + A e^(t/T)) (solid over its
    window, dashed on, so the departure shows), the times the neck leaves each
    refinement level, and shaded: the Shinkai-Hayward window (faint gold) and
    after it, to T_WALL, the slower growth in t once 1+log freezes the neck's
    clock (grey).
(b) Shinkai-Hayward's test: R/R0 - 1 against the neck's proper time, their
    1 + A e^(H tau) fitted over their window (shaded; ``sh_fit``), their
    massless H a = 1.1 and the linear mode as slopes.
(c) the two trapping horizons bounding the anti-trapped throat (theta_k = 0
    our side, cut at its first jump; theta_l = 0 the other side) and the neck.
(d) the lapse at the neck and its global minimum.  (e) the L2 constraint norms.

The time panels shade t >= T_WALL, where the gauge wave is back from the wall.

Sources, from the pack's ``campaign/01_single_throat/seed/
single_eps_m1e2_L512_ml5_oct_t400/`` (``--run`` takes another folder, pack
or run tree): ``neck_horizons.dat``, ``collapse_diagnostics.dat``,
``constraint_norms.dat``; the context arm from ``campaign/01_single_throat/
seed/single_pureq_q1e2_L128_ml4_scalar_t500/``.  Not ``areal_radius.dat``:
its global minimum along the ray falls onto the compactified other end's chi
plateau from t = 60.  ``record``, ``onset_fit``, ``sh_fit`` and
``theta_k_track`` are the arm's method, imported by the paper's inflation
figure and the claims ledger.

Style: house PRD frame; one key per panel ABOVE its frame names every line
(``style.legend_top``, tags by ``style.tag_keys``); GOLD is the accent (the
fits, the horizons), the rest ink and grey; the only text inside a frame is
the level numbers.  ``style.label_audit`` is printed.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT,
    REPO,
    figure_dir,
)

GROUP = "01_single_throat"
F4 = "seed/single_eps_m1e2_L512_ml5_oct_t400"   # under campaign/01_single_throat/
CONTEXT_RUN = "seed/single_pureq_q1e2_L128_ml4_scalar_t500"
# The refinement boxes' outer faces along each axis, finest first, from the
# plotfile headers.  Checked against the run log's regrid history: the neck
# left every box before that box grew, so these faces set the crossing times.
#   level  face  face held until t  neck crossed at t
#     5      5         58.2              43.8
#     4     10         88.7              64.7
#     3     20        167.2             113.2
#     2     40        378.2             234.7
# The faces later grew to 9 / 16 / 24 / 48.  Level 1 (80) is never crossed.
BOXES = ((5, 5.0), (4, 10.0), (3, 20.0), (2, 40.0), (1, 80.0))
# The gauge wave comes back from the outer wall at t = T_WALL; later times are
# not quoted.  Measured from the run's lapse slice cache: the 1+log collapse
# front, moving out at ~1.36 per unit t, reaches the outer face x = 256 at
# t = 218 (the wall cell's alpha 0.02 below its t = 0 value); the reflection
# then travels inward and is at x ~ 67 by t = 390 (the neck is at x = 60.5).
# Two more clocks agree: L2 Ham passes 0.1 at t ~ 222, and the far-horizon
# (theta_k) track is lost at t = 212.  The limit is also held per run in
# results/merger/trust_windows.tsv (closeout.sh cuts the movies there).
T_WALL = 218.0
# The exponential onset in (a): R/R0 - 1 from 3 % to 30 % (t = 16-28 here).
# Earlier the growth is still the start-up transient (local e-fold 7-9 u at
# t <= 12); later the lapse at the neck drops and the rate with it (e-fold
# 6.6 at t = 30, 8.8 at t = 34).  The table the script prints is the check.
ONSET = (0.03, 0.30)
# Shinkai-Hayward's window (2026-09-26, the user: "place the line where we can
# quote shinkai"): the local H R0 = R0 d ln(R/R0 - 1)/d tau over the growth
# phase (R/R0 - 1 >= 0.02, t <= 80), from its peak both ways while >= 1.0.  On
# F4: t = 16-40 (tau = 9.21-20.26, R/R0 1.03 -> 2.01, alpha_neck 0.57 -> 0.23),
# local 1.03-1.26 peaking at t = 26, and one fit there gives H R0 = 1.217.
SH_GROWTH = (0.02, 80.0)
SH_FLOOR = 1.0
# the window's shade: faint gold, it is what the gold fit is compared over
SH_SHADE = dict(facecolor=style.GOLD, alpha=0.13, edgecolor="none", zorder=0)
# after the window, to the end of the quoted record: the neck keeps growing but
# slower in t, because 1+log freezes its lapse (its proper time nearly stops).
# A cool light grey, apart from the warm GRID of the "not quoted" shading.
SLOW_SHADE = dict(facecolor="#eef0f3", edgecolor="none", zorder=0)
# the jump that ends the theta_k track: a fall of more than 5 % in one sample
HK_JUMP = 0.95
# The crash reaches the neck record before the norms run away: the last
# plotfile, t = 392, 0.36 u before the NaN, already has the lapse at the neck
# x5.4 and r/sqrt(chi) -14 % in one sample.  So the runaway is the trailing
# run of samples where L2 Ham exceeds BLOWUP x its value LAG earlier (from
# t = 392.2 here), every neck row within LAG of it goes too (t_end = 390), and
# every stream is cut at the last neck row kept.
BLOWUP = 1.2
LAG = 2.0
# the window of the late rates printed for (c)
RATE_WINDOW = 10.0
DASH = (0, (4, 2.5))
DOT = (0, (1.2, 1.8))


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


# ---- the arm's method, shared: the paper's inflation figure and the claims
# ledger (research/merger/article/claims/extract_single.py) import these, so
# the page, the paper and the quoted numbers cannot drift apart.
def f4_dir(pack_root: pathlib.Path | str = PACK_ROOT) -> pathlib.Path:
    """The arm's pack folder."""
    return pathlib.Path(pack_root).expanduser() / "campaign" / GROUP / F4


def record(run: pathlib.Path) -> dict:
    """The arm's streams, deduplicated and cut where the crash reaches them.

    ``nh``, ``cd``, ``cn``: neck_horizons, collapse_diagnostics and
    constraint_norms, all ending at ``t_end``, the last neck row clear of the
    norms' runaway (BLOWUP, LAG); ``t_run``: where the runaway starts (None
    without one); ``cut_nh``, ``cut_cn``: the rows dropped."""
    run = pathlib.Path(run)
    nh = _dedup(np.atleast_2d(np.loadtxt(_src(run, "neck_horizons.dat"))))
    if len(nh) < 2:
        raise SystemExit(f"[single-inflation-L512] {run}: fewer than two neck_horizons rows")
    cd = _dedup(np.loadtxt(_src(run, "collapse_diagnostics.dat")))
    cn = _dedup(np.loadtxt(_src(run, "constraint_norms.dat")))
    th, ham = cn[:, 0], cn[:, 1]
    calm = (th < th[0] + LAG) | (ham <= BLOWUP * np.interp(th - LAG, th, ham))
    last_calm = int(np.flatnonzero(calm)[-1]) if calm.any() else -1
    t_run = float(th[last_calm + 1]) if last_calm + 1 < len(th) else None
    keep = nh[:, 0] <= (t_run - LAG + 1e-9 if t_run is not None else np.inf)
    t_end = float(nh[keep][-1, 0])
    return dict(nh=nh[keep], cut_nh=nh[~keep], t_end=t_end, t_run=t_run,
                cd=cd[cd[:, 0] <= t_end + 1e-9], cn=cn[cn[:, 0] <= t_end + 1e-9],
                cut_cn=cn[cn[:, 0] > t_end + 1e-9])


def onset_fit(t: np.ndarray, R: np.ndarray) -> dict:
    """R = R0 (1 + A e^(t/T)): ln(R/R0 - 1) linear in t over the ONSET window.
    Returns R0, T, A, the window's first and last times t0, t1, its mask
    ``win``, the rms residual in ln(R/R0 - 1), and the local rate
    d ln(R/R0 - 1)/dt at every sample (``slope``, the table that justifies it)."""
    R0 = float(R[0])
    y = R / R0 - 1.0
    ly = np.log(np.where(y > 0, y, np.nan))
    win = (y >= ONSET[0]) & (y <= ONSET[1]) & (t < t[np.argmax(y > ONSET[1])])
    k, c = np.polyfit(t[win], ly[win], 1)
    return dict(R0=R0, T=float(1.0 / k), A=float(np.exp(c)), t0=float(t[win][0]),
                t1=float(t[win][-1]), win=win, slope=np.gradient(ly, t),
                rms=float(np.sqrt(np.mean((ly[win] - (c + k * t[win])) ** 2))))


def sh_fit(t: np.ndarray, R: np.ndarray, alpha: np.ndarray) -> dict:
    """Shinkai-Hayward's r/a = 1 + A e^(H tau) in the neck's proper time
    tau = int alpha_neck dt, H free, fitted once over the SH WINDOW: the local
    H R0 = R0 d ln(R/R0 - 1)/d tau (smoothed over +-1 sample) peaks in the
    growth phase (SH_GROWTH) and the window runs both ways from the peak while
    it stays >= SH_FLOOR.  Returns R0, y = R/R0 - 1, tau, the local rate
    ``local`` (H R0), the window's ``mask`` and its t and tau ends, the fit's H
    and ln A, H_late (the last five samples once the lapse at the neck is
    below half its t = 0 value) and H_linear, the paper's linear mode (e-fold
    5.13 t at the static throat's lapse)."""
    R0 = float(R[0])
    y = R / R0 - 1.0
    tau = np.concatenate([[0.0], np.cumsum(0.5 * (alpha[1:] + alpha[:-1]) * np.diff(t))])
    ly = np.log(np.where(y > 0, y, np.nan))
    g = np.gradient(ly, tau) * R0
    local = np.full_like(g, np.nan)
    local[1:-1] = (g[:-2] + g[1:-1] + g[2:]) / 3.0
    grow = np.flatnonzero((y >= SH_GROWTH[0]) & (t <= SH_GROWTH[1]) & np.isfinite(local))
    mask = np.zeros(len(t), dtype=bool)
    out = dict(R0=R0, y=y, tau=tau, local=local, mask=mask, H=None, lnA=None, t0=None, t1=None,
               tau0=None, tau1=None, H_late=None, H_linear=float(1.0 / (5.13 * alpha[0])))
    if grow.size:
        lo = hi = int(grow[np.argmax(local[grow])])
        while lo - 1 in grow and local[lo - 1] >= SH_FLOOR:
            lo -= 1
        while hi + 1 in grow and local[hi + 1] >= SH_FLOOR:
            hi += 1
        mask[lo:hi + 1] = True
        out.update(t0=float(t[lo]), t1=float(t[hi]), tau0=float(tau[lo]), tau1=float(tau[hi]))
        if mask.sum() >= 3:
            H, lnA = np.polyfit(tau[mask], ly[mask], 1)
            out.update(H=float(H), lnA=float(lnA))
    late = (alpha < 0.5 * alpha[0]) & (y > 0.1)
    if late.sum() >= 5:
        out["H_late"] = float(np.polyfit(tau[late][-5:], np.log(y[late][-5:]), 1)[0])
    return out


def theta_k_track(R_hk: np.ndarray) -> tuple[np.ndarray, bool]:
    """The theta_k = 0 horizon's samples up to its first jump -- a fall of
    more than 5 % in one sample (HK_JUMP), after which the finder flickers
    between a far root and one just outside the neck -- and whether it jumped."""
    fk = np.flatnonzero(np.isfinite(R_hk))
    jump = np.flatnonzero(R_hk[fk][1:] < HK_JUMP * R_hk[fk][:-1])
    return (fk[: int(jump[0]) + 1] if jump.size else fk), bool(jump.size)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--run", default=None,
                    help="the run's folder (pack or run tree; default: the pack's); a "
                         "relative path resolves against the repo root")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()
    run = pathlib.Path(args.run).expanduser() if args.run else f4_dir(pack)
    if not run.is_absolute():
        run = REPO / run
    ctx_dir = pack / "campaign" / GROUP / CONTEXT_RUN

    # the neck and the horizons, one x-ray per plotfile (NECK_HORIZONS_HEADER),
    # every stream ending with the neck record
    rec = record(run)
    nh, cd, cn, t_end, t_run = rec["nh"], rec["cd"], rec["cn"], rec["t_end"], rec["t_run"]
    cut_nh, cut_cn = rec["cut_nh"], rec["cut_cn"]
    t = nh[:, 0]
    x_nk, R_nk, R_fl, a_nk = nh[:, 1], nh[:, 2], nh[:, 3], nh[:, 5]
    R_hl, R_hk, a_hk = nh[:, 10], nh[:, 14], nh[:, 15]
    ctx = None
    if (ctx_dir / "areal_radius.dat").exists():
        ctx = _dedup(np.loadtxt(ctx_dir / "areal_radius.dat"))
        ctx = ctx[(ctx[:, 2] >= 1.0) | (ctx[:, 0] <= 10.0)]  # drop the r = 0.5-cut artifact rows
        ctx = ctx[ctx[:, 0] <= t_end + 1e-9]

    xmax = 25.0 * np.ceil(t_end / 25.0)
    crossings = []
    for lev, face in BOXES:
        tc = _first_crossing(t, x_nk, face)
        if tc is not None:
            crossings.append((lev, face, tc))

    # the exponential onset: ln(R/R0 - 1) linear in t over the ONSET window
    on = onset_fit(t, R_nk)
    R0, T_on, A_on, rms_on = on["R0"], on["T"], on["A"], on["rms"]
    t_w0, t_w1, win, slope = on["t0"], on["t1"], on["win"], on["slope"]
    y = R_nk / R0 - 1.0
    sh = sh_fit(t, R_nk, a_nk)
    tau = sh["tau"]
    print("[single-inflation-L512] local d ln(R/R0 - 1)/dt (* = the onset window):")
    print("      t   R/R0-1   rate   e-fold  alpha_neck")
    for i in np.flatnonzero((t > 0) & (t <= t_w1 + 16.0)):
        print(f"  {t[i]:5.1f} {y[i]:8.4f} {slope[i]:7.4f} {1.0 / slope[i]:7.2f} "
              f"{a_nk[i]:8.4f}{'  *' if win[i] else ''}")

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 6.8), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.0, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]),
           fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])]
    time_axes = (axT, axs[1], axs[2], axs[3])
    for ax in time_axes:
        ax.axvspan(T_WALL, xmax, facecolor=style.GRID, edgecolor="none", zorder=0)
        ax.set_xlim(0, xmax)
        ax.set_xlabel(r"$t$")

    # ---- (a) the neck ------------------------------------------------------
    wall = Patch(facecolor=style.GRID, edgecolor="none")
    axT.axvspan(sh["t0"], sh["t1"], **SH_SHADE)
    axT.axvspan(sh["t1"], T_WALL, **SLOW_SHADE)
    keyA = [(axT.plot(t, R_nk, color=style.INK, linewidth=1.3, zorder=4)[0],
             r"neck, full-metric $R$"),
            (axT.plot(t, R_fl, color=style.MUTED, linewidth=1.0, linestyle=DASH, zorder=3)[0],
             r"neck, $r/\sqrt{\chi}$")]
    if ctx is not None:
        keyA.append((axT.plot(ctx[:, 0], ctx[:, 1], color=style.CONTEXT, linewidth=1.0,
                              zorder=2)[0], r"unkicked $L=128$ arm, $r/\sqrt{\chi}$"))
    top = max(float(R_nk.max()), float(R_fl.max()),
              float(ctx[:, 1].max()) if ctx is not None else 0.0)
    ylo = 2.0
    # the curves stay under 0.80 of the frame: the level numbers sit above 0.88
    axT.set_ylim(ylo, ylo + (top - ylo) / 0.80)
    tf = np.linspace(t_w0, t_w1, 60)
    fit = axT.plot(tf, R0 * (1.0 + A_on * np.exp(tf / T_on)), color=style.GOLD,
                   linewidth=1.9, zorder=5, solid_capstyle="butt")[0]
    # extended until it leaves the curves' range (the band above is the tags')
    t_top = T_on * np.log((top / R0 - 1.0) / A_on)
    te = np.linspace(t_w1, t_top, 80)
    axT.plot(te, R0 * (1.0 + A_on * np.exp(te / T_on)), color=style.GOLD,
             linewidth=1.3, linestyle=DASH, zorder=5)
    keyA.append((fit, rf"fit $R_0(1+Ae^{{t/T}})$, $T={T_on:.1f}$, $t={t_w0:.0f}$–${t_w1:.0f}$"))
    for lev, _, tc in crossings:
        axT.axvline(tc, ymax=0.865, color=style.FAINT, linewidth=0.7, zorder=1)
        axT.text(tc, 0.885, f"{lev}", transform=axT.get_xaxis_transform(), ha="center",
                 va="bottom", fontsize=6.5, color=style.MUTED)
    if crossings:
        keyA.append((Line2D([], [], color=style.FAINT, linewidth=0.7), r"neck leaves level $N$"))
    keyA.append((Patch(**{k: v for k, v in SH_SHADE.items() if k != "zorder"}),
                 rf"Shinkai–Hayward rate ($t={sh['t0']:.0f}$–${sh['t1']:.0f}$)"))
    keyA.append((Patch(**{k: v for k, v in SLOW_SHADE.items() if k != "zorder"}),
                 r"slower in $t$: $1{+}\log$ freezes the neck's clock"))
    keyA.append((wall, rf"$t\geq{T_WALL:.0f}$: gauge wave at the wall (not quoted)"))
    axT.set_ylabel(r"$R_{\rm areal}$")
    style.legend_top(axT, keyA, ncol=3)

    # ---- (b) Shinkai-Hayward in proper time --------------------------------
    # R/R0 - 1 against tau on a log axis, where their r/a = 1 + b4 exp(H (tau -
    # b5)) is a straight line; fitted (H free) over the Shinkai-Hayward window
    # (shaded; sh_fit) and drawn on, so the late departure shows.  CONTEXT:
    # their massless H a = 1.1 and the paper's linear mode (e-fold 5.13 t at
    # the static throat lapse) as slopes through the window's first point.
    ax = axs[0]
    ms, H_fit, H_late = sh["mask"], sh["H"], sh["H_late"]
    ax.axvspan(sh["tau0"], sh["tau1"], **SH_SHADE)
    H_lin = sh["H_linear"]
    mv = y > 0.01
    # the key reads row by row: the neck and its fit, the two reference
    # slopes, the clock line
    neck = ax.plot(tau[mv], y[mv], color=style.INK, linewidth=1.3, zorder=3)[0]
    keyB, refs = [(neck, "neck")], []
    ytop = float(y[mv].max())
    if H_fit is not None:
        lnA = sh["lnA"]
        i1 = int(np.flatnonzero(ms)[0])
        tt = tau[i1:]
        shl = ax.plot(tt, np.exp(lnA + H_fit * tt), color=style.GOLD, linewidth=1.3,
                      linestyle=DASH, zorder=4)[0]
        for hh, ls, lab in ((1.1 / R0, "solid", r"SH massless, $Ha=1.1$"),
                            (H_lin, DOT, rf"linear mode, $HR_0={H_lin * R0:.2f}$")):
            yy = y[i1] * np.exp(hh * (tt - tau[i1]))
            ytop = max(ytop, float(yy.max()))
            refs.append((ax.plot(tt, yy, color=style.CONTEXT, linewidth=1.0, linestyle=ls,
                                 zorder=2)[0], lab))
        ytop = max(ytop, float(np.exp(lnA + H_fit * tt).max()))
        keyB += [(shl, rf"fit, $HR_0={H_fit * R0:.2f}$")] + refs
        keyB.append((Patch(**{k: v for k, v in SH_SHADE.items() if k != "zorder"}),
                     rf"SH window, $\tau={sh['tau0']:.1f}$–${sh['tau1']:.1f}$"))
    ax.set_yscale("log")
    ax.set_xlim(tau[mv][0] - 0.5, tau[-1] + 0.5)
    ax.set_ylim(0.01, 1.8 * ytop)
    ax.set_xlabel(r"$\tau$ (proper time at the neck)")
    ax.set_ylabel(r"$R/R_0-1$")
    style.legend_top(ax, keyB, ncol=2)

    # ---- (c) the trapping horizons and the neck ----------------------------
    # Inside an inflating throat both null expansions are positive, R is a
    # time function and the neck is slicing-dependent; the theta_l = 0 and
    # theta_k = 0 spheres bounding that region are not.  The theta_k finder
    # loses the far root at its first jump (after it, it flickers between a
    # far root and one just outside the neck): nothing is drawn past it.
    ax = axs[1]
    kk, jumped = theta_k_track(R_hk)
    t_hk = float(t[kk[-1]])
    fl = np.isfinite(R_hl)
    keyC = [(ax.plot(t[kk], R_hk[kk], color=style.GOLD, linewidth=1.4, zorder=3)[0],
             rf"$\theta_k=0$ (our side, to $t={t_hk:.0f}$)")]
    if jumped:
        ax.plot(t[kk[-1]], R_hk[kk[-1]], linestyle="none", marker="o", markersize=2.6,
                color=style.GOLD, zorder=3)
    keyC.append((ax.plot(t[fl], R_hl[fl], color=style.GOLD, linewidth=1.3, linestyle=DOT,
                         zorder=4)[0], r"$\theta_l=0$ (other side)"))
    keyC.append((ax.plot(t, R_nk, color=style.INK, linewidth=1.2, zorder=2)[0], "neck"))
    ax.set_yscale("log")
    ax.set_ylim(0.85 * np.nanmin(np.r_[R_nk, R_hl[fl], R_hk[kk]]),
                1.35 * np.nanmax(np.r_[R_nk, R_hl[fl], R_hk[kk]]))
    lo, hi = ax.get_ylim()
    ax.yaxis.set_major_locator(FixedLocator([v for v in (2, 5, 10, 20, 50, 100, 200)
                                             if lo <= v <= hi]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_ylabel(r"$R_{\rm areal}$")
    style.legend_top(ax, keyC, ncol=2)

    # ---- (d) the lapse at the neck and the global minimum -----------------
    ax = axs[2]
    keyD = [(ax.plot(t, a_nk, color=style.INK, linewidth=1.2, zorder=3)[0],
             r"$\alpha$ at the neck"),
            (ax.plot(cd[:, 0], cd[:, 1], color=style.MUTED, linewidth=1.0, linestyle=DASH,
                     zorder=2)[0], r"global min $\alpha$")]
    ax.set_yscale("log")
    ax.set_ylim(0.5 * min(a_nk.min(), cd[:, 1].min()), 2.0 * max(a_nk.max(), cd[:, 1].max()))
    ax.set_ylabel(r"$\alpha$")
    style.legend_top(ax, keyD, ncol=2)

    # ---- (e) the arm's own constraints ------------------------------------
    ax = axs[3]
    mm = cn[:, 2] > 0
    keyE = [(ax.plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.2, zorder=3)[0],
             r"Hamiltonian, $\mathcal{H}$"),
            (ax.plot(cn[mm, 0], cn[mm, 2], color=style.MUTED, linewidth=1.0, linestyle=DASH,
                     zorder=3)[0], r"momentum, $\mathcal{M}$")]
    ax.set_yscale("log")
    ax.set_ylim(max(1e-8, 0.3 * cn[mm, 2].min()), 3.0 * cn[:, 1].max())
    ax.set_ylabel(r"$L_2$ norms")
    style.legend_top(ax, keyE, ncol=2)

    fig.align_ylabels([axT, axs[0], axs[2]])
    fig.align_ylabels([axs[1], axs[3]])
    style.tag_keys(fig, [axT] + axs, [f"({c})" for c in "abcde"])

    fl_hk = t[kk] >= t_hk - RATE_WINDOW
    g_hk = _late_rate(t[kk], R_hk[kk])
    a_hk_late = float(np.nanmean(a_hk[kk][fl_hk]))
    g_nk = _late_rate(t, R_nk)
    t_ham = _first_crossing(cn[:, 0], cn[:, 1], 0.1)
    print(f"[single-inflation-L512] t_end = {t_end:.2f} (xmax {xmax:.0f}); neck R {R0:.3f} -> "
          f"{R_nk[-1]:.3f} (x{R_nk[-1] / R0:.2f}; r/sqrt(chi) x{R_fl[-1] / R0:.2f}), x_neck "
          f"{x_nk[0]:.2f} -> {x_nk[-1]:.2f}; box crossings "
          f"{[(lev, round(tc, 1)) for lev, _, tc in crossings]}")
    print(f"[single-inflation-L512] onset fit R0(1+A e^(t/T)) over t = {t_w0:.0f}-{t_w1:.0f} "
          f"({win.sum()} samples, R/R0-1 {y[win][0]:.3f}-{y[win][-1]:.3f}): T = {T_on:.3f}, "
          f"A = {A_on:.3e}, rms in ln(R/R0-1) {rms_on:.4f}; drawn on to R = {top:.2f} at "
          f"t = {t_top:.1f}")
    print(f"[single-inflation-L512] SH window t = {sh['t0']:.0f}-{sh['t1']:.0f} (tau "
          f"{sh['tau0']:.2f}-{sh['tau1']:.2f}, {ms.sum()} samples), local H*R0 "
          f"{np.nanmin(sh['local'][ms]):.3f}-{np.nanmax(sh['local'][ms]):.3f}; fit H*R0 = "
          f"{(H_fit * R0) if H_fit is not None else float('nan'):.4f}; linear mode H*R0 = "
          f"{H_lin * R0:.3f}; late local H*R0 = "
          f"{(H_late * R0) if H_late is not None else float('nan'):.3f}; tau_neck "
          f"{tau[-1]:.2f} at t_end")
    print(f"[single-inflation-L512] theta_k track to t = {t_hk:.0f} (R {R_hk[kk[-1]]:.2f}; next "
          f"sample {R_hk[kk[-1] + 1] if kk[-1] + 1 < len(t) else float('nan'):.2f}), its last "
          f"{RATE_WINDOW:.0f} u d ln R/dt = {g_hk:.4f} (= {g_hk / a_hk_late:.3f} per local tau); "
          f"neck late d ln R/dt = {g_nk:.5f}; alpha_neck {a_nk[0]:.3f} -> {a_nk[-1]:.4f}, "
          f"global min {cd[-1, 1]:.2e}")
    print(f"[single-inflation-L512] L2 Ham {cn[0, 1]:.2e} -> {cn[-1, 1]:.2e} (passes 0.1 at "
          f"t = {t_ham if t_ham is None else round(t_ham, 1)}); norm runaway from t = {t_run}; "
          f"dropped past t_end: {len(cut_nh)} neck rows (t "
          f"{', '.join(f'{v:g}' for v in cut_nh[:, 0])}; alpha_neck "
          f"{', '.join(f'{v:.4f}' for v in cut_nh[:, 5])}), {len(cut_cn)} norm rows (max Ham "
          f"{cut_cn[:, 1].max() if len(cut_cn) else float('nan'):.2e}); shaded from "
          f"T_WALL = {T_WALL:.0f}")

    hits = style.label_audit(fig)
    print(f"[single-inflation-L512] label audit: {len(hits)} overlaps")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation_L512.png")
    png = style.save(fig, out)
    print(f"[single-inflation-L512] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
