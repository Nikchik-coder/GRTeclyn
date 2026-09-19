#!/usr/bin/env python3
r"""The lone throat's fate chosen on purpose: the declared-seed pair.

`plot_branches` shows the same throat collapsing at refinement level 3 and
inflating at level 4.  That is a problem rather than a result: the fate is set
by the truncation error's seed, and nobody chose it.  This is the controlled
version -- ONE resolution, one knob: the amplitude of a Gaussian shell laid on
the conformal factor at t = 0, centred on the throat.  The velocity fields are
left at zero, so the momentum constraint stays exact and only the Hamiltonian
is violated, at order epsilon.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_seed_branches \
        [--runs-root DIR] [--out FILE] [--exact 3.8895] [RUN=LABEL ...]

DEFAULT: the +-0.01 and +-0.001 pairs -- two amplitudes a factor ten apart, so
the figure can say whether the crossing time belongs to the kick or to the
throat.  The +-0.1 pair is NOT drawn: those two collapse and NaN inside sixteen
units without ever branching, so putting them on a figure about branching would
say something untrue.  They are a separate statement (the amplitude bound) and
can be added by naming them.

WHAT IT HAS TO GET RIGHT
  * The arms do not start together, and that is the kick: psi -> psi(1 + eps)
    and R goes like psi^2, so R(0) is offset by ~2 eps.
  * From t = 0 each arm moves BACK toward R_star -- it does not first move
    further the way it was pushed -- crosses its twin, and only then runs away
    on the far side, so the fate is OPPOSITE to the push.  Read the initial
    offset as the branch and the sign comes out backwards; the crossing is
    marked rather than hidden.  It falls at the same time for both amplitudes
    (t = 13.01 and 13.04), which is what linearity predicts: a decaying and a
    growing part, both proportional to eps, cancel at an eps-free time.
  * No growth rate is drawn.  The sliding-window rate never went flat, and the
    quotable number is a DELAY instead -- how much later the tenfold smaller kick
    reaches the same state -- which the console prints from the pair
    difference R(-eps) - R(+eps), where any offset common to both arms cancels.
  * A collapse arm does not end where its dot says: the dot is the SCAN losing
    the throat (its minimum walks inside the inner cutoff), not the run dying.
    The +0.01 run lives to t = 100 as a black hole whose radius has stalled
    (horizon R 3.88 -> 2.34 -> 2.57, printed to the console), so from the dot
    a flat MUTED line carries the last read value to the run's end -- stalled,
    still alive.  The inflating arms' throats kept GROWING past their scan
    loss, so a flat line there would lie and they get none; drawing the
    horizon itself as a curve was tried twice (2026-09-16) and rejected as
    clutter.

STYLE (2026-09-16, "PRD review style"): a single-column REVTeX figure -- full
box frame, inward ticks on all four sides with minors, no grid, and NO boxed
key: a five-row legend made the measuring `legend()` grow a dead band above
the curves, so each arm is named in place along its own curve and the axis
hugs the data (user, 2026-09-16).  NO colour: the
user's call, twice (2026-09-10 "no coloring", 2026-09-16 again when a signed
palette was tried) -- identity is the dash (solid in, dashed out) and the
weight (the size).  The numbers that used to sit in the caption (growth rates,
how far each arm has run, where the scan clips) are printed to the console
instead.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import RUNS_ROOT, find_run  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.style import (  # noqa: E402
    DEEP_GREEN, FAINT, INK, MUTED, edge_label, prd, save,
)

R_EXACT = 3.8895      # closed form for the drainhole a = 2, m = 1
SEED_RATE = 0.1702    # level 3's own truncation-seed rate (BRANCHES.md)

DEFAULT_ARMS = [
    ("single_eps_m1e2_t100", "-0.01"), ("single_eps_p1e2_t100", "+0.01"),
    ("single_eps_m1e3_t100", "-0.001"), ("single_eps_p1e3_t100", "+0.001"),
]


def areal(run_dir: pathlib.Path) -> np.ndarray | None:
    """(t, R_min, r_at_min).  The third column is what tells us whether R_min is
    still the throat: the ray scan has an inner cutoff, and once the true
    minimum moves inside it the scan reports the cutoff instead."""
    for rel in ("small_data/areal_radius.dat", "areal_radius.dat"):
        f = run_dir / rel
        if f.is_file():
            a = np.loadtxt(f, ndmin=2)
            return a[np.argsort(a[:, 0])][:, :3] if a.size else None
    return None


def clipped_from(r_at_min: np.ndarray, runs: int = 3) -> int | None:
    """First index of the tail where the minimum's position stops moving.

    A collapsing throat drives its minimum inward until it reaches the scan's
    inner cutoff; from there `r_at_min` is pinned at that value while R_min
    keeps falling for a reason that is no longer the throat.  Anything after
    this index is a property of the diagnostic, not of the spacetime.
    """
    if r_at_min.size < runs + 1:
        return None
    floor = r_at_min.min()
    at = np.isclose(r_at_min, floor, rtol=0, atol=1e-6)
    if not at[-1]:
        return None
    i = r_at_min.size - 1
    while i > 0 and at[i - 1]:
        i -= 1
    if r_at_min.size - i < runs:
        return None
    # A minimum that simply never moved is not a clipped one.  Only call it
    # clipped if the scan walked INWARD to get there -- otherwise a quiet throat
    # whose minimum sits on one grid point for the whole run reads as clipped
    # from t = 0, which would grey out a perfectly good curve.
    return i if i > 0 and r_at_min[:i].max() > floor * 1.05 else None


def mots(run_dir: pathlib.Path) -> np.ndarray | None:
    """(t, R_mots) of the outermost MOTS per output time, from the horizon
    scan.  The scan probes several centres (A/B/C); per time the largest
    horizon among the centres that found one is kept.  None when the run never
    held a horizon -- the inflating arms."""
    for rel in ("small_data/horizon_scan.dat", "horizon_scan.dat"):
        f = run_dir / rel
        if not f.is_file():
            continue
        # usecols skips the non-numeric centre column: time, n_mots, R_mots.
        a = np.genfromtxt(f, usecols=(0, 9, 11), ndmin=2)
        a = a[np.isfinite(a).all(axis=1) & (a[:, 1] > 0)] if a.size else a
        if a.shape[0] == 0:
            return None
        out: dict[float, float] = {}
        for t, _, R in a:
            out[t] = max(out.get(t, -np.inf), R)
        tt = np.array(sorted(out))
        return np.column_stack([tt, [out[t] for t in tt]])
    return None


def died(run_dir: pathlib.Path) -> bool:
    for rel in ("run.log", "run_tail.log"):
        f = run_dir / rel
        if f.is_file():
            try:
                return "NaN in GRAMRLevel" in f.read_text(errors="ignore")[-40000:]
            except OSError:
                pass
    return False


def zero_crossing(t: np.ndarray, d: np.ndarray) -> float | None:
    k = np.where(np.diff(np.sign(d)) != 0)[0]
    if not k.size:
        return None
    i = k[0]
    return float(t[i] - d[i] * (t[i + 1] - t[i]) / (d[i + 1] - d[i]))


def rate(t: np.ndarray, d: np.ndarray, half: float = 3.0) -> np.ndarray:
    """d ln|d| / dt over +-half, only where |d| grows monotonically across it."""
    out, a = np.full(t.size, np.nan), np.abs(d)
    for i, ti in enumerate(t):
        lo, hi = int(np.argmin(np.abs(t - (ti - half)))), int(np.argmin(np.abs(t - (ti + half))))
        if hi > lo and a[lo] > 0 and a[lo] < a[i] < a[hi]:
            out[i] = (np.log(a[hi]) - np.log(a[lo])) / (t[hi] - t[lo])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--out", default=None)
    ap.add_argument("--exact", type=float, default=R_EXACT)
    ap.add_argument("--window", type=float, default=3.0)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("arms", nargs="*", metavar="RUN=LABEL")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.runs_root).expanduser().resolve()
    wanted = [tuple(a.split("=", 1)) for a in args.arms] if args.arms else None

    prd(base=10.0)
    fig, axA = plt.subplots(1, 1, figsize=(3.4, 2.6))
    fig.subplots_adjust(left=0.125, right=0.965, top=0.965, bottom=0.165)
    figure_panel(axA, runs_root=root, arms_spec=wanted,
                 exact=args.exact, window=args.window)

    out = pathlib.Path(args.out) if args.out else (
        root.parents[1] / "results" / "merger" / "figures" / "01_single_throat"
        / "single_throat_seed_branches.png")
    png = save(fig, out, dpi=args.dpi)
    print(f"[seed-branches] wrote {png} (+pdf)")
    return 0


def figure_panel(axA, *, runs_root=RUNS_ROOT, arms_spec=None,
                 exact: float = R_EXACT, window: float = 3.0) -> None:
    """The declared-seed branching panel drawn onto a SUPPLIED axis.

    Everything the module docstring promises -- the crossing mark, the
    stalled continuation, the exponential fits, the names in place --
    happens here; ``main`` wraps it in its own single-column canvas, and
    the article's combined strip (plot_single_throat_row, 2026-09-18) lays
    it beside the undeclared-seed panels.  ``prd`` must already be active,
    and no letter tag is drawn: the caller owns the lettering.
    """
    root = pathlib.Path(runs_root).expanduser().resolve()
    wanted = list(arms_spec) if arms_spec else DEFAULT_ARMS

    arms = []
    for name, label in wanted:
        try:
            d = find_run(root, name)
        except FileNotFoundError:
            print(f"  {name}: not found, skipped"); continue
        a = areal(d)
        if a is None or a.shape[0] < 3:
            print(f"  {name}: nothing to plot yet, skipped"); continue
        m = dict(name=name, label=label, t=a[:, 0], R=a[:, 1], r_at=a[:, 2], dead=died(d))
        m["hz"] = mots(d)
        if m["hz"] is not None:
            # The scan's late-time false positives on the inflating arms sit at
            # R ~ 33 -- a crossing out at the sponge, not a horizon (the
            # registry: no horizon at any time on those arms).  A collapse
            # horizon is born AT the throat's own size and shrinks, so any
            # reading far above R_star is rejected, not drawn.
            hz = m["hz"][m["hz"][:, 1] <= 1.2 * exact]
            m["hz"] = hz if hz.shape[0] else None
        m["clip"] = clipped_from(m["r_at"])
        m["dev"] = m["R"] - exact
        m["cross"] = zero_crossing(m["t"], m["dev"])
        good = slice(0, m["clip"]) if m["clip"] is not None else slice(None)
        m["rate"] = np.full(m["t"].size, np.nan)
        m["rate"][good] = rate(m["t"][good], m["dev"][good], window)
        # A window that reaches back across the crossing measures the crossing:
        # |dev| there is on its way through zero, so the log derivative blows up
        # and reads as a growth rate it is not.  It cost a 2.3x overestimate once.
        if m["cross"] is not None:
            m["rate"][m["t"] < m["cross"] + 2 * window] = np.nan
        arms.append(m)
        note = "   (NaN)" if m["dead"] else ""
        if m["clip"] is not None:
            note += f"   scan clipped from t = {m['t'][m['clip']]:.0f}"
        if m["hz"] is not None:
            note += (f"   horizon t = {m['hz'][0, 0]:.0f} .. {m['hz'][-1, 0]:.0f}"
                     f" (R {m['hz'][0, 1]:.2f} -> {m['hz'][-1, 1]:.2f})")
        print(f"  {label:>7s}  {name:<24s} t = 0 .. {a[-1, 0]:6.2f}{note}")

    if not arms:
        raise SystemExit("no arm has data yet")

    # The axis ends where the last MEASUREMENT ends, not where the last run ends:
    # a curve is cut at its scan clip (see the throat panel), so time after the
    # latest clip would be empty frame.
    def valid_end(m):
        return m["clip"] - 1 if m["clip"] is not None else m["t"].size - 1
    def stalled(m) -> bool:
        """The one continuation that is true: a collapse arm (below R_star at
        its dot) whose run outlived its scan with the radius stalled."""
        e = valid_end(m)
        return (m["clip"] is not None and not m["dead"]
                and m["R"][e] < exact and m["t"][-1] > m["t"][e])

    t_end = max(m["t"][valid_end(m)] for m in arms)
    t_end = max([t_end] + [m["t"][-1] for m in arms if stalled(m)])
    xhi = t_end * 1.05
    crossings = [m["cross"] for m in arms if m["cross"] is not None]
    t_cross = float(np.mean(crossings)) if crossings else None

    # ---- where the two members of a pair cross EACH OTHER --------------------
    # Not the same as where an arm crosses R_star: those four times are spread
    # over 1.6 units, the pair crossings over 0.05.  The pair crossing is the
    # branch point, so that is what gets marked.
    pair_cross, pairs = [], {}
    for m in arms:
        if not m["label"].startswith("-"):
            continue
        mag = abs(float(m["label"]))
        p = next((x for x in arms if x["label"].startswith("+")
                  and abs(abs(float(x["label"])) - mag) < 1e-12), None)
        if p is None:
            continue
        tt = np.intersect1d(np.round(m["t"], 6), np.round(p["t"], 6))
        if tt.size < 3:
            continue
        D = np.interp(tt, m["t"], m["R"]) - np.interp(tt, p["t"], p["R"])
        c = zero_crossing(tt, D)
        if c is not None:
            pair_cross.append((mag, c))
        # The pair difference is only as good as the worse of its two arms: stop
        # it where either arm's scan clips.
        ends = [x["t"][x["clip"]] for x in (m, p) if x["clip"] is not None]
        keep = tt < min(ends) if ends else np.ones(tt.size, bool)
        pairs[mag] = (tt[keep], D[keep])
    if pair_cross:
        t_cross = float(np.mean([c for _, c in pair_cross]))
        for mag, c in sorted(pair_cross, reverse=True):
            print(f"  pair +-{mag:g} crosses itself at t = {c:.2f}")

    # ---- the delay per decade of kick ---------------------------------------
    # How much later the smaller pair's difference reaches each value the larger
    # pair's reached.  If the growth were one clean exponential this would be
    # ln(10)/rate at every level; it lengthens instead while the decaying part of
    # the response still matters, so it is printed as a table, never as one rate.
    def reach(t, y, level):
        i = np.where(y >= level)[0]
        if not i.size or i[0] == 0:
            return np.nan
        j = i[0]
        return t[j - 1] + (level - y[j - 1]) * (t[j] - t[j - 1]) / (y[j] - y[j - 1])
    if len(pairs) >= 2:
        big, small = sorted(pairs, reverse=True)[:2]
        (tb, Db), (ts, Ds) = pairs[big], pairs[small]
        top = min(Db.max(), Ds.max())
        print(f"  delay, pair +-{small:g} after +-{big:g}, at the same R(-eps) - R(+eps)"
              f"  (level 3's own rate {SEED_RATE} would give {np.log(10) / SEED_RATE:.1f}):")
        for level in (0.1, 0.3, 1.0, 1.5, top * 0.98):
            if level > top:
                continue
            d = reach(ts, Ds, level) - reach(tb, Db, level)
            print(f"    at {level:5.2f}:  {d:6.2f}")

    # ---- what used to be the caption, now printed ---------------------------
    for m in arms:
        f = np.isfinite(m["rate"])
        r_now = f"{m['rate'][f][-1]:.2f}" if f.any() else "too soon (still near the crossing)"
        print(f"  {m['label']:>7s}  growth rate {r_now}"
              + (f"   scan clipped from t = {m['t'][m['clip']]:.0f} at r = {m['r_at'][-1]:.3f}"
                 if m["clip"] is not None else ""))
    print(f"  level 3's own truncation seed, for comparison: {SEED_RATE:.4f}")

    def style_of(label: str) -> dict:
        """Identity without colour -- the user's call for THIS figure (2026-09-10
        "no coloring", reaffirmed 2026-09-16), overriding the campaign palette.
        The dash pattern is the SIGN of the kick and the weight is its SIZE, so
        the two members of a pair read as a pair and the amplitudes stay apart.
        """
        return dict(color=INK,
                    linewidth=1.0 if abs(float(label)) < 5e-3 else 1.6,
                    linestyle=(0, (4, 2.5)) if label.startswith("+") else (0, ()))

    def tag(m: dict) -> str:
        return rf"$\varepsilon={m['label']}$" + (r" (NaN)" if m["dead"] else "")

    # ---- the throat ------------------------------------------------------
    if t_cross is not None:
        axA.axvline(t_cross, color=FAINT, linewidth=0.7, linestyle=(0, (2, 3)), zorder=1)
    axA.axhline(exact, color=MUTED, linewidth=0.8, linestyle=(0, (1, 2.5)), zorder=2)
    for m in arms:
        st, e = style_of(m["label"]), valid_end(m)
        # A curve ends at its last MEASUREMENT of the throat.  Past a scan clip
        # the number is the areal radius at the scan's inner edge, and drawn --
        # even pale -- it read as the throat turning over: both inflating arms
        # appeared to fall from R ~ 9 to ~5, with their labels in the wrong
        # order.  A dot marks a curve that stops because the scan lost the
        # throat, a cross one that stops because the run died.
        axA.plot(m["t"][:e + 1], m["R"][:e + 1], zorder=3, **st)
        dead_here = m["dead"] and m["clip"] is None
        # The stalled continuation: from the dot, flat and muted to the run's
        # end -- the radius has settled and the run is still alive (the
        # horizon numbers behind that statement are printed to the console).
        if stalled(m):
            axA.plot([m["t"][e], m["t"][-1]], [m["R"][e]] * 2, color=MUTED,
                     linewidth=0.9, linestyle=st["linestyle"], zorder=2.5)
        axA.plot(m["t"][e], m["R"][e], "X" if dead_here else "o", color=st["color"],
                 markersize=5 if dead_here else 3, markeredgecolor="white",
                 markeredgewidth=0.8, zorder=4)
    # ---- the exponential fit (asked for 2026-09-16) -----------------------
    # Least squares on ln|R - R_star| over each +-0.01 arm's own window:
    # inflation t = 18-34, collapse t = 16-26 (before its scan clip).  The
    # windows are stated because the rate is NOT flat -- the kick's decaying
    # transient runs through them -- so these are LOCAL e-folds, steeper than
    # the unkicked mode's tau = 5.88, and the caption says so.
    fit_top = None
    for lab, (f0, f1) in (("-0.01", (18.0, 31.0)), ("+0.01", (16.0, 26.0))):
        arm = next((m for m in arms if m["label"] == lab), None)
        if arm is None:
            continue
        e = valid_end(arm)
        tt, RR = arm["t"][:e + 1], arm["R"][:e + 1]
        sel = (tt >= f0) & (tt <= f1) & (np.abs(RR - exact) > 0)
        if sel.sum() < 4:
            continue
        lam, lnA = np.polyfit(tt[sel], np.log(np.abs(RR[sel] - exact)), 1)
        sgn = np.sign(RR[sel][-1] - exact)
        tg = np.linspace(f0, f1, 50)
        axA.plot(tg, exact + sgn * np.exp(lnA + lam * tg),
                 color=DEEP_GREEN, linewidth=1.9, zorder=5)
        if sgn > 0:
            fit_top = (f1, exact + np.exp(lnA + lam * f1))
        print(f"  exp fit {lab:>6s} over t = {f0:.0f}-{f1:.0f}:"
              f" rate {lam:.3f}, tau {1 / lam:.2f}")
    # One deep green name serves both deep green lines, in equation form -- the
    # user's call (2026-09-16): "exp. fit" out, the law itself in.  Up-left of
    # the inflation fit's end, where the heavy arm has not yet risen.
    if fit_top is not None:
        axA.text(fit_top[0] - 1.0, fit_top[1] + 0.15, r"$\propto e^{t/\tau}$",
                 color=DEEP_GREEN, fontsize=8, ha="right", va="bottom")
    axA.set_xlim(0, xhi)
    axA.set_xlabel(r"$t$")
    axA.set_ylabel(r"$R_{\mathrm{min}}$")
    # Headroom under the lowest curve, for the stalled arm's name.  Stacked
    # above its own flat line the name shared that line with the dead arm's
    # (the row canvas, 2026-09-18, where the panel is a third of a page
    # wide); the two now sit on opposite sides of it and cannot meet.
    ylo, yhi_ = axA.get_ylim()
    axA.set_ylim(ylo - 0.10 * (yhi_ - ylo), yhi_)
    # ---- names written along the curves, no boxed key ----------------------
    # A five-row key forced the measuring legend to grow the axis until a dead
    # band sat above every curve; a two-column key still needed a third of the
    # frame.  So the box went (user, 2026-09-16) and each arm is named in
    # place: inflating arms along their rise (the heavy one up-left, the light
    # one down-right, each on its own empty side), the stalled arm above its
    # flat line, the dead arm at its cross.  Anchors are read off the data, so
    # the names travel with the curves.
    def t_at(m, level: float) -> float | None:
        """First time an arm's curve reaches ``level``, by linear interpolation."""
        e = valid_end(m)
        tt, RR = m["t"][:e + 1], m["R"][:e + 1]
        i = int(np.argmax(RR >= level))
        if i == 0:
            return None
        return float(tt[i - 1] + (level - RR[i - 1]) * (tt[i] - tt[i - 1])
                     / (RR[i] - RR[i - 1]))

    for m in arms:
        st, e = style_of(m["label"]), valid_end(m)
        heavy = st["linewidth"] > 1.2
        if m["R"][e] > exact:      # inflating: name it along the rise
            level = exact + (0.55 if heavy else 0.42) * (m["R"][e] - exact)
            ta = t_at(m, level)
            if ta is None:
                axA.text(m["t"][e] + 0.015 * xhi, m["R"][e], tag(m),
                         fontsize=8, ha="left", va="center")
            elif heavy:
                axA.text(ta - 1.2, level + 0.08, tag(m),
                         fontsize=8, ha="right", va="bottom")
            else:
                axA.text(ta + 1.2, level - 0.08, tag(m),
                         fontsize=8, ha="left", va="top")
        elif stalled(m):                # collapsed, alive: UNDER the flat line,
            # right-aligned at the run's end, in the headroom opened above.
            axA.annotate(tag(m), (m["t"][-1], m["R"][e]), xytext=(-2, -4),
                         textcoords="offset points", fontsize=8,
                         ha="right", va="top")
        else:                           # collapsed, dead: above its cross, in
            # the band between the stalled line and R_star.  The offsets are
            # in POINTS, so the clearance is the same on a single column and
            # on a third of a page.
            axA.annotate(tag(m), (m["t"][e], m["R"][e]), xytext=(4, 4),
                         textcoords="offset points", fontsize=8,
                         ha="left", va="bottom")
    # The two rulers named in place, small and muted, clear of every curve.
    edge_label(axA, exact, r"$R_\star$")
    if t_cross is not None:
        ylo, yhi_ = axA.get_ylim()
        axA.text(t_cross + 0.012 * xhi, ylo + 0.035 * (yhi_ - ylo),
                 r"$t_\times$", color=MUTED, fontsize=8, ha="left", va="bottom")


if __name__ == "__main__":
    sys.exit(main())
