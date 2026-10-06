#!/usr/bin/env python3
r"""The remnant horizon that shrinks, bottoms out, and grows back.

The single-throat collapse remnants' horizon history across the three arms
with a record past the floor (article Sec. IV D): the eps = +0.01 radial kick
at level 3, `single_eps_p1e2_t100`, and the same kick dressed with a quadrupole
at level 4, `single_eps_p1e2_q5e3_ml4_t100` / `..._q5e2_ml4_t100` (no arm
carries matter damping: core_matter_damping = 0 in all three).  Each swallows
its own phantom support (areal radius and Misner-Sharp mass falling), bottoms
out near t = 43-47, and the scans then regrow +9-11 % in radius and +10-12 % in
mass.  (The pure-quadrupole
arm was drawn as context in an earlier revision and removed on the user's
word 2026-09-23: its floor arrives only at t = 92, so it decides nothing here.)

WHAT THE REGROWTH IS (2026-09-24, reviewer feedback C): not physics.  In
spherical symmetry a massless phantom can only shrink a MOTS -- on it
d_v m = 4 pi R^2 e^f (d_v phi)^2 d_u R <= 0, d_u m = 0, and the tube is timelike
or null, so R = 2m falls on any slicing (checked symbolically in
scripts/analysis/merger_feedback/c_spherical_horizon_law.py).  The growth is the
same in purely spherical arms (a level-4 arm whose binary never read eps_2
lies on the eps_2 = 0.005 curve), no device is active, and it tracks the
Hamiltonian-constraint violation near the horizon, a radial double layer whose
positive lobe reaches the MOTS at the floor time (c_checkpoint_hamiltonian.py,
c_horizon_first_law.py on the L = 128 level-4 twin).  Fits to the regrowth
(c_regrowth_fits.py: tanh, t0 ~ 68, w ~ 17-19) are deliberately NOT drawn:
they would give an artefact a law.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_horizon_regrowth

Reads each arm's ``horizon_scan.dat`` (oriented scan, centre A rows with a
MOTS: the throat-centred fine scan; the coarse common centre C reads
M_MS/(R/2) up to 1.15 at the floor and is not used, 2026-09-23) under ``campaign/01_single_throat/seed/``.  Writes
``figures/01_single_throat/single_horizon_regrowth``.

THE NUMERICAL STRETCH IS SHADED (2026-09-25, the user: "the transition to
numerical should be shown -- the part where numerical errors dominate and we
can't cite it").  From the first floor on (t = 43) the panels carry a grey
band named as numerical, and each curve is drawn faint after its own floor:
what is left at full weight is the shrink, the one thing the figure claims.
The legend names the radial kick on EVERY arm ("eps = +1e-2 with eps_2 =
0.005"): written "+ eps_2 = 0.005" it was read as a pure-quadrupole arm, which
the text says does not regrow (the user's read of the PDF, same date).

STYLE: style.prd, no titles, letter tags above the frames, one shared top
figure legend.  INK is the level-3 kick (the headline numbers of Sec. IV D),
MUTED the two quadrupole-dressed level-4 twins; the floor of each curve carries a small marker.
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
ARMS = (
    ("seed/single_eps_p1e2_t100", "level 3", style.INK, "-", 1.3),
    ("seed/single_eps_p1e2_q5e3_ml4_t100", "level 4, $\\varepsilon_2=0.005$", style.MUTED, (0, (4, 2.5)), 1.1),
    ("seed/single_eps_p1e2_q5e2_ml4_t100", "level 4, $\\varepsilon_2=0.05$", style.MUTED, (0, (1.2, 1.6)), 1.1),
)

def _mots_history(pack: pathlib.Path, arm: str):
    rows = []
    for ln in open(pack / GROUP / arm / "horizon_scan.dat"):
        if ln.startswith("#"):
            continue
        f = ln.split()
        if f[1] != "A" or int(f[9]) < 1:
            continue
        rows.append((float(f[0]), float(f[11]), float(f[12])))
    a = np.array(rows)
    return a[np.argsort(a[:, 0])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root) if args.pack_root else PACK_ROOT
    pack = pack / "campaign" if (pack / "campaign" / GROUP).is_dir() else pack

    style.prd()
    fig, axs = plt.subplots(1, 2, figsize=(7.05, 2.75), constrained_layout=True)

    hist = [_mots_history(pack, arm) for arm, *_ in ARMS]

    t_num = min(float(a[int(np.nanargmin(a[:, 1])), 0]) for a in hist)
    for ax, col in ((axs[0], 1), (axs[1], 2)):
        # The numerical stretch: from the first floor to the end of the record.
        ax.axvspan(t_num, 102, color=style.GRID, lw=0, zorder=0)
        for a, (arm, name, colr, ls, lw) in zip(hist, ARMS):
            i = int(np.nanargmin(a[:, 1]))          # the RADIUS floor times both panels
            ax.plot(a[:i + 1, 0], a[:i + 1, col], color=colr, linestyle=ls,
                    linewidth=lw, zorder=3)
            ax.plot(a[i:, 0], a[i:, col], color=colr, linestyle=ls,
                    linewidth=lw, alpha=0.4, zorder=3)
            ax.plot(a[i, 0], a[i, col], marker="v", markersize=3.6,
                    color=colr, zorder=4, linestyle="none")
        ax.set_xlim(8, 102)
        ax.set_xlabel(r"$t$")

    # ---- (a) areal radius ---------------------------------------------------
    def _gain(col):
        g = [a[-1, col] / a[int(np.nanargmin(a[:, 1])), col] - 1 for a in hist]
        return 100 * min(g), 100 * max(g)

    axs[0].set_ylabel(r"$R_{\rm MOTS}$")
    lo, hi = _gain(1)
    top = max(a[-1, 1] for a in hist)
    axs[0].text(100.5, top + 0.06, f"regrowth +{lo:.0f}–{hi:.0f}%", ha="right",
                va="bottom", fontsize=7, color=style.MUTED)
    axs[0].set_ylim(2.15, 4.0)

    # ---- (b) Misner-Sharp mass ---------------------------------------------
    axs[1].set_ylabel(r"$M_{\rm MS}$")
    lo, hi = _gain(2)
    topm = max(a[-1, 2] for a in hist)
    axs[1].text(100.5, topm + 0.03, f"regrowth +{lo:.0f}–{hi:.0f}%", ha="right",
                va="bottom", fontsize=7, color=style.MUTED)
    axs[1].set_ylim(1.08, 2.0)
    # Name the band where nothing is drawn: its upper half, left of the labels.
    for ax in axs:
        ax.text(0.5 * (t_num + 102), 0.93, "numerical:\nnot a measurement",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=7, color=style.MUTED, linespacing=1.15)

    # One shared legend on top (the censorship figure's rule).
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], color=style.INK, linewidth=1.3,
               label="$\\varepsilon=+10^{-2}$ alone, level 3"),
        Line2D([], [], color=style.MUTED, linewidth=1.1,
               linestyle=(0, (4, 2.5)),
               label="$\\varepsilon=+10^{-2}$ with $\\varepsilon_2=0.005$, level 4"),
        Line2D([], [], color=style.MUTED, linewidth=1.1,
               linestyle=(0, (1.2, 1.6)),
               label="$\\varepsilon=+10^{-2}$ with $\\varepsilon_2=0.05$, level 4"),
        Line2D([], [], color=style.INK, marker="v", markersize=3.6,
               linestyle="none", label="radius floor"),
    ]
    fig.legend(handles=handles, loc="outside upper center", ncol=5,
               frameon=False, fontsize=6.8, handlelength=1.9,
               columnspacing=1.1, handletextpad=0.5)

    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({'ab'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    for a, (arm, *_ ) in zip(hist, ARMS):
        i = int(np.nanargmin(a[:, 1]))
        print(f"[regrowth] {arm}: floor R={a[i,1]:.3f} at t={a[i,0]:.0f}, "
              f"end R={a[-1,1]:.3f} (+{(a[-1,1]/a[i,1]-1)*100:.1f}%), "
              f"M {a[i,2]:.3f} -> {a[-1,2]:.3f} (+{(a[-1,2]/a[i,2]-1)*100:.1f}%)")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_horizon_regrowth.png")
    style.label_audit(fig)      # prints every text box a drawn line crosses
    png = style.save(fig, out)
    print(f"[regrowth] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
