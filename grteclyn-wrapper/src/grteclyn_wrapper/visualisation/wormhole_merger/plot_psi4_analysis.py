#!/usr/bin/env python3
r"""The six-panel wave analysis of one arm, in the campaign's house style.

The panels, in reading order:

  (a) the waveform at every extraction sphere, on simulation time;
  (b) the same on retarded time, where a genuine outgoing wave collapses onto
      one curve, with the ringdown fit on the innermost sphere;
  (c) the power spectrum -- where the power actually sits;
  (d) propagation speed: the matched wavefront peak at each sphere, and the
      speed it implies between them.  A signal at v ~ c is radiation; a much
      slower or faster one is a gauge or constraint mode wearing a wave's
      clothes;
  (e) the spectrogram -- whether the frequency moves, which is what separates
      a chirp from a bell;
  (f) the strain the same event would put through Advanced LIGO at a stated
      mass and distance.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_analysis \
        [--run NAME[+NAME...]] [--group 04_binary_headon] [--name STEM]

The wave physics -- the Tukey-windowed burst spectrum, the ringdown fit, the
strain conversion, the aLIGO curve, the wavelet spectrogram -- is imported from
``visualisation.process_wave.plot_extracted_psi4``, which several campaigns
share; forking those 1000 lines to restyle a figure would have left two copies
to keep in step.  What lives here is this campaign's: which run, which spheres,
where the figure is filed, and how it is drawn.

DEFAULT SUBJECT: the head-on arm ``merge_headon_flip_d8_v1c_latefreeze_t100``,
which is the only one of the head-on arms that was never restarted.  For a
spectrum that matters: a restart seam is a step discontinuity, and an FFT turns
a step into broadband power that looks like signal.  Chains can still be given
(``a+b``) and are stitched on time, later segment winning; the seam times are
then printed, and panels (c)-(f) should be read knowing they are there.
"""

from __future__ import annotations

import argparse
import pathlib
import string

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import ScalarFormatter  # noqa: E402

from grteclyn_wrapper.visualisation.process_wave.plot_extracted_psi4 import (  # noqa: E402
    _aLIGO_noise_psd, _burst_psd, _compute_propagation_speeds,
    _compute_radiated_energy, _compute_snr, _damped_sinusoid, _find_peak_times,
    _fit_qnm, _psd_psi4_to_strain, _scale_to_physical, _smooth_psd,
)
from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    figure_dir, find_packed,
)

DEFAULT_RUN = "merge_headon_flip_d8_v1c_latefreeze_t100"
DEFAULT_GROUP = "04_binary_headon"
STREAM = "psi4_mode_l2m0.dat"


def load_chain(specs: list[str], pack_root=None, stream: str = STREAM, m: int | None = None):
    """(t, radii, {radius: complex}) for one arm, or a restart chain stitched.

    Segments are ordered by start time and the later one wins where two
    overlap -- a restarted arm re-runs the units between its checkpoint and
    where its parent died, and the branch that was continued is the later one.

    ``m`` selects an azimuthal mode out of a combined ``psi4_mode_l2_all.dat``;
    a single-mode file (``psi4_mode_l2m0.dat``) already is one mode and ignores
    it.
    """
    parts = []
    for spec in specs:
        p = pathlib.Path(spec).expanduser()
        path = p if p.is_file() else find_packed(spec, pack_root) / stream
        # A combined stream names its columns; a single-mode one carries an
        # `r =` header instead.  Decide on the file, not on its name -- the
        # hand-stitched full-history file is combined and called neither.
        if m is not None:
            try:
                t, modes = streams.load_l2_all(path)
            except ValueError:
                t, by_r = streams.load_mode(path)
            else:
                by_r = {r: z for (mm, r), z in modes.items() if mm == m}
                if not by_r:
                    raise SystemExit(f"no m = {m} in {path}")
        else:
            t, by_r = streams.load_mode(path)
        parts.append((t, by_r))
    parts.sort(key=lambda x: x[0][0])
    radii = sorted(parts[0][1])
    t_out, series, seams = parts[0][0], {r: parts[0][1][r] for r in radii}, []
    for t_next, by_r in parts[1:]:
        keep = t_out < t_next[0]
        seams.append(float(t_next[0]))
        t_out = np.concatenate([t_out[keep], t_next])
        series = {r: np.concatenate([series[r][keep], by_r[r]]) for r in radii}
    return t_out, radii, series, seams


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=DEFAULT_RUN,
                    help="run name, a path to a stream, or a '+'-joined restart chain")
    ap.add_argument("--group", default=DEFAULT_GROUP, help="figures/<group> to write into")
    ap.add_argument("--name", default=None, help="figure stem (default: psi4_analysis_<run>)")
    ap.add_argument("--stream", default=STREAM)
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--radii", type=float, nargs="*", default=None,
                    help="spheres to draw (default: every one in the stream)")
    ap.add_argument("--t-min", type=float, default=None)
    ap.add_argument("--t-max", type=float, default=None)
    ap.add_argument("--f-max", type=float, default=1.0, help="upper frequency on panel (c)")
    ap.add_argument("--wavelet-w", type=float, default=6.0,
                    help="Morlet cycles per wavelet on panel (e): higher = sharper in "
                         "frequency, wider cone of influence")
    ap.add_argument("--f-min", type=float, default=None,
                    help="lower frequency on panel (e) (default: 1.5 cycles per record)")
    ap.add_argument("--mass-msun", type=float, default=30.0)
    ap.add_argument("--distance-mpc", type=float, default=10.0)
    ap.add_argument("--psd-smooth-window", type=int, default=21)
    ap.add_argument("--psd-smooth-polyorder", type=int, default=5)
    ap.add_argument("--no-qnm", action="store_true")
    ap.add_argument("--m", type=int, default=None,
                    help="azimuthal mode to take out of a combined l = 2 stream")
    ap.add_argument("--mode-label", default=None,
                    help="the (l,m) written on the axes (default: 2,<m> or 2,0)")
    args = ap.parse_args(argv)

    names = args.run.split("+")
    t, radii_all, series, seams = load_chain(names, args.pack_root, args.stream, args.m)
    radii = [r for r in (args.radii or radii_all) if r in series]
    if not radii:
        raise SystemExit(f"none of {args.radii} in the stream (has {radii_all})")
    mode = args.mode_label or f"2,{args.m if args.m is not None else 0}"
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    # These streams are one row per plotfile, so the sampling can be as coarse
    # as dt = 1 and nothing above fs/2 exists.  Drawing a spectrum out to a
    # requested 1.0 when Nyquist is 0.5 puts half the panel in dead space and
    # invites reading the roll-off at the edge as physics.
    f_nyq = 0.5 * fs
    f_max = min(args.f_max, f_nyq)

    print(f"[psi4-analysis] {' + '.join(names)}: t = {t[0]:.2f} .. {t[-1]:.2f}, "
          f"{len(t)} rows, spheres {', '.join(f'{r:g}' for r in radii)}")
    if seams:
        print(f"[psi4-analysis] restart seams at t = {', '.join(f'{s:.2f}' for s in seams)} "
              "-- panels (c)-(f) carry their step")

    spectra = {r: _burst_psd(series[r], fs) for r in radii}

    style.paper(base=10.0)
    fig, axes = plt.subplots(3, 2, figsize=(11.0, 11.4), constrained_layout=True)

    # Radii are an ORDERED family, so they take the ordinal ramp (light = near,
    # dark = far) rather than four unrelated hues, and carry the dash cycle
    # too, so the panel survives a greyscale print.
    kws = style.ordinal_series(len(radii), lw=1.2)
    lbl = [rf"$R={r:g}$" for r in radii]

    def window(x):
        m = np.ones_like(x, dtype=bool)
        if args.t_min is not None:
            m &= x >= args.t_min
        if args.t_max is not None:
            m &= x <= args.t_max
        return m

    # ---- (a) the waveform, on simulation time ---------------------------
    ax = axes[0, 0]
    for i, r in enumerate(radii):
        m = window(t)
        ax.plot(t[m], np.real(series[r])[m], label=lbl[i], **kws[i])
    for s in seams:
        ax.axvline(s, color=style.FAINT, ls=(0, (1, 2)), lw=0.8)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(rf"$r\,\mathrm{{Re}}\,\Psi_4^{{{mode}}}$")
    ax.legend(loc="upper right", ncols=len(radii), columnspacing=1.2)

    # ---- (b) retarded time: does it collapse onto one curve? ------------
    ax = axes[0, 1]
    for i, r in enumerate(radii):
        x = t - r
        m = window(x)
        ax.plot(x[m], np.real(series[r])[m], **kws[i])
    qnm = None if args.no_qnm else _fit_qnm(t, series[radii[0]], radii[0])
    if qnm is not None:
        tq = np.linspace(qnm["t_ret_start"], qnm["t_ret_end"], 300)
        ax.plot(tq, _damped_sinusoid(tq - qnm["t_ret_start"], qnm["A"], qnm["tau"],
                                     qnm["f_qnm"], qnm["phi"]),
                label=rf"ringdown fit: $f={qnm['f_qnm']:.3f}$, $\tau={qnm['tau']:.1f}$",
                **style.series(2, lw=1.6))
        ax.legend(loc="upper right")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.set_ylabel(rf"$r\,\mathrm{{Re}}\,\Psi_4^{{{mode}}}$")

    # ---- (c) where the power is -----------------------------------------
    ax = axes[1, 0]
    for i, r in enumerate(radii):
        f, p = spectra[r]
        ps = _smooth_psd(p, args.psd_smooth_window, args.psd_smooth_polyorder)
        m = f <= f_max
        ax.semilogy(f[m], ps[m], **kws[i])
    ax.set_xlim(0, f_max)
    ax.set_xlabel(r"$f\ (M^{-1})$")
    ax.set_ylabel(rf"$\mathrm{{PSD}}\left[r\,\Psi_4^{{{mode}}}\right]$")

    # ---- (d) is it moving at the speed of light? ------------------------
    ax = axes[1, 1]
    peaks = _find_peak_times(t, series, radii)
    speeds = _compute_propagation_speeds(radii, peaks, t, series)
    for i, r in enumerate(radii):
        x = t - r
        m = window(x)
        ax.plot(x[m], np.abs(series[r])[m], **kws[i])
    # The matched wavefront: the peak the speed was actually measured on.
    ref = peaks[radii[0]][0][0] - radii[0]
    for i, r in enumerate(radii):
        t_pk = min((p[0] for p in peaks[r]), key=lambda tp: abs(tp - r - ref))
        j = int(np.argmin(np.abs(t - t_pk)))
        ax.plot(t_pk - r, np.abs(series[r])[j], marker="o", ms=5, zorder=6,
                color=style.BURGUNDY, mec=style.GROUND, mew=0.8)
    if speeds:
        ax.annotate("\n".join(rf"$R={a:g}\rightarrow{b:g}$:  $v={v:.3f}\,c$"
                              for a, b, v in speeds),
                    xy=(0.02, 0.97), xycoords="axes fraction", va="top",
                    fontsize=8.5, color=style.MUTED, linespacing=1.5)
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.set_ylabel(rf"$|r\,\Psi_4^{{{mode}}}|$")

    # ---- (e) does the frequency move? -----------------------------------
    ax = axes[2, 0]
    R_spec = radii[0]
    # The band has to contain the signal.  A fixed 0.1 floor was above this
    # arm's entire wave -- its swings have a period near 33, i.e. f ~ 0.03 --
    # so the panel showed nothing but the wavelet running off the ends of the
    # record.  Bottom of the band = 1.5 cycles across the record, which is the
    # slowest thing the record can be said to resolve.
    T_rec = float(t[-1] - t[0])
    f_lo = args.f_min if args.f_min else max(1.5 / T_rec, 1e-4)
    f_hi = f_max
    freqs, amp = wavelet_amplitude(np.real(series[R_spec]), dt, f_lo, f_hi, w=args.wavelet_w)
    x = t - R_spec
    pcm = ax.pcolormesh(x, freqs, amp, shading="auto", cmap=style.SEQUENTIAL,
                        vmin=0.0, vmax=1.0, rasterized=True)
    # Cone of influence: within sqrt(2)*s of either end the wavelet overlaps
    # the edge of the record and its amplitude is an artefact of the taper, not
    # of the wave.  Cross-hatched, so the bright corners cannot be read as a
    # burst -- which is exactly how they read before.
    coi = np.sqrt(2.0) * args.wavelet_w / (2.0 * np.pi * freqs)
    for lo_e, hi_e in ((x[0] * np.ones_like(coi), x[0] + coi), (x[-1] - coi, x[-1] * np.ones_like(coi))):
        ax.fill_betweenx(freqs, lo_e, hi_e, facecolor="none", hatch="///",
                         edgecolor=style.GROUND, linewidth=0.0, alpha=0.32, zorder=3)
    for edge in (x[0] + coi, x[-1] - coi):
        ax.plot(edge, freqs, color=style.GROUND, lw=0.9, zorder=4)
    cb = fig.colorbar(pcm, ax=ax, pad=0.02)
    cb.set_label(r"$|W|$, normalised", fontsize=9)
    cb.ax.tick_params(labelsize=8, color=style.FAINT)
    cb.outline.set_edgecolor(style.FAINT)
    ax.set_yscale("log")
    ax.set_ylim(f_lo, f_hi)
    ax.set_yticks([x for x in (0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0)
                   if f_lo <= x <= f_hi])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.set_ylabel(r"$f\ (M^{-1})$")
    ax.grid(False)   # a grid over a heatmap is a fifth colour on top of four

    # ---- (f) what an instrument would see -------------------------------
    ax = axes[2, 1]
    R_strain = radii[-1]
    f_code, p_code = spectra[R_strain]
    strain_code = _psd_psi4_to_strain(
        f_code, _smooth_psd(p_code, args.psd_smooth_window, args.psd_smooth_polyorder))
    f_hz, S_h = _scale_to_physical(f_code, strain_code, args.mass_msun, args.distance_mpc)
    ok = (f_hz > 0) & np.isfinite(S_h) & (S_h > 0)
    ax.loglog(f_hz[ok], np.sqrt(S_h[ok]),
              label=rf"signal at $R={R_strain:g}$", **style.series(0, lw=1.4))
    noise = _aLIGO_noise_psd(f_hz)
    fin = np.isfinite(noise)
    ax.loglog(f_hz[fin], np.sqrt(noise[fin]), label="Advanced LIGO design",
              **style.series(3, lw=1.2))
    # The matched-filter S/N is printed, not drawn: this spectrum is a crude
    # burst estimate whose low-frequency end is set by a high-pass cut, and the
    # integral is dominated by exactly that end. It is an order of magnitude,
    # and an order of magnitude does not belong on a figure as a number.
    snr = _compute_snr(f_hz, S_h, noise)
    ax.annotate(rf"$M={args.mass_msun:g}\,M_\odot$,  $D={args.distance_mpc:g}$ Mpc",
                xy=(0.02, 0.04), xycoords="axes fraction", va="bottom",
                fontsize=8.5, color=style.MUTED)
    ax.set_xlabel(r"$f$ (Hz)")
    ax.set_ylabel(r"$\sqrt{S(f)}\ \ (\mathrm{Hz}^{-1/2})$")
    ax.legend(loc="upper right")

    titles = [
        "(a) waveform",
        "(b) retarded time, and the ringdown fit",
        "(c) power spectrum",
        "(d) envelope and the matched wavefront",
        rf"(e) spectrogram at $R={R_spec:g}$ (hatched: edge of the record)",
        "(f) strain against Advanced LIGO",
    ]
    for ax, title in zip(axes.flatten(), titles):
        ax.set_title(title, loc="left")

    E_rad = _compute_radiated_energy(t, series[radii[0]])
    print(f"[psi4-analysis] radiated energy at R = {radii[0]:g}: {E_rad:.4e} M")
    for a, b, v in speeds:
        print(f"[psi4-analysis] wavefront R = {a:g} -> {b:g}: v = {v:.4f} c")
    if qnm is not None:
        print(f"[psi4-analysis] ringdown fit at R = {radii[0]:g}: "
              f"f = {qnm['f_qnm']:.4f} 1/M, tau = {qnm['tau']:.2f} M")
    print(f"[psi4-analysis] Nyquist {f_nyq:.3f} 1/M (dt = {dt:g}); spectra drawn to {f_max:.3f}")
    print(f"[psi4-analysis] order-of-magnitude S/N at {args.mass_msun:g} Msun, "
          f"{args.distance_mpc:g} Mpc: {snr:.3g}")

    stem = args.name or f"psi4_analysis_{names[-1]}"
    out = pathlib.Path(args.out) if args.out else figure_dir(args.group, args.pack_root)
    png = style.save(fig, (out / f"{stem}.png") if out.is_dir() else out)
    print(f"[psi4-analysis] wrote {png} (+pdf)")
    return 0


def wavelet_amplitude(y: np.ndarray, dt: float, f_lo: float, f_hi: float,
                      n_freq: int = 220, w: float = 8.0):
    """Normalised Morlet wavelet amplitude |W(f, t)| on a log frequency grid.

    A wavelet transform rather than a fixed-window spectrogram: the interesting
    question here is whether the frequency MOVES, and a fixed window either
    resolves the low frequencies or the late ones, not both.
    """
    from scipy.signal import fftconvolve

    freqs = np.logspace(np.log10(f_lo), np.log10(f_hi), n_freq)
    n = len(y)
    pad = n // 2
    yp = np.pad(y, (pad, pad))
    tw = np.arange(-len(yp) // 2, len(yp) // 2) * dt
    amp = np.empty((n_freq, n))
    for i, f in enumerate(freqs):
        s = w / (2.0 * np.pi * f)
        psi = np.exp(2j * np.pi * f * tw) * np.exp(-tw ** 2 / (2.0 * s ** 2))
        psi *= (np.pi * s ** 2) ** -0.25
        amp[i] = np.abs(fftconvolve(yp, psi, mode="same")[pad:pad + n])
    peak = float(np.nanmax(amp))
    return freqs, np.nan_to_num(amp / peak if peak > 0 else amp)


if __name__ == "__main__":
    raise SystemExit(main())
