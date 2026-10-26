#!/usr/bin/env python3
r"""Convergence of the Bondi dipole's resolution sets: the constraints region by region, and the motion.

The members differ only in the grid: N = 128 / 192 / 256 cells on the L = 64 box
(dx = 1/2, 1/3, 1/4), one level, dt = 0.02 dx, on the fixed binary (c12664fd) and the
fixed initial data; everything else is the paper's run.  ``--study pair`` (default):
PM10, the mixed pair at d0 = 10.  ``--study lone``: M, the negative-mass star alone,
5 units off the box centre (N 128 and 192; N 256 joins when it exists).

Top two rows: the L2 norm of the Hamiltonian (first row) and momentum (second row)
constraint in four regions about the box centre, from ``constraint_shells.dat`` (unit
shells, the box's 4-cell outer layer left out), combined by shell volume: (a) r < 24,
inside the absorbing layer, the region the orders are quoted for; (b) r < 12, where
the stars are; (c) 12 <= r < 24; (d) 24 <= r < 30, the absorbing layer, whose added
dissipation is not part of the Einstein equations, so no order is expected there.  As
in the spinning paper's convergence figure, the finest member is redrawn at the
coarsest's resolution for orders 2 and 4, N_max x (N_max / N_min)^p: at order p the
coarsest member lies on the p-th curve.

Bottom row, pair: (i) the displacement Delta X of the midpoint of the two barycentres
(the paper's Eq. mid); (j) each member's distance from the finest, |Delta X_N -
Delta X_256|, with N 192's redrawn for orders 2 and 4 (x (2^p - 1) / (1.5^p - 1), so
at order p N 128 lies on the p-th curve); (k) the separation d of the barycentres;
(l) the acceleration a, twice the quadratic coefficient of X fitted over
5 <= t' <= t (the paper's Eq. fit), against the window's end t.
Bottom row, lone: (i) the core's largest shift on any axis since t = 0 (the paper's
isolated-star test); (j) the barycentre's, redrawn for orders 2 and 4 as the
constraints; (k) the change of the minimum lapse; (l) the peak field's.

    python -m grteclyn_wrapper.visualisation.bondi_dipole.plot_convergence
    ... plot_convergence --study lone
    ... plot_convergence --palette house

Colours (``--palette``): ``paper``, the default, is the Bondi article's look
(2026-10-26): the members in black, dotted / dashed / solid from the coarsest to the
finest as in its Fig. 9(a), the order-2 curve in its orange and the order-4 curve in
its blue, fonts from pdflatex through the pgf backend (``article_figures.RC``).
``rgb`` is red / green / blue from the coarsest member to the finest, the rescaled
curves in the finest's colour, as in the spinning paper; ``house`` is an ordered
light-to-dark ramp with ink rescaled curves.  ``--colors C1,C2,C3`` replaces the
members' colours.

Reads each member from the pack, ``results/bondi-dipole-runaway/campaign/<group>/<run>/``,
once it is packed, and until then from its run directory under ``runs/bondi/``; writes
``results/bondi-dipole-runaway/figures/09_convergence/convergence_pair`` / ``convergence_lone``
(PNG + PDF; the article's appendix figures) and prints every number the panels show.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

# .../GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/bondi_dipole/plot_convergence.py
REPO = pathlib.Path(__file__).resolve().parents[5]
PACK = REPO / "results" / "bondi-dipole-runaway" / "campaign"
RUNS = REPO / "runs" / "bondi"
FIGURES = REPO / "results" / "bondi-dipole-runaway" / "figures"
NN = (128, 192, 256)
STUDIES = {
    "pair": dict(runs=tuple((n, f"PM10_L64_N{n}") for n in NN),
                 experiment="bondi_sg_pair_pm_eqm_w075", stem="09_convergence/convergence_pair"),
    "lone": dict(runs=tuple((n, f"M_L64_N{n}") for n in NN),
                 experiment="bondi_sg_single_m_w07603", stem="09_convergence/convergence_lone"),
}
# Runs still live in staging/ under their launch names; each takes its readable name at close-out (2026-10-23).
LAUNCH_NAMES: dict[str, str] = {}
SHELLS = 33                  # constraint_shells.dat: shell s holds s <= r < s + 1, the last one the corners
SHELL_VOLUME = np.array([(s + 1) ** 3 - s ** 3 for s in range(SHELLS)], float)
# (title, r_min, r_max): shells r_min .. r_max - 1, all whole inside the box's outer layer at every N
# (short enough for a 7-inch row in the article's fonts, 2026-10-26)
ZONES = (("$r<24$", 0, 24), ("$r<12$, the stars", 0, 12),
         (r"$12\leq r<24$", 12, 24), (r"$24\leq r<30$, the layer", 24, 30))
ORDERS = (2, 4)              # the rescaled curves' two orders
T_FROM = 1.0                 # orders are quoted from t = 1, past the first steps
FIT_START = 5.0              # the paper's fit window opens here
FIT_SPAN = 20.0              # (l) starts once the window spans this much (shorter fits follow the start-up)
SOLID, DASHED, DOTTED = "-", (0, (4.0, 1.8)), (0, (1.2, 1.4))
CONSTRAINTS = (r"$\|\mathcal{H}\|_2$", r"$\|\mathcal{M}\|_2$")
TITLE = dict(loc="left", fontsize=7.0, pad=3.0)

# rescaled None: the finest member's own colour.  "paper" takes the article's
# ladder, order colours and fonts from article_figures when it is drawn.
PALETTES = {
    "paper": dict(colours=("k", "k", "k"), rescaled=None, paper=True),
    "rgb": dict(colours=("#d62728", "#2ca02c", "#1f77b4"), rescaled=None),
    "house": dict(colours=tuple(style.ordinal(3)), rescaled=style.INK),
}


def member_dir(run: str, experiment: str) -> tuple[pathlib.Path | None, bool]:
    """The member's files and whether they are packed: the packed cell (flat files)
    if there is one, else the run's own output directory (``data/``, ``small_data/``); a live
    run under its launch name."""
    for name in (run, LAUNCH_NAMES.get(run)):
        if name is None:
            continue
        for d in sorted(PACK.glob(f"*/{name}")):
            return d, True
        for d in (RUNS / "staging" / name / experiment, *sorted(RUNS.glob(f"*/{name}/{experiment}"))):
            if d.is_dir():
                return d, False
    return None, False


def table(d: pathlib.Path, name: str) -> np.ndarray | None:
    """A whitespace table, comment lines dropped; a live run's half-written last row
    (a width the other rows do not share) is dropped too."""
    for path in (d / name, d / "data" / name, d / "small_data" / name):
        if path.is_file():
            rows = [line.split() for line in path.read_text().splitlines()
                    if line.strip() and not line.lstrip().startswith("#")]
            widths = [len(r) for r in rows]
            width = max(set(widths), key=widths.count)
            return np.array([r for r in rows if len(r) == width], dtype=float)
    return None


def load(spec: dict) -> tuple[dict[int, dict[str, np.ndarray]], dict[int, bool]]:
    """Each member's streams: the shell norms (every 0.1), the barycentres and the
    core tracker (every plotfile, 0.8), the collapse diagnostics (every step).
    Members without data yet are left out."""
    data, packed = {}, {}
    for n, run in spec["runs"]:
        d, is_packed = member_dir(run, spec["experiment"])
        if d is None:
            continue
        streams = dict(shells=table(d, "constraint_shells.dat"), bary=table(d, "sector_barycenters.dat"),
                       dyn=table(d, "sector_dynamics.dat"), collapse=table(d, "collapse_diagnostics.dat"))
        if any(v is None or len(v) < 2 for v in streams.values()):
            continue
        if not np.isfinite(streams["shells"]).all():
            raise SystemExit(f"{run}: non-finite rows in constraint_shells.dat")
        data[n], packed[n] = streams, is_packed
    if len(data) < 2:
        raise SystemExit(f"fewer than two members with data: {sorted(data)}")
    return data, packed


def zone(shells: np.ndarray, r_min: int, r_max: int, constraint: int) -> np.ndarray:
    """The region's L2 norm from its shells' (each an L2 over its own volume)."""
    cols = 1 + constraint * SHELLS + np.arange(r_min, r_max)
    w = SHELL_VOLUME[r_min:r_max]
    return np.sqrt((shells[:, cols] ** 2 * w).sum(axis=1) / w.sum())


def occupied(bary: np.ndarray, dyn: np.ndarray) -> tuple[slice, slice, int]:
    """A lone star's barycentre and core columns and its peak column: the sector it
    occupies (the other's columns are zero or nan)."""
    size = np.nan_to_num(np.abs(bary[0, [1, 6]]))
    peak = np.nan_to_num(np.abs(dyn[0, [4, 8]]))
    return (slice(2, 5) if size[0] > size[1] else slice(7, 10),
            slice(1, 4) if peak[0] > peak[1] else slice(5, 8),
            4 if peak[0] > peak[1] else 8)


def midpoint(bary: np.ndarray) -> np.ndarray:
    return 0.5 * (bary[:, 2] + bary[:, 7])


def running_fit(bary: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """a over FIT_START <= t' <= t, against t, once the window spans FIT_SPAN."""
    t, x = bary[:, 0], midpoint(bary)
    ends, a = [], []
    for i in range(len(t)):
        w = (t >= FIT_START - 1e-9) & (t <= t[i] + 1e-9)
        if t[i] - FIT_START >= FIT_SPAN - 1e-9:
            ends.append(t[i])
            a.append(2.0 * np.polyfit(t[w], x[w], 2)[0])
    return np.array(ends), np.array(a)


def bottom_curves(data, ns, study: str) -> dict[str, dict[int, tuple[np.ndarray, np.ndarray]]]:
    """(t, y) of each member for the bottom row's four panels, as drawn."""
    out = {k: {} for k in "ijkl"}
    if study == "pair":
        hi = ns[-1]
        t_hi, x_hi = data[hi]["bary"][:, 0], midpoint(data[hi]["bary"])
        for n in ns:
            b = data[n]["bary"]
            t, x = b[:, 0], midpoint(b)
            out["i"][n] = (t, x - x[0])
            if n != hi:
                keep = t <= t_hi[-1] + 1e-9
                out["j"][n] = (t[keep], np.abs((x[keep] - x[0]) - np.interp(t[keep], t_hi, x_hi - x_hi[0])))
            out["k"][n] = (t, b[:, 2] - b[:, 7])
            out["l"][n] = running_fit(b)
    else:
        for n in ns:
            b, s, c = data[n]["bary"], data[n]["dyn"], data[n]["collapse"]
            bc, cc, pc = occupied(b, s)
            out["i"][n] = (s[:, 0], np.maximum.accumulate(np.abs(s[:, cc] - s[0, cc]).max(axis=1)))
            out["j"][n] = (b[:, 0], np.abs(b[:, bc] - b[0, bc]).max(axis=1))
            out["k"][n] = (c[:, 0], c[:, 1] - c[0, 1])
            out["l"][n] = (s[:, 0], s[:, pc] / s[0, pc] - 1.0)
    return out


def orders(curves: dict[int, tuple[np.ndarray, np.ndarray]], ns) -> dict[str, np.ndarray]:
    """Each neighbouring pair's convergence order and the coarsest-to-finest one,
    on a common t grid from T_FROM to the shortest member's end."""
    t_end = min(t[-1] for t, _ in curves.values())
    tg = np.arange(T_FROM, t_end + 1e-9, 0.5)
    e = {n: np.interp(tg, *curves[n]) for n in ns}
    out = {f"{a}->{b}": np.log(e[a] / e[b]) / np.log(b / a) for a, b in zip(ns, ns[1:])}
    if len(ns) > 2:
        out[f"{ns[0]}->{ns[-1]}"] = np.log(e[ns[0]] / e[ns[-1]]) / np.log(ns[-1] / ns[0])
    return out


def floor_from(ax, t0: float) -> None:
    """A log axis's bottom at the lowest value drawn from t0 on: the first steps
    (a region that starts clean, a difference that starts at zero) would
    otherwise stretch it by decades."""
    lows = [np.min(y[(x >= t0) & (y > 0)]) for x, y in
            (line.get_data() for line in ax.get_lines()) if np.any((x >= t0) & (y > 0))]
    if lows:
        ax.set_ylim(bottom=0.5 * min(lows))


def deviation_scale(ns, p: int) -> float:
    """|q_lo - q_hi| / |q_mid - q_hi| at order p, h ~ 1/N."""
    lo, mid, hi = ns
    return (lo ** -p - hi ** -p) / (mid ** -p - hi ** -p)


def draw(data, ns, study: str, look: dict):
    colours = dict(zip(NN, look["colours"]))
    if look.get("paper"):
        # the article's own look: its rcParams, its ladder of line styles, and
        # its two accents for the two orders
        from . import article_figures as paper
        plt.rcParams.update(paper.RC)
        members = {n: dict(color=colours[n], ls=paper.LADDER[n], lw=1.1 if n == NN[-1] else 0.85)
                   for n in ns}
        brackets = [dict(color=paper.ORDER_COLOUR[p], ls=paper.ORDER_LS[p], lw=0.9) for p in ORDERS]
    else:
        style.prd(8.0)
        rescaled = look["rescaled"] or colours[ns[-1]]
        members = {n: dict(color=colours[n], ls=SOLID, lw=1.1) for n in ns}
        brackets = [dict(color=rescaled, ls=ls, lw=0.9) for ls in (DASHED, DOTTED)]
    fig, axes = plt.subplots(3, len(ZONES), figsize=(7.0, 4.4), sharex=True, layout="constrained")
    lo, hi = ns[0], ns[-1]
    t_end = min(d["shells"][-1, 0] for d in data.values())
    tags = iter("abcdefghijkl")

    def draw_members(ax, curves, scale=None):
        """The members, and the reference member's curve redrawn x scale(p) for each order."""
        for n in ns:
            if n in curves:
                ax.plot(*curves[n], **members[n])
        if scale is not None:
            ref, factor = scale
            t, y = curves[ref]
            for p, b in zip(ORDERS, brackets):
                ax.plot(t, y * factor(p), **b)

    # rows 1-2: the constraints, region by region
    for c in range(2):
        for z, (name, r_min, r_max) in enumerate(ZONES):
            ax = axes[c, z]
            curves = {n: (data[n]["shells"][:, 0], zone(data[n]["shells"], r_min, r_max, c)) for n in ns}
            draw_members(ax, curves, scale=(hi, lambda p: (hi / lo) ** p))
            ax.set_yscale("log")
            if z == 0:
                ax.set_ylabel(CONSTRAINTS[c])
            title = f"({next(tags)})"
            if c == 0:
                title += f"  {name}"
            ax.set_title(title, **TITLE)

    # row 3: the motion
    bottom = bottom_curves(data, ns, study)
    ax_i, ax_j, ax_k, ax_l = axes[2]
    if study == "pair":
        draw_members(ax_i, bottom["i"])
        three = len(ns) == 3
        draw_members(ax_j, bottom["j"],
                     scale=(ns[1], lambda p: deviation_scale(ns, p)) if three else None)
        draw_members(ax_k, bottom["k"])
        draw_members(ax_l, {n: (t, 1e4 * a) for n, (t, a) in bottom["l"].items()})
        ax_i.set_ylabel(r"$\Delta X$")
        ax_j.set(yscale="log", ylabel=rf"$|\Delta X_N-\Delta X_{{{hi}}}|$")
        ax_k.set_ylabel(r"$d$")
        ax_l.set_ylabel(r"$10^4\,a$")
        titles = ("midpoint displacement", rf"distance from $N={hi}$",
                  "separation", rf"$a$, fit over ${FIT_START:g}\leq t'\leq t$")
    else:
        draw_members(ax_i, bottom["i"])
        draw_members(ax_j, bottom["j"], scale=(hi, lambda p: (hi / lo) ** p))
        draw_members(ax_k, {n: (t, 1e4 * y) for n, (t, y) in bottom["k"].items()})
        draw_members(ax_l, {n: (t, 1e2 * y) for n, (t, y) in bottom["l"].items()})
        ax_i.set(yscale="log", ylabel=r"core shift")
        ax_j.set(yscale="log", ylabel=r"barycentre shift")
        ax_k.set_ylabel(r"$10^4\,(\alpha_{\min}-\alpha_{\min}(0))$")
        ax_l.set_ylabel(r"$10^2\,(|\phi|_{\max}/|\phi|_{\max}(0)-1)$")
        titles = ("core shift, largest so far", "barycentre shift",
                  "minimum lapse", "peak field")
    for ax, title in zip(axes[2], titles):
        ax.set_title(f"({next(tags)})  {title}", **TITLE)
        ax.set_xlabel(r"$t$")
    # the runs stop at t 199.6 (their last 0.1 sample): the axis closes at 200
    t_lim = max(t_end, 10.0 * np.ceil(t_end / 10.0 - 0.1))
    for ax in axes.flat:
        ax.set_xlim(0.0, t_lim)
        ax.set_xticks(np.arange(0.0, t_lim + 1e-9, 50.0))
        if ax.get_yscale() == "log":
            floor_from(ax, T_FROM)

    # one key above the whole figure; the lines are the same in every panel
    fig.legend([Line2D([], [], **members[n]) for n in ns] + [Line2D([], [], **b) for b in brackets],
               [rf"$N={n}$" for n in ns] + [f"order {p}, rescaled" for p in ORDERS],
               loc="outside upper center", ncol=len(ns) + len(ORDERS), frameon=False,
               fontsize=7.5, handlelength=2.4, columnspacing=1.8)
    return fig


def at(t: np.ndarray, y: np.ndarray, when: float) -> float:
    """y at ``when``, nan past either end (a live run's plotfile streams can lag its norms)."""
    if when < t[0] - 1e-6 or when > t[-1] + 1e-6:
        return np.nan
    return float(np.interp(when, t, y))


def fmt(v: float, spec: str) -> str:
    return "–" if not np.isfinite(v) else format(v, spec)


def report(data, ns, study: str) -> None:
    """Every number the figure shows, per panel."""
    lo, hi = ns[0], ns[-1]
    r = hi / lo
    print(f"orders over t = {T_FROM:g}-end (min .. max, median), and the share of the time N {lo} "
          f"lies between the order {ORDERS[0]} and {ORDERS[-1]} curves:")
    for name, r_min, r_max in ZONES:
        for c, label in enumerate(("Ham", "Mom")):
            curves = {n: (data[n]["shells"][:, 0], zone(data[n]["shells"], r_min, r_max, c)) for n in ns}
            pairs = "  ".join(f"{k} {v.min():+.1f}..{v.max():+.1f} ({np.median(v):+.1f})"
                              for k, v in orders(curves, ns).items())
            tg = np.arange(T_FROM, min(t[-1] for t, _ in curves.values()), 0.5)
            y_lo, y_hi = (np.interp(tg, *curves[n]) for n in (lo, hi))
            inside = np.mean((y_lo >= y_hi * r ** ORDERS[0]) & (y_lo <= y_hi * r ** ORDERS[-1]))
            print(f"  {r_min}-{r_max} {label}: {pairs}; between the curves {100 * inside:.0f} %")
    t_end = min(d["shells"][-1, 0] for d in data.values())
    marks = [x for x in (25.0, 50.0, 100.0, 150.0, 200.0) if x <= t_end + 1e-6]
    bottom = bottom_curves(data, ns, study)
    if study == "pair":
        print("(i) Delta X at t " + " / ".join(f"{x:g}" for x in marks) + ": " + ", ".join(
            f"N {n} " + " / ".join(fmt(at(*bottom['i'][n], x), '.4f') for x in marks) for n in ns))
        if len(ns) == 3:
            for x in marks:
                d1, d2 = (at(*bottom["j"][n], x) for n in ns[:2])
                q = d1 / d2 if d2 > 0 else np.nan
                print(f"(j) t {x:g}: |dX_{ns[0]} - dX_{hi}| {fmt(d1, '.2e')}, |dX_{ns[1]} - dX_{hi}| "
                      f"{fmt(d2, '.2e')}, ratio {fmt(q, '.2f')} (order 2: {deviation_scale(ns, 2):.2f}, "
                      f"order 4: {deviation_scale(ns, 4):.2f})")
        print("(k) d at t " + " / ".join(f"{x:g}" for x in marks) + ": " + ", ".join(
            f"N {n} " + " / ".join(fmt(at(*bottom['k'][n], x), '.4f') for x in marks) for n in ns))
        print("(l) a over 5 <= t' <= t at t " + " / ".join(f"{x:g}" for x in marks) + ": " + ", ".join(
            f"N {n} " + " / ".join(fmt(at(*bottom['l'][n], x), '.4e') for x in marks if x >= 10) for n in ns))
    else:
        print("(i) core, largest shift since t 0, at t " + " / ".join(f"{x:g}" for x in marks) + ": "
              + ", ".join(f"N {n} " + " / ".join(fmt(at(*bottom['i'][n], x), '.2e') for x in marks) for n in ns))
        print("(j) barycentre shift at t " + " / ".join(f"{x:g}" for x in marks) + ": " + ", ".join(
            f"N {n} " + " / ".join(fmt(at(*bottom['j'][n], x), '.2e') for x in marks) for n in ns))
        print("(k) minimum lapse change at the end: " + ", ".join(
            f"N {n} {bottom['k'][n][1][-1]:+.2e} (t {bottom['k'][n][0][-1]:.0f})" for n in ns))
        print("(l) peak field change at the end: " + ", ".join(
            f"N {n} {bottom['l'][n][1][-1]:+.2e} (t {bottom['l'][n][0][-1]:.0f})" for n in ns))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--study", choices=sorted(STUDIES), default="pair")
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="output stem (default results/bondi-dipole-runaway/figures/<the study's stem>, "
                         "09_convergence/convergence_<study>)")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="paper",
                    help="colour scheme (default paper, the Bondi article's; rgb is the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing the members' colours")
    args = ap.parse_args(argv)
    # the article's look renders its text with pdflatex (pgf); the others need no TeX
    look = dict(PALETTES[args.palette])
    plt.switch_backend("pgf" if look.get("paper") else "Agg")
    if args.colors:
        look["colours"] = tuple(c.strip() for c in args.colors.split(","))
        if len(look["colours"]) != 3:
            ap.error("--colors takes exactly three colours")

    spec = STUDIES[args.study]
    data, packed = load(spec)
    ns = tuple(sorted(data))
    fig = draw(data, ns, args.study, look)
    problems = style.label_audit(fig, pad=0.02)   # a margin, as article_figures.save
    png = style.save(fig, args.out or FIGURES / spec["stem"])

    print(f"{args.study}: N {' / '.join(map(str, ns))}, t <= {min(d['shells'][-1, 0] for d in data.values()):.2f}; "
          + ", ".join(f"N {n} {'packed' if packed[n] else 'from runs/ (not packed yet)'}" for n in ns))
    report(data, ns, args.study)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    print(f"wrote {png.relative_to(REPO) if png.is_relative_to(REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
