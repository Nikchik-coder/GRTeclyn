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
  * They move the way they were pushed for ten units, come back, CROSS, and
    only then run apart -- with the fate OPPOSITE to the push.  Read the first
    separation as the branch and the sign comes out backwards, so the crossing
    is marked rather than hidden.
  * The growth rate was still falling at t = 27 (0.43 -> 0.21).  No rate is
    quoted and no fit is drawn until the sliding-window derivative goes flat.

The figure carries no prose: no caption, no worded axis labels, no worded panel
titles.  Identity is carried by the line itself -- the dash pattern is the SIGN
of the kick, the weight is its SIZE -- and every arm is named at its own end.
The numbers that used to sit in the caption (growth rates, how far each arm has
run, where the scan clips) are printed to the console instead.
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
from grteclyn_wrapper.visualisation.wormhole_merger.style import FAINT, INK, MUTED, paper  # noqa: E402

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
    wanted = [tuple(a.split("=", 1)) for a in args.arms] if args.arms else DEFAULT_ARMS

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
        m["clip"] = clipped_from(m["r_at"])
        m["dev"] = m["R"] - args.exact
        m["cross"] = zero_crossing(m["t"], m["dev"])
        good = slice(0, m["clip"]) if m["clip"] is not None else slice(None)
        m["rate"] = np.full(m["t"].size, np.nan)
        m["rate"][good] = rate(m["t"][good], m["dev"][good], args.window)
        # A window that reaches back across the crossing measures the crossing:
        # |dev| there is on its way through zero, so the log derivative blows up
        # and reads as a growth rate it is not.  It cost a 2.3x overestimate once.
        if m["cross"] is not None:
            m["rate"][m["t"] < m["cross"] + 2 * args.window] = np.nan
        arms.append(m)
        note = "   (NaN)" if m["dead"] else ""
        if m["clip"] is not None:
            note += f"   scan clipped from t = {m['t'][m['clip']]:.0f}"
        print(f"  {label:>7s}  {name:<24s} t = 0 .. {a[-1, 0]:6.2f}{note}")

    if not arms:
        raise SystemExit("no arm has data yet")

    paper(base=10.0)

    t_end = max(m["t"][-1] for m in arms)
    xhi = t_end * 1.10
    crossings = [m["cross"] for m in arms if m["cross"] is not None]
    t_cross = float(np.mean(crossings)) if crossings else None

    # ---- where the two members of a pair cross EACH OTHER --------------------
    # Not the same as where an arm crosses R_star: those four times are spread
    # over 1.6 units, the pair crossings over 0.05.  The pair crossing is the
    # branch point, so that is what gets marked.
    pair_cross = []
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
        c = zero_crossing(tt, np.interp(tt, m["t"], m["R"]) - np.interp(tt, p["t"], p["R"]))
        if c is not None:
            pair_cross.append((mag, c))
    if pair_cross:
        t_cross = float(np.mean([c for _, c in pair_cross]))
        for mag, c in sorted(pair_cross, reverse=True):
            print(f"  pair +-{mag:g} crosses itself at t = {c:.2f}")

    # ---- what used to be the caption, now printed ---------------------------
    for m in arms:
        f = np.isfinite(m["rate"])
        r_now = f"{m['rate'][f][-1]:.2f}" if f.any() else "too soon (still near the crossing)"
        print(f"  {m['label']:>7s}  growth rate {r_now}"
              + (f"   scan clipped from t = {m['t'][m['clip']]:.0f} at r = {m['r_at'][-1]:.3f}"
                 if m["clip"] is not None else ""))
    print(f"  level 3's own truncation seed, for comparison: {SEED_RATE:.4f}")

    # ---- the canvas ---------------------------------------------------------
    # No caption band any more: the strip under the axes holds only the tick
    # labels and the x symbol.  XLAB_H is that strip, measured, not guessed.
    # One panel.  Every arm is named in the right margin, so the right edge is
    # reserved and nothing is written on top of the curves.
    AX_H, XLAB_H = 3.0, 0.60                                 # inches
    H = AX_H + XLAB_H
    fig, axA = plt.subplots(1, 1, figsize=(5.9, H))
    fig.subplots_adjust(left=0.115, right=0.795,
                        top=1 - 0.22 / H, bottom=XLAB_H / H)

    def style_of(label: str) -> dict:
        """Identity without colour.  The dash pattern is the SIGN of the kick and
        the weight is its SIZE, so the two members of a pair read as a pair and
        the two amplitudes stay apart."""
        return dict(color=INK,
                    linewidth=0.9 if abs(float(label)) < 5e-3 else 1.5,
                    linestyle=(0, (4, 2.5)) if label.startswith("+") else "-")

    def tag(m: dict) -> str:
        return rf"$\varepsilon={m['label']}$" + (r"  (NaN)" if m["dead"] else "")

    def place_labels(ax, items, gap=11.0):
        """The arms are named in the right margin, not at their own ends.

        They do not all stop at the same time -- the small-kick pair is younger --
        so a label parked at a curve's end would sit mid-axes on top of another
        curve.  Each is parked at the right edge with a hairline leader back to
        its curve, and pushed clear of its neighbour when two curves finish at
        nearly the same height (the +-0.001 pair does, in panel (a): its whole
        excursion is thinner than the line).
        """
        x0, x1 = ax.get_xlim()
        disp = [ax.transData.transform((x1, y))[1] for _, y, _ in items]
        at, prev = {}, None
        for i in sorted(range(len(items)), key=lambda j: disp[j]):
            prev = disp[i] if prev is None else max(disp[i], prev + gap)
            at[i] = prev
        inv = ax.transData.inverted()
        for i, (xe, ye, text) in enumerate(items):
            yd = float(inv.transform((0.0, at[i]))[1])
            if xe < x1 - 0.01 * (x1 - x0):
                ax.plot([xe, x1], [ye, yd], color=FAINT, linewidth=0.6,
                        linestyle=(0, (1, 2)), zorder=2, clip_on=False)
            ax.annotate(text, (x1, yd), textcoords="offset points", xytext=(6, 0),
                        color=INK, va="center", ha="left", fontsize=9.5,
                        annotation_clip=False)

    # ---- the throat ------------------------------------------------------
    if t_cross is not None:
        axA.axvline(t_cross, color=FAINT, linewidth=0.7, linestyle=(0, (2, 3)), zorder=1)
    axA.axhline(args.exact, color=MUTED, linewidth=0.8, linestyle=(0, (1, 2.5)), zorder=2)
    labA = [(xhi, args.exact, r"$R_\star$")]
    for m in arms:
        st, k = style_of(m["label"]), m["clip"]
        # Past the cutoff the curve is the diagnostic, not the throat: draw it,
        # because hiding it would leave an unexplained stop, but draw it as a
        # ghost so nobody reads a number off it.
        axA.plot(m["t"][:k if k else None], m["R"][:k if k else None], zorder=3, **st)
        if k is not None:
            axA.plot(m["t"][k - 1:], m["R"][k - 1:], alpha=0.28, zorder=3, **st)
            axA.plot(m["t"][k], m["R"][k], "o", color=INK, markersize=3.5,
                     markeredgecolor="white", markeredgewidth=0.9, zorder=4)
        axA.plot(m["t"][-1], m["R"][-1], "X" if m["dead"] else "o", color=INK,
                 markersize=6 if m["dead"] else 3.5, markeredgecolor="white",
                 markeredgewidth=1.0, alpha=0.28 if k is not None else 1.0, zorder=4)
        labA.append((m["t"][-1], m["R"][-1], tag(m)))
    axA.set_xlim(0, xhi)
    axA.set_xlabel(r"$t$")
    axA.set_ylabel(r"$R_{\mathrm{min}}$")
    place_labels(axA, labA)


    out = pathlib.Path(args.out) if args.out else (
        root.parents[1] / "results" / "merger" / "figures" / "01_single_throat"
        / "single_throat_seed_branches.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=args.dpi)
    fig.savefig(out.with_suffix(".pdf"))
    print(f"[seed-branches] wrote {out} and {out.with_suffix('.pdf').name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
