#!/usr/bin/env python3
r"""Convergence of a spinning hold's resolution triplet: the constraints on every level, the throat, the wave zone.

The triplet's members differ only in the base grid: N = 128 / 192 / 256 on the
0.9c's L = 128 box, so level l has dx = (1, 2/3, 1/2) / 2^l; everything else,
the refined boxes' tags included, is the same.

Top two rows: each level's L2 norm of the Hamiltonian (first row) and momentum
(second row) constraint, from the run's ``constraint_norms_levels.dat``: that
level's cells no finer level covers, outside r < 0.75 about the centre (the
compactified far end's floored core) and the box's outer 3 cells (the
Sommerfeld layer).  Level 0 is the base grid out to the box face, level 3 the
throat; levels 1-3 are the tags +/-16, 8, 4 about the centre, rounded to each
grid, so a level's region shrinks slightly with N.

Bottom row, the throat and the wave zone:
(i) the throat's equatorial circumferential radius (``throat_geometry.dat``)
    against the background's exact value, R_e of the packed solver table;
(j) the throat's areal radius (the smallest coordinate sphere's, the
    consumer's ``throat_spheres.dat``) against its own t = 0 value: that value
    is set by the radial spacing the consumer searches on (0.25 to 0.125), not
    by the evolution, so only its drift is drawn;
(k) the (l, m) = (2, 0) mode of Psi4 at R = 18 against its t = 0 value, the
    stationary background's own curvature, signed on a symlog axis (linear
    inside +-1e-6); the m = +-2 modes stay at round-off, ~1e-15, at every N;
(l) the lapse at the far-side puncture (``collapse_diagnostics.dat``), a
    gauge quantity.

As in the ExoZvezda code paper's convergence figure, the finest member is
redrawn at the coarsest's resolution for orders 2 and 4, N 256 x (256/128)^n,
on the constraints and on (i): at order n the coarsest member lies on the n-th
curve, so N 128 between the dashed and the dotted curve brackets the order.
One key above the panels names the lines.  Outcome (the 0.9c, t = 1-150, 128 ->
256): every level converges, level 0 at order 2.3-3.6, levels 1 and 2 at
1.7-2.6, level 3 at 2.6-4.1 (momentum) and 1.6-4.0 (Hamiltonian); the throat's
equatorial radius converges to the exact value at about 2nd order, its areal
radius holds to 6e-5, and Psi4 (2,0) at R = 18 stays within 1.7e-4 / 3.3e-5 /
1.5e-5 (N 128 / 192 / 256) of its t = 0 value to t = 100.  From t ~ 100 every member drifts
alike (Psi4 (2,0) by 2 % at t = 150, level 0's constraints after t ~ 140)
while the far-side lapse falls to 1e-3, the same at every N.  Each panel's
numbers are printed.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_convergence
    ... plot_convergence --palette house
    ... plot_convergence --colors "#c00000,#007a00,#0000c0"

Colours (``--palette``): ``rgb``, the spinning paper's scheme and the default,
red / green / blue from the coarsest member to the finest, the rescaled curves
in the finest's colour; ``house`` is an ordered light-to-dark ramp with ink
rescaled curves.  ``--colors C1,C2,C3`` replaces the members' colours.

Reads the packed triplet under ``results/spinningwormhole/campaign/`` and the
solver table ``results/spinningwormhole/solver/solutions.tsv``; writes
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
from matplotlib.ticker import FuncFormatter, LogLocator  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign"
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"
# spin -> box L, packed group, ((N, run), ...) coarsest first, the background's
# v_e (its row in the solver table holds the exact throat radius), output stem
TRIPLETS = {
    "0.9c": (128.0, "drainhole/00_paper_runs",
             ((128, "spin_hold_L128_N128_ml3_ve090a_spdrv1_sig04_farfix_t150"),
              (192, "spin_hold_L128_N192_ml3_ve090a_spdrv1_sig04_farfix_t150"),
              (256, "spin_hold_L128_ml3_ve090a_spdrv1_sig04_farfix_t150")),
             0.8997849046244889, "convergence_09c"),
}
LEVELS = 4
ORDERS = (2, 4)             # the rescaled finest member's two brackets
T_FROM = 1.0                # orders are quoted from t = 1, past the start-up transient
T_QUIET = 100.0             # Psi4 is quoted to here, before the late drift every member shares
DT_PAGE = 0.1               # one drawn sample per 0.1 (the per-step files hold every coarse step)
PSI4_R = 18
PSI4_LINTHRESH = 1e-6       # (k) is linear inside +-1e-6, below every member's quiet level
SOLID, DASHED, DOTTED = "-", (0, (4.0, 1.8)), (0, (1.2, 1.4))
CONSTRAINTS = (r"$\|\mathcal{H}\|_2$", r"$\|\mathcal{M}\|_2$")
TITLE = dict(loc="left", fontsize=7.0, pad=3.0)

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


def load(group: str, runs) -> dict[int, dict[str, np.ndarray]]:
    """Each member's packed streams: the per-level norms, the throat diagnostics
    and the collapse diagnostics (every coarse step), the throat spheres and
    Psi4 (every plotfile)."""
    out = {}
    for n, run in runs:
        d = PACKED / group / run
        norms = np.loadtxt(d / "constraint_norms_levels.dat")
        if not np.isfinite(norms).all():
            raise SystemExit(f"{run}: non-finite rows in constraint_norms_levels.dat")
        with open(d / "psi4_mode_l2_all.dat") as f:
            head = f.readline().split()[1:]          # time, Re_m-2(R=..), Im_m-2(R=..), ...
        psi4 = np.loadtxt(d / "psi4_mode_l2_all.dat")
        re_, im_ = head.index(f"Re_m0(R={PSI4_R})"), head.index(f"Im_m0(R={PSI4_R})")
        out[n] = dict(
            norms=norms,
            geometry=np.loadtxt(d / "throat_geometry.dat"),      # time, R_eq_min, R_pol_min, ergo_min
            spheres=np.loadtxt(d / "throat_spheres.dat"),        # time, r_throat, R_throat, ...
            psi4=np.column_stack((psi4[:, 0], np.hypot(psi4[:, re_], psi4[:, im_]))),
            collapse=np.loadtxt(d / "collapse_diagnostics.dat"),  # time, min_lapse, ...
        )
    return out


def exact_radius(v_e: float) -> float:
    """The background's equatorial throat radius R_e, from the packed solver table."""
    hit = [r for r in solutions.load(solutions.TABLE) if abs(r["v_e"] - v_e) < 1e-9]
    if len(hit) != 1:
        raise SystemExit(f"v_e {v_e}: {len(hit)} rows in {solutions.TABLE}")
    return hit[0]["R_e"]


def page(a: np.ndarray) -> np.ndarray:
    """The rows at the first time on or after each multiple of DT_PAGE."""
    t = a[:, 0]
    grid = np.arange(0.0, t[-1] + 0.5 * DT_PAGE, DT_PAGE)
    return a[np.unique(np.clip(np.searchsorted(t, grid - 1e-9), 0, len(t) - 1))]


def orders(curves: dict[int, tuple[np.ndarray, np.ndarray]], ns) -> dict[str, np.ndarray]:
    """Each neighbouring pair's convergence order and the coarsest-to-finest one,
    on a common t grid from T_FROM to the shortest member's end."""
    t_end = min(t[-1] for t, _ in curves.values())
    tg = np.arange(T_FROM, t_end + 1e-9, 0.5)
    e = {n: np.interp(tg, *curves[n]) for n in ns}
    out = {f"{a}->{b}": np.log(e[a] / e[b]) / np.log(b / a) for a, b in zip(ns, ns[1:])}
    out[f"{ns[0]}->{ns[-1]}"] = np.log(e[ns[0]] / e[ns[-1]]) / np.log(ns[-1] / ns[0])
    return out


def sci(y: float, _pos=None) -> str:
    """A tick label m x 10^e (matplotlib's log formatter labels only the decades
    once the axis spans more than one)."""
    e = int(np.floor(np.log10(y) + 1e-9))
    m = round(y / 10.0**e)
    return rf"$10^{{{e}}}$" if m == 1 else rf"${m}\times10^{{{e}}}$"


def dx_text(box: float, n: int, level: int) -> str:
    f = Fraction(box / n / 2**level).limit_denominator(1024)
    return f"{f.numerator}" if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def curves_of(data, ns, panel: str, r_exact: float) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """(t, y) of each member for one bottom-row panel, as drawn."""
    out = {}
    for n in ns:
        d = data[n]
        if panel == "eq":
            g = page(d["geometry"])
            out[n] = (g[:, 0], np.abs(g[:, 1] / r_exact - 1.0))
        elif panel == "areal":
            s = d["spheres"]
            out[n] = (s[:, 0], s[:, 2] / s[0, 2] - 1.0)
        elif panel == "psi4":
            p = d["psi4"]
            out[n] = (p[1:, 0], p[1:, 1] / p[0, 1] - 1.0)
        else:
            c = page(d["collapse"])
            out[n] = (c[:, 0], c[:, 1])
    return out


def draw(data, box: float, ns, r_exact: float, look: dict):
    style.prd(8.0)
    fig, axes = plt.subplots(3, LEVELS, figsize=(7.0, 5.6), sharex=True, layout="constrained")
    lo, hi = ns[0], ns[-1]
    rescaled = look["rescaled"] or look["colours"][-1]
    t_end = min(d["norms"][-1, 0] for d in data.values())
    members = [dict(color=c, ls=SOLID, lw=1.1) for c in look["colours"]]
    brackets = [dict(color=rescaled, ls=ls, lw=0.9) for ls in (DASHED, DOTTED)]
    tags = iter("abcdefghijkl")

    def draw_members(ax, curves, bracketed):
        for n, m in zip(ns, members):
            ax.plot(*curves[n], **m)
        if bracketed:
            t, y = curves[hi]
            for p, b in zip(ORDERS, brackets):
                ax.plot(t, y * (hi / lo) ** p, **b)

    # rows 1-2: the constraints, level by level
    for c in range(2):
        for level in range(LEVELS):
            ax = axes[c, level]
            col = column(level, c)
            draw_members(ax, {n: (page(data[n]["norms"])[:, 0], page(data[n]["norms"])[:, col])
                              for n in ns}, bracketed=True)
            ax.set_yscale("log")
            if level == 0:
                ax.set_ylabel(CONSTRAINTS[c])
            # the panel's tag; over the top row, the column's level and its spacings
            title = f"({next(tags)})"
            if c == 0:
                title += rf"  level {level}: $\Delta x$ = " + ", ".join(
                    dx_text(box, n, level) for n in ns)
            ax.set_title(title, **TITLE)

    # row 3: the throat and the wave zone
    ax_i, ax_j, ax_k, ax_l = axes[2]
    draw_members(ax_i, curves_of(data, ns, "eq", r_exact), bracketed=True)
    areal = curves_of(data, ns, "areal", r_exact)
    draw_members(ax_j, {n: (t, 1e5 * y) for n, (t, y) in areal.items()}, bracketed=False)
    draw_members(ax_k, curves_of(data, ns, "psi4", r_exact), bracketed=False)
    draw_members(ax_l, curves_of(data, ns, "lapse", r_exact), bracketed=False)
    ax_i.set(yscale="log", ylabel=r"$|R_{\rm eq}/R_{\rm eq}^{\rm exact}-1|$")
    ax_i.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0, 2.0, 5.0)))
    ax_i.yaxis.set_major_formatter(FuncFormatter(sci))
    ax_j.set_ylabel(r"$10^5\,(R/R(0)-1)$")
    ax_k.set_yscale("symlog", linthresh=PSI4_LINTHRESH, linscale=0.5)
    ax_k.set_ylabel(r"$\psi_4^{20}/\psi_4^{20}(0)-1$")
    ax_l.set(yscale="log", ylabel=r"$\alpha_{\min}$")
    for ax, title in zip(axes[2], ("throat equatorial radius", "throat areal radius",
                                   rf"$\psi_4^{{20}}$ at $R={PSI4_R}$", "far-side puncture lapse")):
        ax.set_title(f"({next(tags)})  {title}", **TITLE)
        ax.set_xlabel(r"$t$")
    for ax in axes.flat:
        ax.set_xlim(0.0, t_end)

    # 2026-10-18: one key above the whole figure; the lines are the same in every panel
    fig.legend([Line2D([], [], **m) for m in members] + [Line2D([], [], **b) for b in brackets],
               [rf"$N={n}$" for n in ns]
               + [rf"$N={hi}\times{hi / lo:g}^{p}$ (order {p})" for p in ORDERS],
               loc="outside upper center", ncol=len(ns) + len(ORDERS), frameon=False,
               fontsize=7.5, handlelength=2.4, columnspacing=1.8)
    return fig


def report(data, ns, r_exact: float) -> None:
    """Every number the figure shows, per panel."""
    lo, hi = ns[0], ns[-1]
    r = hi / lo
    print("orders over t = %g-end (min .. max, median)" % T_FROM)
    for level in range(LEVELS):
        for c, name in enumerate(("Ham", "Mom")):
            col = column(level, c)
            curves = {n: (data[n]["norms"][:, 0], data[n]["norms"][:, col]) for n in ns}
            pairs = "  ".join(f"{k} {v.min():+.1f}..{v.max():+.1f} ({np.median(v):+.1f})"
                              for k, v in orders(curves, ns).items())
            tg = np.arange(T_FROM, min(t[-1] for t, _ in curves.values()), 0.5)
            y_lo, y_hi = (np.interp(tg, *curves[n]) for n in (lo, hi))
            inside = np.mean((y_lo >= y_hi * r ** ORDERS[0]) & (y_lo <= y_hi * r ** ORDERS[-1]))
            print(f"  level {level} {name}: {pairs}; N {lo} between the order {ORDERS[0]} and "
                  f"{ORDERS[-1]} curves {100 * inside:.0f} % of the time")
    eq = curves_of(data, ns, "eq", r_exact)
    print(f"(i) R_eq against the exact {r_exact:.5f}: " + ", ".join(
        f"N {n} {y[0]:.2e} at t 0, {y[-1]:.2e} at t {t[-1]:.0f}" for n, (t, y) in eq.items()))
    print("    orders at t 0: " + ", ".join(
        f"{a}->{b} {np.log(eq[a][1][0] / eq[b][1][0]) / np.log(b / a):+.1f}" for a, b in zip(ns, ns[1:])))
    areal = curves_of(data, ns, "areal", r_exact)
    print("(j) areal radius, max |R/R(0) - 1|: " + ", ".join(
        f"N {n} {np.abs(y).max():.1e}" for n, (_, y) in areal.items()))
    psi4 = curves_of(data, ns, "psi4", r_exact)
    print(f"(k) Psi4 (2,0) at R {PSI4_R}, max change to t {T_QUIET:g} / at the end: " + ", ".join(
        f"N {n} {np.abs(y[t <= T_QUIET]).max():.1e} / {y[-1]:+.1e}" for n, (t, y) in psi4.items()))
    lapse = curves_of(data, ns, "lapse", r_exact)
    print("(l) far-side lapse at t 50 / 100 / end: " + ", ".join(
        f"N {n} " + " / ".join(f"{np.interp(x, t, y):.4f}" for x in (50.0, 100.0, t[-1]))
        for n, (t, y) in lapse.items()))


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

    box, group, runs, v_e, stem = TRIPLETS[args.spin]
    ns = tuple(n for n, _ in runs)
    data = load(group, runs)
    r_exact = exact_radius(v_e)
    fig = draw(data, box, ns, r_exact, look)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out or FIGURES / stem)

    print(f"{args.spin} triplet N {' / '.join(map(str, ns))}, t <= "
          f"{min(d['norms'][-1, 0] for d in data.values()):.2f}")
    report(data, ns, r_exact)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    print(f"wrote {png.relative_to(solutions.REPO) if png.is_relative_to(solutions.REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
