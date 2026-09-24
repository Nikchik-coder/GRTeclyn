#!/usr/bin/env python3
r"""F_cosmology (merger-paper feedback): the conversion bursts in LISA, the
conversion background against LISA, and the negative-energy deposit against
Lambda -- the numbers behind Sec. XI B and Fig. heavy_seeds.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/f_cosmology_lisa.py [--json OUT]

Nothing here is new physics input.  Every campaign number comes from the pack
through the code the article already uses:

* strain: ``gw_search.templates.nr.load_all_arms`` -- the Psi_4 -> h step of
  the O3b search (fixed-frequency integration clamped at f0, optimal
  orientation: (2,2) face-on, (2,0) edge-on) -- tapered exactly as
  ``template_timeseries`` tapers a template;
* LISA noise: ``plot_heavy_seeds.lisa_sn`` (Robson, Cornish & Liu 2019,
  CQG 36, 105011, Eq. 13, the curve Fig. heavy_seeds(b) is built from), and as
  a conservative variant RCL Eq. 13 with its full transfer term plus the
  4-yr galactic confusion noise of RCL Eq. 14 / Table 1;
* energies: the ledger's extractors (claims/extract_detector, extract_waves).

SNR convention (RCL Sec. 2): S_n already sums LISA's two low-frequency
channels and averages over sky position and polarisation angle, so for a
source of fixed inclination
    rho^2 = 4 int_0^inf (|h+~|^2 + |hx~|^2) / S_n df
          = 2 int_-inf^inf |h~(f)|^2 / S_n(|f|) df,     h = h+ - i hx.
Two variants.  "nominal": Fig. heavy_seeds' noise, the template's own (optimal)
orientation, the whole record.  "conservative": RCL Eq. 13 with the full
transfer plus the 4-yr galactic confusion noise, the inclination averaged
(power x 2/5 for the (2,2) records with their m = -2 partner, x 8/15 for the
(2,0) records), and only |F| between the integration corner f0 and the
frequency below which 99% of the record's energy lies.

A source of source-frame total mass M at redshift z is the scale-free record
with M -> M_z = (1+z) M on the clock and amplitude M_z / D_L (= M / D_c).
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import warnings

import numpy as np
from scipy.signal.windows import tukey

warnings.filterwarnings("ignore")

REPO = pathlib.Path(__file__).resolve().parents[4]
CLAIMS = REPO / "research" / "merger" / "article" / "claims"

from astropy.cosmology import Planck18  # noqa: E402

from grteclyn_wrapper.gw_search.templates.nr import TAPER, load_all_arms  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import plot_heavy_seeds as HS  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    M_SUN_METER, M_SUN_SEC,
)

INC_POWER = {"(2,2)": 2.0 / 5.0, "(2,0)": 8.0 / 15.0}
SNR_THRESHOLD = 8.0
# LISA measures "in a band from below 1e-4 Hz to above 1e-1 Hz" (Amaro-Seoane
# et al. 2017, abstract); the RCL model is written down to 1e-5 Hz, which Fig.
# heavy_seeds(b) draws.  The burst SNR starts at 1e-4 Hz unless --fmin says
# otherwise (no mass up to 1e6 M_sun at z <= 20 has signal below it).
F_MIN, F_MAX = 1.0e-4, 1.0
YEAR_S = 3.15576e7
C_MPC_PER_YR = 299792.458 * YEAR_S / 3.0857e19


# ------------------------------------------------------------------ LISA noise
def sn_fig16(f):
    """Fig. heavy_seeds' S_n: RCL Eq. 13, low-frequency transfer (4 P_acc), no
    confusion noise -- the curve the PLS of panel (b) is built from."""
    return HS.lisa_sn(np.asarray(f, dtype=float))


def sn_rcl_conservative(f, years: float = 4.0):
    """RCL Eq. 13 with the full 2(1+cos^2(f/f*)) transfer, plus the galactic
    confusion noise S_c of RCL Eq. 14 (Table 1, 4-yr parameters)."""
    f = np.asarray(f, dtype=float)
    L, fstar = 2.5e9, 1.909e-2
    p_oms = (1.5e-11) ** 2 * (1.0 + (2.0e-3 / f) ** 4)
    p_acc = (3.0e-15) ** 2 * (1.0 + (0.4e-3 / f) ** 2) * (1.0 + (f / 8.0e-3) ** 4)
    sn = (10.0 / (3.0 * L**2)) * (p_oms + 2.0 * (1.0 + np.cos(f / fstar) ** 2) * p_acc
                                  / (2.0 * math.pi * f) ** 4) * (1.0 + 0.6 * (f / fstar) ** 2)
    params = {0.5: (0.133, 243.0, 482.0, 917.0, 2.58e-3),
              1.0: (0.171, 292.0, 1020.0, 1680.0, 2.15e-3),
              2.0: (0.165, 299.0, 611.0, 1340.0, 1.73e-3),
              4.0: (0.138, -221.0, 521.0, 1680.0, 1.13e-3)}
    alpha, beta, kappa, gamma, fk = params[years]
    sc = 9.0e-45 * f ** (-7.0 / 3.0) * np.exp(-f ** alpha + beta * f * np.sin(kappa * f)) \
        * (1.0 + np.tanh(gamma * (fk - f)))
    return sn + sc


NOISES = {"fig16": sn_fig16, "conservative": sn_rcl_conservative}


# ------------------------------------------------------------------ burst SNR
def spectrum(wf, pad: int = 32):
    """(F, |H~(F)|^2) of the tapered template, F in 1/M, H~ in M (two-sided)."""
    H = wf.H * tukey(wf.H.size, alpha=2.0 * TAPER)
    n = 1 << int(math.ceil(math.log2(H.size * pad)))
    Ht = np.fft.fft(H, n=n) * wf.dt_M
    F = np.fft.fftfreq(n, d=wf.dt_M)
    return F, np.abs(Ht) ** 2


def energy_quantile(spec, q: float) -> float:
    """F below which a fraction q of the record's energy lies (dE/dF ~ F^2 |H~|^2)."""
    F, P = spec
    pos = F > 0
    Fp = F[pos]
    neg = np.interp(Fp, -F[F < 0][::-1], P[F < 0][::-1])
    c = np.cumsum(Fp ** 2 * (P[pos] + neg))
    return float(Fp[np.searchsorted(c / c[-1], q)])


def snr_parts(wf, spec, m_src: float, z: float, noise: str, corners: dict[str, float],
              window: tuple[float, float] | None = None):
    """Optimal-orientation rho over |F| in ``window`` (all F if None), and the
    share of that rho^2 from |F| below each corner."""
    F, P = spec
    mz_s = m_src * (1.0 + z) * M_SUN_SEC                    # seconds per unit u
    dl = Planck18.luminosity_distance(z).to("m").value
    amp = m_src * (1.0 + z) * M_SUN_METER / dl
    f = np.abs(F) / mz_s
    band = (f >= F_MIN) & (f <= F_MAX)
    if window is not None:
        band &= (np.abs(F) >= window[0]) & (np.abs(F) <= window[1])
    dF = F[1] - F[0]
    integ = np.zeros_like(P)
    integ[band] = 2.0 * (amp * mz_s) ** 2 * P[band] / NOISES[noise](f[band])
    rho2 = float(integ.sum() * dF / mz_s)
    share = {k: float(integ[np.abs(F) < c].sum() * dF / mz_s / rho2) if rho2 > 0 else float("nan")
             for k, c in corners.items()}
    return math.sqrt(rho2), share


VARIANTS = {
    # name: (noise, inclination-averaged?, window from the record?)
    "nominal": ("fig16", False, False),
    "conservative": ("conservative", True, True),
}


def rho_variant(wf, spec, m, z, variant, f99):
    noise, avg, win = VARIANTS[variant]
    rho, _ = snr_parts(wf, spec, m, z, noise, {}, (wf.f0, f99) if win else None)
    return rho * (math.sqrt(INC_POWER[wf.mode]) if avg else 1.0)


def mass_range(wf, spec, z: float, variant: str, f99: float,
               grid=np.logspace(2.0, 9.0, 281)):
    """Source-frame masses with rho >= 8 (lo, hi, peak mass, peak rho)."""
    rhos = np.array([rho_variant(wf, spec, m, z, variant, f99) for m in grid])
    ok = rhos >= SNR_THRESHOLD
    k = int(np.argmax(rhos))
    if not ok.any():
        return None, None, float(grid[k]), float(rhos[k])
    return float(grid[ok][0]), float(grid[ok][-1]), float(grid[k]), float(rhos[k])


# ------------------------------------------------------------------ background
def omega_gw(n, m, e_over_m, z=HS.Z_EMIT):
    """Omega today of a one-off radiation-like deposit n (E/M) M at z (as the paper)."""
    return n * e_over_m * m / (HS.RHO_C_MSUN_MPC3 * (1.0 + z))


def pls_in_band(m, z=HS.Z_EMIT):
    """min and max of Fig. heavy_seeds' PLS over the mass's observed band."""
    fgrid = np.logspace(-5.0, -0.5, 400)
    pls = HS.lisa_pls(fgrid)
    f_lo = HS.FM_PEAK[0] / (m * HS.MSUN_S * (1.0 + z))
    f_hi = HS.FM_PEAK[1] / (m * HS.MSUN_S * (1.0 + z))
    ff = np.logspace(math.log10(f_lo), math.log10(f_hi), 60)
    curve = np.exp(np.interp(np.log(ff), np.log(fgrid), np.log(pls)))
    return float(curve.min()), float(curve.max()), f_lo, f_hi


def background_snr(wf, spec, m, n, e_over_m, z=HS.Z_EMIT, years=4.0, noise="fig16"):
    """Stationary-background SNR of the population, with the record's own
    spectral shape: Omega(f) = n/(rho_c (1+z)) dE/dlnf_e, dE/dF ~ F^2 |H~|^2
    normalised to the measured E/M; SNR^2 = 2T int (Omega/Omega_n)^2 df with
    Omega_n = 4 pi^2 f^3 S_n / (3 H0^2) -- the construction of HS.lisa_pls."""
    F, P = spec
    pos = F > 0
    Fp = F[pos]
    # fold the negative frequencies onto the positive ones
    neg = np.interp(Fp, -F[F < 0][::-1], P[F < 0][::-1])
    dEdF = Fp ** 2 * (P[pos] + neg)
    norm = np.trapezoid(dEdF, Fp)
    dEdlnF = e_over_m * Fp * dEdF / norm                 # integrates (dlnF) to E/M
    mz_s = m * (1.0 + z) * HS.MSUN_S
    f = Fp / mz_s
    om = n / (HS.RHO_C_MSUN_MPC3 * (1.0 + z)) * dEdlnF * m
    keep = (f >= F_MIN) & (f <= F_MAX)
    h0 = HS.H0_KMSMPC / 3.0857e19
    om_n = 4.0 * math.pi ** 2 * f[keep] ** 3 * NOISES[noise](f[keep]) / (3.0 * h0 ** 2)
    T = years * YEAR_S
    return math.sqrt(2.0 * T * np.trapezoid((om[keep] / om_n) ** 2, f[keep])), float(om.max())


def comoving_distance_mpc(z):
    return float(Planck18.comoving_distance(z).to("Mpc").value)


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    global F_MIN
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=None)
    ap.add_argument("--fmin", type=float, default=F_MIN,
                    help="lower edge of the SNR integral, Hz (default: LISA's 1e-4)")
    args = ap.parse_args(argv)
    F_MIN = args.fmin
    print(f"SNR integral over {F_MIN:g} - {F_MAX:g} Hz")
    out: dict = {}

    sys.path.insert(0, str(CLAIMS))
    import lib  # noqa: F401,E402  (sets up the pack paths for the extractors)
    import extract_detector as XD  # noqa: E402
    import extract_waves as XW  # noqa: E402

    wfs = {wf.name: wf for wf in load_all_arms()}
    specs = {k: spectrum(w) for k, w in wfs.items()}
    E = {k: XD.detector_gw_energy(arm=k) for k in wfs}
    out["E_over_M"] = E

    # ---------------------------------------------------------- 1. burst SNR
    print("\n=== 1. LISA burst SNR ===")
    print("nominal      = Fig. 16 noise (RCL Eq. 13, instrument), optimal orientation, whole record")
    print("conservative = RCL Eq. 13 full transfer + 4-yr galactic confusion, inclination-averaged,")
    print("               only f0 <= |F| <= F99 (above the integration corner, below 99% of the energy)")
    print("Planck18: D_L(10) = %.1f Gpc, D_L(20) = %.1f Gpc" % (
        Planck18.luminosity_distance(10).to("Gpc").value,
        Planck18.luminosity_distance(20).to("Gpc").value))
    f99 = {k: energy_quantile(specs[k], 0.99) for k in wfs}
    out["F99"] = f99
    out["corners"] = {k: dict(f0=w.f0, one_over_T=1.0 / w.duration_M, fpk=w.f_psi4_peak,
                              drift=w.drift) for k, w in wfs.items()}
    for k, w in wfs.items():
        print(f"  {k:18s} f0={w.f0:.4f} 1/T={1 / w.duration_M:.4f} fpk={w.f_psi4_peak:.4f} "
              f"F99={f99[k]:.3f} pedestal={w.drift:.2f}")
    rows = []
    for z in (20.0, 10.0):
        print(f"\n z_e = {z:g}")
        print(f"  {'arm':18s} {'M':>6s} {'nominal':>9s} {'<f0 %':>6s} {'<1/T %':>7s} "
              f"{'(>f0)':>8s} {'conserv.':>9s}")
        for name, wf in wfs.items():
            corners = {"f0": wf.f0, "1/T": 1.0 / wf.duration_M}
            for m in (1e4, 1e5, 1e6):
                rho, share = snr_parts(wf, specs[name], m, z, "fig16", corners)
                rc = rho_variant(wf, specs[name], m, z, "conservative", f99[name])
                r = dict(z=z, arm=name, mode=wf.mode, M=m, rho_nominal=rho,
                         share_below_f0=share["f0"], share_below_1overT=share["1/T"],
                         rho_nominal_above_f0=rho * math.sqrt(max(0.0, 1 - share["f0"])),
                         rho_conservative=rc)
                rows.append(r)
                print(f"  {name:18s} {m:6.0e} {rho:9.3g} {100 * share['f0']:6.1f} "
                      f"{100 * share['1/T']:7.1f} {r['rho_nominal_above_f0']:8.3g} {rc:9.3g}")
    out["burst_snr"] = rows

    print("\n  detectable source-frame mass range, rho >= 8:")
    ranges = []
    for z in (20.0, 10.0):
        for variant in VARIANTS:
            for name, wf in wfs.items():
                lo, hi, mpk, rpk = mass_range(wf, specs[name], z, variant, f99[name])
                ranges.append(dict(z=z, variant=variant, arm=name, lo=lo, hi=hi,
                                   m_peak=mpk, rho_peak=rpk))
                rng = "none" if lo is None else f"{lo:.2g}-{hi:.2g}"
                print(f"  z={z:4.0f} {variant:12s} {name:18s} {rng:>16s}  "
                      f"(peak rho {rpk:.3g} at {mpk:.2g})")
    out["mass_ranges"] = ranges

    # ---------------------------------------------------------- 2. background
    print("\n=== 2. Background against Fig. heavy_seeds' PLS (integrated Omega, as the paper) ===")
    bg = []
    for m in (1e4, 1e5, 1e6):
        pmin, pmax, f_lo, f_hi = pls_in_band(m)
        for eps, lab in ((HS.E_OVER_M[1], "fly-by"), (HS.E_OVER_M[0], "spiral")):
            n_thr = pmin / omega_gw(1.0, m, eps)
            bg.append(dict(M=m, arm=lab, f_lo_mHz=1e3 * f_lo, f_hi_mHz=1e3 * f_hi,
                           pls_min=pmin, pls_max=pmax, n_thr=n_thr,
                           omega_n1e4=omega_gw(1e-4, m, eps), omega_n1e2=omega_gw(1e-2, m, eps)))
            print(f"  M={m:.0e} {lab:7s} band {1e3 * f_lo:6.3g}-{1e3 * f_hi:6.3g} mHz  "
                  f"PLS {pmin:.2e}-{pmax:.2e}  Omega(n=1e-4)={omega_gw(1e-4, m, eps):.2e} "
                  f"Omega(n=1e-2)={omega_gw(1e-2, m, eps):.2e}  n_thr={n_thr:.2e}")
    out["background_pls"] = bg

    print("\n  spectral background SNR (4 yr, record's own spectrum; PLS construction):")
    bgs = []
    for name in ("fly-by", "spiral", "head-on"):
        for m in (1e4, 1e5, 1e6):
            for n in (1e-4, 1e-2):
                s, om_pk = background_snr(wfs[name], specs[name], m, n, E[name])
                bgs.append(dict(arm=name, M=m, n=n, snr_bg=s, omega_peak=om_pk,
                                n_for_snr10=10.0 * n / s))
                print(f"  {name:8s} M={m:.0e} n={n:.0e}: SNR_bg={s:9.3g}  "
                      f"peak Omega(f)={om_pk:.2e}  n(SNR_bg=10)={10.0 * n / s:.2e}")
    out["background_spectral"] = bgs

    dc20 = comoving_distance_mpc(20.0)
    rates = {n: n * 4.0 * math.pi * dc20 ** 2 * C_MPC_PER_YR for n in (1e-4, 1e-2)}
    out["rates_per_yr_z20"] = rates
    print(f"\n  events per year at z_e=20 (Planck18 D_c={dc20 / 1e3:.2f} Gpc): "
          + ", ".join(f"n={n:.0e}: {r:.3g}/yr ({4 * r:.3g} in 4 yr)" for n, r in rates.items()))

    # ---------------------------------------------------------- 3. Lambda
    print("\n=== 3. The negative-energy deposit against Lambda ===")
    rho_c = HS.RHO_C_MSUN_MPC3
    rho_dm = XD.RHO_DM_PLANCK
    om_l, om_m = HS.OMEGA_L, HS.OMEGA_M
    run = "merge_orbit_flip_d12_p045_L128_lvl5_t100"
    ratios = {
        "kin_t50": XW.waves_scalar_ratio(run=run, R=30, t_cut=50.0),
        "kin_t60": XW.waves_scalar_ratio(run=run, R=30, t_cut=60.0),
        "kin_t70": XW.waves_scalar_ratio(run=run, R=30, t_cut=70.0),
        "kin_t80": XW.waves_scalar_ratio(run=run, R=30, t_cut=80.0),
        "band_t60": XW.waves_scalar_ratio(run=run, R=30, t_cut=60.0, estimator="band"),
        "band_t70": XW.waves_scalar_ratio(run=run, R=30, t_cut=70.0, estimator="band"),
        "band_t80": XW.waves_scalar_ratio(run=run, R=30, t_cut=80.0, estimator="band"),
        "wavezone_t60": XW.waves_scalar_ratio(run=run, R=30, t_cut=60.0, estimator="wavezone"),
        "inner_t60": XW.waves_scalar_ratio(run=run, R=14, t_cut=60.0),
    }
    ephi = {f"R{R}_t{int(t)}": XW.waves_scalar_energy(run=run, R=R, t_cut=t, M=2.0)
            for R in (14, 30) for t in (50.0, 60.0, 70.0, 80.0)}
    out["scalar_ratios"], out["ephi_over_M_flyby"] = ratios, ephi
    r_lo, r_hi = min(ratios.values()), max(ratios.values())
    e_lo, e_hi = HS.E_OVER_M
    dep_lo, dep_hi = r_lo * e_lo, r_hi * e_hi               # |E_phi|/M envelope
    print("  |E_phi|/E_GW estimators: " + ", ".join(f"{k}={v:.3f}" for k, v in ratios.items()))
    print("  fly-by |E_phi|/M direct: " + ", ".join(f"{k}={v:.4f}" for k, v in ephi.items()))
    print(f"  envelope |E_phi|/M = r (E_GW/M): {dep_lo:.4f} .. {dep_hi:.4f}")
    lam = {}
    for z in (0.0, 5.0, 10.0, 20.0, 30.0):
        need_hi = om_l * (1.0 + z) / dep_hi                 # Omega_WH, most favourable
        need_lo = om_l * (1.0 + z) / dep_lo
        lam[z] = dict(omega_wh_min=need_hi, omega_wh_max=need_lo,
                      x_dm_min=need_hi * rho_c / rho_dm, x_dm_max=need_lo * rho_c / rho_dm,
                      n_1e5_min=need_hi * rho_c / 1e5, dep_to_rho_m_at_ze=om_l * (1 + z) / om_m)
        print(f"  z_e={z:4.0f}: Omega_WH needed {need_hi:.3g} .. {need_lo:.3g} "
              f"(= {need_hi * rho_c / rho_dm:.3g} .. {need_lo * rho_c / rho_dm:.3g} rho_DM); "
              f"then |rho_phi|/rho_m at z_e = {om_l * (1 + z) / om_m:.3g}")
    out["lambda"] = lam
    ceiling = {z: om_m / (1.0 + z) for z in (10.0, 20.0)}
    out["H2_ceiling_omega_phi0"] = ceiling
    print("  H^2 > 0 at z_e caps |Omega_phi,0| < Omega_m/(1+z_e) (+Omega_r): "
          + ", ".join(f"z_e={z:g}: {c:.3g}" for z, c in ceiling.items()))
    dm_cap = {k: dict(omega_gw=e * om_ratio, omega_phi=d * om_ratio) for k, (e, d, om_ratio) in {
        "z20": (e_hi, dep_hi, rho_dm / rho_c / 21.0)}.items()}
    out["dm_ceiling"] = dm_cap
    print(f"  at the dark-matter ceiling nM = rho_DM, z_e=20: Omega_GW <= {e_hi * rho_dm / rho_c / 21:.3g}, "
          f"|Omega_phi| <= {dep_hi * rho_dm / rho_c / 21:.3g}  (Omega_Lambda = {om_l})")

    print("\n  back-reaction |rho_phi|/rho_m at z_e (z_e independent) for the fiducial population:")
    br = []
    for n, m in ((1e-4, 1e4), (1e-4, 1e5), (1e-2, 1e5), (1e-2, 1e6)):
        lo = n * m * dep_lo / (om_m * rho_c)
        hi = n * m * dep_hi / (om_m * rho_c)
        br.append(dict(n=n, M=m, lo=lo, hi=hi))
        print(f"  n={n:.0e} M={m:.0e}: {lo:.2e} .. {hi:.2e}")
    out["backreaction"] = br
    om_phi = {f"n{n:.0e}_M1e5": (omega_gw(n, 1e5, dep_lo), omega_gw(n, 1e5, dep_hi)) for n in (1e-4, 1e-2)}
    out["omega_phi0_fiducial_M1e5"] = om_phi
    print("  |Omega_phi,0| at M=1e5: " + ", ".join(f"{k}: {a:.2e}..{b:.2e}" for k, (a, b) in om_phi.items()))

    # ---------------------------------------------------------- 4. JWST / LRD abundance
    print("\n=== 4. Little-red-dot number densities, summed over the published bins ===")
    matthee_uv = sum(10 ** x for x in (-5.06, -4.78, -4.98)) * 1.0           # Table 4, 1-mag bins
    matthee_bh = 10 ** -4.86 * 0.4 + 10 ** -4.27 * 0.4 + 10 ** -5.05 * 0.8    # Table 6, dex bins
    greene_uv56 = (3.0 + 2.1 + 2.1) * 1e-5 * 0.5                              # Table 4, 0.5-mag bins
    greene_uv78 = (1.3 + 2.6 + 4.0) * 1e-5 * 0.5
    greene_bol56 = (1.0 + 4.2 + 1.0) * 1e-5 * 1.0                             # Table 5, 1-dex bins
    lrd = dict(matthee_uv=matthee_uv, matthee_bh=matthee_bh, greene_uv_z56=greene_uv56,
               greene_uv_z78=greene_uv78, greene_bol_z56=greene_bol56)
    out["lrd"] = lrd
    for k, v in lrd.items():
        print(f"  {k:16s} n = {v:.3g} Mpc^-3")
    n_lrd = (min(lrd.values()), max(lrd.values()))
    for m in (1e4, 1e5, 1e6):
        print(f"  seeding every LRD at M={m:.0e}: nM = {n_lrd[0] * m:.3g}..{n_lrd[1] * m:.3g} "
              f"Msun/Mpc^3, f_DM = {n_lrd[0] * m / rho_dm:.2g}..{n_lrd[1] * m / rho_dm:.2g}, "
              f"Omega_GW = {omega_gw(n_lrd[0], m, e_lo):.2g}..{omega_gw(n_lrd[1], m, e_hi):.2g}, "
              f"rate {n_lrd[0] * 4 * math.pi * dc20 ** 2 * C_MPC_PER_YR:.2g}.."
              f"{n_lrd[1] * 4 * math.pi * dc20 ** 2 * C_MPC_PER_YR:.2g}/yr")

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(out, indent=1, default=float))
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
