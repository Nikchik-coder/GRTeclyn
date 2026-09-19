#!/usr/bin/env python3
r"""One deformed throat's collapse, on one page: gauge, matter, shells, horizon.

The single-throat analogue of the spiral collapse page, drawn from the pure-
quadrupole arm (`single_pureq_q1e2_ml4_t100`, 2026-09-19): an l = 2 seed of
amplitude 0.01 and NO radial kick, on the refinement level whose own
truncation seed inflates the round throat -- and it still collapses, forming
a MOTS at t = 33.  This arm is the first single-throat collapse with the full
measuring machinery on, and unlike the binary (whose throats orbit at r = 6),
the throat sits INSIDE the r < 4 radial-profile window for the whole run, so
the K/chi/lapse shells watch the collapse from beginning to end.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_collapse

Reads, all under ``campaign/01_single_throat/seed/single_pureq_q1e2_ml4_t100``:
``areal_radius.dat`` (the consumer's per-throat minimal-surface scan),
``horizon_scan.dat`` (the oriented scan; MOTS radius and Misner-Sharp mass),
``collapse_diagnostics.dat`` (min lapse / min chi / max |K| at dt = 0.01),
``core_radial_profile.dat`` (128 shells to r = 4, thinned to dt = 0.05) and
``constraint_norms.dat``.  Writes ``figures/01_single_throat/single_throat_collapse``.

STYLE (the PRD review grammar of the spiral page): a wide context strip over
a 2 x 3 grid, style.prd frame, no titles, letter tags above the frames, no
boxed key, every series named in place.  Monochrome ink plus the one accent:
DEEP_GREEN is the horizon instrument -- the oriented scan's MOTS -- and nothing
else.  Ordered time families (the radial snapshots) are a grey ramp, light =
early.  min chi is labelled as what it is, the ORIGIN monitor (the far
universe's compactified infinity), not the throat.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "01_single_throat"
ARM = "seed/single_pureq_q1e2_ml4_t100"
SNAPS = (33.0, 40.0, 45.0, 48.0, 50.0, 55.0)   # grey ramp, light = early; the collapse is 45-55
T_MOTS = 33.0


def _profile(path: pathlib.Path):
    """time, radii, and the three per-shell blocks of the radial profile."""
    with open(path) as fh:
        fh.readline()
        names = fh.readline().lstrip("#").split()
    data = np.loadtxt(path)
    t = data[:, 0]
    blocks: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in ("chi_min", "absK_max", "lapse_min"):
        idx = [i for i, nm in enumerate(names) if nm.startswith(key + "_r")]
        if not idx:
            continue
        r = np.array([float(names[i].split("_r")[-1]) for i in idx])
        blocks[key] = (r, data[:, idx])
    return t, blocks


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    arm = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP / ARM

    ar = np.loadtxt(arm / "areal_radius.dat")
    cd = np.loadtxt(arm / "collapse_diagnostics.dat")
    cn = np.loadtxt(arm / "constraint_norms.dat")
    tp, blocks = _profile(arm / "core_radial_profile.dat")
    h = np.genfromtxt(arm / "horizon_scan.dat", dtype=None, encoding=None, names=True)
    hA = h[(h["centre"] == "A") & (h["n_mots"] > 0)]

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 5.0), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, height_ratios=[1.15, 1.0, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1 + i // 3, i % 3]) for i in range(6)]
    tags = "abcdefg"

    # ---- context strip: the throat itself, and the horizon instrument -----
    axT.plot(ar[:, 0], ar[:, 1], color=style.INK, linewidth=1.4, zorder=3)
    axT.plot(hA["time"], hA["R_mots"], color=style.DEEP_GREEN, linewidth=0.0,
             marker="o", markersize=2.4, zorder=4)
    axT.axvline(T_MOTS, color=style.FAINT, linewidth=0.7, zorder=1)
    axT.text(T_MOTS + 0.8, 5.35, r"MOTS from $t=33$", fontsize=7,
             color=style.DEEP_GREEN, ha="left")
    axT.text(2, 3.55, "minimal-surface areal radius", fontsize=7.5,
             color=style.INK)
    axT.text(72, 2.85, "oriented scan's MOTS", fontsize=7,
             color=style.DEEP_GREEN)
    axT.set_xlim(0, 100)
    axT.set_ylim(1.5, 6.0)
    axT.set_ylabel(r"$R_{\rm areal}$")
    axT.set_xlabel(r"$t$")
    axT.text(0.012, 0.93, "(a)", transform=axT.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) min lapse, (c) min chi (origin), (d) max |K| -----------------
    t, mlap, mchi, mK = cd[:, 0], cd[:, 1], cd[:, 2], cd[:, 3]
    for ax, y, lab, logy in ((axs[0], mlap, r"$\min\alpha$", True),
                             (axs[1], mchi, r"$\min\chi$ (origin)", True),
                             (axs[2], mK, r"$\max|K|$", False)):
        ax.plot(t, y, color=style.INK, linewidth=1.1, zorder=3)
        ax.axvline(T_MOTS, color=style.FAINT, linewidth=0.7, zorder=1)
        if logy:
            ax.set_yscale("log")
        ax.set_xlim(0, 100)
        ax.set_ylabel(lab)

    # ---- (e)/(f) the shells: |K| and lapse profiles, light = early --------
    ramp = [style.FAINT, "#8f8b81", "#6f6c64", "#54524c", "#37352f", style.INK]
    for ax, key, lab in ((axs[3], "absK_max", r"$|K|$ per shell"),
                         (axs[4], "lapse_min", r"$\alpha$ per shell")):
        r, block = blocks[key]
        for c, ts in zip(ramp, SNAPS):
            i = int(np.argmin(np.abs(tp - ts)))
            ax.plot(r, block[i], color=c, linewidth=1.0, zorder=3)
        ax.set_xlim(0, 4.0)
        ax.set_ylabel(lab)
        ax.set_xlabel(r"$r$")
    axs[3].text(0.96, 0.93, rf"$t={SNAPS[0]:g}$--${SNAPS[-1]:g}$",
                transform=axs[3].transAxes, ha="right", va="top", fontsize=7,
                color=style.MUTED)
    axs[3].text(0.96, 0.82, "light = early", transform=axs[3].transAxes,
                ha="right", va="top", fontsize=7, color=style.MUTED)

    # ---- (g) the constraints ----------------------------------------------
    axs[5].plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    axs[5].plot(cn[:, 0], cn[:, 2], color=style.MUTED, linewidth=1.1,
                linestyle=(0, (4, 2.5)), zorder=3)
    axs[5].axvline(T_MOTS, color=style.FAINT, linewidth=0.7, zorder=1)
    axs[5].set_yscale("log")
    axs[5].set_xlim(0, 100)
    axs[5].set_ylabel(r"$L_2$ norms")
    axs[5].text(0.5, 0.88, r"$\mathcal{H}$", transform=axs[5].transAxes,
                fontsize=7.5, color=style.INK)
    axs[5].text(0.5, 0.72, r"$\mathcal{M}$", transform=axs[5].transAxes,
                fontsize=7.5, color=style.MUTED)

    # Letter tags ABOVE the frames (the spiral page's rule): several of these
    # panels run flat along their own top edge, and an inside tag sits on the
    # curve.
    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({tags[k + 1]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
        if k < 3:
            ax.set_xlabel(r"$t$")
    axs[5].set_xlabel(r"$t$")

    print(f"[single-collapse] MOTS from t = {hA['time'][0]:.1f}, "
          f"R_mots {hA['R_mots'][0]:.3f} -> {hA['R_mots'][-1]:.3f}, "
          f"M_MS {hA['M_MS_mots'][0]:.3f} -> {hA['M_MS_mots'][-1]:.3f}; "
          f"areal {ar[0, 1]:.3f} -> {ar[-1, 1]:.3f}")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_collapse.png")
    png = style.save(fig, out)
    print(f"[single-collapse] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
