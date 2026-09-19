#!/usr/bin/env python3
r"""One kicked throat's inflation, on one page: gauge, origin, shells, shells' fate.

The mirror of ``plot_single_collapse.py``, drawn from the expansion-branch
instrumented arm (`single_eps_m1e2_ml4_t100`, 2026-09-19): the same throat,
the same level 4, the same instruments, and the OPPOSITE sign of the radial
kick, eps = -0.01.  Where +0.01 collapses to a MOTS, this arm inflates: the
mouth's areal radius grows 3.82 -> 11.39 (x3.0) by t = 100 with no horizon of
any kind around the throat, and the certificate is the anti-trapped shell
(theta_+ > 0 AND theta_- > 0, the white-hole-like signature of inflation, the
MOTS's mirror), present at every scan centre over t = 1--36 (t = 1--35 on the mouth probes).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_inflation

Reads, all under ``campaign/01_single_throat/``:
``seed/single_eps_m1e2_ml4_t100/`` -- ``areal_radius.dat``,
``horizon_scan.dat`` (the oriented scan; the anti-trapped counter),
``collapse_diagnostics.dat``, ``core_radial_profile.dat``,
``constraint_norms.dat`` -- and ``hold/single_hold_ml4_t100/areal_radius.dat``,
the UNKICKED level-4 twin whose own truncation seed inflates: the kicked arm
leaves it by 10 % at t = 25.0, the same clock on which the +0.01 twin at this
level forms its horizon.  Symmetric departure, opposite fates.

Writes ``figures/01_single_throat/single_throat_inflation``.

WHAT THE LATE MARGINAL-SURFACE ROWS ARE NOT.  From t = 85 the centre scan
reports flickering theta_+ = 0 rows at R ~ 60.6.  That surface is NOT a
horizon and NOT drawn here: the radial profile shows the R ~ 60--100 areal
peak exists from t = 0 at the innermost shell -- it is the grid's rendering
of the far universe's compactified infinity -- and the inflation pushes its
image outward in coordinate radius (r = 0.016 -> 2.9 over the run) until it
crosses the scan window.  Panel (e) shows exactly that march, in chi.

STYLE (the PRD review grammar of the collapse page): a wide context strip
over a 2 x 3 grid, style.prd frame, no titles, letter tags above the frames,
no boxed key, every series named in place.  Monochrome ink plus the one
accent: DEEP_GREEN is the horizon instrument -- here the anti-trapped
certificate -- and nothing else.  Ordered time families (the radial
snapshots) are a grey ramp, light = early.  min chi is labelled as what it
is, the ORIGIN monitor (the far universe's compactified infinity), not the
throat.
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
ARM = "seed/single_eps_m1e2_ml4_t100"
TWIN = "hold/single_hold_ml4_t100"
SNAPS = (0.0, 20.0, 40.0, 60.0, 80.0, 100.0)   # grey ramp, light = early
T_DEPART = 25.0   # leaves the unkicked twin by 10 % -- the +0.01 twin's horizon clock


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
    root = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP
    arm = root / ARM

    ar = np.loadtxt(arm / "areal_radius.dat")
    tw = np.loadtxt(root / TWIN / "areal_radius.dat")
    cd = np.loadtxt(arm / "collapse_diagnostics.dat")
    cn = np.loadtxt(arm / "constraint_norms.dat")
    tp, blocks = _profile(arm / "core_radial_profile.dat")
    h = np.genfromtxt(arm / "horizon_scan.dat", dtype=None, encoding=None, names=True)
    hA = h[(h["centre"] == "A") & (h["n_anti_trapped"] > 0)]
    t_anti = (hA["time"][0], hA["time"][-1])

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 5.0), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, height_ratios=[1.15, 1.0, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1 + i // 3, i % 3]) for i in range(6)]
    tags = "abcdefg"

    # ---- context strip: the mouth, its unkicked twin, and the certificate --
    axT.plot(ar[:, 0], ar[:, 1], color=style.INK, linewidth=1.4, zorder=3)
    axT.plot(tw[:, 0], tw[:, 1], color=style.CONTEXT, linewidth=1.1, zorder=2)
    m = ar[:, 0] <= t_anti[1]
    axT.plot(ar[m, 0], ar[m, 1], color=style.DEEP_GREEN, linewidth=0.0,
             marker="o", markersize=2.0, zorder=4)
    axT.axvline(T_DEPART, color=style.FAINT, linewidth=0.7, zorder=1)
    # Every label here sits in a gap MEASURED off the two curves, not guessed:
    # the kicked mouth runs 3.81 (t = 0) -> 4.95 (30) -> 9.24 (55) -> 11.39
    # (100) and the twin is flat at 3.89 until t = 60.  So the certificate
    # goes above the early flat stretch (curve <= 4.9 under its whole width),
    # the twin names itself from BELOW its own flat line, and the kicked
    # arm's label tucks under its plateau.
    axT.text(2.0, 6.4, "anti-trapped shell present, $t=1$--$35$", fontsize=7,
             color=style.DEEP_GREEN)
    axT.text(97.5, 10.7, r"$\varepsilon=-0.01$", fontsize=7.5,
             color=style.INK, ha="right", va="top")
    # ONE line, not two: the band between the twin's flat 3.89 and the frame
    # floor is 1.2 units and a two-line note at 7 pt is 0.9 of them, so the
    # second line came out sitting on the bottom spine.
    axT.text(55.0, 3.60, "unkicked twin (truncation seed)", fontsize=7,
             color=style.CONTEXT, ha="right", va="top")
    axT.text(T_DEPART + 1.2, 10.9,
             "leaves the twin by 10 % at $t=25$,\nthe $+0.01$ twin's horizon clock",
             fontsize=7, color=style.MUTED, va="top")
    axT.set_xlim(0, 100)
    axT.set_ylim(2.7, 12.0)
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
        ax.axvline(T_DEPART, color=style.FAINT, linewidth=0.7, zorder=1)
        if logy:
            ax.set_yscale("log")
        ax.set_xlim(0, 100)
        ax.set_ylabel(lab)

    # ---- (e)/(f) the shells: chi and lapse profiles, light = early --------
    # chi, not |K|, leads here: the inflation's signature is the compactified
    # inner sheet's chi-trough marching outward through the shells while the
    # throat's own chi rises -- |K| stays below 0.05 the whole run and shows
    # nothing.
    ramp = [style.FAINT, "#8f8b81", "#6f6c64", "#54524c", "#37352f", style.INK]
    for ax, key, lab, logy in ((axs[3], "chi_min", r"$\chi$ per shell", True),
                               (axs[4], "lapse_min", r"$\alpha$ per shell", False)):
        r, block = blocks[key]
        for c, ts in zip(ramp, SNAPS):
            i = int(np.argmin(np.abs(tp - ts)))
            ax.plot(r, block[i], color=c, linewidth=1.0, zorder=3)
        if logy:
            ax.set_yscale("log")
        ax.set_xlim(0, 4.0)
        ax.set_ylabel(lab)
        ax.set_xlabel(r"$r$")
    axs[3].text(0.96, 0.28, rf"$t={SNAPS[0]:g}$--${SNAPS[-1]:g}$",
                transform=axs[3].transAxes, ha="right", va="top", fontsize=7,
                color=style.MUTED)
    axs[3].text(0.96, 0.15, "light = early", transform=axs[3].transAxes,
                ha="right", va="top", fontsize=7, color=style.MUTED)

    # ---- (g) the constraints ----------------------------------------------
    axs[5].plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    axs[5].plot(cn[:, 0], cn[:, 2], color=style.MUTED, linewidth=1.1,
                linestyle=(0, (4, 2.5)), zorder=3)
    axs[5].axvline(T_DEPART, color=style.FAINT, linewidth=0.7, zorder=1)
    axs[5].set_yscale("log")
    axs[5].set_xlim(0, 100)
    axs[5].set_ylabel(r"$L_2$ norms")
    # In DATA coordinates, each beside its own curve: in axes fractions both
    # labels floated in the empty upper middle of the frame, naming nothing.
    # H passes 2.4e-2 at t = 75 and M 2.0e-3, two decades apart, so each sits
    # just above its own line at that t.
    axs[5].text(75.0, 3.7e-2, r"$\mathcal{H}$", fontsize=7.5,
                color=style.INK, ha="center", va="bottom")
    axs[5].text(75.0, 3.1e-3, r"$\mathcal{M}$", fontsize=7.5,
                color=style.MUTED, ha="center", va="bottom")

    # Letter tags ABOVE the frames (the spiral page's rule).
    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({tags[k + 1]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
        if k < 3:
            ax.set_xlabel(r"$t$")
    axs[5].set_xlabel(r"$t$")

    print(f"[single-inflation] anti-trapped over t = {t_anti[0]:.1f}--{t_anti[1]:.1f}; "
          f"areal {ar[0, 1]:.3f} -> {ar[-1, 1]:.3f} (x{ar[-1, 1] / ar[0, 1]:.2f}); "
          f"twin {tw[0, 1]:.3f} -> {tw[-1, 1]:.3f} (x{tw[-1, 1] / tw[0, 1]:.2f}); "
          f"end state min alpha {cd[-1, 1]:.3f}, min chi {cd[-1, 2]:.2e}, "
          f"max |K| {cd[-1, 3]:.2e}")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation.png")
    png = style.save(fig, out)
    print(f"[single-inflation] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
