#!/usr/bin/env python3
r"""The heavy-seed channel, drawn: the seed race, the LISA bursts, the population curve.

Article Sec. X B.  Panel (a) is arithmetic on quoted numbers; panel (b) reads
the pack (the search templates' strain, through ``gw_search.lisa``); panel (c)
takes its energies and frequencies from the pack (``plot_psi4_ligo.prepare``,
the records of Fig. psi4_ligo, and ``gw_search.lisa.arms``).  Every
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

PANEL (b) -- THE HEADLINE: ONE BURST AGAINST LISA (2026-09-25, replacing the
conversion-background boxes, which showed a time average the text itself says
never forms at these rates and never showed the per-burst SNR the abstract
quotes).  Characteristic strain h_c = 2 f |h~| of a single fly-by (gold) and
spiral (blue) burst at z_e = 20, one track per source-frame mass decade
10^4-10^8 M_sun, against h_n = sqrt(f S_n) of the analytic LISA noise with the
4-yr galactic confusion (Robson, Cornish & Liu 2019).  Conservative count:
inclination averaged, each record over its resolved band only.  The area
between a track and the noise in log f IS the burst's SNR^2, so the panel
carries the numbers of the text: heavier bursts are louder but redder; the
tracks climb one decade per mass decade while the noise wall below ~0.1 mHz
climbs faster, and past 10^7 M_sun they slide out of the band (hatched, not
counted).  Grey dashed: the lone collapse at 10^5 M_sun, below the noise.

PANEL (c) -- THE POPULATION CURVE (2026-09-24, the first author's request:
"draw the statistical curve ... how much was needed to provide what Lambda
requires").  Omega today against the comoving MASS density of converting
wormholes, n M, on which alone both deposits depend: Omega_GW of the
conversions (gold, E/M from the head-on to the spiral; since 2026-09-25 -- it
ran to the fly-by's, which converts nothing) and the negative scalar deposit
|Omega_phi,0| (blue, |E_phi| = r E_GW with r = 0.8-3.2, every estimator of
Sec. VIII F, E_GW from the spiral to the fly-by: every encounter, the most
favourable to Lambda), both radiation-like, Omega_0 = n E / [rho_c (1+z_e)] at
z_e = 20.  Solid up to the dark-matter ceiling n M = rho_DM (vertical rule),
faint beyond it, where the deposit would meet Omega_Lambda only at
Omega_WH = n M / rho_c = 60-800 (top axis).  Dotted: H^2 > 0 at z_e caps any
radiation-like negative deposit at Omega_m/(1+z_e).  Ink ticks: the 4-yr
power-law-integrated sensitivity (Thrane-Romano, instrument noise) at each
mass's conversion frequency, where the gold band meets it.  Grey: the
little-red-dot abundance, (3.4-6.2)e-5 Mpc^-3 summed over the published bins
(Matthee+2024 Tables 4 and 6; Greene+2024 Tables 4 and 5), seeded at
10^4-10^6 M_sun.

STYLE: PRD frame, three panels in one row.  GOLD is spent on the channel the
page introduces (the drainhole seeds, their loudest burst and their
background); the light-seed ceiling and the lone collapse are CONTEXT;
observations and the noise are INK.  Cosmology: flat LCDM, H0 = 67.7 km/s/Mpc,
Om = 0.31 (panels a, c); Planck18 distances for the strain (panel b, as the
SNRs of the text).
"""

from __future__ import annotations

import functools
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.gw_search import lisa as LISA  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

# --- cosmology (flat LCDM) -------------------------------------------------
H0_KMSMPC = 67.7
OMEGA_M = 0.31
OMEGA_L = 1.0 - OMEGA_M
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


# --- the campaign's measured numbers (read from the pack) -------------------
CONVERSIONS = ("head-on", "spiral")   # the encounters that end in one black hole
DEPOSIT = ("spiral", "fly-by")        # the Lambda envelope's E_GW (every encounter)
BURSTS = (("fly-by", style.GOLD), ("spiral", style.DEEP_BLUE))
Z_EMIT = 20.0
SALPETER_MYR = 45.0
SEED_RANGE = (1.0e4, 1.0e6)   # the Table-II decade band the section quotes
N_RANGE = (1.0e-4, 1.0e-2)    # one seed per massive galaxy, comoving Mpc^-3
BURST_MASSES = (1.0e4, 1.0e5, 1.0e6, 1.0e7, 1.0e8)

SCALAR_RATIO = (0.8, 3.2)     # |E_phi|/E_GW, extremes over the Sec. VIII F estimators
RHO_DM_MSUN_MPC3 = 0.1200 * 2.775e11   # Planck 2018 Omega_c h^2 (the ledger's f_DM)


@functools.lru_cache(maxsize=None)
def energies() -> dict[str, float]:
    """E_rad/M in the dominant multipole per arm: Fig. psi4_ligo(d), Sec. IX B."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_psi4_ligo as L
    return {a["name"]: float(a["E"]) for a in L.prepare(PACK_ROOT)}


def e_range(arms: tuple[str, ...]) -> tuple[float, float]:
    e = [energies()[a] for a in arms]
    return min(e), max(e)


def conversion_fM() -> float:
    """The conversions' resolved Psi_4 peak, fM (head-on and spiral: 0.060)."""
    return max(LISA.arms()[a][0].f_psi4_peak for a in CONVERSIONS)


def f_obs(fM: float, mass: float, z: float = Z_EMIT) -> float:
    return fM / (mass * MSUN_S * (1.0 + z))


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
        (UHZ1, "UHZ1", (18.0, 0.92), "left"),
        (GNZ11, "GN-z11", (-72.0, 0.1875), "center"),
        (J1342, "J1342", (72.0, 2.9), "center"),
    ):
        tz = float(t_of_z(z))
        ax.errorbar([tz], [m], yerr=[[m - mlo], [mhi - m]], fmt="o",
                    color=style.INK, ms=4.0, capsize=1.8, lw=0.9, zorder=4)
        # 6.5 pt: GN-z11's name at 6.8 pt (219 Myr) is wider than the constant
        # 212-Myr gap between the 1e5 ceiling and the light seed it sits in.
        ax.text(tz + xy[0], m * xy[1], name, color=style.INK, fontsize=6.5,
                ha=ha, va="center", zorder=5,
                bbox=dict(facecolor=style.GROUND, edgecolor="none", pad=0.4))
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



# --- LISA (gw_search.lisa; kept under these names for the claims extractors) --
lisa_sn = LISA.sn_instrument


def lisa_pls(f: np.ndarray, years: float = 4.0, snr: float = 10.0) -> np.ndarray:
    """Power-law-integrated sensitivity (Thrane-Romano) from the instrument noise."""
    return LISA.pls(f, years, snr, H0_KMSMPC)


def _track(wf, spec, f99, mass: float, share: float = 0.90, dlog: float = 0.04):
    """A burst's h_c for drawing: log-binned (rms weighted by dln f, so each bin
    keeps its share of the SNR^2) and cut to the band holding ``share`` of
    int h_c^2 dln f -- whole tracks one mass decade apart touch end to end."""
    f, hc = LISA.characteristic_strain(wf, spec, mass, Z_EMIT, "conservative", f99,
                                       fmin=1.0e-7)
    w = np.gradient(np.log(f))
    c = np.cumsum(hc**2 * w)
    c /= c[-1]
    keep = (c >= 0.5 * (1.0 - share)) & (c <= 1.0 - 0.5 * (1.0 - share))
    f, hc, w = f[keep], hc[keep], w[keep]
    edges = np.arange(np.log10(f[0]), np.log10(f[-1]) + dlog, dlog)
    idx = np.digitize(np.log10(f), edges)
    fb, hb = [], []
    for i in np.unique(idx):
        m = idx == i
        fb.append(10.0 ** np.average(np.log10(f[m]), weights=w[m]))
        hb.append(math.sqrt(np.average(hc[m] ** 2, weights=w[m])))
    return np.array(fb), np.array(hb)


def panel_bursts(ax) -> None:
    """The fly-by at every mass decade, the spiral and the lone collapse at
    1e5 M_sun, against the LISA noise."""
    ax.axvspan(1.0e-7, LISA.F_MIN, facecolor="none", edgecolor=style.FAINT, lw=0.0,
               hatch="////", zorder=0)
    f = np.logspace(-5.0, 0.0, 400)
    noise, = ax.plot(f, LISA.noise_strain(f, "conservative"), color=style.INK, lw=1.3,
                     zorder=4, label="LISA noise, 4 yr")

    arms = LISA.arms()
    fly = arms["fly-by"]
    for i, m in enumerate(BURST_MASSES):
        ff, hc = _track(*fly, m)
        line, = ax.plot(ff, hc, color=style.GOLD, lw=1.8, solid_capstyle="round", zorder=3,
                        label="fly-by" if i == 0 else None)
        if i == 0:
            h_fly = line
        k = int(np.argmax(hc))
        style.callout(ax, ff[k], hc[k], rf"$10^{{{int(round(math.log10(m)))}}}$",
                      above=True, color=style.INK, fontsize=6.8, gap=3.0)
    ff, hc = _track(*arms["spiral"], 1.0e5)
    h_sp, = ax.plot(ff, hc, color=style.DEEP_BLUE, lw=1.6, solid_capstyle="round", zorder=3,
                    label=r"spiral, $10^5$")
    ff, hc = _track(*arms["collapsing throat"], 1.0e5)
    h_lc, = ax.plot(ff, hc, color=style.CONTEXT, lw=1.4, ls=(0, (3.0, 1.6)), zorder=3,
                    label=r"lone collapse, $10^5$")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-7, 1.0)
    ax.set_ylim(1.0e-22, 1.0e-14)
    ax.set_xticks([1e-6, 1e-4, 1e-2, 1e0])
    ax.set_xlabel(r"$f_{\rm obs}$ [Hz]")
    ax.set_ylabel(r"$h_c$,  $\sqrt{f S_n}$")
    # The key takes the top; the unit of the mass names sits in the one empty
    # corner, under the noise floor's right arm.
    style.note(ax, r"$M$ [$M_\odot$], $z_e=20$", loc="lower right", color=style.INK,
               fontsize=6.8)
    style.note(ax, "below\nthe band", loc="lower left", fontsize=6.5)
    style.legend(ax, handles=[h_fly, h_sp, h_lc, noise], loc="upper right", fontsize=6.5,
                 frameon=False, handlelength=1.8, borderaxespad=0.3, labelspacing=0.25)


def panel_population(ax) -> None:
    """Omega_GW and |Omega_phi,0| against the comoving MASS density of converting
    wormholes, n M: both depend on n and M only through it, so the mass decades
    fall on one band, and the masses re-enter only where the frequency matters
    (the LISA ticks) and where an abundance n is quoted."""
    x_min, x_max = 1.0e-2, 1.0e15
    e_gw = e_range(CONVERSIONS)
    e_dep = e_range(DEPOSIT)
    dep = (SCALAR_RATIO[0] * e_dep[0], SCALAR_RATIO[1] * e_dep[1])   # |E_phi|/M
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
        ax.fill_between(x, k * x * e_gw[0], k * x * e_gw[1], color=style.GOLD,
                        alpha=alpha_g, lw=0.0, zorder=2)
    ax.axvline(RHO_DM_MSUN_MPC3, color=style.INK, lw=0.9, zorder=3)

    # Omega_Lambda, and the ceiling H^2 > 0 at z_e puts on ANY radiation-like
    # negative deposit: |rho_phi(z_e)| < rho_m(z_e), i.e. Omega_m/(1+z_e) today.
    ax.axhline(OMEGA_L, color=style.INK, lw=1.0, zorder=3)
    ax.axhline(OMEGA_M / (1.0 + Z_EMIT), color=style.INK, lw=0.8, ls=(0, (1.2, 1.6)),
               zorder=3)

    # The PLS at each mass's conversion frequency, where the gold band meets it.
    # Each tick is named to its right, clear of the band's lower edge (which,
    # at slope one, is 0.8 decades above the tick there); the 1e5 name hangs
    # under its tick so that it does not stack onto the 1e6 name.
    fgrid = np.logspace(-5.0, -0.5, 400)
    pls_grid = lisa_pls(fgrid)
    fM = conversion_fM()
    for mass, name, va in ((1.0e4, r"$10^{4}\,M_\odot$", "center"),
                           (1.0e5, r"$10^{5}\,M_\odot$", "top"),
                           (1.0e6, r"$10^{6}\,M_\odot$", "center")):
        pls = float(np.exp(np.interp(math.log(f_obs(fM, mass)), np.log(fgrid),
                                     np.log(pls_grid))))
        x_hit = pls / (k * math.sqrt(e_gw[0] * e_gw[1]))
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
    ax.text(x1, k * x1 * e_gw[0] / 4.0, r"$\Omega_{\rm GW}$", color="#8b5c00",
            fontsize=7.5, ha="left", va="top")


def main() -> None:
    style.prd()
    fig = plt.figure(figsize=(7.2, 3.0))
    gs = fig.add_gridspec(1, 3, width_ratios=(2.0, 1.2, 1.0))
    ax_a, ax_b, ax_c = (fig.add_subplot(gs[0, i]) for i in range(3))
    panel_seed_race(ax_a)
    panel_bursts(ax_b)
    panel_population(ax_c)
    fig.tight_layout(w_pad=0.9)
    # Letter tags ABOVE the frames, the paper's rule, at one height for all
    # panels: over the top-axis tick labels of (a) and (c).
    top = ax_a.get_position().y1 + 0.085
    for ax, tag in ((ax_a, "(a)"), (ax_b, "(b)"), (ax_c, "(c)")):
        fig.text(ax.get_position().x0, top, tag, ha="left", va="bottom",
                 fontsize=10.0, color=style.INK)
    style.declutter(fig, max_shift=16.0)
    style.label_audit(fig)
    out = style.save(fig, figure_dir("08_waves") / "heavy_seeds")
    print(out)


if __name__ == "__main__":
    main()
