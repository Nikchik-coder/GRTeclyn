#!/usr/bin/env python3
r"""Every scenario against the detector: power, strain, and frequency.

The gallery (``plot_psi4_gallery``) answers "what did each system radiate";
this strip answers the three follow-ups that decide whether anyone on Earth
would care, and whether the numbers are believable at all:

  (a)  what SHAPE is each burst, and how loud? -- the envelope of every
       scenario's innermost-sphere record, all five on one axis and on (c)'s
       merger clock.  This panel was briefly the |r Psi_4|^2 spectrum, which
       is (b) multiplied by (2 pi f)^4: one plot drawn twice (2026-09-18);
  (b)  would aLIGO see it? -- the same records as strain amplitude spectral
       density over the aLIGO design floor, so LOUDNESS ORDER is read
       directly, with the analytic Newtonian inspiral ramp of the same
       binary for the band the simulation does not cover;
  (c)  how does the frequency MOVE? -- the instantaneous frequency of each
       record against the analytic chirp of a point-mass binary of the same
       mass, every track on its own merger clock.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_ligo

Sources, streams, gates and the innermost spheres are the gallery's ARMS
table -- ONE table, so the two figures can never disagree about what a
scenario is.

TWO THINGS THIS FIGURE GOT WRONG UNTIL 2026-09-18
-------------------------------------------------
*The calibration was not shared.*  The panel says "total mass M = 30 Msun",
and the conversion mapped ONE CODE UNIT to 30 Msun for every arm.  But four
of the five sources are binaries carrying M_ADM = 1 per body -- a total of 2
code units -- and only the lone throat is a single unit mass (the runs' own
``evolution_params.txt``; see ``M_CODE``).  So the binaries were being drawn
as 60 Msun systems at half their proper frequency, beside a 30 Msun throat.
Everything here is now reduced to the source's OWN total mass first, which
is what "frequency scales as 1/M" means, and only then scaled to 30 Msun.
The check that settles it: the BBH control's peak |r Psi_4| sits at
f M = 0.065, the textbook merger value, and its ringdown climbs toward
f M = 0.0885 -- both statements about the TOTAL mass, both satisfied only
under this normalisation.

*The wavelet ridge hid the chirp.*  Panel (c) used to be the peak of a
Morlet transform.  A Morlet ridge needs the cone of influence trimmed off
both ends, which on these short records is half the data, and it smears a
sweep into the band it is measured in: the vacuum BBH twin, whose phase
sweeps through a factor of 80 and whose merger is textbook, came out as a
FLAT shelf, and so did the spiral's factor-9 climb.  The frequency is now
the waveform's own phase derivative -- the standard numerical-relativity
diagnostic, with no cone of influence -- taken on the analytic signal so the
real (2,0) records have a phase at all, and energy-weighted over a cycle so
that a record which beats rather than chirps cannot report the frequency of
its own nulls (see ``envelope_and_frequency``).  It is gated on amplitude,
not on the wavelet: the longest run above ``GATE`` of the record's peak,
with at least ``MIN_SPP`` samples per cycle, so a decayed tail cannot report
the sampling grid as a frequency.

STYLE (the seed-branches grammar): a two-column strip (7.05 x 2.9), three
panels side by side under one flat key -- with five sources in three narrow
panels there is no room to name a curve in place, which is the one condition
under which this package draws a key -- style.prd frame, letter tags above
the frames, semantics and the verified numbers in the caption.  Each
scenario keeps ONE identity (ink solid = spiral, ink dashed = head-on, ink
dash-dot = fly-by, muted dotted = collapsing throat, grey solid = the vacuum
control) across all three panels.  The deep green accent is the reference the
panel is read against, and only that: the aLIGO design floor in (b), the
analytic point-mass chirp in (c).
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.signal import hilbert  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery import (  # noqa: E402
    ARMS, load, trim_zeros_tail,
)
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    C_SI, G_SI, M_SUN_KG, M_SUN_SEC, MPC_METER, _aLIGO_noise_psd, _burst_psd,
    _compute_radiated_energy, _psd_psi4_to_strain, _scale_to_physical,
    _smooth_psd,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "08_waves"
MASS_MSUN = 30.0     # the dashboards' calibration: one common physical
DIST_MPC = 10.0      # scaling so the five sources are comparable, not tuned

# TOTAL ADM mass of each source in CODE units, from the runs' own
# evolution_params.txt.  The calibration above is a statement about the total
# mass, so every record is reduced to units of ITS OWN total mass before it
# is given a frequency in Hz.  Getting this wrong is a factor of two in every
# binary's frequency and a factor of 2.8 in its strain (2026-09-18).
M_CODE = {
    "collapsing throat": 1.0,   # one drainhole, wormhole_drainhole_mass_A = 1
    "head-on": 2.0,             # two drainholes, M_ADM = 1 each
    "spiral": 2.0,              # ditto, d = 12
    "fly-by": 2.0,              # ditto, d = 12
    "vacuum BBH twin": 2.0,     # bare 0.9615 -> per-hole ADM ~ 1.00 at d = 12
}

GATE = 0.25          # frequency drawn over the record's body: |rPsi4| above
MIN_SPP = 8.0        # this fraction of peak, and >= this many samples/cycle
ETA = 0.25           # equal mass, for the analytic chirp
A_FINAL, M_FINAL = 0.6864, 0.9516    # equal-mass non-spinning remnant

# The two vacuum answers this campaign's binaries are read between: published
# numerical-relativity results for the equal-mass non-spinning binary from
# rest at infinity, both as E_rad / M.  They are references, NOT closed forms
# and NOT runs of this campaign.
E_BBH_CIRCULAR = 1.0 - M_FINAL       # 4.84e-2: quasi-circular inspiral-merger
E_BBH_HEADON = 5.5e-4                # head-on infall, the other extreme

SHORT = {"collapsing throat": "throat", "head-on": "head-on",
         "spiral": "spiral", "fly-by": "fly-by", "vacuum BBH twin": "BBH twin"}

# One identity per scenario, shared by all three panels (and nothing else):
# the wormhole sources are ink told apart by dash, the lone throat is the
# quiet muted one, the vacuum control is the grey context it is everywhere.
LOOKS = {
    "collapsing throat": dict(color=style.MUTED, linestyle=(0, (1, 1.8)), linewidth=1.1),
    "head-on": dict(color=style.INK, linestyle=(0, (4, 2.5)), linewidth=1.0),
    "spiral": dict(color=style.INK, linestyle=(0, ()), linewidth=1.4),
    "fly-by": dict(color=style.INK, linestyle=(0, (5, 2, 1, 2)), linewidth=1.0),
    "vacuum BBH twin": dict(color=style.CONTEXT, linestyle=(0, ()), linewidth=1.3),
}


def _smooth_window(nbins: int) -> int:
    """Savitzky-Golay width in BINS, as a fraction of the record's band.

    It was a hard-coded 21 for every arm, which is not one filter but five:
    these records differ by two orders of magnitude in length, so 21 bins is
    a light touch on the spiral's 5000-bin spectrum and most of the band on
    the throat's 36.  A fifth of the spectrum, odd, at least 5.
    """
    return max(5, min(21, (nbins // 5) | 1))


def f_isco_M() -> float:
    """f_GW * M at the Schwarzschild ISCO of the total mass."""
    return 6.0 ** -1.5 / np.pi


def f_qnm_M() -> float:
    """f * M of the l = m = 2 fundamental of the equal-mass remnant.

    Berti-Cardoso-Will fit, at the remnant of a non-spinning equal-mass
    inspiral (M_f = 0.9516 M, a_f = 0.6864).
    """
    return (1.5251 - 1.1568 * (1.0 - A_FINAL) ** 0.1292) / (2.0 * np.pi * M_FINAL)


def newtonian_chirp_M(tau_M: np.ndarray) -> np.ndarray:
    """f_GW * M, ``tau_M`` total masses before coalescence (Newtonian)."""
    return ((1.0 / np.pi) * (5.0 / (256.0 * tau_M)) ** 0.375
            * (ETA ** 0.6) ** -0.625)


def envelope_and_frequency(y: np.ndarray, dt: float, f_guess: float):
    """``(|A|, f)``: the record's envelope and its instantaneous frequency.

    Both come from the same analytic signal, and they have to: the (2,0)
    records are real to one part in 10^8, so ``|y|`` is not an envelope at
    all -- it is the rectified wave, touching zero twice a cycle, and a gate
    laid on it keeps one half-cycle lobe instead of the record's body
    (2026-09-18).  The (2,2) records are complex and carry their own.

    The frequency is the ENERGY-WEIGHTED first moment of d(phase)/dt over a
    Hann window of about a cycle at ``f_guess``.  The bare derivative is only
    a frequency for a narrowband record, and two of these are not: the
    spiral's (2,2) envelope swings by a factor of two within one carrier
    period, so its phase alternately stalls and races and the bare
    derivative swings between 3 Hz and 7.6 kHz on a record whose whole band
    is a factor of three wide.  Weighting by |A|^2 puts that variance where
    it belongs -- the phase races exactly where the amplitude is near a null,
    and a null carries no energy and so no frequency.
    """
    z = y if np.abs(y.imag).max() > 1e-6 * np.abs(y.real).max() else hilbert(np.real(y))
    env = np.abs(z)
    fi = np.gradient(np.unwrap(np.angle(z)), dt) / (2.0 * np.pi)
    win = int(round(1.0 / max(f_guess, 1e-12) / dt)) | 1
    win = max(5, min(win, (env.size - 1) | 1))
    ker = np.hanning(win)
    ker /= ker.sum()
    w = env ** 2
    num = np.convolve(w * fi, ker, mode="same")
    den = np.convolve(w, ker, mode="same")
    return env, np.abs(np.divide(num, den, out=np.zeros_like(num),
                                 where=den > 0))


def body(amp: np.ndarray, gate: float) -> np.ndarray:
    """The longest contiguous run above ``gate`` of the peak.

    Not "first loud sample to last": the BBH control opens with an
    initial-data burst reaching 0.29 of its merger peak, and a first-to-last
    gate hands the track that junk and the quiet gap behind it.
    """
    loud = amp >= gate * amp.max()
    best, run, start = (0, 0), 0, 0
    for i, v in enumerate(np.append(loud, False)):
        if v:
            if run == 0:
                start = i
            run += 1
        else:
            if run > best[1] - best[0]:
                best = (start, i)
            run = 0
    keep = np.zeros(amp.size, bool)
    keep[best[0]:best[1]] = True
    return keep


def prepare(pack: pathlib.Path):
    """Every packed arm, reduced to units of its OWN total mass.

    ``u`` is retarded time in total masses, ``y`` the dimensionless
    (r Psi_4) M, ``dt`` the step in total masses -- so one physical
    calibration applies to all five without a per-arm correction anywhere
    downstream.
    """
    arms = []
    for name, knob, mode, rel, m, R0, t_max, _note in ARMS:
        got = load(pack, rel, m)
        if got is None:
            print(f"  {name:<18s} PENDING -- no {rel}")
            continue
        t_raw, series_raw = got          # kept ungated for the sphere spread
        t, series = t_raw, series_raw
        if t_max is not None:
            keep = t <= t_max + 1e-9
            t, series = t[keep], {r: y[keep] for r, y in series.items()}
        R_in = min(series, key=lambda r: abs(r - R0))
        tt, yy = trim_zeros_tail(t, series[R_in])
        M = M_CODE[name]
        mm = 0 if mode == "(2,0)" else 2
        u = (tt - R_in) / M
        dt = float(tt[1] - tt[0]) / M
        # The radiated energy, and its one honest error bar: the spread over
        # the extraction spheres.  Radiation is r-independent once r Psi_4 is
        # formed, so a number that falls with r is near-zone content.  The
        # spheres have to be compared over a COMMON RETARDED window -- the
        # ARMS gate is a coordinate-time cap chosen at the innermost sphere,
        # and the same physics reaches R later, so applying it as written
        # left R = 44 sixteen masses of record against R = 20's twenty-eight
        # and read a factor of twenty between them (2026-09-18).
        def band_energy(uu, ww):
            f, S = _burst_psd(ww, (uu.size - 1) / (uu[-1] - uu[0]))
            return _compute_radiated_energy(
                uu, ww, m=mm,
                f_peak=float(f[1:][np.argmax(_smooth_psd(S, _smooth_window(S.size), 5)[1:])]))

        E = band_energy(u, yy * M)
        spread = []
        for R in sorted(series_raw):
            keep = (t_raw - R) / M <= u[-1]
            if keep.sum() < 64:
                continue
            t2, y2 = trim_zeros_tail(t_raw[keep], series_raw[R][keep])
            if t2.size >= 64:
                spread.append(band_energy((t2 - R) / M, y2 * M))
        arms.append(dict(name=name, knob=knob, mode=mode, R_in=R_in, M=M,
                         u=u, y=yy * M, dt=dt, E=E,
                         E_lo=min(spread) if spread else E,
                         E_hi=max(spread) if spread else E))
    return arms


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    arms = prepare(pathlib.Path(args.pack_root).expanduser())
    if not arms:
        raise SystemExit("no arm has a packed stream yet")

    to_hz = 1.0 / (MASS_MSUN * M_SUN_SEC)      # f*M -> Hz at the calibration
    print(f"[ligo] calibration M = {MASS_MSUN:g} Msun, D = {DIST_MPC:g} Mpc: "
          f"f*M = 1 is {to_hz:.0f} Hz, ISCO {f_isco_M() * to_hz:.0f} Hz, "
          f"ringdown {f_qnm_M() * to_hz:.0f} Hz")

    style.prd(base=10.0)
    fig, (axA, axB, axC, axD) = plt.subplots(1, 4, figsize=(7.05, 2.75),
                                             constrained_layout=True)
    # The key is one flat frameless strip over all three panels (the
    # identities are shared); constrained layout knows nothing about figure
    # legends, so the top band is reserved by hand.
    fig.get_layout_engine().set(rect=(0, 0, 1, 0.86))

    f_hz_band = np.logspace(np.log10(20.0), np.log10(5000.0), 600)

    # ---- (a) the records themselves, on the same clock as (c) ------------
    # NOT the power spectrum: that is panel (b) multiplied by (2 pi f)^4, so
    # the two panels carried one plot twice (the user, 2026-09-18).  What the
    # strip was missing is the time domain -- the burst SHAPES and the
    # loudness ordering that (b) states in frequency, on (c)'s merger clock,
    # so a shape in (a) and a sweep in (c) are read off the same abscissa.
    for a in arms:
        f, S = _burst_psd(a["y"], 1.0 / a["dt"])
        f_pk = float(f[1:][np.argmax(_smooth_psd(S, _smooth_window(S.size), 5)[1:])])
        env, _ = envelope_and_frequency(a["y"], a["dt"], f_pk)
        a["env"], a["f_pk"] = env, f_pk
        a["tau"] = a["u"] - a["u"][int(np.argmax(env))]
        # The key names, and only names: the energies are panel (d)'s subject
        # and repeating them here made the key a second table.
        axA.semilogy(a["tau"], env, zorder=3, label=a["name"],
                     **LOOKS[a["name"]])
        print(f"  {a['name']:<18s} peak |rPsi4| M = {env.max():.3e} at "
              f"u = {a['u'][int(np.argmax(env))]:.1f} M, "
              f"band peak f M = {f_pk:.4f} ({f_pk * to_hz:.0f} Hz); "
              f"E/M = {a['E']:.3e} (spheres {a['E_lo']:.2e}-{a['E_hi']:.2e}, "
              f"{(a['E_hi'] - a['E_lo']) / a['E'] * 100:.0f}%), "
              f"{a['E'] * MASS_MSUN:.4f} Msun c^2")
    axA.set_xlim(-45, 30)
    axA.set_ylim(2e-4, 2e-1)
    axA.set_xlabel(r"$(t-R_{\mathrm{ext}}-t_{\mathrm{peak}})\,/\,M$")
    axA.set_ylabel(r"$|r\Psi_4|\,M$")

    # ---- (b) strain over the design floor -------------------------------
    # DRAWN ONLY WHERE THE RECORD MEASURES (2026-09-18).  This panel used to
    # run from 20 Hz and quote the maximum of the curve.  After the 1/f^4
    # weight the strain PSD of every one of these bursts still RISES toward
    # low frequency, so that maximum landed wherever the high-pass guard
    # stopped it -- and the guard is one cycle per record.  The quoted
    # numbers were therefore 1/T_record wearing a physical name: throat
    # 95.3 Hz against 1/T = 96.7, head-on 135.3 against 136.7, spiral 135.3
    # against 135.3, fly-by 178.0 against 178.1, BBH twin 89.9 against 90.2.
    # Lengthen a record or move its gate and every one of them moves.
    #
    # Below 1/T the spectrum is not measured, it is extrapolated, so the
    # curve now STARTS at the record's own corner, the corner is ticked on
    # the axis, and what is quoted is the strain at the one frequency in
    # these records that is genuinely resolved: the Psi_4 band peak of
    # panel (a) (bins 3-5, not bin 1).  Read this panel as a falling power
    # law with a stated left edge, never as a bump with a peak.
    for a in arms:
        f, S = _burst_psd(a["y"], 1.0 / a["dt"])
        S = _smooth_psd(S, _smooth_window(S.size), 5)
        Sh = _psd_psi4_to_strain(f, S)
        f_hz, Sh_hz = _scale_to_physical(f, Sh, MASS_MSUN, DIST_MPC)
        f_corner = to_hz / float(a["u"][-1] - a["u"][0])      # 1 cycle/record
        band = ((f_hz >= f_corner) & (f_hz <= 5000.0)
                & np.isfinite(Sh_hz) & (Sh_hz > 0))
        fb, hb = f_hz[band], np.sqrt(Sh_hz[band])
        a["f_corner"], a["h_corner"] = f_corner, float(hb[0])
        axB.loglog(fb, hb, zorder=3, **LOOKS[a["name"]])
        axB.plot([fb[0]], [hb[0]], marker="|", ms=4.5, mew=0.9, zorder=4,
                 color=LOOKS[a["name"]]["color"])
        h_at_pk = float(np.interp(a["f_pk"] * to_hz, fb, hb))
        a["h_at_pk"] = h_at_pk
        print(f"  {a['name']:<18s} strain {h_at_pk:.2e} at the resolved "
              f"Psi_4 peak {a['f_pk'] * to_hz:.0f} Hz; record corner "
              f"1/T = {f_corner:.0f} Hz (curve starts there, value "
              f"{hb[0]:.2e}); logarithmic slope "
              f"{np.polyfit(np.log(fb), np.log(hb), 1)[0]:+.2f}")
    # What the record cannot hold: the numerical BBH stream opens at the
    # last orbits, but an astrophysical binary of the SAME mass arrives
    # there up a long inspiral ramp.  The Newtonian chirp of the equal-mass
    # binary, |h(f)| ~ Mc^{5/6} f^{-7/6}/D, drawn to the ISCO and through
    # the same 1/sqrt(T) normalization as the BBH record, is that ramp.
    bbh = next(a for a in arms if a["name"] == "vacuum BBH twin")
    T_sec = float(bbh["u"][-1] - bbh["u"][0]) * MASS_MSUN * M_SUN_SEC
    Mc_kg = (MASS_MSUN * ETA ** 0.6) * M_SUN_KG
    f_isco_hz = f_isco_M() * to_hz
    f_chirp = f_hz_band[f_hz_band <= f_isco_hz]
    htilde = (np.sqrt(5.0 / 24.0) * np.pi ** (-2.0 / 3.0)
              * (G_SI * Mc_kg) ** (5.0 / 6.0) / C_SI ** 1.5
              / (DIST_MPC * MPC_METER) * f_chirp ** (-7.0 / 6.0))
    axB.loglog(f_chirp, htilde / np.sqrt(T_sec), color=style.FAINT,
               linewidth=1.0, zorder=2, label="BBH inspiral (analytic)")
    # A pure power law IS a straight line on these axes; the open circle
    # says the line ends at the ISCO on purpose, not from a cut record.
    axB.plot(f_chirp[-1], htilde[-1] / np.sqrt(T_sec), marker="o", ms=3.0,
             mfc=style.GROUND, mec=style.FAINT, mew=1.0, zorder=2)
    axB.loglog(f_hz_band, np.sqrt(_aLIGO_noise_psd(f_hz_band)),
               color=style.DEEP_GREEN, linewidth=1.2, zorder=2,
               label="aLIGO design")
    axB.set_xlim(20.0, 5000.0)
    axB.set_ylim(1e-25, 6e-20)
    axB.set_xlabel(r"$f$  [Hz]")
    axB.set_ylabel(r"$\sqrt{S_h(f)}$  [$\mathrm{Hz}^{-1/2}$]")
    # Bottom LEFT, under every curve's left end: centred it sat on the
    # vacuum twin's descent (2026-09-18).
    axB.text(0.03, 0.03,
             rf"${MASS_MSUN:.0f}\,M_\odot$, ${DIST_MPC:.0f}$ Mpc",
             transform=axB.transAxes, ha="left", va="bottom", fontsize=6.5,
             color=style.MUTED)

    # ---- (c) the frequency, against the point-mass chirp ----------------
    # Every track on its OWN merger clock (peak |rPsi4| at tau = 0), which is
    # the only clock on which a ringdown, a fly-by and a chirp are the same
    # kind of statement -- and the clock the analytic curve is written in.
    for a in arms:
        _, fM = envelope_and_frequency(a["y"], a["dt"], a["f_pk"])
        keep = body(a["env"], GATE) & (fM * a["dt"] <= 1.0 / MIN_SPP)
        k = int(np.argmax(a["env"]))
        hz = np.where(keep, fM * to_hz, np.nan)
        axC.plot(a["tau"], hz, zorder=3, **LOOKS[a["name"]])
        kk = np.isfinite(hz)
        print(f"  {a['name']:<18s} f = {np.nanmin(hz):.0f} .. {np.nanmax(hz):.0f} Hz "
              f"over tau = {a['tau'][kk][0]:+.0f} .. {a['tau'][kk][-1]:+.0f} M; "
              f"at peak f M = {fM[k]:.4f} ({fM[k] * to_hz:.0f} Hz)")
    # The reference: a point-mass binary of the same mass, coalescing at
    # tau = 0.  Drawn from the panel's left edge to where the Newtonian
    # formula reaches the ringdown frequency and stops meaning anything.
    tau_end = 5.0 / 256.0 * (np.pi * f_qnm_M() / (ETA ** 0.6) ** -0.625) ** (-8.0 / 3.0)
    tau_an = np.linspace(60.0, tau_end, 400)
    axC.plot(-tau_an, newtonian_chirp_M(tau_an) * to_hz, color=style.DEEP_GREEN,
             linewidth=1.1, zorder=4)
    # The two rules are named at the LEFT edge, where only the chirp runs and
    # it is far below both: at the right edge the ringdown name sat on the
    # spiral's climb and on the throat's tail (2026-09-18).
    for lev, lab in ((f_isco_M(), "ISCO"), (f_qnm_M(), "ringdown")):
        axC.axhline(lev * to_hz, color=style.FAINT, lw=0.7, ls=(0, (1, 2.5)),
                    zorder=1)
        axC.annotate(lab, (0.0, lev * to_hz),
                     xycoords=matplotlib.transforms.blended_transform_factory(
                         axC.transAxes, axC.transData),
                     xytext=(3, 2), textcoords="offset points", ha="left",
                     va="bottom", fontsize=6.5, color=style.MUTED)
    # Under its own curve, where the panel is empty: laid along it the name
    # was struck through by the curve it names.
    axC.text(-43.0, 68.0, "point-mass\nchirp", fontsize=6.5, ha="left",
             va="bottom", color=style.DEEP_GREEN, linespacing=1.2)
    axC.set_xlim(-45, 30)
    axC.set_ylim(55, 1300)
    axC.set_yscale("log")
    axC.set_xlabel(r"$(t-R_{\mathrm{ext}}-t_{\mathrm{peak}})\,/\,M$")
    axC.set_ylabel(r"$f$  [Hz]")

    # ---- (d) how much went out, against the two vacuum answers -----------
    # The two vacuum answers are BARS, not rules: as vertical rules their
    # names had to be set rotated inside the bars they cross, and a reference
    # a reader cannot name is not a reference.  As open deep green bars in the
    # same ranking they say the same thing and are read in the same glance.
    rows = [(SHORT[a["name"]], a["E"], a["E_lo"], a["E_hi"],
             LOOKS[a["name"]]["color"], True) for a in arms]
    # NOT "BBH head-on": this campaign has no head-on black-hole run, and a
    # row named like one reads as data (the user, 2026-09-18).  Nor "analytic":
    # both are PUBLISHED numerical-relativity results for the equal-mass
    # non-spinning binary, not closed forms -- the only closed form on this
    # page is panel (c)'s Newtonian chirp.
    rows += [("literature\nhead-on", E_BBH_HEADON, None, None, style.DEEP_GREEN, False),
             ("literature\ncircular", E_BBH_CIRCULAR, None, None, style.DEEP_GREEN, False)]
    rows.sort(key=lambda r: r[1])
    for i, (lab, E, lo, hi, col, measured) in enumerate(rows):
        axD.barh(i, E, height=0.62, left=1e-6, zorder=3,
                 color=col if measured else style.GROUND,
                 edgecolor=col, linewidth=0.0 if measured else 0.9)
        if measured:
            # The error bar is the spread over the extraction spheres, the
            # only one that catches near-zone content posing as a wave.
            axD.plot([lo, hi], [i, i], color=style.GROUND, lw=2.0,
                     solid_capstyle="butt", zorder=4)
            axD.plot([lo, hi], [i, i], color=style.INK, lw=0.8,
                     solid_capstyle="butt", zorder=5)
    axD.set_xscale("log")
    axD.set_xlim(1e-5, 4e-1)
    axD.set_ylim(-0.7, len(rows) - 0.3)
    axD.set_yticks(np.arange(len(rows)))
    axD.set_yticklabels([r[0] for r in rows], fontsize=6.5)
    axD.tick_params(axis="y", length=0)
    axD.set_xticks([1e-5, 1e-3, 1e-1])
    axD.set_xlabel(r"$E_{\mathrm{rad}}/M$")
    print("  analytic vacuum references: head-on from rest "
          f"{E_BBH_HEADON:.1e}, quasi-circular merger {E_BBH_CIRCULAR:.3e}")

    for ax, letter in zip((axA, axB, axC, axD), "abcd"):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=9, color=style.INK)

    # The scenarios are labelled where they are first drawn (a), the two
    # references where they are (b); one strip carries both.
    hA, lA = axA.get_legend_handles_labels()
    hB, lB = axB.get_legend_handles_labels()
    fig.legend(hA + hB, lA + lB, loc="upper center", bbox_to_anchor=(0.5, 1.0),
               ncols=4, fontsize=6.5, frameon=False, handlelength=2.4,
               columnspacing=1.4, borderaxespad=0.2)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "psi4_ligo.png")
    png = style.save(fig, out)
    print(f"[ligo] wrote {png} (+pdf); {len(arms)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
