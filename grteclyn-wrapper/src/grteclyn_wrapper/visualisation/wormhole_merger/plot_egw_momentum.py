#!/usr/bin/env python3
r"""E_GW against the initial momentum: the turnover at the capture boundary.

OFF THE PAPER since 2026-10-05 ("not representative ... describe
it in text, wipe the figure"): three points, one a floor, read better as the
sentence sec:gw:flyby already carries.  Kept as a check of those numbers.

One panel, three measured points (p = 0.25 / 0.45 / 0.60, the d = 12 boosted
arms), each the band energy of the (2,2) burst through R = 20 in units of its
own pair's solved mass -- the ledger rows clmEgwEnergyTwoFive / FortyFive /
Sixty, recomputed here from the packed streams with the same conventions:

  p = 0.25 / 0.45  gated at the R = 20 trough, where the decaying arch meets
                   the mouths' growing contamination (t = 83.68 / 94.17);
  p = 0.60         the glued SERIES record cut at its trust window t = 80,
                   12 units past its R = 20 peak, so the point is a FLOOR
                   (open marker, upward arrow);
  p = 0.90         no point: both legs end before the burst crosses R = 20.

The R = 28 reading rides each measured point as a second, smaller marker --
the near-zone spread the article quotes (for p = 0.60, R = 28 peaks 2.6 units
before the cut, so no second marker).  The capture boundary (scatter below,
plunge above; Sec. VII A) lies in (0.45, 0.60): shaded.  The outcome: the
pair radiates hardest at the boundary, where the pass is deepest and slowest.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_egw_momentum
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    _compute_radiated_energy,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, boosted_adm_mass, figure_dir,
)

GROUP = "08_waves"

# (p, stream under campaign/, M = the pair's ADM mass -- the boosted solve's
#  face estimate plus each throat's kinetic energy (run_tree.boosted_adm_mass),
#  {R: t_gate}, floor?)  -- the ledger rows' own inputs.
POINTS = [
    (0.25, "06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm/Weyl4_mode_22.dat",
     boosted_adm_mass("merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm"),
     {20.0: 83.68, 28.0: 98.99}, False),
    (0.45, "06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm/Weyl4_mode_22.dat",
     boosted_adm_mass("merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm"),
     {20.0: 94.17, 28.0: 98.99}, False),
    (0.60, "06_binary_flyby/merge_orbit_flip_d12_p060_L128_SERIES/Weyl4_mode_22.dat",
     boosted_adm_mass("merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm"),
     {20.0: 80.00}, True),
]
BOUNDARY = (0.45, 0.60)   # the capture boundary's bracket (Sec. VII A)


def band_energy(path: pathlib.Path, R: float, M: float, t_max: float) -> float:
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_psi4_ligo, psi4_math
    t, ser = streams.load_mode(path)
    y = ser[R]
    keep = t <= t_max + 1e-9
    u, w = (t[keep] - R) / M, y[keep] * M
    dt = float((u[-1] - u[0]) / (u.size - 1))
    f, S = psi4_math._burst_psd(w, 1.0 / dt)
    f_pk = float(f[1:][np.argmax(psi4_math._smooth_psd(
        S, plot_psi4_ligo._smooth_window(S.size), 5)[1:])])
    return float(_compute_radiated_energy(u, w, m=2, f_peak=f_pk))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.4), constrained_layout=True)
    ax.axvspan(*BOUNDARY, color=style.GOLD, alpha=0.14, lw=0, zorder=0)

    pack = pathlib.Path(args.pack_root)
    for p, rel, M, gates, floor in POINTS:
        path = pack / "campaign" / rel
        E20 = band_energy(path, 20.0, M, gates[20.0])
        print(f"  p={p}: E/M(R=20) = {E20:.4e}", end="")
        if 28.0 in gates:
            E28 = band_energy(path, 28.0, M, gates[28.0])
            print(f"  (R=28: {E28:.4e})", end="")
            ax.plot([p], [E28], marker="o", ms=3.0, mfc="none", mec=style.MUTED,
                    mew=0.9, ls="none", zorder=3)
        print("  floor" if floor else "")
        if floor:
            ax.plot([p], [E20], marker="o", ms=5.0, mfc="white", mec=style.INK,
                    mew=1.1, ls="none", zorder=4)
            ax.annotate("", xy=(p, E20 * 1.7), xytext=(p, E20 * 1.12),
                        arrowprops=dict(arrowstyle="-|>", color=style.INK, lw=0.9))
        else:
            ax.plot([p], [E20], marker="o", ms=5.0, color=style.INK, ls="none",
                    zorder=4)

    ax.set_yscale("log")
    ax.set_xlim(0.15, 0.72)
    ax.set_ylim(1.2e-2, 1.6e-1)
    ax.set_xlabel(r"$p$ (per one-body mass)")
    ax.set_ylabel(r"$E_{\rm GW}/M$")
    # legend above the frame, per the house grammar
    ax.text(0.0, 1.04, r"filled: $R=20$   open small: $R=28$   "
            r"open + arrow: floor (trust cut)", transform=ax.transAxes,
            fontsize=6.5, color=style.MUTED, ha="left", va="bottom")
    ax.text(0.5 * sum(BOUNDARY), 1.3e-2 * 1.15, "capture\nboundary",
            fontsize=6.5, color=style.GOLD, ha="center", va="bottom")
    style.label_audit(fig)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "egw_momentum.png")
    png = style.save(fig, out)
    print(f"[egw momentum] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
