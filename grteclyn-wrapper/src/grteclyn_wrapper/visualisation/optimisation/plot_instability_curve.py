"""Compare the evolved D0/D21/D30/D40/D46 potentials with the spinning paper at N=128.

Reuse the spinning paper's radius-derivative fit, not its plotting style.
The comparison is between finite-resolution evolutions, not a continuum
growth-rate estimate or an exactly matched control experiment. All inputs
are tracked; no cluster connection or evolution is needed.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto
from grteclyn_wrapper.optimisation.exoticity import throat
from grteclyn_wrapper.visualisation.spinning_wormhole.plot_instability_curve import (
    BAND, RUNS, fit_zero, rate_tau, table_meta,
)
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, LIGHT_BLUE, INK, GREY
from .paper_results import REPO

CLASSICAL = REPO / "results/spinningwormhole/campaign/drainhole/00_paper_runs"
POTENTIAL = REPO / "results/optimisation/campaign/D21_X1p829_L64_N128_ml3_spdrv0_t150"
FIGURES = REPO / "results/optimisation/figures"
GROWTH_TABLE = REPO / "results/optimisation/article/instability_curve.tsv"
MODELS = ("D0", "D21", "D30", "D40", "D46", "D51")


def measure(path, collapse=True, tmax=None):
    a = np.loadtxt(path)
    if tmax is not None:
        a = a[a[:, 0] <= tmax]
    tau, span = rate_tau(a[:, 0], a[:, 2], collapse=collapse)
    if tau is None or tau <= 0:
        raise ValueError(f"No positive growth-time fit for {path}")
    return dict(tau=float(tau), fit_start=float(span[0]), fit_end=float(span[1]),
                rate=1.0 / float(tau)), a


def load():
    points, histories = [], {}
    for spec in RUNS:
        if spec["label"] not in MODELS:
            continue
        root = CLASSICAL / spec["run"]
        # Every reference point in this restricted spin range uses N=128.
        params = dict(line.split("=", 1) for line in
                      (root / "evolution_params.txt").read_text().splitlines()
                      if "=" in line and not line.lstrip().startswith("#"))
        assert int(next(v for k, v in params.items() if k.strip() == "N1")) == 128
        history = np.loadtxt(root / "throat_spheres.dat")
        expansion_tau, _ = rate_tau(history[:, 0], history[:, 2], collapse=False)
        # Match the original figure: expansion after an initial contraction
        # takes precedence when it crosses the full fitting interval.
        expands = expansion_tau is not None
        measured, history = measure(root / "throat_spheres.dat", collapse=not expands)
        j, frac = table_meta(spec["table"])
        points.append(dict(label=spec["label"], j=j, frac=frac,
                           branch="inflates" if expands else "collapses", **measured))
        if spec["label"] == "D21":
            histories["classical"] = history
    with np.load(REPO / "results/optimisation/article/d21_e140_210x42.npz") as d:
        meta = json.loads(str(d["meta"]))
        sx, dx = lobatto(d["sx"].size - 1)
        np.testing.assert_allclose(sx, d["sx"], atol=1e-14)
        geom = throat(1.0, ArctanMap(1.0), sx, d["sy"], dx, d["F"], d["N"], d["B"])
    # The saved fields use grid units: physical areas carry sigma squared.
    area = geom["area_throat"] * meta["sigma"] ** 2
    np.testing.assert_allclose(geom["R_e"] * meta["sigma"], meta["R_e"], rtol=1e-9)
    measured, histories["potential"] = measure(POTENTIAL / "small_data/throat_spheres.dat.gz")
    candidate = dict(label="D21 potential", j=meta["J"],
                     frac=100 * 8 * np.pi * meta["J"] / area,
                     branch="collapses", **measured)
    d0_root = REPO / "results/optimisation/completed/2026-10-31/d0"
    measured, _ = measure(d0_root / "small_data/throat_spheres.dat.gz")
    # The validated D0 background is static: J/A is exactly zero.
    with np.load(REPO / "results/optimisation/validation/2026-10-30-alternatives/d0/009_e0211/handoff.npz") as d:
        assert json.loads(str(d["meta"]))["J"] == 0
    d0 = dict(label="D0 potential", j=0.0, frac=0.0,
              branch="collapses", **measured)
    d30_root = REPO / "results/optimisation/completed/2026-10-31/d30"
    with np.load(d30_root / "fam_a_r1_0005_cma_resolution_20261030_best_clean.npz") as d:
        meta30 = json.loads(str(d["meta"]))
        assert meta30["resolution"]["passed"] and meta30["verdict"] == "PASS"
        sx, dx = lobatto(d["sx"].size - 1)
        np.testing.assert_allclose(sx, d["sx"], atol=1e-14)
        geom30 = throat(1.0, ArctanMap(1.0), sx, d["sy"], dx,
                        d["F"], d["N"], d["B"])
    area30 = geom30["area_throat"] * meta30["sigma"] ** 2
    np.testing.assert_allclose(geom30["R_e"] * meta30["sigma"], meta30["R_e"], rtol=1e-9)
    measured, _ = measure(d30_root / "evolution/small_data/throat_spheres.dat.gz")
    d30 = dict(label="D30 potential", j=meta30["J"],
               frac=100 * 8 * np.pi * meta30["J"] / area30,
               branch="collapses", **measured)
    d40_root = REPO / "results/optimisation/completed/2026-10-31/d40"
    with np.load(d40_root / "fam_a_r1_0008_cma_resolution_20261031_best_clean.npz") as d:
        meta40 = json.loads(str(d["meta"]))
        assert meta40["resolution"]["passed"] and meta40["verdict"] == "PASS"
        sx, dx = lobatto(d["sx"].size - 1)
        np.testing.assert_allclose(sx, d["sx"], atol=1e-14)
        geom40 = throat(1.0, ArctanMap(1.0), sx, d["sy"], dx,
                        d["F"], d["N"], d["B"])
    area40 = geom40["area_throat"] * meta40["sigma"] ** 2
    np.testing.assert_allclose(geom40["R_e"] * meta40["sigma"], meta40["R_e"], rtol=1e-9)
    measured, _ = measure(d40_root / "evolution/small_data/throat_spheres.dat")
    d40 = dict(label="D40 potential", j=meta40["J"],
               frac=100 * 8 * np.pi * meta40["J"] / area40,
               branch="collapses", **measured)
    d46_root = REPO / "results/optimisation/completed/2026-10-31/d46"
    with np.load(d46_root / "fam_a_r1_0010_cma_resolution_20261031_r2_best_clean.npz") as d:
        meta46 = json.loads(str(d["meta"]))
        assert meta46["resolution"]["passed"] and meta46["verdict"] == "PASS"
        sx, dx = lobatto(d["sx"].size - 1)
        np.testing.assert_allclose(sx, d["sx"], atol=1e-14)
        geom46 = throat(1.0, ArctanMap(1.0), sx, d["sy"], dx,
                        d["F"], d["N"], d["B"])
    area46 = geom46["area_throat"] * meta46["sigma"] ** 2
    np.testing.assert_allclose(geom46["R_e"] * meta46["sigma"], meta46["R_e"], rtol=1e-9)
    measured, _ = measure(d46_root / "evolution/small_data/throat_spheres.dat.gz", tmax=100)
    d46 = dict(label="D46 potential", j=meta46["J"],
               frac=100 * 8 * np.pi * meta46["J"] / area46,
               branch="collapses", **measured)
    return points, [d0, candidate, d30, d40, d46], histories


def draw(points, candidates, histories, with_history=False):
    style.prd(8.0)
    if with_history:
        fig, (ax, time_ax) = plt.subplots(1, 2, figsize=(7.05, 2.5), layout="constrained")
    else:
        fig, ax = plt.subplots(figsize=(3.4, 2.3), layout="constrained")
    fitted = fit_zero(points)
    a, b, zero = fitted
    xs = np.linspace(0, zero, 300)
    ax.plot(xs, a - b * xs**2, "--", color=GREY, lw=1, zorder=1)
    potential_fit = fit_zero(candidates)
    if potential_fit is not None:
        pa, pb, potential_zero = potential_fit
        px = np.linspace(min(p["frac"] for p in candidates),
                         max(p["frac"] for p in candidates), 200)
        ax.plot(px, pa - pb * px**2, color=BLUE, lw=1, zorder=2)
        # Continue the same fit as a prediction, ending at zero growth.
        prediction_end = min(38., potential_zero) if potential_zero is not None else 38.
        if prediction_end > px[-1]:
            predicted_x = np.linspace(px[-1], prediction_end, 200)
            ax.plot(predicted_x, pa - pb * predicted_x**2, ls="--",
                    color=BLUE, lw=1, zorder=2)
    for p in points:
        ax.scatter(p["frac"], p["rate"], marker="^" if p["branch"] == "inflates" else "o",
                   s=9, color=INK, zorder=3)
    for candidate in candidates:
        ax.scatter(candidate["frac"], candidate["rate"], marker="s", s=9,
                   facecolor="white", edgecolor=BLUE, linewidth=.65, zorder=4)
    ax.set(xlim=(-1.5, 38), ylim=(-.005, .205), xlabel="Reference model",
           ylabel=r"Growth rate $1/\tau$")
    # Model ticks label the physical spin coordinates; do not make the
    # samples equally spaced or shift the potential's own J/A coordinate.
    ax.set_xticks([p["frac"] for p in points], [p["label"] for p in points])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    entries = [
        (Line2D([], [], marker="o", ls="none", color=INK, ms=4), r"$V=0$, collapse"),
        (Line2D([], [], marker="^", ls="none", color=INK, ms=4), r"$V=0$, expansion"),
        (Line2D([], [], marker="s", ls="-", color=BLUE, mfc="white",
                lw=1, mew=.95, ms=4.8), "With potential"),
        (Line2D([], [], ls="--", color=GREY, lw=1), r"$V=0$ fit"),
    ]
    style.legend_top(ax, entries, ncol=2, fontsize=6.8, columnspacing=.8, borderpad=.6)
    if with_history:
        for key, color in (("classical", INK), ("potential", BLUE)):
            data = histories[key]
            time_ax.plot(data[:, 0], 100 * (1 - data[:, 2] / data[0, 2]), color=color, lw=1.3)
        time_ax.axhspan(100 * BAND[0], 100 * BAND[1], color=LIGHT_BLUE, alpha=.2, zorder=0)
        time_ax.set(xlim=(25, 75), ylim=(-.03, 2.1), xlabel=r"Time $t$",
                    ylabel=r"Areal-radius decrease [%]")
        style.legend_top(time_ax, [
            (Line2D([], [], color=INK, lw=1.3), r"D21, $V=0$"),
            (Line2D([], [], color=BLUE, lw=1.3), "D21 with potential"),
            (Patch(facecolor=LIGHT_BLUE, alpha=.2), "0.2–1% fitting interval"),
        ], ncol=1, fontsize=6.8)
        style.tag_keys(fig, (ax, time_ax), ("(a)", "(b)"), fontsize=8)
    return fig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=FIGURES / "instability_curve")
    ap.add_argument("--table-out", type=Path, default=GROWTH_TABLE,
                    help="Measured growth-rate table (separate from figure outputs)")
    ap.add_argument("--with-history", action="store_true", help="Add the radius-history panel")
    args = ap.parse_args(argv)
    points, candidates, histories = load()
    fig = draw(points, candidates, histories, args.with_history)
    print(style.save(fig, args.out))
    issues = style.label_audit(fig)
    print("label audit:", issues or "clean")
    plt.close(fig)
    args.table_out.parent.mkdir(parents=True, exist_ok=True)
    with args.table_out.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(points[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(points + candidates)
    for candidate in candidates:
        ref = next(p for p in points if p["label"] == candidate["label"].split()[0])
        print(f"{candidate['label']}, N=128: tau {candidate['tau']:.6f}; "
              f"reference tau {ref['tau']:.6f} ({ref['branch']})")
    return bool(issues)


if __name__ == "__main__":
    raise SystemExit(main())
