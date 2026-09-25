r"""LISA: the analytic noise, and a campaign burst at a mass and a redshift.

One implementation for the three places that need it: Fig. heavy_seeds (the
burst panel and the power-law-integrated curve of the population panel), the
claims extractors behind the article's Sec. X B, and
``scripts/analysis/merger_feedback/f_cosmology_lisa.py``.  Until 2026-09-25 the
noise lived in the figure and the SNR in that script, and the SNR rows of the
ledger were typed in by hand from its printout.

NOISE (Robson, Cornish & Liu 2019, CQG 36, 105011).  ``sn_instrument`` is
their Eq. 13 in its low-frequency transfer form (4 P_acc for
2(1+cos^2(f/f*)) P_acc), instrument only; ``sn_confusion`` is Eq. 13 with the
full transfer plus the galactic confusion noise of Eq. 14 (Table 1, 4-yr
parameters).  S_n sums LISA's two low-frequency channels and averages over
sky position and polarisation angle, so for a source of fixed inclination

    rho^2 = 4 int (|h+~|^2 + |hx~|^2) / S_n df
          = 2 int_-inf^inf |h~(f)|^2 / S_n(|f|) df,          h = h+ - i hx
          = int (h_c / h_n)^2 dln f,

with h_c = 2 f |h~_1|, |h~_1|^2 = (|h~(f)|^2 + |h~(-f)|^2) / 2 and
h_n = sqrt(f S_n): the characteristic strain a figure draws against the noise
carries the SNR as the area between the two in log frequency.

VARIANTS.  "nominal": instrument noise, the record's own (optimal)
orientation, the whole record.  "conservative": confusion noise added, the
inclination averaged (power x 2/5 for the (2,2) records with their m = -2
partner, x 8/15 for the (2,0) records), and only |F| between the integration
corner f0 and the frequency below which 99 % of the record's energy lies.
The article's "above 8" statements are conservative; its "optimal" SNRs are
nominal.

SCALING.  A record of source-frame total mass M at redshift z is the
scale-free record with M -> (1+z) M on the clock and amplitude
(1+z) M / D_L = M / D_c (Planck 2018 cosmology, astropy's ``Planck18``).

BAND.  The SNR integral runs over 1e-4 - 1 Hz: LISA measures "in a band from
below 1e-4 Hz to above 1e-1 Hz" (Amaro-Seoane et al. 2017).  The noise model
is written down to 1e-5 Hz and the figure draws it there; opening the integral
to 2e-5 Hz moves the fly-by's heaviest detectable mass from 2e7 to 2.8e7 Msun
and the head-on's not at all.
"""

from __future__ import annotations

import functools
import math

import numpy as np
from scipy.signal.windows import tukey

from grteclyn_wrapper.gw_search.templates.nr import TAPER, load_all_arms
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import M_SUN_METER, M_SUN_SEC

__all__ = ["F_MIN", "F_MAX", "INC_POWER", "VARIANTS", "sn_instrument", "sn_confusion",
           "noise_strain", "pls", "spectrum", "energy_quantile", "snr", "snr_parts",
           "mass_range", "characteristic_strain", "arms"]

F_MIN, F_MAX = 1.0e-4, 1.0
INC_POWER = {"(2,2)": 2.0 / 5.0, "(2,0)": 8.0 / 15.0}
SNR_THRESHOLD = 8.0
YEAR_S = 3.15576e7

_L, _FSTAR = 2.5e9, 1.909e-2


def _p_oms(f):
    return (1.5e-11) ** 2 * (1.0 + (2.0e-3 / f) ** 4)


def _p_acc(f):
    return (3.0e-15) ** 2 * (1.0 + (0.4e-3 / f) ** 2) * (1.0 + (f / 8.0e-3) ** 4)


def sn_instrument(f):
    """RCL Eq. 13, low-frequency transfer (4 P_acc), no confusion noise [1/Hz]."""
    f = np.asarray(f, dtype=float)
    return (10.0 / (3.0 * _L**2)) * (_p_oms(f) + 4.0 * _p_acc(f) / (2.0 * math.pi * f) ** 4) \
        * (1.0 + 0.6 * (f / _FSTAR) ** 2)


_CONFUSION = {0.5: (0.133, 243.0, 482.0, 917.0, 2.58e-3),
              1.0: (0.171, 292.0, 1020.0, 1680.0, 2.15e-3),
              2.0: (0.165, 299.0, 611.0, 1340.0, 1.73e-3),
              4.0: (0.138, -221.0, 521.0, 1680.0, 1.13e-3)}


def sn_confusion(f, years: float = 4.0):
    """RCL Eq. 13 with the full 2(1+cos^2(f/f*)) transfer, plus the galactic
    confusion noise S_c of RCL Eq. 14 (Table 1) [1/Hz]."""
    f = np.asarray(f, dtype=float)
    sn = (10.0 / (3.0 * _L**2)) * (_p_oms(f) + 2.0 * (1.0 + np.cos(f / _FSTAR) ** 2) * _p_acc(f)
                                   / (2.0 * math.pi * f) ** 4) * (1.0 + 0.6 * (f / _FSTAR) ** 2)
    alpha, beta, kappa, gamma, fk = _CONFUSION[years]
    sc = 9.0e-45 * f ** (-7.0 / 3.0) * np.exp(-f ** alpha + beta * f * np.sin(kappa * f)) \
        * (1.0 + np.tanh(gamma * (fk - f)))
    return sn + sc


NOISES = {"instrument": sn_instrument, "confusion": sn_confusion}
# name: (noise, inclination-averaged?, band cut to the record's resolved band?)
VARIANTS = {"nominal": ("instrument", False, False),
            "conservative": ("confusion", True, True)}


def noise_strain(f, variant: str = "conservative"):
    """h_n = sqrt(f S_n), the curve a characteristic strain is drawn against."""
    f = np.asarray(f, dtype=float)
    return np.sqrt(f * NOISES[VARIANTS[variant][0]](f))


def pls(f, years: float = 4.0, snr: float = 10.0, h0_kmsmpc: float = 67.7):
    """Power-law-integrated sensitivity in Omega (Thrane & Romano 2013) from
    the instrument noise, over the frequency grid ``f`` (log-spaced)."""
    f = np.asarray(f, dtype=float)
    h0_s = h0_kmsmpc / 3.0857e19
    omega_n = (4.0 * math.pi**2 / (3.0 * h0_s**2)) * f**3 * sn_instrument(f)
    T = years * 3.1557e7
    lo = np.log(f)
    out = np.zeros_like(f)
    for beta in np.linspace(-8.0, 8.0, 81):
        integ = np.trapezoid((f / 1.0e-3) ** (2.0 * beta) / omega_n**2 * f, lo)
        out = np.maximum(out, snr / math.sqrt(2.0 * T * integ) * (f / 1.0e-3) ** beta)
    return out


# ------------------------------------------------------------------ the record
def spectrum(wf, pad: int = 32):
    """(F, |H~(F)|^2) of the tapered record, F in 1/M, H~ in M (two-sided)."""
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


@functools.lru_cache(maxsize=None)
def _distances(z: float) -> tuple[float, float]:
    from astropy.cosmology import Planck18
    return (float(Planck18.luminosity_distance(z).to("m").value),
            float(Planck18.comoving_distance(z).to("Mpc").value))


def comoving_distance_mpc(z: float) -> float:
    return _distances(float(z))[1]


def _scale(m_src: float, z: float) -> tuple[float, float]:
    """(seconds per unit of the record's clock, strain per unit of r h / M)."""
    mz_s = m_src * (1.0 + z) * M_SUN_SEC
    return mz_s, m_src * (1.0 + z) * M_SUN_METER / _distances(float(z))[0]


def snr_parts(wf, spec, m_src: float, z: float, noise: str, corners: dict[str, float],
              window: tuple[float, float] | None = None, fmin: float = F_MIN,
              fmax: float = F_MAX):
    """Optimal-orientation rho over |F| in ``window`` (all F if None), and the
    share of that rho^2 from |F| below each corner."""
    F, P = spec
    mz_s, amp = _scale(m_src, z)
    f = np.abs(F) / mz_s
    band = (f >= fmin) & (f <= fmax)
    if window is not None:
        band &= (np.abs(F) >= window[0]) & (np.abs(F) <= window[1])
    dF = F[1] - F[0]
    integ = np.zeros_like(P)
    integ[band] = 2.0 * (amp * mz_s) ** 2 * P[band] / NOISES[noise](f[band])
    rho2 = float(integ.sum() * dF / mz_s)
    share = {k: float(integ[np.abs(F) < c].sum() * dF / mz_s / rho2) if rho2 > 0 else float("nan")
             for k, c in corners.items()}
    return math.sqrt(rho2), share


def snr(wf, spec, m_src: float, z: float, variant: str, f99: float,
        fmin: float = F_MIN, fmax: float = F_MAX) -> float:
    """rho of one burst of source-frame mass ``m_src`` at redshift ``z``."""
    noise, avg, win = VARIANTS[variant]
    rho, _ = snr_parts(wf, spec, m_src, z, noise, {}, (wf.f0, f99) if win else None,
                       fmin=fmin, fmax=fmax)
    return rho * (math.sqrt(INC_POWER[wf.mode]) if avg else 1.0)


def mass_range(wf, spec, z: float, variant: str, f99: float,
               grid=np.logspace(2.0, 9.0, 281), fmin: float = F_MIN):
    """Source-frame masses with rho >= 8: (lo, hi, peak mass, peak rho)."""
    rhos = np.array([snr(wf, spec, m, z, variant, f99, fmin=fmin) for m in grid])
    ok = rhos >= SNR_THRESHOLD
    k = int(np.argmax(rhos))
    if not ok.any():
        return None, None, float(grid[k]), float(rhos[k])
    return float(grid[ok][0]), float(grid[ok][-1]), float(grid[k]), float(rhos[k])


def characteristic_strain(wf, spec, m_src: float, z: float, variant: str, f99: float,
                          fmin: float = F_MIN, fmax: float = F_MAX):
    """(f [Hz], h_c) over the band ``snr`` integrates, one-sided, so that
    int (h_c / noise_strain)^2 dln f is snr(...)^2 with the same arguments."""
    F, P = spec
    noise, avg, win = VARIANTS[variant]
    mz_s, amp = _scale(m_src, z)
    pos = F > 0
    Fp = F[pos]
    neg = np.interp(Fp, -F[F < 0][::-1], P[F < 0][::-1])
    h1 = np.sqrt(0.5 * (P[pos] + neg)) * amp * mz_s          # |h~_1(f)|, s
    if avg:
        h1 = h1 * math.sqrt(INC_POWER[wf.mode])
    f = Fp / mz_s
    keep = (f >= fmin) & (f <= fmax)
    if win:
        keep &= (Fp >= wf.f0) & (Fp <= f99)
    return f[keep], 2.0 * f[keep] * h1[keep]


@functools.lru_cache(maxsize=None)
def arms(pack: str | None = None) -> dict:
    """Every packed arm as {name: (NRWaveform, spectrum, F99)}."""
    out = {}
    for wf in load_all_arms(pack=pack):
        spec = spectrum(wf)
        out[wf.name] = (wf, spec, energy_quantile(spec, 0.99))
    return out
