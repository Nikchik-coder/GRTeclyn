#!/usr/bin/env python3
"""D21 resolution study from the final, tracked diagnostic streams.

Constraints use the common t <= 50 interval. The lower row shows each
run's complete recorded diagnostic history, with missing throat estimates
left as gaps. Rescaling is applied only to constraints whose exact value
is zero, never to the throat drift. No spinning-paper layout is imported.
"""
from __future__ import annotations
import argparse
import csv
import gzip
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, LIGHT_BLUE, INK, GREY, RESOLUTIONS

REPO = Path(__file__).resolve().parents[5]
PACKED = REPO / "results/optimisation/campaign"
FIGURES = REPO / "results/optimisation/figures"
RUNS = tuple((n, f"D21_X1p829_L64_N{n:03d}_ml3_spdrv0_t150") for n in (96, 128, 192))
R_EXACT = 4.063830498135651
TIMES = (10., 20., 30., 40., 50.)


def stream(root, folder, name):
    p = root / folder / name
    return p if p.exists() else p.with_suffix(p.suffix + ".gz")


def load():
    data = {}
    for n, name in RUNS:
        root = PACKED / name
        d = {k: np.loadtxt(stream(root, "data", f)) for k, f in (
            ("norms", "constraint_norms_levels.dat"),
            ("geometry", "throat_geometry.dat"), ("collapse", "collapse_diagnostics.dat"))}
        for key, a in d.items():
            if not np.isfinite(a).all() or np.any(np.diff(a[:, 0]) <= 0):
                raise ValueError(f"{name}: non-finite or unordered {key}")
        d["spheres"] = np.loadtxt(stream(root, "small_data", "throat_spheres.dat"))
        p = stream(root, "small_data", "psi4_mode_l2_all.dat")
        with (gzip.open(p, "rt") if p.suffix == ".gz" else p.open()) as f:
            head = f.readline().split()[1:]
        wave = np.loadtxt(p)
        d["wave"] = wave[:, [0, head.index("Re_m0(R=14)")]]
        data[n] = d
    return data


def order_rows(data):
    rows = []
    for level in range(4):
        for j, name in enumerate(("Ham", "Mom")):
            for t in TIMES:
                e = []
                for n, _ in RUNS:
                    a = data[n]["norms"]
                    if not a[0, 0] <= t <= a[-1, 0]:
                        raise ValueError("order time lies outside a recorded stream")
                    e.append(np.interp(t, a[:, 0], a[:, 1 + 2 * level + j]))
                rows.append(dict(constraint=name, level=level, time=t,
                                 p96_128=np.log(e[0]/e[1])/np.log(128/96),
                                 p128_192=np.log(e[1]/e[2])/np.log(192/128)))
    return rows


def draw(data, t_constraints=50.):
    style.prd(8.0)
    fig, axes = plt.subplots(3, 4, figsize=(7.05, 3.85), layout="constrained")
    formats = [dict(color=c, lw=1.1) for c in RESOLUTIONS]
    rescaled = [dict(color=GREY, lw=.85, ls=ls) for ls in ("--", ":")]
    for j in range(2):
        for level in range(4):
            ax = axes[j, level]
            for (n, _), fmt in zip(RUNS, formats):
                a = data[n]["norms"]
                a = a[a[:, 0] <= t_constraints + 1e-8]
                ax.plot(a[:, 0], a[:, 1 + 2*level + j], **fmt)
            a = data[192]["norms"]
            a = a[a[:, 0] <= t_constraints + 1e-8]
            for p, fmt in zip((2, 4), rescaled):
                ax.plot(a[:, 0], a[:, 1 + 2*level + j] * 2**p, **fmt)
            ax.set(yscale="log", xlim=(0, t_constraints), xticks=[0, 25, 50])
            title = f"({chr(97+j*4+level)})" + (f" Level {level}" if j == 0 else "")
            ax.set_title(title, loc="left", fontsize=7.5, pad=4)
            if j == 0:
                ax.tick_params(labelbottom=False)
            else:
                ax.set_xlabel(r"$t$")
            if level == 0:
                ax.set_ylabel((r"$\|\mathcal{H}\|_2$", r"$\|\mathcal{M}\|_2$")[j])
    for (n, _), fmt in zip(RUNS, formats):
        d = data[n]
        g, a, w, c = (d[k] for k in ("geometry", "spheres", "wave", "collapse"))
        axes[2, 0].plot(g[:, 0], 100*(g[:, 1]/g[0, 1]-1), **fmt)
        axes[2, 1].plot(a[:, 0], 100*(a[:, 2]/a[0, 2]-1), **fmt)
        axes[2, 2].plot(w[:, 0], 1e5*(w[:, 1]-w[0, 1]), **fmt)
        axes[2, 3].plot(c[:, 0], c[:, 1], **fmt)
    names = ("Equatorial radius", "Areal radius", "Wave extraction", "Minimum lapse")
    labels = (r"$\Delta R_{\rm eq}/R_{\rm eq}(0)$ [%]", r"$\Delta R_A/R_A(0)$ [%]",
              r"$10^5\Delta(r\,\mathrm{Re}\,\Psi_4^{20})$", r"$\alpha_{\min}$")
    for i, ax in enumerate(axes[2]):
        ax.set_title(f"({chr(105+i)}) {names[i]}", loc="left", fontsize=7.5, pad=4)
        ax.set(xlabel=r"$t$", ylabel=labels[i], xlim=(0, 115), xticks=[0, 50, 100])
    axes[2, 3].set_yscale("log")
    fig.legend([Line2D([], [], **f) for f in formats + rescaled],
               [f"$N={n}$" for n, _ in RUNS] + [r"$N=192\times 2^2$", r"$N=192\times 2^4$"],
               loc="outside upper center", ncol=5, frameon=False, fontsize=7.5,
               handlelength=2, columnspacing=1.5)
    return fig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=FIGURES / "convergence_d21")
    args = ap.parse_args(argv)
    data = load()
    fig = draw(data)
    issues = style.label_audit(fig)
    print(style.save(fig, args.out))
    plt.close(fig)
    rows = order_rows(data)
    with (PACKED / "constraint_orders.tsv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    for n, d in data.items():
        g = d["geometry"]
        t1 = g[np.flatnonzero(g[:, 1]/g[0, 1] <= .99)[0], 0]
        print(f"N={n}: last t={g[-1,0]:g}; first 1% contraction t={t1:g}")
    print(f"label audit: {issues or 'clean'}")
    return bool(issues)

if __name__ == "__main__":
    raise SystemExit(main())
