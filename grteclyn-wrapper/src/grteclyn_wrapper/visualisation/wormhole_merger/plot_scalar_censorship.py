#!/usr/bin/env python3
r"""The horizon shuts the scalar channel off -- and nothing else does.

Two panels, three fates, one instrument: the ghost dipole's flux at the
extraction spheres, drawn as its ENVELOPE -- a running MAXIMUM of
$|F_\phi|$ over a 25-unit window, about one period of the dipole's own
oscillation on these records.  The raw flux changes sign every ~13 units and
dives to the log floor at each zero, which on a log axis is a thicket of
spikes hiding the one thing the figure is about: how the amplitude behaves.
(A running r.m.s. was tried first and is not enough -- over any window
shorter than a period it still carries the oscillation, and over a longer
one it smears the decay it is meant to show.  The running maximum rides the
successive peaks, which is exactly the envelope.)

(a) THE CENSORSHIP, on the head-on production chain's glued scalar record
(`04_binary_headon/csm/merge_headon_flip_d8_v1_L128_SERIES`, three legs on
one dt = 1 axis, seam mismatch 0 on the shared rows -- its README).  The
mouths are swallowed by the common MOTS at t = 18 (the chain's mots_spectral
replay); what scalar hair remains leaves as one $\ell=1$, $m=0$ pulse
sweeping outward -- the envelope crests later at each sphere (t = 34/39 at
R = 14/18), the causal ordering of a pulse crossing them -- and then the
source is gone.  The decay is exponential and fitted: log-linear fits over
t = 30-95 give e-fold times tau = 20/25/32 at R = 10/14/18 (dashed).  The
integrated post-horizon energies (t >= 18) are negative on all three
spheres, $E_\phi = -0.0294/-0.0525/-0.0600$: the hair leaves as negative
energy.  (The rise at $R=10$ before t = 26 is the two mouths' static hair
superposing and draining inward -- canonically ingoing, near zone, not
radiation -- which is why no pre-horizon integral is quoted anywhere.)

(b) THE CONTROL EXPERIMENT NATURE RAN FOR US: the same envelope, one sphere
per encounter, across the fates.  The d = 6 ORBITAL MERGER (its own glued
SERIES record, common MOTS from t = 13) sheds exactly like the head-on:
crest at t = 39 on R = 20, then an exponential fall, tau = 22 over t =
45-95, nineteen-fold down at R = 14 by t = 100.  The FLY-BY (no horizon, no
merger) shows its complete dipole arch instead: on this longer-lived
boosted-solve run the trusted record (u = t - R <= 67.6, the pack's stated
convention for it) contains the whole burst at R = 30 -- crest at t = 60,
subsiding as the arch passes -- but the mouths leave the encounter still
carrying their charges, so there is no shedding clock, only a passing
pulse; its late inner-sphere climb is the inflating mouths' near field
(plot_scalar_channel's docstring) and is not drawn here.  The LONE THROAT
enters twice.  CORRECTED 2026-09-23: both scalar re-runs lack their
quadrupole seed (t = 0 constraint norms bit-identical to the controls; the
binary they ran on ignores wormhole_seed_l2_amplitude).  SINGLE
(`single_pureq_q1e2_ml4_scalar_t100`) is therefore the UNKICKED level-4
throat, which inflates on its own truncation seed -- horizonless by scan and
flow finder -- and whose monopole grows quasi-exponentially (reproduced by
the L = 128 twin through t ~ 80, so not the boundary); counted to t ~ 80
only.  KICKED (`single_eps_p1e2_q1e2_ml4_scalar_t100`) is the spherical
eps = +1e-2 kick at level 4: it collapses on schedule (permanent MOTS from
t = 11, R 3.88 -> 2.45) and its envelope decays 30-100x across the spheres
by t = 80.  The contrast is also a collapse-versus-inflation contrast, and
the article says so.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_scalar_censorship

Reads ``scalar_modes.dat`` from, all under ``campaign/``:
``04_binary_headon/csm/merge_headon_flip_d8_v1_L128_SERIES/``,
``05_binary_spiral/merger_d6/spiral_d6_p010_L128_SERIES/``,
``06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm/``, and
``01_single_throat/seed/single_pureq_q1e2_ml4_scalar_t100/`` (+ the kicked
twin).  Writes ``figures/08_waves/scalar_censorship``.

STYLE: full-width pair (7.05 x 3.35), style.prd, no titles, no boxed key.
MONOCHROME THROUGHOUT (2026-09-23, on the user's word -- the scenario
colours of the first revision read as a rainbow): (a)'s three spheres are an
ink ramp, dark = inner, and (b) carries identity in GREY LEVEL + LINE STYLE
-- fly-by ink solid, merger ink dashed, lone throat muted (collapsed solid,
inflated dotted), the head-on its (a) outer-sphere grey -- with the top key
naming every curve.  The MOTS rule is the lighter grey (CONTEXT).
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "08_waves"
HEADON = "04_binary_headon/csm/merge_headon_flip_d8_v1_L128_SERIES"
MERGER = "05_binary_spiral/merger_d6/spiral_d6_p010_L128_SERIES"
FLYBY = "06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm"
SINGLE = "01_single_throat/seed/single_pureq_q1e2_ml4_scalar_t100"
KICKED = "01_single_throat/seed/single_eps_p1e2_q1e2_ml4_scalar_t100"

T_MOTS = 18.0        # head-on chain: common MOTS, the mots_spectral replay
T_MOTS_MERGER = 13.0  # d6 merger chain: common MOTS, its own mots_spectral
FIT = (30.0, 95.0)   # head-on decay-fit window (the article's rows)
FIT_MERGER = (45.0, 95.0)  # merger: past its t = 39 crest on R = 20
WINDOW = 25.0      # running-max window: about one period of the dipole
SMOOTH = 5.0       # Gaussian on log amplitude, to round the staircase
FLYBY_U_GATE = 67.6  # fly-by drawn to t - R <= 67.6 (trust_windows.tsv)
RAMP = {10: "#1a1a18", 14: "#54524c", 18: "#8f8b81"}   # dark = inner


def _flux(path: pathlib.Path, radius: int) -> tuple[np.ndarray, np.ndarray]:
    head = open(path).readline().lstrip("#").split()
    d = np.loadtxt(path)
    return d[:, 0], d[:, head.index(f"R{radius}_scalar_flux_kin")]


def _envelope(t: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Peak envelope of |F|: running maximum over one period, then smoothed.

    The running maximum rides the successive peaks, which is the envelope; on
    a coarse cadence it comes out as a staircase, so it is rounded by a
    Gaussian in LOG amplitude -- log, because the quantity decays
    exponentially and the smoothing must not bias the decay rate that is
    fitted from it.  A running integral was tried instead and rejected: a
    cumulative curve rises for every source, so the eye cannot separate one
    that has switched off from one that has not.
    """
    dt = float(t[1] - t[0])
    a = np.abs(k)
    m = np.array([a[(t >= ti - WINDOW / 2) & (t <= ti + WINDOW / 2)].max()
                  for ti in t])
    return np.exp(gaussian_filter1d(np.log(np.maximum(m, 1e-30)),
                                    SMOOTH / dt, mode="nearest"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    camp = pathlib.Path(args.pack_root).expanduser() / "campaign"

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.05, 3.35))
    # Fixed margins, no layout engine: the key needs a band of its own, and
    # constrained_layout does not reserve one for a FIGURE legend.
    fig.subplots_adjust(left=0.088, right=0.988, top=0.78, bottom=0.135,
                        wspace=0.17)

    # ---- (a) one horizon, three spheres ------------------------------------
    for R in (10, 14, 18):
        t, k = _flux(camp / HEADON / "scalar_modes.dat", R)
        e = _envelope(t, k)
        axA.semilogy(t, e, color=RAMP[R], lw=1.2, zorder=3,
                     label=f"head-on, $R={R}$")
        fit = (t >= FIT[0]) & (t <= FIT[1])
        c = np.polyfit(t[fit], np.log(e[fit]), 1)
        axA.semilogy(t[fit], np.exp(np.polyval(c, t[fit])), color=RAMP[R],
                     lw=0.8, ls=(0, (3, 2.2)), zorder=4)
        s = t >= T_MOTS
        print(f"[censorship] head-on R={R}: crest t={t[np.argmax(e)]:.0f}, "
              f"envelope {e.max():.2e} -> {np.interp(95.0, t, e):.2e} at t=95, "
              f"tau = {-1 / c[0]:.1f}, E_post(t>={T_MOTS:g}) = "
              f"{-np.trapezoid(k[s], t[s]):+.4e}")
    axA.axvline(T_MOTS, color=style.CONTEXT, lw=0.8, ls=(0, (1, 2)), zorder=1)

    # NOTHING is written inside either frame (every note tried ended against
    # a spine); the key above carries the identities and the caption the
    # numbers.
    axA.set_xlim(0, 100)
    axA.set_ylim(1.0e-4, 2.2e-2)
    axA.set_xlabel(r"$t$")
    axA.set_ylabel(r"$|F_\phi|$ envelope")
    axA.text(0.0, 1.03, "(a)", transform=axA.transAxes, ha="left",
             va="bottom", fontsize=9, color=style.INK)

    # ---- (b) the fates, one sphere each ------------------------------------
    # The fly-by to its retarded gate, t - R <= 67.6 (t = 97.6 on R = 30): on
    # the boosted-solve run that window holds the complete dipole arch, and
    # the envelope is built from the gated flux.
    t, k = _flux(camp / FLYBY / "scalar_modes.dat", 30)
    gate = t <= FLYBY_U_GATE + 30 + 1e-9
    t, k = t[gate], k[gate]
    ef = _envelope(t, k)
    axB.semilogy(t, ef, color=style.INK, lw=1.35, zorder=3,
                 label=r"fly-by, $R=30$")
    print(f"[censorship] fly-by R=30 to t={t[-1]:.1f} (t-R <= {FLYBY_U_GATE:g}): "
          f"crest {ef.max():.2e} at t={t[np.argmax(ef)]:.0f} -> {ef[-1]:.2e} at "
          f"the gate (x{ef.max() / ef[-1]:.1f} down: the arch passes, no clock)")

    # The merger: its chain's glued record, the one orbital encounter with a
    # horizon.  It sheds like the head-on.
    tm, km = _flux(camp / MERGER / "scalar_modes.dat", 20)
    em = _envelope(tm, km)
    axB.semilogy(tm, em, color=style.INK, lw=1.1, ls=(0, (4, 2.2)), zorder=3,
                 label=r"merger, $R=20$")
    fitm = (tm >= FIT_MERGER[0]) & (tm <= FIT_MERGER[1])
    cm = np.polyfit(tm[fitm], np.log(em[fitm]), 1)
    axB.semilogy(tm[fitm], np.exp(np.polyval(cm, tm[fitm])), color=style.INK,
                 lw=0.8, ls=(0, (1.2, 1.8)), zorder=4)
    t14, k14 = _flux(camp / MERGER / "scalar_modes.dat", 14)
    e14 = _envelope(t14, k14)
    print(f"[censorship] merger R=20: crest {em.max():.2e} at "
          f"t={tm[np.argmax(em)]:.0f}, tau = {-1 / cm[0]:.1f} over "
          f"t={FIT_MERGER[0]:g}-{FIT_MERGER[1]:g}; R=14 down "
          f"x{e14.max() / e14[-1]:.1f} by t={t14[-1]:.0f}")

    # The lone throat enters twice (docstring: neither re-run carries its
    # quadrupole seed).  KICKED collapses behind a MOTS from t = 11: solid.
    # SINGLE inflates and GROWS; dashed at half weight, counted to t ~ 80.
    tk, kk = _flux(camp / KICKED / "scalar_modes.dat", 18)
    ek = _envelope(tk, kk)
    axB.semilogy(tk, ek, color=style.MUTED, lw=1.2, zorder=3,
                 label="lone throat, collapsed")
    tl, kl = _flux(camp / SINGLE / "scalar_modes.dat", 18)
    el = _envelope(tl, kl)
    axB.semilogy(tl, el, color=style.MUTED, lw=0.9,
                 ls=(0, (1.2, 1.6)), alpha=0.75, zorder=2,
                 label="lone throat, inflated")
    g = (tl >= 50.0) & (tl <= 95.0)
    c = np.polyfit(tl[g], np.log(el[g]), 1)
    print(f"[censorship] lone throat: collapsed arm peak {ek.max():.2e} -> "
          f"{np.interp(95.0, tk, ek):.2e} at t=95 (x{ek.max()/np.interp(95.0, tk, ek):.0f} down); "
          f"inflated grows e-fold {1 / c[0]:.1f}, max {el.max():.2e}")

    # The head-on enters (b) on its OUTER sphere, so it wears the OUTER
    # sphere's colour: the top legend serves both panels.
    t, k = _flux(camp / HEADON / "scalar_modes.dat", 18)
    axB.semilogy(t, _envelope(t, k), color=RAMP[18], lw=1.6, zorder=4)

    axB.set_xlim(0, 100)
    axB.set_ylim(1.0e-4, 4.5e-1)
    axB.set_xlabel(r"$t$")
    axB.text(0.0, 1.03, "(b)", transform=axB.transAxes, ha="left",
             va="bottom", fontsize=9, color=style.INK)

    # ONE key for the page, above both frames (plot_psi4_ligo's idiom): the
    # curves of (a) interleave twice and (b)'s fates cross, so no in-frame
    # naming is unambiguous anywhere on this page.
    hA, lA = axA.get_legend_handles_labels()
    hB, lB = axB.get_legend_handles_labels()
    rules = [Line2D([], [], color=style.CONTEXT, lw=0.8, ls=(0, (1, 2)),
                    label=r"common MOTS, $t=18$")]
    fig.legend(hA + hB + rules, lA + lB + [h.get_label() for h in rules],
               loc="upper center", bbox_to_anchor=(0.5, 1.0), ncols=4,
               fontsize=6.5, frameon=False, handlelength=2.4,
               columnspacing=1.6, labelspacing=0.45, borderaxespad=0.35)

    style.label_audit(fig)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "scalar_censorship.png")
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[label audit] {'clean' if not hits else hits}")
    print(f"[censorship] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
