"""The psi4 mathematics the merger figures need, owned by this package.

Moved here 2026-09-16 so every figure in ``wormhole_merger`` can be drawn from
this folder alone -- ``plot_psi4_analysis`` used to reach into
``visualisation/process_wave/plot_extracted_psi4`` for eleven private helpers,
which meant a merger figure could not be produced without that module.

It is a MOVE, not a copy: ``plot_extracted_psi4`` now imports these from here,
so there is exactly one implementation and the two cannot drift.  Nothing about
the functions changed.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
from scipy.signal.windows import tukey

M_SUN_KG = 1.98892e30
G_SI = 6.67430e-11
C_SI = 2.99792458e8
M_SUN_SEC = G_SI * M_SUN_KG / C_SI**3
M_SUN_METER = G_SI * M_SUN_KG / C_SI**2
MPC_METER = 3.08568e22


def _smooth_psd(psd: np.ndarray, window: int, polyorder: int) -> np.ndarray:
    psd = np.asarray(psd, dtype=float)
    out = psd.copy()
    m = np.isfinite(psd) & (psd > 0)
    if np.sum(m) < 7:
        return out
    y = np.log10(psd[m])
    n = y.size
    w = int(window)
    if w < 5:
        return out
    if w % 2 == 0:
        w += 1
    if w > n:
        w = n if (n % 2 == 1) else (n - 1)
    p = int(polyorder)
    if p < 1:
        return out
    if p >= w:
        p = max(1, w - 2)
    y_s = savgol_filter(y, window_length=w, polyorder=p, mode="interp")
    out[m] = 10 ** y_s
    return out


def _burst_psd(
    psi4_complex: np.ndarray, fs: float, tukey_alpha: float = 0.25
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute the one-sided power spectral density of r*Psi4 for a burst.

    Uses a Tukey window (to taper edges) and a straight FFT rather than
    Welch's method, which is designed for stationary noise and destroys
    frequency resolution of short transients.  Both the + and x
    polarizations are included: PSD = (|FFT(Re)|^2 + |FFT(Im)|^2) * dt^2/T.
    The 1/T normalization gives units of amplitude^2 / frequency.
    """
    N = len(psi4_complex)
    win = tukey(N, alpha=tukey_alpha)
    dt = 1.0 / fs
    T = N * dt

    re_part = np.real(psi4_complex) * win
    im_part = np.imag(psi4_complex) * win

    re_fft = np.fft.rfft(re_part)
    im_fft = np.fft.rfft(im_part)
    freqs = np.fft.rfftfreq(N, d=dt)

    norm = dt**2 / T
    esd = (np.abs(re_fft) ** 2 + np.abs(im_fft) ** 2) * norm
    esd[1:-1] *= 2.0  # one-sided doubling (exclude DC and Nyquist)

    return freqs, esd


def _psd_psi4_to_strain(
    freqs: np.ndarray,
    psd_psi4: np.ndarray,
    f_low: float | None = None,
    cycles_per_record: float = 1.0,
) -> np.ndarray:
    """Convert Psi4 PSD to strain PSD: S_h(f) = S_{Psi4}(f) / (2*pi*f)^4.

    A high-pass roll-off below ``f_low`` suppresses the unphysical divergence
    from dividing numerical noise by f^4 as f -> 0.

    THE CORNER IS SET BY THE RECORD, NOT BY THE SAMPLING RATE.  Until
    2026-09-16 it was ``0.05 * freqs.max()``, i.e. 5 % of the NYQUIST -- which
    is a property of how often the waveform was written out, not of the
    physics.  Sampling the same signal more finely moved the corner up and
    silently deleted the signal: measured on the p = 0.12 spiral, the in-code
    stream (dt = 0.01, Nyquist 50) put the corner at f = 2.5 while the burst
    sits at f = 0.033, so the 8th-order roll-off suppressed the peak by
    (2.5/0.033)^8 ~ 8e14 and the strain came out 1e-29 instead of 1e-22.  The
    same physics read from a dt = 0.5 stream (Nyquist 1.0) was barely touched.
    Two arms of one campaign were being compared through different filters.

    The defensible corner is the lowest frequency the RECORD resolves: one
    cycle per record, ``df = 1/T``, which is the frequency spacing of the
    transform.  Below that the spectrum is not measured, it is extrapolated,
    and that is exactly the divergence this guard exists to remove.  Pass
    ``f_low`` to override.
    """
    strain_psd = np.zeros_like(psd_psi4)
    nz = freqs > 0
    if not np.any(nz):
        return strain_psd

    if f_low is None:
        pos = freqs[nz]
        df = float(np.min(np.diff(np.sort(pos)))) if pos.size > 1 else float(pos[0])
        f_low = cycles_per_record * df

    omega4 = (2.0 * np.pi * freqs[nz]) ** 4
    strain_psd[nz] = psd_psi4[nz] / omega4
    strain_psd[nz] *= 1.0 / (1.0 + (f_low / freqs[nz]) ** 8)
    return strain_psd


def _scale_to_physical(
    freqs_code: np.ndarray,
    strain_psd_code: np.ndarray,
    mass_msun: float,
    distance_mpc: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert code-unit strain PSD to physical (Hz, 1/Hz) units.

    In code units (G=c=1, M=1) the time unit is T_M = M * M_sun_sec.
    The radius-scaled quantity r*Psi4 is dimensionless; after dividing by
    (2*pi*f_code)^2 the strain PSD in code units has dimensions M^3.
    Physical scaling:
        f_phys = f_code / T_M
        S_h_phys = S_h_code * T_M * (M * M_sun_meter / D)^2
    """
    T_M = mass_msun * M_SUN_SEC
    D_m = distance_mpc * MPC_METER

    f_phys = freqs_code / T_M
    amp_scale = (mass_msun * M_SUN_METER / D_m) ** 2 * T_M
    S_h_phys = strain_psd_code * amp_scale
    return f_phys, S_h_phys


def _aLIGO_noise_psd(freqs_hz: np.ndarray) -> np.ndarray:
    """Advanced LIGO design sensitivity noise PSD S_n(f) [1/Hz].

    Analytic fit from Ajith et al. (2011) / LIGO-T0900288-v3,
    valid for 10 Hz < f < 5000 Hz.  Outside this band we return +inf.
    """
    S = np.full_like(freqs_hz, np.inf)
    f0 = 215.0  # Hz reference frequency
    valid = (freqs_hz >= 10.0) & (freqs_hz <= 5000.0)
    x = freqs_hz[valid] / f0

    S0 = 1.0e-49  # 1/Hz overall scale (approximate design)
    S[valid] = S0 * (
        x ** (-4.14)
        - 5.0 * x ** (-2)
        + 111.0 * (1.0 - x**2 + 0.5 * x**4) / (1.0 + 0.5 * x**2)
    )
    S[valid] = np.abs(S[valid])
    S[valid] = np.where(S[valid] > 0, S[valid], np.inf)
    return S


def _compute_snr(
    freqs_hz: np.ndarray, strain_psd: np.ndarray, noise_psd: np.ndarray
) -> float:
    """Optimal matched-filter SNR^2 = 4 * int |h(f)|^2 / S_n(f) df."""
    valid = np.isfinite(noise_psd) & (noise_psd > 0) & np.isfinite(strain_psd)
    if np.sum(valid) < 2:
        return 0.0
    integrand = strain_psd[valid] / noise_psd[valid]
    snr_sq = 4.0 * np.trapezoid(integrand, freqs_hz[valid])
    return float(np.sqrt(max(0.0, snr_sq)))


def _damped_sinusoid(t, A, tau, f0, phi):
    return A * np.exp(-t / tau) * np.sin(2.0 * np.pi * f0 * t + phi)


def _fit_qnm(
    t: np.ndarray,
    psi4_complex: np.ndarray,
    R: float,
    tail_fraction: float = 0.4,
) -> dict | None:
    """Fit A*exp(-t/tau)*sin(2*pi*f*t + phi) to the late-time ringdown.

    Works on the retarded-time Re(r*Psi4) waveform at a single extraction
    radius.  Returns dict with fit parameters, or None if the fit fails.
    """
    # Trailing exact zeros carry no signal -- they are gated or padded
    # samples (gate_psi4_junk.py) and poison the fit if included.
    envelope_full = np.abs(psi4_complex)
    nz = np.nonzero(envelope_full > 0.0)[0]
    if len(nz) < 10:
        return None
    t = t[: nz[-1] + 1]
    psi4_complex = psi4_complex[: nz[-1] + 1]

    t_ret = t - R
    y = np.real(psi4_complex)

    envelope = np.abs(psi4_complex)
    i_peak = np.argmax(envelope)
    if i_peak >= len(t) - 10:
        return None

    t_tail = t_ret[i_peak:]
    y_tail = y[i_peak:]
    t_tail = t_tail - t_tail[0]

    n_start = max(1, int(tail_fraction * len(t_tail)))
    t_fit_raw = t_tail[n_start:]
    y_fit = y_tail[n_start:]
    if len(t_fit_raw) < 10:
        return None

    t_fit = t_fit_raw - t_fit_raw[0]

    env_fit = np.abs(y_fit)
    A0 = float(np.max(env_fit)) if np.max(env_fit) > 0 else 1e-6
    tau0 = float(t_fit[-1] - t_fit[0]) / 2.0

    # Seed the frequency, and never trust ONE seed.  With coarse sampling the
    # old peak-spacing guess (fallback 2.0) let curve_fit converge onto aliased
    # super-Nyquist solutions (seen 2026-09-15 on gated data: f = 0.95 for a
    # 0.047 signal), so the seed was moved to the FFT peak of the fit segment
    # and the fit capped at that segment's Nyquist.  That traded one failure
    # for another: on a short tail whose FFT peak lands in the wrong bin (the
    # BBH control's (2,2) stream, 2026-09-16) curve_fit walks DOWN to the lower
    # bound and returns f = 1e-3, tau = 1e-6 -- a flat line that is not a fit
    # at all, and was drawn as one.  So: three independent seeds, every result
    # that came to rest ON a bound rejected, and the best remaining one by
    # residual.  A fit that reaches a bound is a failure however plausible its
    # curve looks, and a failure must be None, not a red dashed line.
    dt_med = float(np.median(np.diff(t_fit))) if len(t_fit) > 1 else 1.0
    f_nyq = 0.5 / dt_med if dt_med > 0 else np.inf
    f_lo, f_hi = 1e-3, f_nyq

    seeds = []
    yf = np.abs(np.fft.rfft(y_fit - np.mean(y_fit)))
    ff = np.fft.rfftfreq(len(y_fit), dt_med)
    if len(yf) > 1 and np.max(yf[1:]) > 0:
        seeds.append(float(ff[1 + int(np.argmax(yf[1:]))]))
    # Zero crossings: robust where the FFT of a sub-cycle tail is not.
    y_c = y_fit - np.mean(y_fit)
    n_cross = int(np.count_nonzero(np.diff(np.signbit(y_c))))
    span = float(t_fit[-1] - t_fit[0])
    if n_cross > 0 and span > 0:
        seeds.append(0.5 * n_cross / span)
    seeds.append(0.5 * f_nyq)
    seeds = sorted({round(min(max(f, 2e-3), 0.9 * f_nyq), 10) for f in seeds})

    t_ret_fit_start = t_ret[i_peak] + t_fit_raw[0]

    best = None
    for f0_guess in seeds:
        try:
            popt, pcov = curve_fit(
                _damped_sinusoid, t_fit, y_fit,
                p0=[A0, tau0, f0_guess, 0.0],
                bounds=([0, 1e-6, f_lo, -2 * np.pi], [np.inf, np.inf, f_hi, 2 * np.pi]),
                maxfev=10000,
            )
        except Exception:
            continue
        A, tau, f_qnm, phi = popt
        # Resting on a bound is the signature of a fit that never found the
        # signal: the optimiser ran out of room, it did not converge.
        if f_qnm <= f_lo * 1.01 or f_qnm >= f_hi * 0.99 or tau <= 1e-6 * 1.01:
            continue
        # An e-fold several times longer than the segment it was fitted on is
        # not a measurement of a decay -- the record simply does not contain
        # one, and quoting tau = 595 M off a 60 M window (the wide-fill (2,2)
        # arm, 2026-09-16) reads as a ringdown that was never seen.
        if tau > 5.0 * span:
            continue
        resid = float(np.sqrt(np.mean((y_fit - _damped_sinusoid(t_fit, *popt)) ** 2)))
        if best is None or resid < best[0]:
            perr = np.sqrt(np.diag(pcov))
            best = (resid, {
                "A": A, "tau": tau, "f_qnm": f_qnm, "phi": phi,
                "A_err": perr[0], "tau_err": perr[1], "f_qnm_err": perr[2],
                "t_ret_start": t_ret_fit_start,
                "t_ret_end": t_ret_fit_start + t_fit[-1],
            })
    return best[1] if best is not None else None


def _compute_radiated_energy(
    t: np.ndarray, psi4_complex: np.ndarray
) -> float:
    """E_rad = (1/16*pi) * int |r*Psi4|^2 dt  (code units, G=c=1)."""
    integrand = np.abs(psi4_complex) ** 2
    return float(np.trapezoid(integrand, t) / (16.0 * np.pi))


def _find_peak_times(
    t: np.ndarray,
    series: Dict[float, np.ndarray],
    radii: List[float],
    t_skip_frac: float = 0.05,
) -> Dict[float, List[Tuple[float, float]]]:
    """For each radius find (t_peak, amplitude) of dominant and secondary peaks."""
    result: Dict[float, List[Tuple[float, float]]] = {}
    t_skip = t[0] + t_skip_frac * (t[-1] - t[0])

    for R in radii:
        psi4 = series[R]
        envelope = np.abs(psi4)
        mask = t >= t_skip
        env_masked = envelope.copy()
        env_masked[~mask] = 0.0

        peaks_list: List[Tuple[float, float]] = []

        prominence = 0.1 * np.max(env_masked[mask]) if np.any(mask) else 0.0
        idxs, props = find_peaks(env_masked, prominence=max(prominence, 1e-30))
        if len(idxs) > 0:
            order = np.argsort(-env_masked[idxs])
            for idx in idxs[order[:5]]:
                peaks_list.append((float(t[idx]), float(envelope[idx])))
        else:
            i_max = np.argmax(env_masked)
            peaks_list.append((float(t[i_max]), float(envelope[i_max])))

        result[R] = peaks_list
    return result


def wavefront_speeds_xcorr(
    t: np.ndarray, series: Dict[float, np.ndarray], radii: List[float],
) -> List[Tuple[float, float, float, float]]:
    """Propagation speed between neighbouring spheres from the lag of the
    WHOLE complex waveform, not of one envelope peak.

    ``(R1, R2, v, resid)`` per pair, where ``resid`` is the lag in excess of
    light travel (so the matched front at R2 sits at retarded time
    ``u(R1) + resid``).  Peak-to-peak timing fails two ways this survives:
    a flat-topped envelope parks its maximum wherever noise tips it (the
    BBH control's merger plateau is ~15 units wide at both spheres, and the
    peak times alone read v = 0.57 where the waveform lag reads 0.82), and
    a record that ends mid-burst has no outer peak at all.  Correlating
    only over the retarded interval BOTH spheres cover keeps a truncated
    record from biasing the lag toward zero.
    """
    out: List[Tuple[float, float, float, float]] = []
    dt = float(t[1] - t[0])
    for R1, R2 in zip(radii[:-1], radii[1:]):
        m1 = t <= t[-1] - (R2 - R1) + 1e-9
        m2 = t >= t[0] + (R2 - R1) - 1e-9
        w1, w2 = series[R1][m1], series[R2][m2]
        n = min(w1.size, w2.size)
        cc = np.abs(np.correlate(w2[:n], w1[:n], mode="full"))
        k = int(np.argmax(cc))
        frac = 0.0
        if 0 < k < cc.size - 1:
            den = cc[k - 1] - 2.0 * cc[k] + cc[k + 1]
            if den != 0.0:
                frac = 0.5 * (cc[k - 1] - cc[k + 1]) / den
        resid = (k - (n - 1) + frac) * dt
        v = (R2 - R1) / (R2 - R1 + resid) if (R2 - R1 + resid) else np.inf
        out.append((R1, R2, float(v), float(resid)))
    return out


def _compute_propagation_speeds(
    radii: List[float], peak_data: Dict[float, List[Tuple[float, float]]],
    t: np.ndarray = None, series: Dict[float, np.ndarray] = None,
) -> List[Tuple[float, float, float]]:
    """Return list of (R1, R2, speed).

    Uses wavefront tracking: the dominant peak at the innermost radius
    defines a reference retarded time.  At each subsequent radius, the
    peak whose retarded time is closest to that reference is selected,
    ensuring we track the *same* physical wavefront rather than jumping
    to a different (potentially constraint-dominated) feature.
    """
    if not radii or not peak_data:
        return []

    R_ref = radii[0]
    t_ref_sim = peak_data[R_ref][0][0]
    t_ref_ret = t_ref_sim - R_ref

    matched_sim: Dict[float, float] = {R_ref: t_ref_sim}
    for R in radii[1:]:
        best_t_sim = peak_data[R][0][0]
        best_dt_ret = abs((best_t_sim - R) - t_ref_ret)
        for (t_pk, _) in peak_data[R]:
            dt_ret = abs((t_pk - R) - t_ref_ret)
            if dt_ret < best_dt_ret:
                best_dt_ret = dt_ret
                best_t_sim = t_pk
        matched_sim[R] = best_t_sim

    speeds = []
    for i in range(len(radii) - 1):
        R1, R2 = radii[i], radii[i + 1]
        dt = matched_sim[R2] - matched_sim[R1]
        v = (R2 - R1) / dt if abs(dt) > 1e-15 else np.inf
        speeds.append((R1, R2, v))
    return speeds

