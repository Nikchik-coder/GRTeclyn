#!/usr/bin/env python3
r"""The heavy-seed channel, drawn: the seed race, the LISA band, the population curve.

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

PANEL (c) -- THE POPULATION CURVE (2026-09-24, the first author's request:
"draw the statistical curve ... how much was needed to provide what Lambda
requires").  Omega today against the comoving MASS density of converting
wormholes, n M, on which alone both deposits depend: Omega_GW (gold, E/M over
the measured range) and the negative scalar deposit |Omega_phi,0| (blue,
|E_phi| = r E_GW with r = 0.8-3.2, every estimator of Sec. VIII F), both
radiation-like, Omega_0 = n E / [rho_c (1+z_e)] at z_e = 20.  Solid up to the
dark-matter ceiling n M = rho_DM (vertical rule), where they reach at most
(E/M) Omega_c/(1+z_e) = 3e-3; faint beyond it, where they would meet
Omega_Lambda only at Omega_WH = n M / rho_c = 60-800 (top axis).  Dotted:
H^2 > 0 at z_e caps any radiation-like negative deposit at Omega_m/(1+z_e).
Ink ticks: the PLS of panel (b) at each mass's band, where the gold band meets
it.  Grey: the little-red-dot abundance, (3.4-6.2)e-5 Mpc^-3 summed over the
published bins (Matthee+2024 Tables 4 and 6; Greene+2024 Tables 4 and 5),
seeded at 10^4-10^6 M_sun.

STYLE: PRD frame, three panels in one row.  GOLD is spent on the channel the
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

SCALAR_RATIO = (0.8, 3.2)     # |E_phi|/E_GW, extremes over the Sec. VIII F estimators
RHO_DM_MSUN_MPC3 = 0.1200 * 2.775e11   # Planck 2018 Omega_c h^2 (the ledger's f_DM)

# --- the observed population (refs in the article's bibliography) ----------
UHZ1 = (10.07, 4.0e7, 1.0e7, 1.0e8)       # z, M, lo, hi  [Bogdan/Natarajan 2024]
GNZ11 = (10.60, 1.6e6, 8.0e5, 3.2e6)      # [Maiolino et al. 2024]
J1342 = (7.54, 7.8e8, 5.9e8, 1.1e9)       # ULAS J1342+0928: 7.8 (+3.3, -1.9) e8 [Banados 2018]
LRD_BOX = ((4.5, 8.0), (1.0e6, 1.0e8))    # z-range, M-range [Greene/Matthee 2024]
# Little-red-dot comoving number density, summed over the published bins:
# Matthee+2024 (ApJ 963, 129) Table 4 (UV, 1-mag bins) 3.6e-5 and Table 6 (BH
# mass, dex bins) 3.4e-5; Greene+2024 (ApJ 964, 39) Table 4 (UV, 0.5-mag bins)
# 3.6e-5 (z~5-6) / 4.0e-5 (z~7-8) and Table 5 (L_bol, 1-dex bins) 6.2e-5.
# Both papers call their densities lower limits (incompleteness).
LRD_DENSITY = (3.4e-5, 6.2e-5)


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

    # Observations.  Placed for the three-panel strip (2026-09-24).  The 1e5
    # ceiling and the light seed have the same e-fold, so between them runs a
    # wedge of constant width, 45 Myr x ln(1e3) - 50 Myr = 261 Myr, and all
    # three points sit in it: each name is a one-liner placed inside the wedge
    # (the label audit found the light seed's line through GN-z11, J1342+0928
    # and the region's name in the two-panel layout).  UHZ1 right of its
    # point; GN-z11 below-left of its error bar; J1342 above-right of its.
    for (z, m, mlo, mhi), name, xy, ha in (
        (UHZ1, "UHZ1", (22.0, 0.92), "left"),
        (GNZ11, "GN-z11", (-80.0, 0.1875), "center"),
        (J1342, "J1342", (72.0, 2.9), "center"),
    ):
        tz = float(t_of_z(z))
        ax.errorbar([tz], [m], yerr=[[m - mlo], [mhi - m]], fmt="o",
                    color=style.INK, ms=4.0, capsize=1.8, lw=0.9, zorder=4)
        ax.text(tz + xy[0], m * xy[1], name, color=style.INK, fontsize=6.8,
                ha=ha, va="center", zorder=5)
    (z0, z1), (m0, m1) = LRD_BOX
    ax.fill_between([float(t_of_z(z1)), float(t_of_z(z0))], m0, m1,
                    facecolor="none", edgecolor=style.INK, lw=0.8, zorder=3,
                    hatch="///")
    ax.text(1040.0, 1.0e7, "little\nred dots", color=style.INK,
            fontsize=7.0, ha="center", va="center", linespacing=1.0,
            bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=1.0))

    # Curve names in place, no boxed key.  The region's name sits in the one
    # corner no curve reaches: right of the light seed (which leaves the top
    # at t ~ 990 Myr) and above the little-red-dot box.
    ax.text(1575.0, 1.25e10, "drainhole seeds\n" r"$10^{4}$–$10^{6}\,M_\odot$," "\n"
            r"converted at $z\simeq20$" "\n(Table II)", color="#8b5c00", fontsize=7.0,
            ha="right", va="top", zorder=5, linespacing=1.05)
    # Up-left of the heavy ceiling, clear of it and with no patch.
    ax.text(112.0, 9.0e9, "Eddington\nceilings", color=style.GOLD, fontsize=7.0,
            ha="left", va="top", zorder=5, linespacing=1.05)
    # The light seed named ON its line, down-right of it below the gold floor.
    t_a = t_light + SALPETER_MYR * math.log(15.0)       # where it passes 1.5e3
    ax.annotate(r"$10^2\,M_\odot$ light seed, $z=25$", (t_a, 1.5e3),
                xytext=(7, -2), textcoords="offset points", color=style.CONTEXT,
                fontsize=7.0, ha="left", va="top", zorder=5)

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
    sec.tick_params(labelsize=7.5)
    sec.set_xlabel(r"redshift $z$", fontsize=8.5)


def lisa_sn(f: np.ndarray) -> np.ndarray:
    """Sky-averaged LISA sensitivity S_n(f) [1/Hz] (Robson, Cornish & Liu 2019,
    CQG 36, 105011, Eq. 13) in its low-frequency transfer form (4 P_acc for
    2(1+cos^2(f/f*)) P_acc), instrument only (no galactic confusion noise).
    S_n sums LISA's two low-frequency channels (R_0 = 3/10), so a burst's
    sky- and polarisation-averaged SNR is 4 int (|h+~|^2+|hx~|^2)/S_n df."""
    L, fstar = 2.5e9, 1.909e-2
    p_oms = (1.5e-11) ** 2 * (1.0 + (2.0e-3 / f) ** 4)
    p_acc = (3.0e-15) ** 2 * (1.0 + (0.4e-3 / f) ** 2) * (1.0 + (f / 8.0e-3) ** 4)
    return (10.0 / (3.0 * L**2)) * (p_oms + 4.0 * p_acc / (2.0 * math.pi * f) ** 4) \
        * (1.0 + 0.6 * (f / fstar) ** 2)


def lisa_pls(f: np.ndarray, years: float = 4.0, snr: float = 10.0) -> np.ndarray:
    """Power-law-integrated sensitivity from the analytic LISA noise model
    (Robson, Cornish & Liu 2019, Eq. 13), Thrane-Romano construction."""
    s_n = lisa_sn(f)
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
    ax.text(5.0e-3, 2.2e-9, "LISA, 4 yr\npower-law\nintegrated",
            color=style.INK, fontsize=7.0, ha="center", va="center", linespacing=1.05)

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
        # Under each box: over it, the 1e4 name sat on the curve's rising arm.
        ax.text(math.sqrt(f_lo * f_hi) / 1.9, o_lo / 1.8, label, color=style.INK,
                fontsize=7.0, ha="center", va="top", zorder=5)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-5, 3.0e-1)
    ax.set_ylim(1.0e-15, 1.0e-8)
    ax.set_xlabel(r"$f_{\rm obs}$ [Hz]")
    ax.set_ylabel(r"$\Omega_{\rm GW}$")


def panel_population(ax) -> None:
    """Omega_GW and |Omega_phi,0| against the comoving MASS density of converting
    wormholes, n M: both depend on n and M only through it, so the three mass
    decades of panel (b) fall on one band, and the masses re-enter only where the
    frequency matters (the LISA ticks) and where an abundance n is quoted."""
    x_min, x_max = 1.0e-2, 1.0e15
    dep = (SCALAR_RATIO[0] * E_OVER_M[0], SCALAR_RATIO[1] * E_OVER_M[1])   # |E_phi|/M
    blue = "#6a93bd"                           # the pale member of the deep-blue family
    k = 1.0 / (RHO_C_MSUN_MPC3 * (1.0 + Z_EMIT))  # Omega_0 per unit of n E

    # The little-red-dot abundance, seeded at 1e4-1e6 M_sun (grey).
    ax.axvspan(LRD_DENSITY[0] * SEED_RANGE[0], LRD_DENSITY[1] * SEED_RANGE[1],
               color=style.FAINT, alpha=0.45, lw=0.0, zorder=0)

    # The deposits: solid up to the dark-matter ceiling, faint beyond it.
    for lo, hi, alpha_b, alpha_g in ((x_min, RHO_DM_MSUN_MPC3, 0.45, 0.85),
                                     (RHO_DM_MSUN_MPC3, x_max, 0.12, 0.25)):
        x = np.logspace(math.log10(lo), math.log10(hi), 40)
        ax.fill_between(x, k * x * dep[0], k * x * dep[1], color=blue, alpha=alpha_b,
                        lw=0.0, zorder=1)
        if alpha_b > 0.2:                      # the blue band's edges, where it is solid
            for d in dep:
                ax.plot(x, k * x * d, color=blue, lw=0.7, zorder=1)
        ax.fill_between(x, k * x * E_OVER_M[0], k * x * E_OVER_M[1], color=style.GOLD,
                        alpha=alpha_g, lw=0.0, zorder=2)
    ax.axvline(RHO_DM_MSUN_MPC3, color=style.INK, lw=0.9, zorder=3)

    # Omega_Lambda, and the ceiling H^2 > 0 at z_e puts on ANY radiation-like
    # negative deposit: |rho_phi(z_e)| < rho_m(z_e), i.e. Omega_m/(1+z_e) today.
    ax.axhline(OMEGA_L, color=style.INK, lw=1.0, zorder=3)
    ax.axhline(OMEGA_M / (1.0 + Z_EMIT), color=style.INK, lw=0.8, ls=(0, (1.2, 1.6)),
               zorder=3)

    # The PLS of panel (b) at each mass's band, where the gold band meets it.
    fgrid = np.logspace(-5.0, -0.5, 400)
    pls_grid = lisa_pls(fgrid)
    # Each tick is named to its right, clear of the band's lower edge (which,
    # at slope one, is 0.8 decades above the tick there); the 1e5 name hangs
    # under its tick so that it does not stack onto the 1e6 name.
    for mass, name, va in ((1.0e4, r"$10^{4}\,M_\odot$", "center"),
                           (1.0e5, r"$10^{5}\,M_\odot$", "top"),
                           (1.0e6, r"$10^{6}\,M_\odot$", "center")):
        f_lo = FM_PEAK[0] / (mass * MSUN_S * (1.0 + Z_EMIT))
        f_hi = FM_PEAK[1] / (mass * MSUN_S * (1.0 + Z_EMIT))
        ff = np.logspace(math.log10(f_lo), math.log10(f_hi), 40)
        pls = float(np.exp(np.interp(np.log(ff), np.log(fgrid), np.log(pls_grid))).min())
        x_hit = pls / (k * math.sqrt(E_OVER_M[0] * E_OVER_M[1]))
        ax.plot([x_hit / 6.0, x_hit * 6.0], [pls, pls], color=style.INK, lw=1.5,
                zorder=4, solid_capstyle="butt")
        ax.text(x_hit * (16.0 if va == "center" else 9.0),
                pls if va == "center" else pls / 1.4, name, color=style.INK,
                fontsize=6.5, ha="left", va=va, zorder=5)
    ax.text(2.0e2, 4.0e-15, "LISA PLS", color=style.INK, fontsize=6.8, ha="left",
            va="top")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(1.0e-17, 30.0)
    ax.set_xlabel(r"$nM$ [$M_\odot$ Mpc$^{-3}$]")
    ax.set_ylabel(r"$\Omega_0$")
    ax.set_xticks([1e-1, 1e3, 1e7, 1e11, 1e15])
    ax.set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1e0])

    # The same axis in units of the critical density.
    sec = ax.secondary_xaxis("top", functions=(lambda x: x / RHO_C_MSUN_MPC3,
                                               lambda x: x * RHO_C_MSUN_MPC3))
    sec.set_xticks([1e-12, 1e-8, 1e-4, 1e0, 1e4])
    sec.tick_params(labelsize=7.5)
    sec.set_xlabel(r"$\Omega_{\rm WH}=nM/\rho_c$", fontsize=8.5)

    # Names in place.  Each deposit is named against its own band edge: the
    # bands rise at slope one, so a name set up-left of the blue edge (or
    # down-right of the gold one) touches it at one corner and clears it
    # everywhere else.
    ax.text(2.0e-2, OMEGA_L * 1.8, r"$\Omega_\Lambda$", color=style.INK, fontsize=7.5,
            ha="left", va="bottom")
    ax.text(2.0e-2, OMEGA_M / (1.0 + Z_EMIT) / 2.5, r"$|\rho_\phi|=\rho_m$ at $z_e$",
            color=style.INK, fontsize=6.8, ha="left", va="top")
    ax.text(RHO_DM_MSUN_MPC3 * 1.8, 3.0e-15, r"$nM=\rho_{\rm DM}$", color=style.INK,
            fontsize=6.8, ha="left", va="bottom", rotation=90)
    ax.text(3.0, 2.0e-9, "LRD seeds", color=style.INK, fontsize=6.8, ha="center",
            va="bottom", rotation=90)
    x0 = 3.0e6
    ax.text(x0, 1.6 * k * x0 * dep[1], r"$|\Omega_\phi|$", color=style.DEEP_BLUE,
            fontsize=7.5, ha="right", va="bottom")
    x1 = 3.0e7
    ax.text(x1, k * x1 * E_OVER_M[0] / 4.0, r"$\Omega_{\rm GW}$", color="#8b5c00",
            fontsize=7.5, ha="left", va="top")


def main() -> None:
    style.prd()
    fig = plt.figure(figsize=(7.2, 3.0))
    gs = fig.add_gridspec(1, 3, width_ratios=(1.75, 0.9, 1.1))
    ax_a, ax_b, ax_c = (fig.add_subplot(gs[0, i]) for i in range(3))
    panel_seed_race(ax_a)
    panel_lisa(ax_b)
    panel_population(ax_c)
    fig.tight_layout(w_pad=0.9)
    # Letter tags ABOVE the frames, the paper's rule, at one height for all
    # panels: over the top-axis tick labels of (a) and (c).
    top = ax_a.get_position().y1 + 0.085
    for ax, tag in ((ax_a, "(a)"), (ax_b, "(b)"), (ax_c, "(c)")):
        fig.text(ax.get_position().x0, top, tag, ha="left", va="bottom",
                 fontsize=10.0, color=style.INK)
    out = style.save(fig, figure_dir("08_waves") / "heavy_seeds")
    print(out)


if __name__ == "__main__":
    main()
