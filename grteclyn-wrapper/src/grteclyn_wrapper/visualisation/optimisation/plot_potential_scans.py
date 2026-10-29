#!/usr/bin/env python3
r"""Campaign M step 3: the exotic bill across the potential's knobs.

Three spins (fam_b_0003 / 0012 / 0025, v_e 0.27 / 0.50 / 0.85), every
solve at pinned J and R_e, grid 150x30, from the packed TSVs:

- (a)-(c) the shape landscape per spin: every solved point of the box
  scan and the open ray walks in the (q1, q2) plane of
  Q = 1 + q1 u + q2 u^2 (u = psi/psi_minus) at kink mass 0.3, coloured
  by the bill's shift against the pure kink, X/X_kink - 1 in percent.
  The bill falls toward +q1, +q2 at every spin and keeps falling along
  every ray; a grey cross is a point with no solution (Newton), the
  black circle the best clean point of the m = 0.3 scan (all monitors
  inside the 1e-8 gate), the gold square the screened CMA-ES champion
  (mass and q3 free; its (q1, q2) is overlaid on this slice).
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
  pure kink m 0.3, the best clean shape over the box plus the open
  ray walks (q-rays stages; every ray ended on Newton or the monitor
  limit with X still falling, so those are frontier values at this
  grid, not the landscape's bottom), and the screened CMA-ES PASS
  points (STATUS: 1.63372 / 1.49461 / 1.09759; the 0.50 loop-best
  PASS 1.477 is an open twin and is not plotted).

Colours are red / green / blue by spin (the keys above (a)-(c) name
them); ``--colors C1,C2,C3`` redraws in another scheme.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_potential_scans

Reads ``results/optimisation/scans/*.tsv``,
``results/optimisation/ladders_150x30.tsv``, and the packed CMA-ES
opt4s TSVs under ``results/optimisation/opt/``; writes
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

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[5]
SCANS = REPO / "results" / "optimisation" / "scans"
OPT = REPO / "results" / "optimisation" / "opt"
RUNS_OPT = REPO / "runs" / "optimisation" / "opt"
LADDERS = REPO / "results" / "optimisation" / "ladders_150x30.tsv"
OUT = REPO / "results" / "optimisation" / "figures" / "potential_scans"
RGB = ("#d62728", "#2ca02c", "#1f77b4")
# (member, nominal v_e) in spin order; the scan grid and its anchor mass
MEMBERS = (("fam_b_0003", 0.27), ("fam_b_0012", 0.50), ("fam_b_0025", 0.85))
MASS = 0.3
GRID = "150x30"
TIGHT = dict(handlelength=1.5, handletextpad=0.35, columnspacing=0.5)
# Screened CMA-ES PASS X from research/optimisation/STATUS.md (150x30).
# fam_b_0012's loop-best PASS (1.477) is an open twin; the quoted row
# is the milder PASS that grid-checks.
QUOTED_CMA_X = {
    "fam_b_0003": 1.63372,
    "fam_b_0012": 1.49461,
    "fam_b_0025": 1.09759,
}


def read(path: pathlib.Path) -> list[dict]:
    with open(path) as fh:
        return [{k: (v if k in ("member", "mode", "verdict") else float(v))
                 for k, v in row.items()}
                for row in csv.DictReader(
                    (ln for ln in fh if not ln.startswith("#")),
                    delimiter="\t")]


def shape(member: str) -> dict:
    """The member's (q1, q2) landscape over everything explored, box scan
    plus ray walks: per point X / X_kink - 1 in percent, the points with
    no solution, and the best clean point."""
    rows = read(SCANS / f"{member}_shape_{GRID}.tsv")
    rays = SCANS / f"{member}_rays_{GRID}.tsv"
    kink = next(r["X"] for r in rows if r["q1"] == 0.0 and r["q2"] == 0.0)
    pts: dict[tuple, float] = {}
    failed, best = [], (math.inf, None)
    for r in rows + (read(rays) if rays.exists() else []):
        q = (r["q1"], r["q2"])
        if math.isnan(r["X"]):
            failed.append(q)
            continue
        pts.setdefault(q, 100.0 * (r["X"] / kink - 1.0))
        if r["verdict"] == "PASS" and r["X"] < best[0]:
            best = (r["X"], q)
    return {"pts": pts, "failed": failed, "kink": kink, "best": best}


def gamma(member: str) -> dict:
    """The gamma walk: X(gamma) / X(0) at the pure kink."""
    rows = read(SCANS / f"{member}_gamma_{GRID}.tsv")
    rows.sort(key=lambda r: -r["gamma"])
    x0 = next(r["X"] for r in rows if r["gamma"] == 0.0)
    return {"g": np.array([-r["gamma"] / math.pi for r in rows]),
            "rel": np.array([r["X"] / x0 for r in rows])}


def rays(member: str) -> list[dict]:
    """The member's ray walks as (far-well mass, X) curves, in the walk
    order: pure q1, pure q2, the diagonal."""
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


def cma(member: str) -> dict:
    """The member's screened CMA-ES PASS champion (STATUS X, with q)."""
    name = f"{member}_opt4s_{GRID}.tsv"
    path = next((root / name for root in (OPT, RUNS_OPT)
                 if (root / name).is_file()), None)
    if path is None:
        raise FileNotFoundError(
            f"no search TSV {name} under {OPT} or {RUNS_OPT}")
    rows = []
    with open(path) as fh:
        for raw in csv.DictReader(
                (ln for ln in fh if not ln.startswith("#")), delimiter="\t"):
            try:
                x = float(raw["X"])
            except (TypeError, ValueError):
                continue
            if raw.get("verdict") != "PASS" or math.isnan(x):
                continue
            rows.append({"X": x, "q1": float(raw["q1"]),
                         "q2": float(raw["q2"]), "q3": float(raw["q3"]),
                         "mass": float(raw["mass"])})
    if not rows:
        raise ValueError(f"{path} has no PASS evaluations")
    pick = min(rows, key=lambda r: abs(r["X"] - QUOTED_CMA_X[member]))
    return {"X": pick["X"], "q": (pick["q1"], pick["q2"]),
            "mass": pick["mass"], "q3": pick["q3"]}


def ladders() -> dict[str, dict]:
    rows = read(LADDERS)
    out: dict[str, dict] = {}
    for member, _ in MEMBERS:
        keep = sorted((r for r in rows if r["member"] == member),
                      key=lambda r: r["mass"])
        out[member] = {"m": np.array([r["mass"] for r in keep]),
                       "X": np.array([r["X"] for r in keep])}
    return out


def draw(shapes, gammas, lads, rayss, cmas, colours):
    style.prd(8.0)
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.6), layout="constrained")
    top, (ax_d, ax_e, ax_f) = axes
    dot = dict(ls="none", marker="o", ms=4.5, mfc="black", mec="black",
               zorder=6, clip_on=False)
    champ = dict(ls="none", marker="s", ms=4.5, mfc=style.GOLD, mec="black",
                 mew=0.5, zorder=7, clip_on=False)
    rule = dict(color=style.FAINT, lw=0.6, zorder=0)

    def line(color, ls="-", lw=1.3, **kw):
        return dict(color=color, ls=ls, lw=lw, **kw)

    def key(fmt, label):
        return (Line2D([], [], **{k: v for k, v in fmt.items()
                                  if k != "clip_on"}), label)

    # (a)-(c) everything explored in the (q1, q2) plane, one spin per
    # panel, shared colour scale; red deepens where the shape pays, blue
    # where it costs
    vmax = max(max(abs(v) for v in s["pts"].values()) for s in shapes)
    cmap = plt.get_cmap("RdBu")
    cross = dict(ls="none", marker="x", ms=3.2, mec="#9a9a96", mew=0.9)
    mesh = None
    for ax, (member, ve), s, cm, c in zip(top, MEMBERS, shapes, cmas, colours):
        qs = np.array(list(s["pts"]))
        mesh = ax.scatter(qs[:, 0], qs[:, 1], c=list(s["pts"].values()),
                          s=13, marker="s", cmap=cmap, vmin=-vmax,
                          vmax=vmax, lw=0)
        if s["failed"]:
            f = np.array(s["failed"])
            ax.plot(f[:, 0], f[:, 1], **cross)
        ax.plot([s["best"][1][0]], [s["best"][1][1]], **dot)
        ax.plot([cm["q"][0]], [cm["q"][1]], **champ)
        ax.set(xlim=(-1.1, 7.9), ylim=(-1.1, 7.9), xticks=(0, 2, 4, 6),
               yticks=(0, 2, 4, 6), xlabel="$q_1$", aspect="equal")
        style.legend_top(ax, [key(line(c), f"$v_e = {ve:.2f}$")], **TIGHT)
    top[0].set_ylabel("$q_2$")
    cb = fig.colorbar(mesh, ax=list(top), pad=0.015, fraction=0.05)
    cb.set_label(r"$X/X_{\rm kink} - 1$ [%]")

    # (d) every walk on the far-well mass axis: the kink ladders (dots,
    # m_- = m) continued by the open ray walks (thin lines, m = 0.3)
    for (member, ve), rr, c in zip(MEMBERS, rayss, colours):
        ax_d.plot(lads[member]["m"], lads[member]["X"],
                  marker="o", ms=2.8, **line(c))
        for r in rr:
            ax_d.plot(r["mm"], r["X"], **line(c, lw=0.8))
    ax_d.set(xlim=(-0.02, 1.25), ylim=(1.0, 3.1),
             xlabel=r"far-well mass $m_- = m\sqrt{1 + q_1 + q_2}$",
             ylabel=r"$X = |{\rm VIQ}|/R_e$")
    style.legend_top(ax_d, [key(dict(line(style.INK), marker="o", ms=2.8),
                                "kink ladder"),
                            key(line(style.INK, lw=0.8), "ray walks")],
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
        ("CMA-ES", dict(color=style.GOLD, ls="-", lw=1.3, marker="s",
                        ms=3.4, mfc=style.GOLD, mec="black", mew=0.5),
         [cm["X"] for cm in cmas]),
    )
    for label, fmt, x in designs:
        ax_f.plot(ve, x, **fmt)
    ax_f.set(xlim=(0.2, 0.92), ylim=(0.9, 3.2), xlabel="$v_e$")
    style.legend_top(ax_f, [key(fmt, label) for label, fmt, _ in designs],
                     ncol=2, borderpad=0.4, **TIGHT)

    fig.legend(*zip(*[key(dot, "best clean point"),
                      key(champ, "CMA-ES"),
                      key(cross, "no solution (Newton stop)")]),
               loc="outside upper center", ncol=3, frameon=False,
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
    cmas = [cma(m) for m, _ in MEMBERS]
    fig = draw(shapes, gammas, lads, rayss, cmas, colours)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    for (member, ve), s, cm in zip(MEMBERS, shapes, cmas):
        print(f"{member} (v_e {ve:g}): kink X {s['kink']:.6f}, best clean "
              f"{s['best'][0]:.6f} at q = {s['best'][1]}; CMA-ES "
              f"{cm['X']:.6f} at m = {cm['mass']:.3f}, q = {cm['q']}, "
              f"q3 = {cm['q3']:.3f}")
    print(f"label audit: {'clean' if not problems else problems}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
