#!/usr/bin/env python3
"""Compare the wormhole p012 merger waveform with the vacuum BBH control.

Both series come from the SAME instrument: the in-code Weyl4 mode integrals
GRTeclyn writes while it runs (the extraction chain validated against
independent Simpson quadrature).  The two runs share ADM masses (1.0 each),
separation (d = 12) and tangential momentum (p = 0.12), so every difference
in the panels is the object, not the orbit.

Inputs (the packed campaign under results/merger, found from the repo root
this file sits in, or given explicitly):
  campaign/merge_twin_p012_plain_t100/Weyl4_mode_2{0,2}.dat     (wormholes)
  campaign/bbh_control_d12_p012/weyl_extraction_mode_2{0,2}.dat (black holes)

Usage: plot_bbh_vs_wormhole_psi4.py [--pack-root DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import pathlib
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch

R_PLOT = 14.0   # innermost extraction sphere, common to both runs


def load_mode(path: pathlib.Path, radius: float):
    """Return (t, complex psi4 mode integral) at the requested radius.

    Handles the GRTeclyn stream header ('r =  14.000000 ...') used by both
    the packed wormhole files and the BBH extraction files.
    """
    radii = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") and "r =" in line:
                vals = [float(x) for x in re.findall(r"[\d.eE+-]+", line)]
                radii = vals[::2]
                break
    if radii is None:
        raise ValueError(f"no radius header in {path}")
    i = radii.index(radius)
    a = np.loadtxt(path)
    return a[:, 0], a[:, 1 + 2 * i] + 1j * a[:, 2 + 2 * i]


def main() -> int:
    # …/GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/merger
    root = pathlib.Path(__file__).resolve().parents[5]
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-root", default=str(root / "results" / "merger"))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    pack = pathlib.Path(args.pack_root)
    camp = pack / "campaign"
    if args.out is None:
        args.out = str(pack / "figures")

    wh_dir = camp / "merge_twin_p012_plain_t100"
    bh_dir = camp / "bbh_control_d12_p012_t150"
    series = {
        ("wh", 2): load_mode(wh_dir / "Weyl4_mode_22.dat", R_PLOT),
        ("wh", 0): load_mode(wh_dir / "Weyl4_mode_20.dat", R_PLOT),
        ("bh", 2): load_mode(bh_dir / "weyl_extraction_mode_22.dat", R_PLOT),
        ("bh", 0): load_mode(bh_dir / "weyl_extraction_mode_20.dat", R_PLOT),
    }

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Computer Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "axes.labelsize": 13,
        "axes.titlesize": 14,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.linewidth": 1.1,
        "legend.fontsize": 10,
    })
    STYLE = {"wh": dict(color="black", ls="-", lw=1.2),
             "bh": dict(color="#9b2226", ls="--", lw=1.2)}
    LBL = {"wh": "wormholes (p012 twin)", "bh": "black holes (control)"}

    fig, axs = plt.subplots(2, 2, figsize=(12, 8.5))

    ax = axs[0, 0]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        ax.plot(t - R_PLOT, np.real(psi), label=LBL[k], **STYLE[k])
    ax.set_title(r"(a) $\mathrm{Re}\,\Psi_4^{2,2}$ mode at $R=14$")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)

    ax = axs[0, 1]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        env = np.abs(psi)
        ax.plot(t - R_PLOT, env, label=LBL[k], **STYLE[k])
        i = int(np.argmax(env))
        ax.plot(t[i] - R_PLOT, env[i], "o", ms=5, color=STYLE[k]["color"])
        ax.annotate(f"{env[i]:.4f}", (t[i] - R_PLOT, env[i]),
                    textcoords="offset points", xytext=(6, 4), fontsize=10)
    ax.set_title(r"(b) $|\Psi_4^{2,2}|$ envelope — wormholes peak $2.3\times$ higher, $\sim 35$ earlier")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")

    ax = axs[1, 0]
    for k in ("wh", "bh"):
        t, psi = series[(k, 0)]
        env = np.abs(psi)
        ax.plot(t - R_PLOT, env, label=LBL[k], **STYLE[k])
        i = int(np.argmax(env))
        ax.plot(t[i] - R_PLOT, env[i], "o", ms=5, color=STYLE[k]["color"])
        ax.annotate(f"{env[i]:.4f}", (t[i] - R_PLOT, env[i]),
                    textcoords="offset points", xytext=(6, 4), fontsize=10)
    ax.set_title(r"(c) $|\Psi_4^{2,0}|$ envelope — the wormholes' extra channel ($5.5\times$)")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")

    ax = axs[1, 1]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        dt = float(np.median(np.diff(t)))
        f, p = welch(np.real(psi), 1.0 / dt, nperseg=min(len(psi) // 2, 256))
        ax.semilogy(f, p, label=LBL[k], **STYLE[k])
    ax.set_xlim(0, 0.6)
    ax.set_title(r"(d) PSD of $\Psi_4^{2,2}$ — wormhole power sits lower in frequency")
    ax.set_xlabel(r"$f\ (M^{-1})$")

    for ax in axs.flat:
        ax.grid(True, ls="--", alpha=0.5)
        ax.tick_params(direction="in", top=True, right=True)

    fig.suptitle("Same masses, same orbit ($d=12$, $p=\\pm0.12$, $M_{\\rm ADM}=1$ each) — different object",
                 fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    out_dir = pathlib.Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"bbh_vs_wormhole_psi4.{ext}", dpi=300, bbox_inches="tight")
    print(f"[compare] wrote {out_dir}/bbh_vs_wormhole_psi4.png (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
