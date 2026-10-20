#!/usr/bin/env python3
r"""How a rotating Ellis--Bronnikov wormhole changes with spin, at fixed eta0.

Both solved families against the throat's equatorial velocity v_e, every
quantity in units of the family's own throat parameter eta0 (the solver holds
eta0 fixed along a family, so mass and size grow without bound as v_e -> 1):

- solid: the drainhole family (eta0 = 2, gamma = -pi: the 3D runs' static
  drainhole a = 2, M = 1 spun up); dashed: the symmetric family (eta0 = 1,
  gamma = 0, equal masses on both sides, CKK's);
- (a) mass M/eta0, angular momentum J/eta0^2 and equatorial throat radius
  R_e/eta0 (log); thin grey rules mark the drainhole holds evolved in 3D;
- (b) J/M^2 against the Kerr bound 1 (log);
- (c) the far side's mass over ours, M_-/M_+ (the drainhole's far side turns
  from negative to positive mass);
- (d) the throat's flattening R_p/R_e;
- (e) the phantom field's scalar charge D/eta0;
- (f) the throat's rotation rate Omega eta0.

Black dots: the extremal-Kerr values at v_e = 1 (J/M^2 = 1, R_p/R_e from
the closed form, D = 0, Omega eta0 = 0 at fixed eta0).  The static members
(v_e = 0) are exact and drawn where the axis is linear: M_-/M_+ = -1 and
+1, R_p/R_e = 1, D^2 = eta0^2 + M^2, Omega = 0.

Colours follow the spinning paper's red / green / blue by quantity (mass and
shape red, angular momentum green, size and rotation blue; the scalar charge
ink); ``--colors C1,C2,C3`` redraws in another scheme.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends

Reads ``results/spinningwormhole/solver/solutions.tsv``; writes
``results/spinningwormhole/figures/solver/spin_trends`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import kk2014, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

OUT = solutions.REPO / "results" / "spinningwormhole" / "figures" / "solver" / "spin_trends"
RGB = ("#d62728", "#2ca02c", "#1f77b4")
SOLID, DASHED = "-", (0, (3.0, 1.6))       # short dashes: the keys' short handles show them
# (eta0, gamma, name in the keys, the line style)
FAMILIES = (
    (2.0, -math.pi, "drainhole", SOLID),
    (1.0, 0.0, "symmetric", DASHED),
)
HOLDS = (0.5127, 0.6988)       # the drainhole holds live in 3D (2026-10-13)
# three keys to a row fit a third of the page with shorter handles
TIGHT = dict(handlelength=1.5, handletextpad=0.35, columnspacing=0.5)


def family(rows: list[dict], eta0: float, gamma: float) -> dict[str, np.ndarray]:
    """The family's members that pass the tail gate, one per J, by v_e."""
    seen, keep = set(), []
    for r in rows:
        if (r["eta0"] != eta0 or abs(r["gamma"] - gamma) > 1e-12
                or r["tail_max"] > kk2014.TAIL_GATE):
            continue
        if round(r["J"], 9) not in seen:
            seen.add(round(r["J"], 9))
            keep.append(r)
    keep.sort(key=lambda r: r["v_e"])
    c = {k: np.array([r[k] for r in keep]) for k in
         ("v_e", "J", "mu_plus", "mu_minus", "D", "R_e", "R_pol", "Omega_throat")}
    m0 = -gamma * eta0 / (2.0 * math.pi)            # the static member's mass
    return {
        "v": c["v_e"], "M": c["mu_plus"] / eta0, "J": c["J"] / eta0**2,
        "Re": c["R_e"] / eta0, "JM2": c["J"] / c["mu_plus"] ** 2,
        "Mratio": c["mu_minus"] / c["mu_plus"], "Rp": c["R_pol"] / c["R_e"],
        "D": c["D"] / eta0, "Om": c["Omega_throat"] * eta0,
        # exact static ends (v_e = 0) for the linear panels
        "static": {"Mratio": -1.0 if m0 > 0 else 1.0, "Rp": 1.0,
                   "D": math.sqrt(eta0**2 + m0**2) / eta0, "Om": 0.0},
    }


def draw(fams, colours):
    style.prd(8.0)
    # 2026-10-20: a lower grid (7 x 5 in took half a page); the top row keeps its v_e
    # tick labels, which hold the rows far enough apart for the bottom row's tags
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.5), layout="constrained")
    (ax_a, ax_b, ax_c), (ax_d, ax_e, ax_f) = axes
    red, green, blue = colours
    dot = dict(ls="none", marker="o", ms=4.5, mfc="black", mec="black", zorder=6,
               clip_on=False)
    rule = dict(color=style.FAINT, lw=0.6, zorder=0)
    blank = (Line2D([], [], alpha=0.0), "")      # keeps a lone entry in the right column

    def line(color, ls, **kw):
        return dict(color=color, ls=ls, lw=1.3, **kw)

    def key(fmt, label):
        return (Line2D([], [], **{k: v for k, v in fmt.items() if k != "clip_on"}), label)

    def curve(ax, f, q, color, ls, static=True, **kw):
        v, y = f["v"], f[q]
        if static and q in f["static"]:
            v, y = np.concatenate(([0.0], v)), np.concatenate(([f["static"][q]], y))
        ax.plot(v, y, **line(color, ls, **kw))

    # J's markers keep it apart from M where red and green cross
    jmark = dict(marker="s", ms=2.6, mfc="none", mew=0.6, markevery=0.08)

    # (a) mass, angular momentum, size
    for ax_v in HOLDS:
        ax_a.axvline(ax_v, **rule)
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_a, f, "M", red, ls)
        curve(ax_a, f, "J", green, ls, **jmark)
        curve(ax_a, f, "Re", blue, ls)
    # colour names the quantity, the dash the family
    ax_a.set(yscale="log", xlim=(0, 1), ylim=(1e-3, 1e4))
    style.legend_top(ax_a, [key(line(red, SOLID), r"$M/\eta_0$"),
                            key(line(green, SOLID, **jmark), r"$J/\eta_0^2$"),
                            key(line(blue, SOLID), r"$R_e/\eta_0$")]
                     + [key(line(style.INK, ls), name) for *_, name, ls in FAMILIES]
                     + [key(rule, "3D holds")], ncol=3, **TIGHT)

    # (b) J/M^2 against the Kerr bound
    ax_b.axhline(1.0, **rule)
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_b, f, "JM2", green, ls)
    ax_b.plot([1.0], [1.0], **dot)
    ax_b.set(yscale="log", xlim=(0, 1), ylim=(0.1, 100), ylabel=r"$J/M^2$")
    ax_b.set_yticks([0.1, 1.0, 10.0])      # no label on the top edge, where the tag sits
    style.legend_top(ax_b, [key(line(green, ls), name) for *_, name, ls in FAMILIES]
                     + [key(rule, "Kerr bound"), key(dot, "extremal Kerr")], ncol=2)

    # (c) far-side mass over ours
    ax_c.axhline(0.0, **rule)
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_c, f, "Mratio", red, ls)
    ax_c.set(xlim=(0, 1), ylim=(-1.1, 1.1), ylabel=r"$M_-/M_+$")
    style.legend_top(ax_c, [key(line(red, ls), name) for *_, name, ls in FAMILIES], ncol=2)

    # (d) flattening
    ext = kk2014.kerr(np.array([1.0]))
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_d, f, "Rp", red, ls)
    ax_d.plot([1.0], ext["Rp"], **dot)
    ax_d.set(xlim=(0, 1), ylim=(0.58, 1.02), ylabel=r"$R_p/R_e$", xlabel=r"$v_e$")
    style.legend_top(ax_d, [key(line(red, ls), name) for *_, name, ls in FAMILIES]
                     + [blank, key(dot, "extremal Kerr")], ncol=2, **TIGHT)

    # (e) scalar charge
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_e, f, "D", style.INK, ls)
    ax_e.plot([1.0], [0.0], **dot)
    ax_e.set(xlim=(0, 1), ylim=(0.0, 1.25), ylabel=r"$D/\eta_0$", xlabel=r"$v_e$")
    ax_e.set_yticks([0.0, 0.5, 1.0])       # as (b): the top edge is the tag's
    style.legend_top(ax_e, [key(line(style.INK, ls), name) for *_, name, ls in FAMILIES]
                     + [blank, key(dot, "extremal Kerr")], ncol=2, **TIGHT)

    # (f) rotation rate
    for f, (_, _, name, ls) in zip(fams, FAMILIES):
        curve(ax_f, f, "Om", blue, ls)
    ax_f.plot([1.0], [0.0], **dot)
    ax_f.set(xlim=(0, 1), ylim=(0.0, 0.55), ylabel=r"$\Omega\,\eta_0$", xlabel=r"$v_e$")
    style.legend_top(ax_f, [key(line(blue, ls), name) for *_, name, ls in FAMILIES]
                     + [blank, key(dot, "extremal Kerr")], ncol=2, **TIGHT)

    style.tag_keys(fig, [ax_a, ax_b, ax_c, ax_d, ax_e, ax_f],
                   ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"], row="last")
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing red, green, blue")
    args = ap.parse_args(argv)
    colours = RGB
    if args.colors:
        colours = tuple(c.strip() for c in args.colors.split(","))
        if len(colours) != 3:
            ap.error("--colors takes exactly three colours")

    rows = solutions.load(args.table)
    fams = [family(rows, eta0, gamma) for eta0, gamma, *_ in FAMILIES]
    fig = draw(fams, colours)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    for f, (_, _, name, _) in zip(fams, FAMILIES):
        print(f"{name}: {len(f['v'])} solutions, v_e {f['v'][0]:.3f}-{f['v'][-1]:.4f}")
    print(f"label audit: {'clean' if not problems else problems}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
