#!/usr/bin/env python3
r"""Constraint convergence on every refinement level: a spinning hold's resolution triplet.

The triplet's members differ only in the base grid: N = 128 / 192 / 256 on the
0.9c's L = 128 box, so level l has dx = (1, 2/3, 1/2) / 2^l; everything else,
the refined boxes' tags included, is the same.  Each panel is one level's L2
norm of the Hamiltonian (top row) or momentum (bottom row) constraint, from the
run's ``constraint_norms_levels.dat``: that level's cells no finer level covers,
outside r < 0.75 about the centre (the compactified far end's floored core) and
the box's outer 3 cells (the Sommerfeld layer).  Level 0 is the base grid out
to the box face, level 3 the throat; levels 1-3 are the tags +/-16, 8, 4 about
the centre, rounded to each grid, so a level's region shrinks slightly with N.

As in the ExoZvezda code paper's convergence figure, the finest member is
redrawn at the coarsest's resolution for orders 2 and 4, N 256 x (256/128)^n:
at order n the coarsest member lies on the n-th curve, so N 128 between the
dashed and the dotted curve brackets the order; one key above the panels names
the lines, the same in all eight.  Outcome (the 0.9c, t = 1-150, 128 -> 256):
every level converges, level 0 at order 2.3-3.6, levels 1 and 2 at 1.7-2.6,
level 3 at 2.6-4.1 (momentum) and 1.6-4.0 (Hamiltonian); level 0's rise after
t ~ 140 is in every member.  Each panel's pair orders are printed.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_convergence
    ... plot_convergence --palette house
    ... plot_convergence --colors "#c00000,#007a00,#0000c0"

Colours (``--palette``): ``rgb``, the spinning paper's scheme and the default,
red / green / blue from the coarsest member to the finest, the rescaled curves
in the finest's colour; ``house`` is an ordered light-to-dark ramp with ink
rescaled curves.  ``--colors C1,C2,C3`` replaces the members' colours.

Reads the packed triplet under ``results/spinningwormhole/campaign/``; writes
``results/spinningwormhole/figures/convergence_09c`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import pathlib
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign"
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"
# spin -> box L, packed group, ((N, run), ...) coarsest first, output stem
TRIPLETS = {
    "0.9c": (128.0, "drainhole/00_paper_runs",
             ((128, "spin_hold_L128_N128_ml3_ve090a_spdrv1_sig04_farfix_t150"),
              (192, "spin_hold_L128_N192_ml3_ve090a_spdrv1_sig04_farfix_t150"),
              (256, "spin_hold_L128_ml3_ve090a_spdrv1_sig04_farfix_t150")),
             "convergence_09c"),
}
LEVELS = 4
ORDERS = (2, 4)             # the rescaled finest member's two brackets
T_FROM = 1.0                # orders are quoted from t = 1, past the start-up transient
DT_PAGE = 0.1               # one drawn sample per 0.1 (the files hold every coarse step)
SOLID, DASHED, DOTTED = "-", (0, (4.0, 1.8)), (0, (1.2, 1.4))
CONSTRAINTS = (r"$\|\mathcal{H}\|_2$", r"$\|\mathcal{M}\|_2$")

# 2026-10-13: the spinning paper colours red / green / blue; gold is the merger
# paper's accent.  rescaled None: the finest member's own colour.
PALETTES = {
    "rgb": dict(colours=("#d62728", "#2ca02c", "#1f77b4"), rescaled=None),
    "house": dict(colours=tuple(style.ordinal(3)), rescaled=style.INK),
}


def column(level: int, constraint: int) -> int:
    """The column of ``constraint`` (0 Ham, 1 Mom) on ``level``: time first, then
    the (Ham, Mom) pair of each level, then the all-level pair."""
    return 1 + 2 * level + constraint


def load(group: str, runs) -> dict[int, np.ndarray]:
    out = {}
    for n, run in runs:
        a = np.loadtxt(PACKED / group / run / "constraint_norms_levels.dat")
        if not np.isfinite(a).all():
            raise SystemExit(f"{run}: non-finite rows in constraint_norms_levels.dat")
        out[n] = a
    return out


def page(a: np.ndarray) -> np.ndarray:
    """The rows at the first time on or after each multiple of DT_PAGE."""
    t = a[:, 0]
    grid = np.arange(0.0, t[-1] + 0.5 * DT_PAGE, DT_PAGE)
    return a[np.unique(np.clip(np.searchsorted(t, grid - 1e-9), 0, len(t) - 1))]


def orders(data: dict[int, np.ndarray], ns, col: int) -> dict[str, np.ndarray]:
    """Each neighbouring pair's convergence order and the coarsest-to-finest one,
    on a common t grid from T_FROM to the shortest member's end."""
    t_end = min(a[-1, 0] for a in data.values())
    tg = np.arange(T_FROM, t_end + 1e-9, 0.5)
    e = {n: np.interp(tg, data[n][:, 0], data[n][:, col]) for n in ns}
    out = {f"{a}->{b}": np.log(e[a] / e[b]) / np.log(b / a) for a, b in zip(ns, ns[1:])}
    out[f"{ns[0]}->{ns[-1]}"] = np.log(e[ns[0]] / e[ns[-1]]) / np.log(ns[-1] / ns[0])
    return out


def dx_text(box: float, n: int, level: int) -> str:
    f = Fraction(box / n / 2**level).limit_denominator(1024)
    return f"{f.numerator}" if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def draw(data: dict[int, np.ndarray], box: float, ns, look: dict):
    style.prd(8.0)
    fig, axes = plt.subplots(2, LEVELS, figsize=(7.0, 4.0), sharex=True, layout="constrained")
    lo, hi = ns[0], ns[-1]
    rescaled = look["rescaled"] or look["colours"][-1]
    t_end = min(a[-1, 0] for a in data.values())
    drawn = {n: page(data[n]) for n in ns}
    members = [dict(color=c, ls=SOLID, lw=1.1) for c in look["colours"]]
    brackets = [dict(color=rescaled, ls=ls, lw=0.9) for ls in (DASHED, DOTTED)]
    for c, row in enumerate(axes):
        for level, ax in enumerate(row):
            col = column(level, c)
            for n, m in zip(ns, members):
                ax.plot(drawn[n][:, 0], drawn[n][:, col], **m)
            for p, b in zip(ORDERS, brackets):
                ax.plot(drawn[hi][:, 0], drawn[hi][:, col] * (hi / lo) ** p, **b)
            ax.set(yscale="log", xlim=(0.0, t_end))
            if level == 0:
                ax.set_ylabel(CONSTRAINTS[c])
            if c == 1:
                ax.set_xlabel(r"$t$")
            # the panel's tag; over the top row, the column's level and its spacings
            tag = f"({'abcdefgh'[c * LEVELS + level]})"
            if c == 0:
                tag += rf"  level {level}: $\Delta x$ = " + ", ".join(
                    dx_text(box, n, level) for n in ns)
            ax.set_title(tag, loc="left", fontsize=7.5, pad=3.0)
    # 2026-10-18: one key above the whole figure; the lines are the same in all eight panels
    fig.legend([Line2D([], [], **m) for m in members] + [Line2D([], [], **b) for b in brackets],
               [rf"$N={n}$" for n in ns]
               + [rf"$N={hi}\times{hi / lo:g}^{p}$ (order {p})" for p in ORDERS],
               loc="outside upper center", ncol=len(ns) + len(ORDERS), frameon=False,
               fontsize=7.5, handlelength=2.4, columnspacing=1.8)
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--spin", choices=sorted(TRIPLETS), default="0.9c")
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="output stem (default results/spinningwormhole/figures/<the spin's stem>)")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="rgb",
                    help="colour scheme (default rgb, the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing the members' colours")
    args = ap.parse_args(argv)
    look = dict(PALETTES[args.palette])
    if args.colors:
        look["colours"] = tuple(c.strip() for c in args.colors.split(","))
        if len(look["colours"]) != 3:
            ap.error("--colors takes exactly three colours")

    box, group, runs, stem = TRIPLETS[args.spin]
    ns = tuple(n for n, _ in runs)
    data = load(group, runs)
    fig = draw(data, box, ns, look)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out or FIGURES / stem)

    print(f"{args.spin} triplet N {' / '.join(map(str, ns))}, t <= "
          f"{min(a[-1, 0] for a in data.values()):.2f}; orders over t = {T_FROM:g}-end "
          "(min .. max, median)")
    for level in range(LEVELS):
        for c, name in enumerate(("Ham", "Mom")):
            col = column(level, c)
            o = orders(data, ns, col)
            pairs = "  ".join(f"{k} {v.min():+.1f}..{v.max():+.1f} ({np.median(v):+.1f})"
                              for k, v in o.items())
            # where the coarsest member sits against the rescaled finest
            lo_t = np.interp(np.arange(T_FROM, data[ns[-1]][-1, 0], 0.5), data[ns[0]][:, 0],
                             data[ns[0]][:, col])
            hi_t = np.interp(np.arange(T_FROM, data[ns[-1]][-1, 0], 0.5), data[ns[-1]][:, 0],
                             data[ns[-1]][:, col])
            r = ns[-1] / ns[0]
            inside = np.mean((lo_t >= hi_t * r ** ORDERS[0]) & (lo_t <= hi_t * r ** ORDERS[-1]))
            print(f"  level {level} {name}: {pairs}; N {ns[0]} between the order "
                  f"{ORDERS[0]} and {ORDERS[-1]} curves {100 * inside:.0f} % of the time")
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    print(f"wrote {png.relative_to(solutions.REPO) if png.is_relative_to(solutions.REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
