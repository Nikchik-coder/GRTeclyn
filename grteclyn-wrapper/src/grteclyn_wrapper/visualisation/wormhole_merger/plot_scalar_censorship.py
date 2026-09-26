#!/usr/bin/env python3
r"""The horizon shuts the scalar channel off -- and nothing else does.

Two panels, three fates, one instrument: the ghost dipole's flux at the
extraction spheres, drawn as its ENVELOPE -- a running MAXIMUM of
$|F_\phi|$ over a 25-unit window, one full period of the dipole's own
oscillation on these records.  The raw flux changes sign every ~20 units and
dives to the log floor at each zero, which on a log axis is a thicket of
spikes hiding the one thing the figure is about: how the amplitude behaves.
(A running r.m.s. was tried first and is not enough -- over any window
shorter than a period it still carries the oscillation, and over a longer
one it smears the decay it is meant to show.  The running maximum rides the
successive peaks, which is exactly the envelope.)

(a) THE CENSORSHIP, on the seamless head-on arm
(`merge_headon_flip_d8_v1_lvl5from0_scalar_t100`, 2026-09-21, level 5 from
t = 0, no fill, no seam).  The mouths are swallowed by the common MOTS at
t = 21.5; what scalar hair remains leaves as one $\ell=1$, $m=0$ burst
sweeping outward -- the envelope crests later at each sphere, the causal
ordering of a pulse crossing them -- and then the source is gone.  The decay
is exponential and fitted: log-linear fits over t = 30-95 give e-fold times
tau = 19/23/28 at R = 10/14/18 (dashed).  THAT IS THE HORIZON'S OWN CLOCK:
the remnant's Misner-Sharp mass settles onto its asymptote with
tau = 19.4 +- 0.8 (Fig. headon_collapse_diagnostics (b)).  The hair is shed,
the source goes quiet, and the mass stops changing, all on one timescale.  The integrated post-horizon energies are negative on all
three spheres, $E_\phi = -0.056/-0.071/-0.075$: the hair leaves as negative
energy.  (The pre-horizon rise at $R=10$ is the two mouths' static hair
superposing -- canonically ingoing, near zone, not radiation -- which is why
no full-record integral is quoted anywhere.)

(b) THE CONTROL EXPERIMENT NATURE RAN FOR US: the same envelope, one outer
sphere per encounter, across the four fates.  The head-on, the only one
with a horizon, decays.  The fly-by (no horizon, no merger) GROWS to the end
of its trusted record.  SINCE 2026-09-26 (referee) that record stops at its
trust window: the fly-by's constraint norms grow by orders of magnitude as its
mouths inflate, so nothing past t = 70 at the source is used, nor anything a
sphere records past the matching retarded time t - R = 50 (the wave gallery's
fly-by gate) -- t = 80 on R = 30, where it had been drawn to t = 100.  Its
envelope is built from the GATED flux: the running maximum centred on t reads
the flux up to t + WINDOW/2, so enveloping the whole record and clipping the
drawing would still show t = 92.5 at the cut (2.7e-2 there against |F| =
9.4e-3 at t = 80).  At the cut the flux is still growing -- one sign since
t ~ 40, rising at every sample from its t ~ 64 minimum (x3.2 by t = 80) --
but the drawn envelope levels off over its last half-window, as every rising
record's does at its end (the window loses its leading half).  The p = 0.12
spiral -- whose common MOTS the shape-free
finder recovers from t = 55 -- is still climbing when its grid dies at the
t = 59.9 wall, its horizon too young to shed on a ~20 clock.  The LONE
THROAT enters twice.  CORRECTED 2026-09-23: both scalar re-runs lack their
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

THE SPIRAL'S LATE STRETCH IS DRAWN, BUT MUST NOT BE READ AS PHYSICS.  Past
its wall the curve is the freeze arm (`..._lvl5_t100_freeze_r05700`), whose
exterior is certified against the no-fill arm -- the two agree to 0.1 % on
this very flux over their t = 58-59 overlap, and the two freeze twins to
0.01 % -- but whose SOURCE REGION is frozen by construction.  A frozen core
cannot be asked how its radiation decays.  So the claim stops at the wall:
through the end of its uncensored record the spiral's dipole is still
rising, and what the freeze arm adds is only that the exterior does not
collapse afterwards.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_scalar_censorship

Reads ``scalar_modes.dat`` from, all under ``campaign/``:
``04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100/``,
``05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl5from0_t100/`` and
its ``..._lvl5_t100_freeze_r05700/``,
``06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100/``, and
``01_single_throat/seed/single_pureq_q1e2_ml4_scalar_t100/``.  Writes
``figures/08_waves/scalar_censorship``.

STYLE: full-width pair (7.05 x 3.35), style.prd, no titles, no boxed key.
MONOCHROME THROUGHOUT (2026-09-23, on the user's word -- the scenario
colours of the first revision read as a rainbow): (a)'s three spheres are an
ink ramp, dark = inner, and (b) carries identity in GREY LEVEL + LINE STYLE
-- fly-by ink solid, spiral ink dashed, lone throat muted (collapsed solid,
inflated dotted), the head-on its (a) outer-sphere grey -- with the top key
naming every curve.  The frozen-core and suspect stretches are half weight
and broken: same arm's physics, not the same standing.  The two rules are
lighter greys (CONTEXT for the MOTS, FAINT for the wall).
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
HEADON = "04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100"
SPIRAL = "05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl5from0_t100"
SPIRAL_FRZ = "05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl5_t100_freeze_r05700"
FLYBY = "06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100"
SINGLE = "01_single_throat/seed/single_pureq_q1e2_ml4_scalar_t100"
KICKED = "01_single_throat/seed/single_eps_p1e2_q1e2_ml4_scalar_t100"

T_MOTS = 21.5      # head-on: first live corrected-orientation common MOTS
T_WALL = 59.94     # spiral (level 5 from t = 0): NaN in h11, 0.94 after its t = 59 MOTS
WINDOW = 25.0      # running-max window: one full period of the dipole
SMOOTH = 5.0       # Gaussian on log amplitude, to round the staircase
FLYBY_U_GATE = 50.0  # fly-by drawn to t - R <= 50 (its t = 70 trust window at R = 20)
RAMP = {10: "#1a1a18", 14: "#54524c", 18: "#8f8b81"}   # dark = inner


def _flux(path: pathlib.Path, radius: int) -> tuple[np.ndarray, np.ndarray]:
    head = open(path).readline().lstrip("#").split()
    d = np.loadtxt(path)
    return d[:, 0], d[:, head.index(f"R{radius}_scalar_flux_kin")]


def _envelope(t: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Peak envelope of |F|: running maximum over one period, then smoothed.

    The running maximum rides the successive peaks, which is the envelope; on
    a 0.5-unit cadence it comes out as a staircase, so it is rounded by a
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
    # constrained_layout does not reserve one for a FIGURE legend -- both
    # "bbox_to_anchor" and "outside upper center" drew it over the frames.
    # Ten entries at ncols 4 are three rows, so the band is taller than the
    # two-row original (top 0.745 at height 3.05).
    fig.subplots_adjust(left=0.088, right=0.988, top=0.78, bottom=0.135,
                        wspace=0.17)

    # ---- (a) one horizon, three spheres ------------------------------------
    for R in (10, 14, 18):
        t, k = _flux(camp / HEADON / "scalar_modes.dat", R)
        e = _envelope(t, k)
        axA.semilogy(t, e, color=RAMP[R], lw=1.2, zorder=3,
                     label=f"head-on, $R={R}$")
        fit = (t >= 30.0) & (t <= 95.0)
        c = np.polyfit(t[fit], np.log(e[fit]), 1)
        axA.semilogy(t[fit], np.exp(np.polyval(c, t[fit])), color=RAMP[R],
                     lw=0.8, ls=(0, (3, 2.2)), zorder=4)
        print(f"[censorship] head-on R={R}: envelope {e.max():.2e} -> "
              f"{np.interp(95.0, t, e):.2e} at t=95 "
              f"(x{e.max() / np.interp(95.0, t, e):.0f} down), tau = {-1 / c[0]:.1f}")
    axA.axvline(T_MOTS, color=style.CONTEXT, lw=0.8, ls=(0, (1, 2)), zorder=1)

    # NOTHING is written inside either frame.  Three notes were tried and all
    # three ended up against a spine or a tick label; the key above carries the
    # identities and the caption carries the numbers.
    axA.set_xlim(0, 100)
    axA.set_ylim(1.0e-4, 2.2e-2)
    axA.set_xlabel(r"$t$")
    axA.set_ylabel(r"$|F_\phi|$ envelope")
    axA.text(0.0, 1.03, "(a)", transform=axA.transAxes, ha="left",
             va="bottom", fontsize=9, color=style.INK)

    # ---- (b) three fates, one outer sphere each ----------------------------
    # The fly-by only to its trust window's retarded gate, t - R <= 50 (t = 80
    # on R = 30), its envelope built from the gated flux (docstring).
    t, k = _flux(camp / FLYBY / "scalar_modes.dat", 30)
    gate = t <= FLYBY_U_GATE + 30 + 1e-9
    t, k = t[gate], k[gate]
    ef = _envelope(t, k)
    axB.semilogy(t, ef, color=style.INK, lw=1.35, zorder=3,
                 label=r"fly-by, $R=30$")
    late = t >= 50.0
    t0 = float(t[late][np.argmin(np.abs(k[late]))])
    rise = np.abs(k[t >= t0])
    whole = t <= t[-1] - WINDOW / 2 + 1e-9
    print(f"[censorship] fly-by R=30 to t={t[-1]:.0f} (t-R <= {FLYBY_U_GATE:g}): envelope "
          f"{np.interp(50.0, t, ef):.2e} at t=50 -> {ef[whole][-1]:.2e} at t={t[whole][-1]:.1f} "
          f"(last whole window) -> {ef[-1]:.2e} at the cut; raw |F| {rise[0]:.2e} at t={t0:.0f} "
          f"-> {rise[-1]:.2e} at the cut (x{rise[-1] / rise[0]:.1f}), rising at every sample: "
          f"{bool(np.all(np.diff(rise) > 0))}")

    # The spiral, spliced: its own record to the wall, then the freeze arm.
    # They overlap over t = 58-59 and agree to 0.1 % on this very flux, so the
    # join is certified rather than assumed -- but the frozen stretch is drawn
    # dashed and half-weight, because a frozen core cannot be asked about its
    # own emission.
    ts, ks = _flux(camp / SPIRAL / "scalar_modes.dat", 30)
    tf, kf = _flux(camp / SPIRAL_FRZ / "scalar_modes.dat", 30)
    join = ts < tf[0]
    t_all = np.concatenate([ts[join], tf])
    e_all = _envelope(t_all, np.concatenate([ks[join], kf]))
    live = t_all <= T_WALL
    axB.semilogy(t_all[live], e_all[live], color=style.INK, lw=1.1,
                 ls=(0, (4, 2.2)), zorder=3, label=r"spiral, $R=30$")
    axB.semilogy(t_all[~live], e_all[~live], color=style.FAINT, lw=0.9,
                 ls=(0, (4, 2.2)), zorder=2, label="spiral, core frozen")
    print(f"[censorship] spiral R=30: {np.interp(T_WALL, t_all, e_all):.2e} at its "
          f"wall, still rising; frozen continuation flat to {e_all[-1]:.2e}")

    # The lone throat enters twice (see the docstring: neither re-run carries
    # its quadrupole seed).  KICKED = eps = +1e-2 at level 4, collapses behind
    # a MOTS from t = 11 and its envelope decays: solid.  SINGLE = the
    # unkicked level-4 throat, which inflates and GROWS; dashed at half
    # weight, counted to t ~ 80 only.
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

    # The head-on enters (b) on its OUTER sphere, so it must wear the OUTER
    # sphere's colour: the top legend serves both panels, and drawing this in
    # INK made the black swatch mean R = 10 in (a) and R = 18 here (2026-09-21).
    t, k = _flux(camp / HEADON / "scalar_modes.dat", 18)
    axB.semilogy(t, _envelope(t, k), color=RAMP[18], lw=1.6, zorder=4)
    axB.axvline(T_WALL, color=style.FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)

    axB.set_xlim(0, 100)
    axB.set_ylim(1.0e-4, 4.5e-1)
    axB.set_xlabel(r"$t$")
    axB.text(0.0, 1.03, "(b)", transform=axB.transAxes, ha="left",
             va="bottom", fontsize=9, color=style.INK)

    # ONE key for the page, above both frames (plot_psi4_ligo's idiom): the
    # curves of (a) interleave twice and (b)'s three fates cross, so no
    # in-frame naming is unambiguous anywhere on this page.
    hA, lA = axA.get_legend_handles_labels()
    hB, lB = axB.get_legend_handles_labels()
    rules = [Line2D([], [], color=style.CONTEXT, lw=0.8, ls=(0, (1, 2)),
                    label=r"common MOTS, $t=21.5$"),
             Line2D([], [], color=style.FAINT, lw=0.8, ls=(0, (4, 3)),
                    label=r"spiral's wall, $t=59.9$")]
    # "outside upper center" so constrained_layout RESERVES the strip: with a
    # plain bbox_to_anchor the key is drawn over the frames and over the
    # letter tags, which is what happened first.
    fig.legend(hA + hB + rules, lA + lB + [h.get_label() for h in rules],
               loc="upper center", bbox_to_anchor=(0.5, 1.0), ncols=4,
               fontsize=6.5, frameon=False, handlelength=2.4,
               columnspacing=1.6, labelspacing=0.45, borderaxespad=0.35)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "scalar_censorship.png")
    png = style.save(fig, out)
    print(f"[censorship] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
