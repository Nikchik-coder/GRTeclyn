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

DEFAULT: the +-0.01 pair, the arms that branch.  The +-0.1 pair is NOT drawn --
those two collapse and NaN inside sixteen units without ever branching, so
putting them on a figure about branching would say something untrue.  They are
a separate statement (the amplitude bound) and can be added by naming them.

WHAT IT HAS TO GET RIGHT
  * The arms do not start together, and that is the kick: psi -> psi(1 + eps)
    and R goes like psi^2, so R(0) is offset by ~2 eps.
  * They move the way they were pushed for ten units, come back, CROSS, and
    only then run apart -- with the fate OPPOSITE to the push.  Read the first
    separation as the branch and the sign comes out backwards, so the crossing
    is marked rather than hidden.
  * The growth rate was still falling at t = 27 (0.43 -> 0.21).  No rate is
    quoted and no fit is drawn until the sliding-window derivative goes flat.

Everything explanatory lives in the caption, not on top of the curves.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import RUNS_ROOT, find_run  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.style import (  # noqa: E402
    FAINT, GRID, INK, MUTED, SIGNED, paper,
)

R_EXACT = 3.8895      # closed form for the drainhole a = 2, m = 1
SEED_RATE = 0.1702    # level 3's own truncation-seed rate (BRANCHES.md)

DEFAULT_ARMS = [("single_eps_m1e2_t100", "-0.01"), ("single_eps_p1e2_t100", "+0.01")]


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
    return i if r_at_min.size - i >= runs else None


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

    # ---- the caption decides the figure height, so build it first ----------
    # The band under the axes has to hold the tick labels, the x-axis label AND
    # the caption.  Reserving only the caption is what drove it through the
    # x-labels twice; XLAB_H is the rest of that band, measured, not guessed.
    now = ", ".join(rf"$\varepsilon={m['label']}$: {m['rate'][np.isfinite(m['rate'])][-1]:.2f}"
                    for m in arms if np.isfinite(m["rate"]).any())
    state = ", ".join(f"{m['label']} to $t={m['t'][-1]:.0f}$"
                      + (" (NaN)" if m["dead"] else "") for m in arms)
    clipped = [m for m in arms if m["clip"] is not None]
    lines = [
        r"A Gaussian shell of amplitude $\varepsilon$ multiplies the conformal factor at $t=0$. "
        r"Since $R\propto\psi^{2}$ the arms start $2\varepsilon$ apart: that offset is the kick.",
        r"Each throat first moves the way it was pushed, returns, and crosses "
        + (rf"at $t\simeq{t_cross:.1f}$ (dotted). " if t_cross is not None else ". ")
        + r"Only after the crossing does the fate declare itself, with the opposite sign.",
    ]
    if clipped:
        which = ", ".join(rf"$\varepsilon={m['label']}$ from $t={m['t'][m['clip']]:.0f}$"
                          for m in clipped)
        lines.append(
            r"Pale: the ray scan's minimum has reached its inner cutoff "
            rf"($r={clipped[0]['r_at'][-1]:.2f}$) and no longer tracks the throat — {which}. "
            r"Nothing after that point is a measurement of the throat.")
    lines.append(
        rf"Growth rate still settling ({now}; level 3's own seed gives {SEED_RATE:.2f}), so none "
        rf"is quoted. Level 3, stop time 100; as of this build, {state}.")

    wrapped = []
    for ln in lines:                      # mathtext spans never contain spaces
        wrapped += textwrap.wrap(ln, width=150, break_long_words=False) or [""]

    AX_H, LINE_H, XLAB_H, PAD = 3.0, 0.145, 0.62, 0.16      # inches
    cap_h = len(wrapped) * LINE_H + PAD
    H = AX_H + XLAB_H + cap_h
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.4, H))
    fig.subplots_adjust(left=0.085, right=0.885, wspace=0.42,
                        top=1 - 0.34 / H, bottom=(XLAB_H + cap_h) / H)

    def label_end(ax, m, y, va="center"):
        ax.annotate(rf"$\varepsilon={m['label']}$" + (r"  (NaN)" if m["dead"] else ""),
                    (m["t"][-1], y), textcoords="offset points", xytext=(7, 0),
                    color=SIGNED.get(m["label"], INK), va=va, ha="left",
                    fontsize=9.5, annotation_clip=False)

    # ---- (a) the throat ------------------------------------------------------
    if t_cross is not None:
        axA.axvline(t_cross, color=FAINT, linewidth=0.7, linestyle=(0, (2, 3)), zorder=1)
    axA.axhline(args.exact, color=MUTED, linewidth=0.8, linestyle=(0, (5, 4)), zorder=2,
                label=rf"exact, $R_\star={args.exact:.4f}$")
    for m in arms:
        c = SIGNED.get(m["label"], INK)
        k = m["clip"]
        # Past the cutoff the curve is the diagnostic, not the throat: draw it,
        # because hiding it would leave an unexplained stop, but draw it as a
        # ghost so nobody reads a number off it.
        axA.plot(m["t"][:k if k else None], m["R"][:k if k else None],
                 color=c, linewidth=1.6, zorder=3)
        if k is not None:
            axA.plot(m["t"][k - 1:], m["R"][k - 1:], color=c, linewidth=1.6,
                     alpha=0.28, zorder=3)
            axA.plot(m["t"][k], m["R"][k], "o", color=c, markersize=3.5,
                     markeredgecolor="white", markeredgewidth=0.9, zorder=4)
        axA.plot(m["t"][-1], m["R"][-1], "X" if m["dead"] else "o", color=c,
                 markersize=6 if m["dead"] else 4, markeredgecolor="white",
                 markeredgewidth=1.0, alpha=0.28 if k is not None else 1.0, zorder=4)
        label_end(axA, m, m["R"][-1])
    axA.set_xlim(0, xhi)
    axA.set_xlabel(r"$t$  (code units)")
    axA.set_ylabel(r"minimum areal radius  $R_{\mathrm{min}}$")
    axA.set_title(r"(a)  the fate is opposite to the push", loc="left", pad=7)
    # Every curve carries its own epsilon at its end, so the legend has one job:
    # name the dashed line.  Repeating the series here would be pure clutter.
    axA.legend(loc="upper left", handlelength=1.8, borderaxespad=0.2, fontsize=8.5)

    # ---- (b) the separation, log --------------------------------------------
    if t_cross is not None:
        axB.axvline(t_cross, color=FAINT, linewidth=0.7, linestyle=(0, (2, 3)), zorder=1)
    for m in arms:
        c = SIGNED.get(m["label"], INK)
        d = np.abs(m["dev"]) / args.exact
        k = m["clip"]
        ok = d > 0
        head = ok.copy()
        if k is not None:
            head[k:] = False
            tail = ok.copy(); tail[:k - 1] = False
            axB.semilogy(m["t"][tail], d[tail], color=c, linewidth=1.6, alpha=0.28, zorder=3)
        axB.semilogy(m["t"][head], d[head], color=c, linewidth=1.6, zorder=3)
        label_end(axB, m, d[-1], va="bottom" if m["dev"][-1] < 0 else "top")
    axB.set_xlim(0, xhi)
    axB.set_xlabel(r"$t$  (code units)")
    axB.set_ylabel(r"$|R_{\mathrm{min}}-R_\star|\,/\,R_\star$")
    axB.set_title(r"(b)  the transient drains, then the branch grows", loc="left", pad=7)

    fig.text(0.085, cap_h / H, "\n".join(wrapped),
             color=MUTED, fontsize=7.6, va="top", ha="left", linespacing=1.6)

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
