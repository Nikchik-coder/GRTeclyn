#!/usr/bin/env python3
r"""Campaign M step 3: the exotic bill across the potential's knobs.

Three spins (fam_b_0003 / 0012 / 0025, v_e 0.27 / 0.50 / 0.85), every
solve at pinned J and R_e, grid 150x30, from the packed TSVs:

- (a)-(c) the shape landscape per spin: the bill's shift against the
  pure kink, X/X_kink - 1 in percent, over the scanned (q1, q2) box of
  Q = 1 + q1 u + q2 u^2 (u = psi/psi_minus) at kink mass 0.3.  The bill
  falls toward +q1, +q2 at every spin; the black dot is the box's best
  clean point (all monitors inside the 1e-8 gate), grey cells have no
  solution (min Q <= 0, or Newton stalled).
- (d) every walk down the landscape on one axis, the far-well mass
  m_- = m sqrt(1 + q1 + q2) (the curvature of the psi_minus well): the
  pure-kink mass ladders (dots, q = 0, m_- = m) and the open ray walks
  (thin lines, m = 0.3).  The rays nearly collapse onto m_-, pure q1
  running lowest -- the far well's steepness carries most of the shape
  knob.
- (e) the end-mass asymmetry: X(gamma)/X(0) walking gamma to the
  drainhole's -pi at the pure kink m 0.3 -- a ~ +42 % penalty, nearly
  spin-independent.
- (f) the summary by design: X against v_e for the V = 0 member, the
  pure kink m 0.3, and the best clean shape over the box plus the open
  ray walks (q-rays stages; every ray ended on Newton or the monitor
  limit with X still falling, so these are frontier values at this
  grid, not the landscape's bottom).

Colours are red / green / blue by spin (the keys above (a)-(c) name
them); ``--colors C1,C2,C3`` redraws in another scheme.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_potential_scans

Reads ``results/optimisation/scans/*.tsv`` and
``results/optimisation/ladders_150x30.tsv``; writes
``results/optimisation/figures/potential_scans`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[5]
SCANS = REPO / "results" / "optimisation" / "scans"
LADDERS = REPO / "results" / "optimisation" / "ladders_150x30.tsv"
OUT = REPO / "results" / "optimisation" / "figures" / "potential_scans"
RGB = ("#d62728", "#2ca02c", "#1f77b4")
# (member, nominal v_e) in spin order; the scan grid and its anchor mass
MEMBERS = (("fam_b_0003", 0.27), ("fam_b_0012", 0.50), ("fam_b_0025", 0.85))
QS = (-0.6, -0.3, 0.0, 0.3, 0.6)
MASS = 0.3
GRID = "150x30"
TIGHT = dict(handlelength=1.5, handletextpad=0.35, columnspacing=0.5)


def read(path: pathlib.Path) -> list[dict]:
    with open(path) as fh:
        return [{k: (v if k in ("member", "mode", "verdict") else float(v))
                 for k, v in row.items()}
                for row in csv.DictReader(
                    (ln for ln in fh if not ln.startswith("#")),
                    delimiter="\t")]


def shape(member: str) -> dict:
    """The member's (q1, q2) landscape: X / X_kink - 1 in percent over the
    box (nan where no solution exists), the box's best clean point, and the
    best clean point over the box plus the open ray walks."""
    rows = read(SCANS / f"{member}_shape_{GRID}.tsv")
    rays = SCANS / f"{member}_rays_{GRID}.tsv"
    kink = next(r["X"] for r in rows if r["q1"] == 0.0 and r["q2"] == 0.0)
    rel = np.full((len(QS), len(QS)), np.nan)      # [q2, q1]
    box_best = best = (math.inf, None)
    for r in rows + (read(rays) if rays.exists() else []):
        if math.isnan(r["X"]):
            continue
        if r["q1"] in QS and r["q2"] in QS:
            rel[QS.index(r["q2"]), QS.index(r["q1"])] = \
                100.0 * (r["X"] / kink - 1.0)
            if r["verdict"] == "PASS" and r["X"] < box_best[0]:
                box_best = (r["X"], (r["q1"], r["q2"]))
        if r["verdict"] == "PASS" and r["X"] < best[0]:
            best = (r["X"], (r["q1"], r["q2"]))
    return {"rel": rel, "kink": kink, "box_best": box_best, "best": best}


def gamma(member: str) -> dict:
    """The gamma walk: X(gamma) / X(0) at the pure kink."""
    rows = read(SCANS / f"{member}_gamma_{GRID}.tsv")
    rows.sort(key=lambda r: -r["gamma"])
    x0 = next(r["X"] for r in rows if r["gamma"] == 0.0)
    return {"g": np.array([-r["gamma"] / math.pi for r in rows]),
            "rel": np.array([r["X"] / x0 for r in rows])}


RAY_STYLES = (("$+q_1$", "-"), ("$+q_2$", (0, (1.0, 1.2))),
              ("diagonal", (0, (3.0, 1.6))))


def rays(member: str) -> list[dict]:
    """The member's ray walks as (far-well mass, X) curves, in the
    RAY_STYLES order: pure q1, pure q2, the diagonal."""
    rows = read(SCANS / f"{member}_rays_{GRID}.tsv")
    picks = (lambda r: r["q2"] == 0.0, lambda r: r["q1"] == 0.0,
             lambda r: r["q1"] == r["q2"])
    out = []
    for pick in picks:
        keep = sorted((r for r in rows if pick(r) and not math.isnan(r["X"])),
                      key=lambda r: r["q1"] + r["q2"])
        out.append({"mm": MASS * np.sqrt([1.0 + r["q1"] + r["q2"]
                                          for r in keep]),
                    "X": np.array([r["X"] for r in keep])})
    return out


def ladders() -> dict[str, dict]:
    rows = read(LADDERS)
    out: dict[str, dict] = {}
    for member, _ in MEMBERS:
        keep = sorted((r for r in rows if r["member"] == member),
                      key=lambda r: r["mass"])
        out[member] = {"m": np.array([r["mass"] for r in keep]),
                       "X": np.array([r["X"] for r in keep])}
    return out


def draw(shapes, gammas, lads, rayss, colours):
    style.prd(8.0)
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.6), layout="constrained")
    top, (ax_d, ax_e, ax_f) = axes
    nosol = dict(facecolor="#d9d9d6", edgecolor="none")
    dot = dict(ls="none", marker="o", ms=4.5, mfc="black", mec="black",
               zorder=6, clip_on=False)
    rule = dict(color=style.FAINT, lw=0.6, zorder=0)

    def line(color, ls="-", lw=1.3, **kw):
        return dict(color=color, ls=ls, lw=lw, **kw)

    def key(fmt, label):
        return (Line2D([], [], **{k: v for k, v in fmt.items()
                                  if k != "clip_on"}), label)

    # (a)-(c) the shape landscape, one spin per panel, shared colour scale;
    # red deepens where the shape pays, blue where it costs
    vmax = max(float(np.nanmax(np.abs(s["rel"]))) for s in shapes)
    cmap = plt.get_cmap("RdBu").copy()
    cmap.set_bad(nosol["facecolor"])
    edges = np.array([q - 0.15 for q in QS] + [QS[-1] + 0.15])
    mesh = None
    for ax, (member, ve), s, c in zip(top, MEMBERS, shapes, colours):
        mesh = ax.pcolormesh(edges, edges, np.ma.masked_invalid(s["rel"]),
                             cmap=cmap, vmin=-vmax, vmax=vmax,
                             edgecolors="white", lw=0.4)
        ax.plot([s["box_best"][1][0]], [s["box_best"][1][1]], **dot)
        ax.set(xticks=QS, yticks=QS, xlabel="$q_1$", aspect="equal")
        style.legend_top(ax, [key(line(c), f"$v_e = {ve:.2f}$")], **TIGHT)
    top[0].set_ylabel("$q_2$")
    cb = fig.colorbar(mesh, ax=list(top), pad=0.015, fraction=0.05)
    cb.set_label(r"$X/X_{\rm kink} - 1$ [%]")

    # (d) every walk on the far-well mass axis: the kink ladders (dots,
    # m_- = m) continued by the open ray walks (thin lines, m = 0.3)
    for (member, ve), rr, c in zip(MEMBERS, rayss, colours):
        ax_d.plot(lads[member]["m"], lads[member]["X"],
                  marker="o", ms=2.8, **line(c))
        for r, (_, ls) in zip(rr, RAY_STYLES):
            ax_d.plot(r["mm"], r["X"], **line(c, ls=ls, lw=0.9))
    ax_d.set(xlim=(-0.02, 1.25), ylim=(1.0, 3.1),
             xlabel=r"far-well mass $m_- = m\sqrt{1 + q_1 + q_2}$",
             ylabel=r"$X = |{\rm VIQ}|/R_e$")
    style.legend_top(ax_d, [key(dict(line(style.INK), marker="o", ms=2.8),
                                "kink ladder")] +
                           [key(line(style.INK, ls=ls, lw=0.9), lab)
                            for lab, ls in RAY_STYLES],
                     ncol=2, borderpad=0.4, **TIGHT)

    # (e) the gamma walk, relative to gamma = 0; the three curves lie on
    # top of one another (the penalty is nearly spin-independent), so
    # staggered markers keep all three spins visible
    ax_e.axhline(1.0, **rule)
    for i, ((member, ve), g, c) in enumerate(zip(MEMBERS, gammas, colours)):
        ax_e.plot(g["g"], g["rel"], marker=("o", "s", "^")[i], ms=2.8,
                  markevery=(i, 3), **line(c, lw=1.0))
    ax_e.set(xlim=(0, 1), ylim=(0.97, 1.48), xlabel=r"$-\gamma/\pi$",
             ylabel=r"$X(\gamma)/X(0)$")
    style.legend_top(ax_e, [key(rule, rf"pure kink $m = {MASS:g}$, "
                                      r"$\gamma = 0$")], **TIGHT)

    # (f) the bill by design, across spin
    ve = np.array([v for _, v in MEMBERS])
    designs = (
        (r"$V = 0$", line(style.INK), [lads[m]["X"][0] for m, _ in MEMBERS]),
        (rf"kink $m = {MASS:g}$", line("#6a6a66", (0, (3.0, 1.6))),
         [s["kink"] for s in shapes]),
        ("best shape", dict(ls="none", marker="o", ms=3.4, mfc="white",
                            mec=style.INK, mew=0.8),
         [s["best"][0] for s in shapes]),
    )
    for label, fmt, x in designs:
        ax_f.plot(ve, x, **fmt)
    ax_f.set(xlim=(0.2, 0.92), ylim=(1.0, 3.2), xlabel="$v_e$")
    style.legend_top(ax_f, [key(fmt, label) for label, fmt, _ in designs],
                     ncol=3, borderpad=0.4, **TIGHT)

    fig.legend(*zip(*[key(dot, "best clean point in the box"),
                      (Patch(**nosol), r"no solution ($\min Q \leq 0$, stall)")]),
               loc="outside upper center", ncol=2, frameon=False,
               fontsize=7.0, handlelength=1.2, columnspacing=1.8)
    style.tag_keys(fig, list(top) + [ax_d, ax_e, ax_f],
                   ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"], row="last")
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing red, "
                         "green, blue")
    args = ap.parse_args(argv)
    colours = RGB
    if args.colors:
        colours = tuple(c.strip() for c in args.colors.split(","))
        if len(colours) != 3:
            ap.error("--colors takes exactly three colours")

    shapes = [shape(m) for m, _ in MEMBERS]
    gammas = [gamma(m) for m, _ in MEMBERS]
    lads = ladders()
    rayss = [rays(m) for m, _ in MEMBERS]
    fig = draw(shapes, gammas, lads, rayss, colours)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    for (member, ve), s in zip(MEMBERS, shapes):
        print(f"{member} (v_e {ve:g}): kink X {s['kink']:.6f}, best clean "
              f"{s['best'][0]:.6f} at q = {s['best'][1]}")
    print(f"label audit: {'clean' if not problems else problems}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
