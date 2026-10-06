"""BBH control t150: the full ringdown at the outer sphere, with its QNM fit.

GPU_PLAN #2 close-out figure: the t = 150 rerun exists to deliver the ringdown
tail that the t100 run cut at 96 % of peak.  Panels: (a) Re/Im of the (2,2)
mode at R = 30 over the whole run, (b) the log envelope with the fitted
exponential decay and the fit window marked.

This is the known-answer calibration for every other waveform in the campaign:
a vacuum binary must ring down at the Kerr frequency of its remnant, and the
figure exists to show that this instrument does.

Reads the in-code extraction stream from the pack, resolved BY NAME wherever
the run is filed; writes bbh_t150_ringdown.png/.pdf into figures/07_bbh_control.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import figure_dir, find_packed  # noqa: E402

RUN = "bbh_control_d12_p012_t150"
R_PLOT = 30.0
M_F = 1.9   # remnant mass; the Schwarzschild reference below is quoted per M_f


def series_at(run_dir: pathlib.Path, radius: float):
    """(t, complex (2,2) mode) from whichever stream this run carries.

    The t150 rerun was packed with the combined l = 2 stream; the t100 control
    with one file per mode.  Reading the combined file by COLUMN INDEX is what
    silently broke this figure when the pack was refiled, so both shapes are
    named here and neither is assumed.
    """
    combined = run_dir / "psi4_mode_l2_all.dat"
    if combined.exists():
        t, modes = streams.load_l2_all(combined)
        return t, modes[(2, radius)]
    per_mode = run_dir / "weyl_extraction_mode_22.dat"
    t, by_r = streams.load_mode(per_mode)
    return t, by_r[radius]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=RUN, help="run name, resolved in the pack")
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run_dir = find_packed(args.run, args.pack_root)
    t, z = series_at(run_dir, R_PLOT)
    env = np.abs(z)
    ip = int(np.argmax(env))

    # QNM fit: one damped sinusoid z ~ A exp(i(om t + phi) + sl t) on the tail,
    # started late enough that the merger transient has cleared.
    w = (t > t[ip] + 8) & (t < t[-1] - 1)
    ph = np.unwrap(np.angle(z[w]))
    om, phi0 = np.polyfit(t[w], ph, 1)
    sl, lnA0 = np.polyfit(t[w], np.log(env[w]), 1)
    period, tau = 2 * np.pi / abs(om), -1 / sl
    z_fit = np.exp(lnA0 + sl * t[w]) * np.exp(1j * (om * t[w] + phi0))

    style.paper(base=10.0)
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 6.0), sharex=True,
                            constrained_layout=True)

    # (a) the mode.  Re and Im are the two halves of one complex series, not
    # two competing measurements, so they take the first two slots and the fit
    # -- which is a model, not data -- takes the recessive one.
    ax = axs[0]
    ax.plot(t - R_PLOT, np.real(z), label=r"$\mathrm{Re}\,\Psi_4^{2,2}$", **style.series(0, lw=1.0))
    ax.plot(t - R_PLOT, np.imag(z), label=r"$\mathrm{Im}\,\Psi_4^{2,2}$", **style.series(1, lw=1.0))
    ax.plot(t[w] - R_PLOT, np.real(z_fit),
            label=rf"ringdown fit:  $T={period:.1f}$, $\tau={tau:.1f}$",
            **style.series(2, lw=1.6))
    ax.set_ylabel(r"$\Psi_4^{2,2}$")
    ax.set_title(rf"(a) the $(2,2)$ mode at $R={R_PLOT:g}$, BBH control to $t=150$", loc="left")
    # Room below the trough for the calibration numbers: they are the point of
    # the panel and must not be read through the curve.  The note goes down
    # first so the key knows it is there and picks another corner.
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo - 0.30 * (hi - lo), hi)
    style.note(
        ax,
        rf"per $M_f\!\approx\!{M_F}$:  $T={period / M_F:.1f}\,M$,  $\tau={tau / M_F:.1f}\,M$"
        "\n"
        r"Schwarzschild $(2,2,0)$:  $T=16.8\,M$,  $\tau=11.2\,M$",
        loc="lower right", fontsize=8.5)
    style.legend(ax, ncols=3, columnspacing=1.4)

    # (b) the envelope.  The fit window is a band, not a line: it says which
    # part of the curve the two numbers above were measured on.
    ax = axs[1]
    tw = t[w]
    ax.axvspan(tw[0] - R_PLOT, tw[-1] - R_PLOT, color=style.GRID, lw=0, zorder=0)
    ax.annotate("fit window", (0.5 * (tw[0] + tw[-1]) - R_PLOT, 1.0),
                xycoords=("data", "axes fraction"), xytext=(0, -4),
                textcoords="offset points", ha="center", va="top",
                fontsize=8.5, color=style.MUTED)
    ax.semilogy(t - R_PLOT, env, **style.series(0, lw=1.0))
    ax.semilogy(tw - R_PLOT, env[w][0] * np.exp(sl * (tw - tw[0])),
                label=rf"$\exp(-t/\tau)$,  $\tau={tau:.1f}$", **style.series(2, lw=1.6))
    ax.set_ylabel(r"$|\Psi_4^{2,2}|$")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.set_title("(b) envelope and the fitted exponential decay", loc="left")
    style.legend(ax)

    out = pathlib.Path(args.out) if args.out else figure_dir("07_bbh_control", args.pack_root)
    png = style.save(fig, (out / "bbh_t150_ringdown.png") if out.is_dir() else out)
    print(f"[ringdown] wrote {png} (+pdf); period {period:.2f}, tau {tau:.2f} "
          f"({period / M_F:.2f} / {tau / M_F:.2f} per M_f = {M_F})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
