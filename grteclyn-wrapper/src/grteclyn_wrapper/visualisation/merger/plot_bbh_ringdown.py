"""BBH control t150: full ringdown at the outer sphere, with QNM fit.

GPU_PLAN #2 close-out figure: the t = 150 rerun exists to deliver the
ringdown tail that the t100 run cut at 96 % of peak.  Panels: (a) Re/Im
of the (2,2) mode at R = 30 over the whole run, (b) log-envelope with
the fitted exponential decay and the fit window marked.

Reads the in-code extraction stream from the results pack; writes
bbh_t150_ringdown.png/.pdf into the pack's figures directory.
"""

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

R_PLOT = 30.0


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[5]
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-root", default=str(root / "results" / "merger"))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    pack = pathlib.Path(args.pack_root)
    if args.out is None:
        args.out = str(pack / "figures")

    stream = (pack / "campaign" / "bbh_control_d12_p012_t150"
              / "weyl_extraction_mode_22.dat")
    a = np.loadtxt(stream)
    t = a[:, 0]
    z = a[:, 7] + 1j * a[:, 8]  # R = 30 pair
    env = np.abs(z)
    ip = int(np.argmax(env))

    # QNM fit: single damped sinusoid z ~ A exp(i(om t + phi) + sl t) on the
    # tail, starting late enough that the merger transient has cleared
    w = (t > t[ip] + 8) & (t < t[-1] - 1)
    ph = np.unwrap(np.angle(z[w]))
    om, phi0 = np.polyfit(t[w], ph, 1)
    sl, lnA0 = np.polyfit(t[w], np.log(env[w]), 1)
    period, tau = 2 * np.pi / abs(om), -1 / sl
    z_fit = np.exp(lnA0 + sl * t[w]) * np.exp(1j * (om * t[w] + phi0))
    # known-answer comparison: Kerr (2,2,0) for the ~1.9 M remnant;
    # Schwarzschild reference T = 16.8 M, tau = 11.2 M — spin shortens T
    M_F = 1.9

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Computer Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "axes.labelsize": 13,
        "axes.titlesize": 14,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.linewidth": 1.1,
        "legend.fontsize": 10,
    })

    fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    ax = axs[0]
    ax.plot(t - R_PLOT, np.real(z), color="black", lw=1.0, label=r"$\mathrm{Re}$")
    ax.plot(t - R_PLOT, np.imag(z), color="#9b2226", lw=1.0, ls="--",
            label=r"$\mathrm{Im}$")
    ax.plot(t[w] - R_PLOT, np.real(z_fit), color="#0a9396", lw=1.6, ls=":",
            label=rf"QNM fit: $T={period:.1f}$, $\tau={tau:.1f}$")
    ax.set_title(r"(a) $\Psi_4^{2,2}$ mode at $R=30$, BBH control to $t=150$")
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)
    ax.annotate(
        rf"per $M_f\!\approx\!{M_F}$:  $T={period / M_F:.1f}M$, "
        rf"$\tau={tau / M_F:.1f}M$"
        "\n"
        r"Kerr $(2,2,0)$ ref (Schw.): $T=16.8M$, $\tau=11.2M$",
        xy=(0.98, 0.04), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=10, bbox=dict(boxstyle="round", fc="white", alpha=0.85))

    ax = axs[1]
    ax.semilogy(t - R_PLOT, env, color="black", lw=1.0)
    tw = t[w]
    ax.semilogy(tw - R_PLOT, env[w][0] * np.exp(sl * (tw - tw[0])),
                color="#9b2226", lw=1.4, ls="--",
                label=rf"fit: $T={period:.1f}$, $\tau={tau:.1f}$")
    ax.axvspan(tw[0] - R_PLOT, tw[-1] - R_PLOT, color="0.9", zorder=0)
    ax.set_title(r"(b) $|\Psi_4^{2,2}|$ envelope and exponential ringdown fit")
    ax.set_xlabel(r"$t - R_{\mathrm{ext}}$")
    ax.legend(loc="lower left", frameon=True, framealpha=0.9)

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"bbh_t150_ringdown.{ext}", dpi=150,
                    bbox_inches="tight")
    print(f"[ringdown] wrote {out / 'bbh_t150_ringdown.png'} (+pdf); "
          f"fit period {period:.2f}, tau {tau:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
