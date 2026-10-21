#!/usr/bin/env python3
r"""How a rotating Ellis--Bronnikov wormhole changes with spin, at fixed eta0.

Both solved families against the throat's equatorial velocity v_e, every
quantity in units of the family's own throat parameter eta0 (the solver holds
eta0 fixed along a family, so mass and size grow without bound as v_e -> 1):

- solid: the drainhole family (eta0 = 2, gamma = -pi: the 3D runs' static
  drainhole a = 2, M = 1 spun up); dashed: the symmetric family (eta0 = 1,
  gamma = 0, equal masses on both sides, CKK's);
- (a) mass M/eta0, angular momentum J/eta0^2 and equatorial throat radius
  R_e/eta0 (log);
- (b) J/M^2 against the Kerr bound 1 (log);
- (c) the far side's mass over ours, M_-/M_+ (the drainhole's far side turns
  from negative to positive mass); the dotted rule marks the drainhole's sign
  change (v_e ~ 0.72), the squares the 3D runs' backgrounds at their own
  M_-/M_+ (the packed table headers), and the grey band the rungs whose runs
  broke down at the compactified far end before t = 150 (0.46c-0.7c);
- (d) the throat's flattening R_p/R_e;
- (e) the exotic matter: the phantom field's volume integral quantifier
  |int (rho + p_eta) dV| (Visser, Kar & Dadhich 2003) over the equatorial
  throat radius, relative to the family's static member (1 at v_e = 0; log),
  from the packed solutions; squares: the 3D runs, each
  rung's value scaled by (D_run / D_background)^2 with D_run the charge
  measured on the run's own t = 0 slice (results/spinningwormhole/
  scalar_charge_runs.tsv);
- (f) the throat's rotation rate Omega eta0.

Black dots: the extremal-Kerr values at v_e = 1 (J/M^2 = 1, R_p/R_e from
the closed form, Omega eta0 = 0 at fixed eta0).  The static members
(v_e = 0) are exact: M_-/M_+ = -1 and +1, R_p/R_e = 1, Omega = 0, and the
exotic matter in closed form (observables.static_exotic_matter).

One key above the figure names the families' dashes and the extremal
dots; a panel's own key names only what is its alone (the quantities of
(a), the Kerr bound of (b)).

Colours follow the spinning paper's red / green / blue by quantity (mass and
shape red, angular momentum green, size and rotation blue; the exotic matter
ink); ``--colors C1,C2,C3`` redraws in another scheme.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends

Reads ``results/spinningwormhole/solver/solutions.tsv``, the packed solutions
under ``results/spinningwormhole/solutions/`` and ``scalar_charge_runs.tsv``; writes
``results/spinningwormhole/figures/solver/spin_trends`` (PNG + PDF).
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
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from scipy.interpolate import PchipInterpolator  # noqa: E402

from grteclyn_wrapper.analysis.spinning_wormhole.observables import (  # noqa: E402
    exotic_matter, static_exotic_matter)
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution  # noqa: E402
from grteclyn_wrapper.visualisation.spinning_wormhole import headers, kk2014, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

OUT = solutions.REPO / "results" / "spinningwormhole" / "figures" / "solver" / "spin_trends"
PACKED = solutions.REPO / "results" / "spinningwormhole" / "solutions"
CHARGES = solutions.REPO / "results" / "spinningwormhole" / "scalar_charge_runs.tsv"
RGB = ("#d62728", "#2ca02c", "#1f77b4")
SOLID, DASHED = "-", (0, (3.0, 1.6))       # short dashes: the keys' short handles show them
# (eta0, gamma, name in the keys, the line style)
FAMILIES = (
    (2.0, -math.pi, "drainhole", SOLID),
    (1.0, 0.0, "symmetric", DASHED),
)
# three keys to a row fit a third of the page with shorter handles
TIGHT = dict(handlelength=1.5, handletextpad=0.35, columnspacing=0.5)
# 2026-10-20: the first and last rung whose 3D runs broke down at the far-side centre
# (the compactified far end) before t = 150: 0.46c at 130.2, 0.5c at 100.1, 0.6c at
# 66.7, 0.7c at 52.9; the slower rungs form a horizon first and the 0.9c holds
FAR_END_BAND = ("fam_a_ve045", "fam_a_ve070")


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
    exotic = []                    # |VIQ| / R_e where the solution itself is packed
    for r in keep:
        path = PACKED / r["leg"] / f"{r['leg']}_{r['step']:04d}.npz"
        exotic.append(abs(exotic_matter(Solution.load(path), r["D"])) / r["R_e"]
                      if path.exists() else math.nan)
    viq0, re0 = static_exotic_matter(eta0, gamma)
    x0 = abs(viq0) / re0
    return {
        "v": c["v_e"], "M": c["mu_plus"] / eta0, "J": c["J"] / eta0**2,
        "Re": c["R_e"] / eta0, "JM2": c["J"] / c["mu_plus"] ** 2,
        "Mratio": c["mu_minus"] / c["mu_plus"], "Rp": c["R_pol"] / c["R_e"],
        "X": np.array(exotic), "Xrel": np.array(exotic) / x0, "Om": c["Omega_throat"] * eta0,
        "D0": math.sqrt(eta0**2 + m0**2),          # the static member's charge
        # exact static ends (v_e = 0)
        "static": {"Mratio": -1.0 if m0 > 0 else 1.0, "Rp": 1.0,
                   "X": x0, "Xrel": 1.0, "Om": 0.0},
    }


def sign_change(fam: dict) -> float:
    """The v_e where the family's M_-/M_+ crosses zero (linear between the two
    members that bracket it)."""
    v, m = fam["v"], fam["Mratio"]
    i = int(np.flatnonzero((m[:-1] < 0.0) & (m[1:] >= 0.0))[0])
    return float(v[i] - m[i] * (v[i + 1] - v[i]) / (m[i + 1] - m[i]))


def run_ratios() -> tuple[np.ndarray, np.ndarray]:
    """The 3D runs on (c): each evolved background's own v_e and M_-/M_+ from its
    packed header; the static drainhole's ends are exactly -1."""
    vs, ms = [0.0], [-1.0]
    for bg in headers.ARTICLE:
        meta = headers.meta(bg)
        vs.append(float(meta["v_e"]))
        ms.append(float(meta["mu_minus"]) / float(meta["mu_plus"]))
    return np.array(vs), np.array(ms)


def run_points(fam: dict) -> tuple[np.ndarray, np.ndarray]:
    """The 3D runs on (e): per background, the family's curve at its v_e times
    (D_run / D_background)^2, D_run the median t = 0 charge its runs measured
    (VIQ goes as D^2 on a fixed geometry)."""
    charges: dict[str, list[float]] = {}
    with open(CHARGES) as fh:
        for row in csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"):
            if row["which"] == "t0":
                charges.setdefault(row["background"], []).append(float(row["D"]))
    v = np.concatenate(([0.0], fam["v"]))
    x = np.concatenate(([fam["static"]["X"]], fam["X"]))
    ok = np.isfinite(x)
    log_x = PchipInterpolator(v[ok], np.log(x[ok]))
    vs, xs = [], []
    for bg, ds in sorted(charges.items()):
        if bg == "static":
            v_bg, d_bg = 0.0, fam["D0"]
        else:
            meta = headers.meta(bg)
            v_bg, d_bg = float(meta["v_e"]), float(meta["D"])
        vs.append(v_bg)
        xs.append(float(np.exp(log_x(v_bg))) * (float(np.median(ds)) / d_bg) ** 2)
    return np.array(vs), np.array(xs)


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

    def line(color, ls, **kw):
        return dict(color=color, ls=ls, lw=1.3, **kw)

    def key(fmt, label):
        return (Line2D([], [], **{k: v for k, v in fmt.items() if k != "clip_on"}), label)

    def curve(ax, f, q, color, ls, static=True, **kw):
        v, y = f["v"], f[q]
        if static and q in f["static"]:
            v, y = np.concatenate(([0.0], v)), np.concatenate(([f["static"][q]], y))
        ok = np.isfinite(y)                     # (e) has only the packed solutions
        ax.plot(v[ok], y[ok], **line(color, ls, **kw))

    # J's markers keep it apart from M where red and green cross
    jmark = dict(marker="s", ms=2.6, mfc="none", mew=0.6, markevery=0.08)

    # (a) mass, angular momentum, size
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_a, f, "M", red, ls)
        curve(ax_a, f, "J", green, ls, **jmark)
        curve(ax_a, f, "Re", blue, ls)
    # colour names the quantity; the figure's key names the dashes
    ax_a.set(yscale="log", xlim=(0, 1), ylim=(1e-3, 1e4))
    style.legend_top(ax_a, [key(line(red, SOLID), r"$M/\eta_0$"),
                            key(line(green, SOLID, **jmark), r"$J/\eta_0^2$"),
                            key(line(blue, SOLID), r"$R_e/\eta_0$")], ncol=3, **TIGHT)

    # (b) J/M^2 against the Kerr bound
    ax_b.axhline(1.0, **rule)
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_b, f, "JM2", green, ls)
    ax_b.plot([1.0], [1.0], **dot)
    ax_b.set(yscale="log", xlim=(0, 1), ylim=(0.1, 100), ylabel=r"$J/M^2$")
    ax_b.set_yticks([0.1, 1.0, 10.0])      # no label on the top edge, where the tag sits
    style.legend_top(ax_b, [key(rule, "Kerr bound")])

    # the 3D runs' marker, on (c) and (e)
    runmark = dict(ls="none", marker="s", ms=3.4, mfc="white", mec=style.INK, mew=0.8,
                   zorder=6, clip_on=False)

    # (c) far-side mass over ours; 2026-10-20: the drainhole's sign change as a dotted
    # rule (named in the key, as on the instability curve) and the 3D runs on it
    ax_c.axhline(0.0, **rule)
    vrule = dict(color="#b5b5b2", lw=0.8, ls=":")
    v0 = sign_change(fams[0])
    ax_c.axvline(v0, **vrule)
    band = dict(facecolor="#d9d9d6", edgecolor="#9a9a96", lw=0.6, ls="--")
    ax_c.axvspan(*(float(headers.meta(bg)["v_e"]) for bg in FAR_END_BAND), zorder=0, **band)
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_c, f, "Mratio", red, ls)
    ax_c.plot(*run_ratios(), **runmark)
    ax_c.set(xlim=(0, 1), ylim=(-1.1, 1.1), ylabel=r"$M_-/M_+$")
    style.legend_top(ax_c, [key(vrule, rf"$M_-=0$, $v_e={v0:.2f}$"), key(runmark, "3D runs"),
                            (Patch(**band), "run breaks down at the far end")],
                     ncol=2, borderpad=0.4, **TIGHT)

    # (d) flattening
    ext = kk2014.kerr(np.array([1.0]))
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_d, f, "Rp", red, ls)
    ax_d.plot([1.0], ext["Rp"], **dot)
    ax_d.set(xlim=(0, 1), ylim=(0.58, 1.02), ylabel=r"$R_p/R_e$", xlabel=r"$v_e$")

    # (e) exotic matter per throat radius (2026-10-20: replaces the scalar charge, which
    # Table II lists); the 3D runs' measured charge put on the drainhole curve.
    # 2026-10-21: each family over its own static member, so the fall with spin reads
    # at a glance (|I|/R_e alone needed the caption)
    ax_e.axhline(1.0, **rule)
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_e, f, "Xrel", style.INK, ls)
    v_runs, x_runs = run_points(fams[0])
    ax_e.plot(v_runs, x_runs / fams[0]["static"]["X"], **runmark)
    ax_e.set(yscale="log", xlim=(0, 1), ylim=(0.005, 2.0),
             ylabel=r"$\mathcal{I}/\mathcal{I}_{\rm static}$", xlabel=r"$v_e$")
    ax_e.set_yticks([0.01, 0.1, 1.0], ["0.01", "0.1", "1"])
    # a marker-only handle measures half a marker past its box: a little more border keeps
    # it inside the key
    style.legend_top(ax_e, [key(rule, "static wormhole"), key(runmark, r"3D runs, $t=0$")],
                     ncol=2, borderpad=0.4, **TIGHT)

    # (f) rotation rate
    for f, (*_, ls) in zip(fams, FAMILIES):
        curve(ax_f, f, "Om", blue, ls)
    ax_f.plot([1.0], [0.0], **dot)
    ax_f.set(xlim=(0, 1), ylim=(0.0, 0.55), ylabel=r"$\Omega\,\eta_0$", xlabel=r"$v_e$")

    # 2026-10-20: the families' dashes and the extremal dots keyed once, above the
    # figure (every panel repeated them)
    fig.legend(*zip(*[key(line(style.INK, ls), name) for *_, name, ls in FAMILIES],
                    key(dot, "extremal Kerr")),
               loc="outside upper center", ncol=3, frameon=False, fontsize=7.0,
               handlelength=2.0, columnspacing=1.8)

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
