#!/usr/bin/env python3
"""Same masses, same orbit, different object: the p012 wormhole pair against
the vacuum black-hole control.

Both series come from the SAME instrument: the in-code Weyl4 mode integrals
GRTeclyn writes while it runs (the extraction chain validated against
independent Simpson quadrature).  The two runs share ADM masses (1.0 each),
separation (d = 12) and tangential momentum (p = 0.12), so every difference in
the panels is the object, not the orbit.

Inputs: the packed campaign under results/merger, with each run resolved BY
NAME wherever it is filed -- the pack is refiled by physics as the campaign
grows and a hard-coded `campaign/<run>` path stops working the day it is.

Usage: plot_bbh_vs_wormhole_psi4.py [--pack-root DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.signal import welch  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import figure_dir, find_packed  # noqa: E402

R_PLOT = 14.0   # innermost extraction sphere, common to both runs
WORMHOLE = "merge_twin_p012_plain_t100"
BLACKHOLE = "bbh_control_d12_p012_t150"


def mode(run_dir: pathlib.Path, lm: str, radius: float):
    """(t, complex) for one mode, from whichever naming this run was packed under."""
    for stem in (f"Weyl4_mode_{lm}.dat", f"weyl_extraction_mode_{lm}.dat"):
        p = run_dir / stem
        if p.exists():
            t, by_r = streams.load_mode(p)
            return t, by_r[radius]
    # The t150 rerun carries only the combined l = 2 stream.
    t, modes = streams.load_l2_all(run_dir / "psi4_mode_l2_all.dat")
    return t, modes[(int(lm[1:]), radius)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--wormhole", default=WORMHOLE)
    ap.add_argument("--black-hole", default=BLACKHOLE)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    dirs = {"wh": find_packed(args.wormhole, args.pack_root),
            "bh": find_packed(args.black_hole, args.pack_root)}
    series = {(k, m): mode(d, f"2{m}", R_PLOT) for k, d in dirs.items() for m in (0, 2)}

    style.paper(base=10.0)
    # Two objects, so two slots: the wormhole is the subject (ink, solid), the
    # control is what it is measured against (deep blue, dashed).
    KW = {"wh": style.series(0, lw=1.2), "bh": style.series(1, lw=1.2)}
    LBL = {"wh": "wormholes ($p=0.12$ twin)", "bh": "black holes (vacuum control)"}

    fig, axs = plt.subplots(2, 2, figsize=(9.6, 6.6), constrained_layout=True)

    peaks: dict[tuple[str, int], tuple[float, float]] = {}

    def peak_mark(ax, k, m, t, y):
        """Name the peak once, on the curve, instead of in a caption."""
        i = int(np.argmax(y))
        peaks[(k, m)] = (t[i], y[i])
        ax.plot(t[i], y[i], marker="o", ms=4, color=KW[k]["color"], zorder=5)
        ax.annotate(f"{y[i]:.4f}", (t[i], y[i]), textcoords="offset points",
                    xytext=(6, 4), fontsize=8.5, color=style.MUTED)

    def ratio(m: str) -> str:
        """The comparison the panel is making, measured rather than remembered.

        These used to be typed into the titles by hand; when the control was
        repacked as the longer t150 run the '35 earlier' stayed put and became
        wrong by 17 units.  Read them off the curves instead.
        """
        (t_w, y_w), (t_b, y_b) = peaks[("wh", m)], peaks[("bh", m)]
        return rf"${y_w / y_b:.1f}\times$ higher, ${t_b - t_w:.0f}$ earlier"

    ax = axs[0, 0]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        ax.plot(t - R_PLOT, np.real(psi), label=LBL[k], **KW[k])
    ax.set_title(r"(a) $\mathrm{Re}\,\Psi_4^{2,2}$ at $R=14$", loc="left")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")

    ax = axs[0, 1]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        env = np.abs(psi)
        ax.plot(t - R_PLOT, env, **KW[k])
        peak_mark(ax, k, 2, t - R_PLOT, env)
    ax.set_title(r"(b) $|\Psi_4^{2,2}|$ — the wormholes peak " + ratio(2), loc="left")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")

    ax = axs[1, 0]
    for k in ("wh", "bh"):
        t, psi = series[(k, 0)]
        env = np.abs(psi)
        ax.plot(t - R_PLOT, env, **KW[k])
        peak_mark(ax, k, 0, t - R_PLOT, env)
    ax.set_title(r"(c) $|\Psi_4^{2,0}|$ — the wormholes' extra channel, " + ratio(0), loc="left")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")

    ax = axs[1, 1]
    for k in ("wh", "bh"):
        t, psi = series[(k, 2)]
        dt = float(np.median(np.diff(t)))
        f, p = welch(np.real(psi), 1.0 / dt, nperseg=min(len(psi) // 2, 256))
        ax.semilogy(f, p, **KW[k])
    ax.set_xlim(0, 0.6)
    ax.set_title(r"(d) PSD of $\Psi_4^{2,2}$ — wormhole power sits lower in frequency", loc="left")
    ax.set_xlabel(r"$f\ (M^{-1})$")

    fig.suptitle(r"Same masses, same orbit ($d=12$, $p=\pm0.12$, $M_{\mathrm{ADM}}=1$ each)"
                 " — different object")
    # One legend for the whole figure: the two curves mean the same thing in
    # every panel, so repeating the key four times is four times the ink for
    # nothing, and inside panel (a) it sat on top of the wormhole trough.
    handles = [plt.Line2D([], [], **KW[k]) for k in ("wh", "bh")]
    fig.legend(handles, [LBL["wh"], LBL["bh"]], loc="outside lower center", ncols=2,
               columnspacing=3.0)

    out = pathlib.Path(args.out) if args.out else figure_dir("05_binary_spiral", args.pack_root)
    png = style.save(fig, (out / "bbh_vs_wormhole_psi4.png") if out.is_dir() else out)
    print(f"[compare] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
