#!/usr/bin/env python3
r"""Merger or fly-by: the orbits of the momentum scan, p = 0 to 0.45.

Every opposite-signed pair released at d = 12 with tangential Bowen-York
momentum p (article Sec. VII A), drawn from its tracked throat centres: the
head-on release from rest (p = 0), the plunges p = 0.12, 0.15, 0.20, 0.25 and
the two fly-bys p = 0.35, 0.45.  (a) both throats in the orbital plane,
(b) their coordinate separation.  Every p <= 0.25 falls into one core; every
p >= 0.35 swings round and recedes -- the boundary the text places at 50-70 %
of the circular value.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_momentum_orbits

WHAT IS DRAWN (2026-09-25, the user: "draw the trajectories for different p,
head-on p = 0 to p = 0.45; we have precise orbits from those runs").  The
chi-pit barycentres of ``binary_throat_diagnostics.dat`` -- identical to the
throat tracker's centres until the tracker fuses the two (separation ~ 2,
t = 31-38), and the only record after it.  The pits are found in the two
half-spaces of a FIXED plane, so their labels swap when an orbit turns past
90 degrees; each track is therefore followed by continuity (nearest pit to
the previous point).  A plunge is drawn only while its pits are trackable:
until chi first touches its 1e-8 floor (after which the minimum is a flat
patch, not a point -- Fig. 8 of the article pales its pits there for the same
reason) or until either pit first jumps by more than 0.2 in one output step
(dt = 0.05: four times the light speed, a hop between two minima, not
motion), whichever comes first; otherwise to the run's end.

THE GRIDS.  The plunges and p = 0.35 are level 3 (finest dx = 1/16): p = 0.12
is the production chain's level-3 leg (L = 128), whose pits agree with the
L = 64 arm to every printed digit through t = 44, the others the L = 64 scan.
p = 0.45 is the level-5 fly-by on L = 128 whose numbers Sec. VII A quotes.
Its level-3 twin is NOT drawn: at t = 34.75 its pit hops six cells toward the
companion in a quarter of a unit (1.5c, a jump between two minima of an
under-resolved far end), which alone moves its closest approach from ~4.8 to
3.95; at level 5 the same stretch is smooth.

SMOOTHING.  A level-3 pit sits on a cell centre, so its track is a staircase
of 1/16 steps with +-2-cell jitter near closest approach; every track is
resampled at dt = 0.05 and averaged over two time units (centred; the window
shrinks at the ends, so every track keeps its last point), which moves no
drawn minimum by more than a few hundredths.  The caption says so.

Reads ``campaign/`` streams only (no frames).  Writes
``figures/05_binary_spiral/momentum_scan_orbits``.

WHERE THE FLY-BY STOPS BEING TWO BODIES (2026-09-25, the user: "why do they
fly by if they are attracted so strongly -- is this fly-away the inflation of
one of the throats?").  The turn at closest approach (t ~ 40) is orbital: the
pull is central and the pair keeps its angular momentum.  But the fly-by's
mouths inflate -- both, by symmetry -- and from t = 43 the areal minimum of its
per-mouth scan sits on the scan window's edge (the article's
clmFlybyScanEdgeTime), after which the separation drawn is that of two chi
pits inside two inflating mouths, not of two compact throats.  So p = 0.45 is
drawn at full weight to that time and faint after it, with a note.  p = 0.35
carries no mouth scan and is drawn as recorded.

THE FLY-BY STOPS AT ITS TRUST WINDOW, t = 70 (2026-09-26, referee).  Its
constraint norms grow by orders of magnitude as the mouths inflate, so the
paper quotes nothing from it after t = 70 (the wave gallery's retarded gate,
t - R <= 50, is the same window read at R = 20).  The pit record is cut there
BEFORE the two-unit smoothing, so no later sample leaks into the last drawn
point: full weight to t = 43, faint over 43-70, nothing after.  It had been
drawn to the run's end, t = 100.  Every other arm is unchanged.

STYLE: style.prd, letter tags above the frames.  The plunges are one grey
ramp, light (p = 0) to ink (p = 0.25), keyed in (a)'s empty corner (five
curves converging on one point cannot each carry a name); the fly-bys take
the one accent, gold, named where they leave -- the eye sorts merger from
fly-by before it reads a number.  A plunge ends in a dot, where its pits stop
being trackable.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir, find_packed,
)

GROUP = "05_binary_spiral"
CHI_FLOOR = 1.0e-8     # min_chi of every arm here
HOP = 0.2              # a one-step jump of the pit separation larger than this is a hop

# Since 2026-10-05 the arms are the boosted mode-3 campaign (the caption of
# fig:orbits): the d = 6 merger, the d = 12 p = 0.12 arm (pits merge, no
# horizon), the plunges p = 0.60 / 0.90 (two legs each, concatenated), and
# the gold scatterers p = 0.25 / 0.45, each cut at its trust window.  The
# p = 0.90 continuation runs on a 1e-4 chi floor, so the floor cut is
# per-arm.
# (p, runs, colour, dash, width, merges, chi floor)
ARMS = (
    (0.10, ("spiral_d6_p010_L128_lvl5from0_t060_lbf_csm",),
     style.INK, (0, ()), 1.4, True, 0.0),
    # the boosted (lb) arm the text quotes, since 2026-10-06 (validation B1)
    (0.12, ("v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm",),
     "#918e87", (0, ()), 1.2, True, 0.0),
    (0.60, ("merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm",
            "merge_orbit_flip_d12_p060_L128_lvl4_t100_lbf_csm_r04000"),
     "#474540", (0, ()), 1.2, True, 0.0),
    (0.90, ("merge_orbit_flip_d12_p090_L128_lvl4_t040_lbf_csm",
            "merge_orbit_flip_d12_p090_L128_lvl4from40_chi1e4_t100_lbf_csm_r04000"),
     "#6f6d67", (0, ()), 1.2, True, 0.0),
    (0.25, ("merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm",),
     style.GOLD, (0, ()), 1.5, False, 1.0e-8),
    (0.45, ("merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm",),
     style.GOLD, (0, (4.5, 2.0)), 1.3, False, 1.0e-8),
)
SMOOTH = 2.0           # time units, centred running mean of the resampled track
DT = 0.05
# Last trusted time per arm, keyed by its FIRST leg (trust_windows.tsv).
TRUST_END = {"v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm": 56.5,
             "merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm": 63.3,
             "merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm": 67.6,
             "merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm": 55.5,
             "merge_orbit_flip_d12_p090_L128_lvl4_t040_lbf_csm": 45.2}


def pit_tracks(run, pack_root=None, merges: bool = True, floor: float = CHI_FLOOR):
    """(t, track 1, track 2, cut reason) from the run's chi-pit barycentres.

    Track 1 starts at the throat on -x.  Each row's two pits are assigned by
    continuity, and a plunge is cut where its pits stop being trackable.
    ``run`` may be a tuple of legs, concatenated in time order.
    """
    runs = (run,) if isinstance(run, str) else tuple(run)
    parts = [np.loadtxt(find_packed(r, pack_root) / "binary_throat_diagnostics.dat")
             for r in runs]
    b = parts[0]
    for q in parts[1:]:
        # a restart leg's tracker needs a step to lock on (its first row sits
        # at the box origin or at the t = 0 throat positions): drop its
        # leading rows until a pit lands within HOP of the previous leg's end
        last = b[-1]
        while q.shape[0] and min(
                np.hypot(q[0, 2] - last[2], q[0, 3] - last[3]),
                np.hypot(q[0, 2] - last[7], q[0, 3] - last[8])) > HOP:
            q = q[1:]
        b = np.vstack([b[b[:, 0] < q[0, 0]], q])
    t = b[:, 0]
    P = np.stack([b[:, 2:4], b[:, 7:9]], axis=1)          # (n, 2 pits, xy)
    chi = np.minimum(b[:, 5], b[:, 10])
    one = np.empty((len(t), 2))
    two = np.empty((len(t), 2))
    first = 0 if P[0, 0, 0] < P[0, 1, 0] else 1
    one[0], two[0] = P[0, first], P[0, 1 - first]
    for i in range(1, len(t)):
        keep = (np.hypot(*(P[i, 0] - one[i - 1])) + np.hypot(*(P[i, 1] - two[i - 1]))
                <= np.hypot(*(P[i, 1] - one[i - 1])) + np.hypot(*(P[i, 0] - two[i - 1])))
        one[i], two[i] = (P[i, 0], P[i, 1]) if keep else (P[i, 1], P[i, 0])
    end, why = len(t), "run end"
    if merges:
        floored = (np.nonzero(chi <= floor * (1 + 1e-6))[0] if floor > 0.0
                   else np.array([], dtype=int))
        step = np.maximum(np.hypot(*np.diff(one, axis=0).T),
                          np.hypot(*np.diff(two, axis=0).T))
        hops = np.nonzero(step > HOP)[0]
        if len(floored) and floored[0] < end:
            end, why = int(floored[0]), "chi floor"
        if len(hops) and hops[0] + 1 < end:
            end, why = int(hops[0] + 1), "pit hop"
    return t[:end], one[:end], two[:end], why


def scan_edge_time(run: str, pack_root=None) -> float | None:
    """First time the per-mouth scan's areal minimum sits on the window edge
    (centre A of horizon_scan.dat), or None if the run has no scan."""
    path = find_packed(run, pack_root) / "horizon_scan.dat"
    if not path.exists():
        return None
    rows = []
    for ln in path.read_text().splitlines():
        f = ln.split()
        if not f or ln.startswith("#") or f[1] != "A":
            continue
        rows.append((float(f[0]), float(f[6])))
    a = np.array(sorted(rows))
    return float(a[np.argmax(a[:, 1] >= a[:, 1].max() - 1e-6), 0])


def smoothed(t, *tracks):
    """Resample at DT and take the centred running mean over SMOOTH (the
    window shrinks at the ends, so a track keeps its first and last point)."""
    tu = np.arange(t[0], t[-1] + 0.5 * DT, DT)
    half = int(round(0.5 * SMOOTH / DT))
    out = []
    for trk in tracks:
        xy = np.stack([np.interp(tu, t, trk[:, k]) for k in (0, 1)], axis=1)
        c = np.vstack([np.zeros((1, 2)), np.cumsum(xy, axis=0)])
        i = np.arange(len(tu))
        lo, hi = np.maximum(i - half, 0), np.minimum(i + half + 1, len(tu))
        w = np.minimum(i - lo, hi - 1 - i)          # symmetric window
        lo, hi = i - w, i + w + 1
        out.append((c[hi] - c[lo]) / (hi - lo)[:, None])
    return (tu, *out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd()
    fig = plt.figure(figsize=(7.05, 3.0), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.35])
    axO, axS = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

    lim = 7.0
    axO.axhline(0.0, color=style.GRID, linewidth=0.6, zorder=0)
    axO.axvline(0.0, color=style.GRID, linewidth=0.6, zorder=0)
    for p, run, colr, ls, lw, merges, floor in ARMS:
        t, one, two, why = pit_tracks(run, args.pack_root, merges, floor)
        key = run[0] if not isinstance(run, str) else run
        if key in TRUST_END and t[-1] > TRUST_END[key]:
            # Cut before smoothing: the last drawn point sees no later sample.
            keep = t <= TRUST_END[key] + 1e-6
            t, one, two = t[keep], one[keep], two[keep]
            why = f"trust window, t <= {TRUST_END[key]:g}"
        raw = np.hypot(*(one - two).T)
        t, one, two = smoothed(t, one, two)
        sep = np.hypot(*(one - two).T)
        kw = dict(color=colr, linestyle=ls, linewidth=lw, zorder=3 if merges else 4)
        t_edge = None if merges else scan_edge_time(key, args.pack_root)
        live = t <= t_edge if t_edge is not None else np.ones(len(t), bool)
        for trk in (one, two):
            axO.plot(trk[live, 0], trk[live, 1], **kw)
            if not live.all():
                k0 = max(int(live.sum()) - 1, 0)
                axO.plot(trk[k0:, 0], trk[k0:, 1], alpha=0.4, **kw)
        axS.plot(t[live], sep[live], **kw)
        if not live.all():
            k0 = max(int(live.sum()) - 1, 0)
            axS.plot(t[k0:], sep[k0:], alpha=0.4, **kw)
            inflating = (p, t_edge, t[k0:], sep[k0:])
        # every track ends in a dot (the scatterers' at their trust window)
        for trk in (one, two):
            axO.plot(*trk[-1], marker="o", ms=2.6, color=colr, zorder=5)
        axS.plot(t[-1], sep[-1], marker="o", ms=2.6, color=colr, zorder=5)
        i = int(np.argmin(sep))
        print(f"[orbits] p = {p:.2f} {key}: t = 0-{t[-1]:.2f} ({why}); "
              f"min separation {sep[i]:.3f} at t = {t[i]:.2f} (raw {raw.min():.3f}), "
              f"last {sep[-1]:.3f}")

    # ---- (a) the orbital plane ---------------------------------------------
    axO.set_xlim(-lim, lim)
    axO.set_ylim(-lim, lim)
    axO.set_aspect("equal")
    axO.set_xlabel(r"$x$")
    axO.set_ylabel(r"$y$")
    # One key above both frames (the house rule: no key inside a frame), naming
    # every arm and its outcome; the two panels draw the same arms alike.
    from matplotlib.lines import Line2D
    fate = {0.10: r"$d{=}6$ merger", 0.12: "contact", 0.60: "plunge", 0.90: "plunge",
            0.25: "scatter", 0.45: "scatter"}
    keys = [Line2D([], [], color=c, linestyle=ls, linewidth=lw,
                   label=f"$p={p:.2f}$, {fate[p]}")
            for p, _, c, ls, lw, _m, _f in ARMS]
    fig.legend(handles=keys, loc="outside upper center", ncol=6, fontsize=7.0,
               frameon=False, handlelength=1.8, handletextpad=0.4, columnspacing=1.1)

    # ---- (b) separation -------------------------------------------------------
    # The longest record drawn is the p = 0.45 scatterer's (trust t = 67.6),
    # so the clock runs to 70.
    axS.set_xlim(0, 70)
    axS.set_ylim(0, 13.5)
    axS.set_xlabel(r"$t$")
    axS.set_ylabel(r"separation")

    for k, ax in enumerate((axO, axS)):
        ax.text(0.0, 1.03, f"({'ab'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "momentum_scan_orbits.png")
    style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[orbits] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
