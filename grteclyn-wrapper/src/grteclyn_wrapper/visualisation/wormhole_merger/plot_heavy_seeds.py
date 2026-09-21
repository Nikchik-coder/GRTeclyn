#!/usr/bin/env python3
r"""The heavy-seed channel, drawn: the seed race and the LISA band.

Article Sec. XI B claims two things that are arithmetic on measured numbers,
and this figure is that arithmetic made visible.  Nothing here reads a run;
every campaign number is quoted from the frozen pack (E_rad/M of Sec. IX B,
the (fM) peaks of Sec. X C, the conversion times of Table II) and every
astrophysical number carries its reference in the article's bibliography.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_heavy_seeds

PANEL (a) -- THE SEED RACE.  Black-hole mass against cosmic time.  A drainhole
population of 10^4-10^6 M_sun converts to black holes at birth (z ~ 20, in
seconds to minutes -- Table II), so its reachable region is bounded below by
the lightest seed idling and above by the heaviest seed's Eddington ceiling
(Salpeter e-fold 45 Myr).  The JWST points -- UHZ1, GN-z11, a z = 7.5 quasar,
the little-red-dot box -- sit inside that region and ABOVE the ceiling of a
100 M_sun light seed started at z = 25: the light seed misses UHZ1 by two
decades at continuous Eddington, which is the heavy-seed timing argument in
one picture [Bogdan 2024; Natarajan 2024; Inayoshi 2020].

PANEL (b) -- THE FALSIFIABLE PART.  The conversion background against LISA.
Omega_GW = n E_rad / (rho_c (1+z_e)) per mass decade, each box spanning the
measured energy range (spiral 2.2e-2 M to fly-by 7.4e-2 M) and the
one-seed-per-galaxy abundance range (n = 1e-4 to 1e-2 Mpc^-3), at the
observed frequency f = (fM)_peak / [M (1+z_e)] with the measured
(fM)_peak = 0.03-0.06.  The ink curve is the 4-yr power-law-integrated
sensitivity built from the standard analytic LISA noise model
(Robson-Cornish-Liu 2019, SNR = 10): the 10^5-10^6 M_sun boxes straddle it.
A pure burst population -- Sec. XI A forbids inspirals -- so no f^(2/3) ramp.

STYLE: PRD frame, two panels side by side.  GOLD is spent on the channel the
page introduces (the drainhole seeds and their background); the light-seed
ceiling is CONTEXT; observations are INK.  Cosmology: flat LCDM,
H0 = 67.7 km/s/Mpc, Om = 0.31.
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import figure_dir  # noqa: E402

# --- cosmology (flat LCDM) -------------------------------------------------
H0_KMSMPC = 67.7
OMEGA_M = 0.31
OMEGA_L = 1.0 - OMEGA_M
H0_PER_MYR = H0_KMSMPC / (3.0857e19 * 1.0e-6) * (3.1557e7 * 1.0e6) / 1.0e6  # placeholder, set below
# 1/H0 in Myr: (Mpc/km) s * (Myr/s)
H0_INV_MYR = (3.0857e19 / H0_KMSMPC) / 3.1557e13
RHO_C_MSUN_MPC3 = 2.775e11 * (H0_KMSMPC / 100.0) ** 2  # critical density
MSUN_S = 4.9255e-6  # GM_sun/c^3 in seconds


def t_of_z(z: np.ndarray | float) -> np.ndarray | float:
    """Cosmic time in Myr, matter + Lambda (exact for a flat universe)."""
    a32 = np.asarray(1.0 + z, dtype=float) ** -1.5
    return (2.0 / 3.0) * H0_INV_MYR / math.sqrt(OMEGA_L) * np.arcsinh(
        math.sqrt(OMEGA_L / OMEGA_M) * a32
    )


# --- the campaign's measured numbers (frozen pack) -------------------------
E_OVER_M = (2.2e-2, 7.4e-2)   # spiral .. fly-by, Sec. IX B
FM_PEAK = (0.03, 0.06)        # resolved Psi4 peaks across channels, Sec. X C
Z_EMIT = 20.0
SALPETER_MYR = 45.0
SEED_RANGE = (1.0e4, 1.0e6)   # the Table-II decade band the section quotes
N_RANGE = (1.0e-4, 1.0e-2)    # one seed per massive galaxy, comoving Mpc^-3

# --- the observed population (refs in the article's bibliography) ----------
UHZ1 = (10.07, 4.0e7, 1.0e7, 1.0e8)       # z, M, lo, hi  [Bogdan/Natarajan 2024]
GNZ11 = (10.60, 1.6e6, 8.0e5, 3.2e6)      # [Maiolino et al. 2024]
J1342 = (7.54, 7.8e8, 4.5e8, 1.1e9)       # ULAS J1342+0928
LRD_BOX = ((4.5, 8.0), (1.0e6, 1.0e8))    # z-range, M-range [Greene/Matthee 2024]


def eddington(t_myr: np.ndarray, t0: float, m0: float) -> np.ndarray:
    return m0 * np.exp(np.clip(t_myr - t0, 0.0, None) / SALPETER_MYR)


def panel_seed_race(ax) -> None:
    t_birth = float(t_of_z(Z_EMIT))            # ~180 Myr
    t_light = float(t_of_z(25.0))              # ~130 Myr
    t = np.linspace(100.0, 1600.0, 600)

    # Reachable region of the drainhole seeds: idle floor to Eddington ceiling.
    lo = np.where(t >= t_birth, SEED_RANGE[0], np.nan)
    hi = np.where(t >= t_birth, eddington(t, t_birth, SEED_RANGE[1]), np.nan)
    ax.fill_between(t, lo, hi, color=style.GOLD, alpha=0.18, lw=0.0, zorder=1)
    mid = eddington(t[t >= t_birth], t_birth, 1.0e5)
    ax.plot(t[t >= t_birth], mid, **style.series(2))
    ax.plot(t[t >= t_birth], eddington(t[t >= t_birth], t_birth, SEED_RANGE[1]),
            color=style.GOLD, lw=0.9, ls="-", zorder=2)
    ax.plot(t[t >= t_birth], np.full((t >= t_birth).sum(), SEED_RANGE[0]),
            color=style.GOLD, lw=0.9, ls="-", zorder=2)

    # The conversion itself: full seed mass at birth, in minutes (Table II).
    ax.plot([t_birth, t_birth], [SEED_RANGE[0], SEED_RANGE[1]],
            color=style.GOLD, lw=2.6, solid_capstyle="butt", zorder=3)

    # The light-seed control: 100 M_sun at z = 25, same ceiling rule.
    ax.plot(t[t >= t_light], eddington(t[t >= t_light], t_light, 1.0e2),
            **style.series(3))

    # Observations.
    for (z, m, mlo, mhi), name, dx, dy in (
        (UHZ1, "UHZ1", -30.0, 3.2), (GNZ11, "GN-z11", 25.0, 0.28),
        (J1342, "J1342+0928", 28.0, 0.28),
    ):
        tz = float(t_of_z(z))
        ax.errorbar([tz], [m], yerr=[[m - mlo], [mhi - m]], fmt="o",
                    color=style.INK, ms=4.5, capsize=2.0, lw=0.9, zorder=4)
        ax.text(tz + dx, m * dy, name, color=style.INK, fontsize=8.0,
                ha="left" if dx > 0 else "right", va="center", zorder=5,
                bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))
    (z0, z1), (m0, m1) = LRD_BOX
    ax.fill_between([float(t_of_z(z1)), float(t_of_z(z0))], m0, m1,
                    facecolor="none", edgecolor=style.INK, lw=0.8, zorder=3,
                    hatch="///")
    ax.text(float(t_of_z(4.9)), 2.6e6, "little red dots", color=style.INK,
            fontsize=8.0, ha="center", va="center",
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.2))

    # Curve names in place, no boxed key.
    ax.text(1560.0, 1.35e10, r"drainhole reachable region:" "\n"
            r"seeds $10^{4}$--$10^{6}\,M_\odot$ at $z\simeq20$," "\n"
            r"converted in minutes (Table II)", color="#8b5c00", fontsize=8.0,
            ha="right", va="top", zorder=5,
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.2))
    ax.text(135.0, 3.0e8, "Eddington\nceilings\n" r"($t_e=45$ Myr)",
            color=style.GOLD, fontsize=8.0, ha="left", va="center", zorder=5,
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))
    ax.text(1230.0, 3.0e4, r"$10^2\,M_\odot$ light seed, $z=25$",
            color=style.CONTEXT, fontsize=8.0, ha="center", va="center",
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))

    ax.set_yscale("log")
    ax.set_xlim(100.0, 1600.0)
    ax.set_ylim(1.0e2, 2.0e10)
    ax.set_xlabel(r"cosmic time [Myr]")
    ax.set_ylabel(r"$M_{\rm BH}$ [$M_\odot$]")

    # Redshift on the top edge of the same axis (one scale, relabelled).
    zt = np.array([20.0, 15.0, 10.0, 8.0, 7.0, 6.0, 5.0, 4.0])
    sec = ax.secondary_xaxis("top")
    sec.set_xticks([float(t_of_z(z)) for z in zt])
    sec.set_xticklabels([f"{z:g}" for z in zt])
    sec.tick_params(labelsize=8.0)
    sec.set_xlabel(r"redshift $z$", fontsize=9.0)


def lisa_pls(f: np.ndarray, years: float = 4.0, snr: float = 10.0) -> np.ndarray:
    """Power-law-integrated sensitivity from the analytic LISA noise model
    (Robson, Cornish & Liu 2019, Eq. 13), Thrane-Romano construction."""
    L, fstar = 2.5e9, 1.909e-2
    p_oms = (1.5e-11) ** 2 * (1.0 + (2.0e-3 / f) ** 4)
    p_acc = (3.0e-15) ** 2 * (1.0 + (0.4e-3 / f) ** 2) * (1.0 + (f / 8.0e-3) ** 4)
    s_n = (10.0 / (3.0 * L**2)) * (p_oms + 4.0 * p_acc / (2.0 * math.pi * f) ** 4) \
        * (1.0 + 0.6 * (f / fstar) ** 2)
    h0_s = H0_KMSMPC / 3.0857e19
    omega_n = (4.0 * math.pi**2 / (3.0 * h0_s**2)) * f**3 * s_n
    T = years * 3.1557e7
    fref = 1.0e-3
    lo = np.log(f)
    pls = np.zeros_like(f)
    for beta in np.linspace(-8.0, 8.0, 81):
        integ = np.trapezoid((f / fref) ** (2.0 * beta) / omega_n**2 * f, lo)
        a_beta = snr / math.sqrt(2.0 * T * integ)
        pls = np.maximum(pls, a_beta * (f / fref) ** beta)
    return pls


def panel_lisa(ax) -> None:
    f = np.logspace(-5.0, -0.5, 400)
    ax.plot(f, lisa_pls(f), **style.series(0))
    ax.text(6.0e-3, 3.0e-9, "LISA, 4 yr\npower-law integrated",
            color=style.INK, fontsize=8.0, ha="center", va="center",
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))

    denom = RHO_C_MSUN_MPC3 * (1.0 + Z_EMIT)
    for mass, label in ((1.0e4, r"$10^{4}\,M_\odot$"),
                        (1.0e5, r"$10^{5}\,M_\odot$"),
                        (1.0e6, r"$10^{6}\,M_\odot$")):
        f_lo = FM_PEAK[0] / (mass * MSUN_S * (1.0 + Z_EMIT))
        f_hi = FM_PEAK[1] / (mass * MSUN_S * (1.0 + Z_EMIT))
        o_lo = N_RANGE[0] * E_OVER_M[0] * mass / denom
        o_hi = N_RANGE[1] * E_OVER_M[1] * mass / denom
        ax.fill_between([f_lo, f_hi], o_lo, o_hi, color=style.GOLD, alpha=0.42,
                        lw=0.0, zorder=2)
        ax.plot([f_lo, f_hi, f_hi, f_lo, f_lo], [o_lo, o_lo, o_hi, o_hi, o_lo],
                color=style.GOLD, lw=0.9, zorder=3)
        ax.text(math.sqrt(f_lo * f_hi), o_hi * 1.9, label, color=style.INK,
                fontsize=8.0, ha="center", va="bottom", zorder=5,
                bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))

    ax.text(1.3e-5, 1.8e-15,
            r"$n=10^{-4}$--$10^{-2}\,{\rm Mpc}^{-3}$, "
            r"$E/M=2.2$--$7.4\times10^{-2}$, $z_e\simeq20$" "\n"
            r"burst population: no $f^{2/3}$ inspiral ramp (Sec. XI A)",
            color=style.MUTED, fontsize=7.4, ha="left", va="bottom",
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-5, 3.0e-1)
    ax.set_ylim(1.0e-15, 1.0e-8)
    ax.set_xlabel(r"$f_{\rm obs}$ [Hz]")
    ax.set_ylabel(r"$\Omega_{\rm GW}$")


def main() -> None:
    style.prd()
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 3.15))
    panel_seed_race(ax_a)
    panel_lisa(ax_b)
    for ax, tag in ((ax_a, "(a)"), (ax_b, "(b)")):
        ax.text(0.02, 0.975, tag, transform=ax.transAxes, ha="left", va="top",
                fontsize=10.0, color=style.INK)
    fig.tight_layout(w_pad=1.6)
    out = style.save(fig, figure_dir("08_waves") / "heavy_seeds")
    print(out)


if __name__ == "__main__":
    main()
