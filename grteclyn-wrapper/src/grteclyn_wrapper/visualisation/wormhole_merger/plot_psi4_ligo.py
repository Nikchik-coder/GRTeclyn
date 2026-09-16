#!/usr/bin/env python3
r"""Every scenario against the detector: strain spectra and frequency tracks.

The gallery (``plot_psi4_gallery``) answers "what did each system radiate";
this figure answers the two follow-ups that decide whether anyone on Earth
would care:

  (a)  would aLIGO see it? -- the strain amplitude spectral density of every
       scenario's innermost-sphere waveform, scaled to one common physical
       calibration (M = 30 Msun total, D = 10 Mpc), over the aLIGO design
       floor.  One panel, all sources, so LOUDNESS ORDER is read directly;
  (b)  what does each source LOOK like in time-frequency? -- not five
       spectrograms but their ridges: the peak-frequency track of the
       Morlet wavelet transform, one line per scenario, its WIDTH the
       signal's own envelope, drawn only where the wavelet has signal
       (column maximum above 0.2 of the record's peak) and outside the
       cone of influence.  A ringdown is a flat shelf, a chirp climbs, a
       fly-by is a low arch -- the shapes overlap and that is the point:
       one frame separates the sources by shape.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_ligo

Sources, streams, gates and the innermost spheres are the gallery's ARMS
table -- ONE table, so the two figures can never disagree about what a
scenario is.  The wavelet band and width per record follow the dashboard
heuristics (``plot_psi4_analysis``): band bottom = the slowest thing the
record resolves (1.5 cycles per record) or 0.35 of the spectral peak, width
w the widest that leaves half the record outside the cone at the wave's own
frequency.  The ridge is refined by a parabola across the winning bin in
log f -- without it the track is the frequency GRID, a staircase of bin
edges, not the wave.

STYLE (the seed-branches grammar): figure* width, style.prd frame, no boxed
keys -- every curve is named in place, and each scenario keeps ONE identity
(ink solid = spiral, ink dashed = head-on, ink dash-dot = fly-by, muted
dotted = collapsing throat, grey solid = the vacuum control) across both
panels; the burgundy accent is the aLIGO design floor, the reference
everything is read against.  Time in panel (b) is the gallery's retarded
clock, frequency is physical, so (b) lines up with the gallery by row and
with (a) by axis.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_analysis import (  # noqa: E402
    wavelet_amplitude,
)
from grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery import (  # noqa: E402
    ARMS, load, trim_zeros_tail,
)
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    C_SI, G_SI, M_SUN_KG, M_SUN_SEC, MPC_METER, _aLIGO_noise_psd, _burst_psd,
    _psd_psi4_to_strain, _scale_to_physical, _smooth_psd,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "08_waves"
MASS_MSUN = 30.0     # the dashboards' calibration: one common physical
DIST_MPC = 10.0      # scaling so the five sources are comparable, not tuned
RIDGE_FLOOR = 0.2    # ridge drawn only where the column peaks above this

# One identity per scenario, shared by both panels (and nothing else): the
# wormhole sources are ink told apart by dash, the lone throat is the quiet
# muted one, the vacuum control is the grey context it is everywhere else.
LOOKS = {
    "collapsing throat": dict(color=style.MUTED, linestyle=(0, (1, 1.8)), linewidth=1.1),
    "head-on": dict(color=style.INK, linestyle=(0, (4, 2.5)), linewidth=1.0),
    "spiral": dict(color=style.INK, linestyle=(0, ()), linewidth=1.4),
    "fly-by": dict(color=style.INK, linestyle=(0, (5, 2, 1, 2)), linewidth=1.0),
    "vacuum BBH twin": dict(color=style.CONTEXT, linestyle=(0, ()), linewidth=1.3),
}

# Panel (a) is keyed by a measured legend (style.legend): six spectra share
# one octave of frequency, so every in-place name landed on somebody else's
# curve -- this is the one panel where the box earns its place.  Panel (b)'s
# tracks have air around them, so they keep in-place names, each at the
# track end that has empty air beside it: (anchor end, du, df, ha, va).
NAMES_B = {
    "collapsing throat": ("last", 2.5, 0.0, "left", "center"),
    "head-on": ("last", 2.5, 0.0, "left", "center"),
    "spiral": ("first", -0.5, -7.0, "left", "top"),
    "fly-by": ("last", 1.5, 2.0, "left", "bottom"),
    "vacuum BBH twin": ("last", 0.0, 9.0, "right", "bottom"),
}


def prepare(pack: pathlib.Path):
    """Load every packed arm once: trimmed innermost waveform + clocking."""
    arms = []
    for name, knob, mode, rel, m, R0, t_max, _note in ARMS:
        got = load(pack, rel, m)
        if got is None:
            print(f"  {name:<18s} PENDING -- no {rel}")
            continue
        t, series = got
        if t_max is not None:
            keep = t <= t_max + 1e-9
            t, series = t[keep], {r: y[keep] for r, y in series.items()}
        R_in = min(series, key=lambda r: abs(r - R0))
        tt, yy = trim_zeros_tail(t, series[R_in])
        arms.append(dict(name=name, knob=knob, mode=mode, R_in=R_in, t=tt, y=yy))
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

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.05, 3.2),
                                   constrained_layout=True)
    # The key is one flat frameless strip over BOTH panels (the identities
    # are shared); constrained layout knows nothing about figure legends,
    # so the top band is reserved by hand.
    fig.get_layout_engine().set(rect=(0, 0, 1, 0.89))

    # ---- (a) strain spectra over the design floor -----------------------
    f_hz_band = np.logspace(np.log10(20.0), np.log10(5000.0), 600)
    aligo = np.sqrt(_aLIGO_noise_psd(f_hz_band))
    for a in arms:
        dt = float(a["t"][1] - a["t"][0])
        f, S = _burst_psd(a["y"], 1.0 / dt)
        S = _smooth_psd(S, 21, 5)
        Sh = _psd_psi4_to_strain(f, S)
        f_hz, Sh_hz = _scale_to_physical(f, Sh, MASS_MSUN, DIST_MPC)
        band = (f_hz >= 20.0) & (f_hz <= 5000.0) & np.isfinite(Sh_hz) & (Sh_hz > 0)
        fb, hb = f_hz[band], np.sqrt(Sh_hz[band])
        axA.loglog(fb, hb, zorder=3, label=a["name"], **LOOKS[a["name"]])
        print(f"  {a['name']:<18s} strain peak {hb.max():.2e} at "
              f"{fb[np.argmax(hb)]:.0f} Hz")
    # What the record cannot hold: the numerical BBH stream opens at the
    # last orbits, but an astrophysical binary of the SAME mass arrives
    # there up a long inspiral ramp.  The Newtonian chirp of the equal-mass
    # binary, |h(f)| ~ Mc^{5/6} f^{-7/6}/D, drawn to the ISCO and through
    # the same 1/sqrt(T) normalization as the BBH record, is that ramp.
    bbh = next(a for a in arms if a["name"] == "vacuum BBH twin")
    T_sec = float(bbh["t"][-1] - bbh["t"][0]) * MASS_MSUN * M_SUN_SEC
    Mc_kg = (MASS_MSUN / 4.0 ** 0.6) * M_SUN_KG
    f_isco = C_SI ** 3 / (6.0 ** 1.5 * np.pi * G_SI * MASS_MSUN * M_SUN_KG)
    f_chirp = f_hz_band[f_hz_band <= f_isco]
    htilde = (np.sqrt(5.0 / 24.0) * np.pi ** (-2.0 / 3.0)
              * (G_SI * Mc_kg) ** (5.0 / 6.0) / C_SI ** 1.5
              / (DIST_MPC * MPC_METER) * f_chirp ** (-7.0 / 6.0))
    axA.loglog(f_chirp, htilde / np.sqrt(T_sec), color=style.FAINT,
               linewidth=1.0, zorder=2, label="BBH inspiral (analytic)")
    # A pure power law IS a straight line on these axes; the open circle
    # says the line ends at the ISCO on purpose, not from a cut record.
    axA.plot(f_chirp[-1], htilde[-1] / np.sqrt(T_sec), marker="o", ms=3.0,
             mfc=style.GROUND, mec=style.FAINT, mew=1.0, zorder=2)
    axA.loglog(f_hz_band, aligo, color=style.BURGUNDY, linewidth=1.2, zorder=2,
               label="aLIGO design")
    axA.set_xlim(20.0, 5000.0)
    axA.set_ylim(1e-25, 6e-20)
    axA.set_xlabel(r"$f$  [Hz]")
    axA.set_ylabel(r"$\sqrt{S_h(f)}$  [$\mathrm{Hz}^{-1/2}$]")
    axA.text(0.03, 0.955, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    axA.text(0.97, 0.955,
             rf"$M={MASS_MSUN:.0f}\,M_\odot$,  $D={DIST_MPC:.0f}$ Mpc",
             transform=axA.transAxes, ha="right", va="top", fontsize=7,
             color=style.MUTED)
    fig.legend(*axA.get_legend_handles_labels(), loc="upper center",
               bbox_to_anchor=(0.5, 1.0), ncols=4, fontsize=6.5,
               frameon=False, handlelength=2.4, columnspacing=1.2,
               borderaxespad=0.2)

    # ---- (b) the peak-frequency ridge of every source -------------------
    # The line's WIDTH is the signal's own envelope (the wavelet column
    # peak), so a track is not a wire: it swells where the source is loud
    # and tapers where it dies -- the "shape" a full spectrogram would
    # show, without five panels of it.
    for a in arms:
        t, y = a["t"], np.real(a["y"])
        dt = float(t[1] - t[0])
        T_rec = float(t[-1] - t[0])
        f, S = _burst_psd(a["y"], 1.0 / dt)
        f_pk = float(f[1:][np.argmax(_smooth_psd(S, 21, 5)[1:])])
        f_lo = max(1.5 / T_rec, 0.35 * f_pk)
        f_hi = min(0.5 / dt, max(8.0 * f_pk, 4.0 * f_lo))
        w = float(np.clip(2.0 * np.pi * f_pk * 0.25 * T_rec / np.sqrt(2.0), 3.0, 8.0))
        freqs, amp = wavelet_amplitude(y, dt, f_lo, f_hi, w=w)
        ridge_i = np.argmax(amp, axis=0)
        cols = np.arange(ridge_i.size)
        # Parabolic refinement across the winning bin, in log f (the grid
        # is log-spaced): without it the ridge is the frequency GRID.
        dlf = np.log10(freqs[1]) - np.log10(freqs[0])
        lo = amp[np.maximum(ridge_i - 1, 0), cols]
        mid = amp[ridge_i, cols]
        hi = amp[np.minimum(ridge_i + 1, freqs.size - 1), cols]
        den = lo - 2.0 * mid + hi
        shift = np.zeros(ridge_i.size)
        inner = (ridge_i > 0) & (ridge_i < freqs.size - 1) & (den != 0)
        np.divide(0.5 * (lo - hi), den, out=shift, where=inner)
        ridge_f = 10.0 ** (np.log10(freqs[ridge_i])
                           + np.clip(shift, -0.5, 0.5) * dlf)
        col_pk = amp.max(axis=0)
        u = t - a["R_in"]
        # Only where there is signal to track and the wavelet is not riding
        # the record's edge (the cone of influence at the ridge's own f).
        coi = np.sqrt(2.0) * w / (2.0 * np.pi * ridge_f)
        ok = (col_pk >= RIDGE_FLOOR) & (u - u[0] >= coi) & (u[-1] - u >= coi)
        ridge_hz = ridge_f / (MASS_MSUN * M_SUN_SEC)

        # The swelling body is a light underlay (width = the signal's own
        # envelope); the arm's IDENTITY -- its dash -- rides on top at
        # constant weight, because a dash pattern cannot survive being cut
        # into one-sample segments of varying width.
        pts = np.column_stack([u, ridge_hz])
        seg_ok = ok[:-1] & ok[1:]
        segs = np.stack([pts[:-1][seg_ok], pts[1:][seg_ok]], axis=1)
        widths = 0.8 + 3.4 * col_pk[:-1][seg_ok]
        axB.add_collection(LineCollection(
            segs, colors=LOOKS[a["name"]]["color"], linewidths=widths,
            alpha=0.28, capstyle="round", zorder=2))
        axB.plot(np.where(ok, u, np.nan), ridge_hz, zorder=3, **LOOKS[a["name"]])
        uu, ff = u[ok], ridge_hz[ok]
        end, du, df_, ha, va = NAMES_B[a["name"]]
        ux, fx = (uu[-1], ff[-1]) if end == "last" else (uu[0], ff[0])
        axB.text(ux + du, fx + df_, a["name"], fontsize=7.5,
                 color=LOOKS[a["name"]]["color"], ha=ha, va=va)
        print(f"  {a['name']:<18s} ridge u = {uu[0]:.0f} .. {uu[-1]:.0f}, "
              f"f = {ff.min():.0f} .. {ff.max():.0f} Hz")
    axB.set_xlim(-5, 118)
    axB.set_ylim(135, 365)
    axB.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    axB.set_ylabel(r"$f$  [Hz]")
    axB.text(0.03, 0.955, "(b)", transform=axB.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "psi4_ligo.png")
    png = style.save(fig, out)
    print(f"[ligo] wrote {png} (+pdf); {len(arms)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
