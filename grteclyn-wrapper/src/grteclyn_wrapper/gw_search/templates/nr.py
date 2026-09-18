#!/usr/bin/env python3
r"""Campaign waveforms as detector templates: :math:`\Psi_4 \to h \to` PyCBC.

The scenario table is NOT restated here.  It is ``ARMS`` in
``visualisation.wormhole_merger.plot_psi4_gallery`` -- the same table the
article's two wave figures read -- so the search and the figures can never
disagree about what a scenario is, which stream it lives in, which sphere is
its innermost, or where it is gated.  Everything below is the step the
figures do not take: turning a gated ``r Psi_4`` record into a strain
template a matched filter can be run with.

THE ONE HARD STEP: Psi_4 -> h
-----------------------------
``Psi_4 = \ddot h_+ - i \ddot h_\times``, so the strain is a DOUBLE time
integral, and in the Fourier domain that is a division by
:math:`(2\pi f)^2`.  Two integration constants ride in, and on a record this
short they are not small: the low-frequency end of a numerical ``Psi_4``
stream carries drift (gauge, near-zone content, the junk the gate could not
reach), and dividing drift by :math:`f^2` turns it into a parabola that
dwarfs the wave.

This module uses **fixed-frequency integration** (Reisswig & Pollney 2011):

.. math::  \tilde h(f) = -\,\tilde\Psi_4(f) \,/\, [2\pi\,\max(|f|, f_0)]^2

-- the divisor is CLAMPED below :math:`f_0` rather than rolled off.  Clamping
keeps the sub-corner band at finite amplitude instead of deleting it, which
is what a template needs: a filter that zeroes a band cannot be told apart
from a signal that has none.  (``psi4_math._psd_psi4_to_strain`` rolls off
instead, and is right to, because it serves an *energy* integral where the
sub-corner band is pure extrapolation and must not contribute.  Different
question, different guard -- that is why this is a second implementation and
not a call into the first.)

``f_0`` is NOT a free dial.  It is measured per arm as the lowest
instantaneous frequency the record actually carries over its body
(``plot_psi4_ligo.envelope_and_frequency``, gated at ``GATE`` of peak),
times ``F0_SAFETY``.  Below that the record has no wave in it, so clamping
there cannot clamp signal.

WHAT THIS MODULE MEASURED THAT THE FIGURES DID NOT (2026-09-18)
---------------------------------------------------------------
The article's Fig. ``psi4_ligo`` panel (b) quotes a peak strain and a peak
frequency per arm.  **Every one of those frequencies is 1/T_record**, to two
digits: throat 95.3 Hz against 96.7, head-on 135.3 against 136.7, spiral
135.3 against 135.3, fly-by 178.0 against 178.1, BBH twin 89.9 against 90.2.
The reason is structural, not a typo: after the :math:`1/f^4` weight the
strain PSD of every one of these bursts still rises monotonically toward low
frequency, so the plotted curve peaks wherever the guard stops it, and the
guard is one cycle per record.  The quoted amplitudes are therefore the
amplitude AT THE KNEE, and both numbers move if the record is lengthened or
the gate is changed.  The physical, resolved peak is the one in ``Psi_4``
(bins 3-5, not bin 1): throat ``fM = 0.042``, head-on ``0.060``, spiral
``0.060``, fly-by ``0.026``, BBH twin ``0.066`` -- and that last one is the
textbook equal-mass merger value, which is the check that the reduction to
each source's own total mass (``M_CODE``) is right.

ORIENTATION, AND WHY THE AMPLITUDES HERE ARE NOT THE FIGURE'S
--------------------------------------------------------------
The figures plot the mode coefficient :math:`|r\Psi_4| M`.  A detector sees
:math:`h = \sum_{\ell m} h_{\ell m}\, {}_{-2}Y_{\ell m}(\theta,\varphi)`, so
a template needs the harmonic evaluated at an orientation.  Each arm is
given its OPTIMAL one, stated in ``SKY``:

* ``(2,2)`` records, counted with the ``m = -2`` partner, face-on
  (:math:`\theta = 0`): factor :math:`\sqrt{5/4\pi} = 0.6308`;
* ``(2,0)`` records, edge-on (:math:`\theta = \pi/2`), where the head-on
  axis radiates at all: factor :math:`\sqrt{15/32\pi} = 0.3862`.

Optimal orientation is the honest convention for a REACH statement (the
distance at which the loudest possible geometry would be seen) and it is the
convention every horizon distance in the search report is quoted in.  It is
NOT an average over the sky, and the two differ by a factor of order 2.5.
"""

from __future__ import annotations

import dataclasses
import pathlib

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal.windows import tukey

from grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery import (
    ARMS, load, trim_zeros_tail,
)
from grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_ligo import (
    GATE, M_CODE, body, envelope_and_frequency,
)
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (
    MPC_METER, M_SUN_METER, M_SUN_SEC,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT

__all__ = ["ARM_NAMES", "NRWaveform", "SKY", "load_arm", "load_all_arms",
           "template_timeseries"]

# -2 Y_lm at the orientation that maximises each mode's strain.  (2,2) is
# read face-on WITH its m = -2 partner (the campaign writes one of the pair;
# for a non-precessing source h_{2,-2} = conj(h_{22}) and face-on only the
# +m member contributes, so the factor is sqrt(5/4pi) and not twice it).
# (2,0) is axisymmetric and vanishes on the axis -- it is read edge-on.
SKY = {
    "(2,2)": float(np.sqrt(5.0 / (4.0 * np.pi))),     # 0.63078, theta = 0
    "(2,0)": float(np.sqrt(15.0 / (32.0 * np.pi))),   # 0.38627, theta = pi/2
}

F0_SAFETY = 0.75   # clamp below 0.75 x the lowest frequency the record carries
TAPER = 0.12       # Tukey fraction, both ends, before the transform

ARM_NAMES = [row[0] for row in ARMS]


@dataclasses.dataclass(frozen=True)
class NRWaveform:
    """One campaign arm, reduced to its own total mass and integrated to strain.

    ``u`` is retarded time in units of the source's total ADM mass and ``H``
    is the dimensionless ``(r/M) h`` at the optimal orientation -- both
    scale-free, so one record covers every candidate mass at once.  Physical
    units arrive only in :func:`template_timeseries`.
    """

    name: str
    mode: str
    knob: str
    radius: float          # innermost extraction sphere, code units
    m_code: float          # total ADM mass of the source, code units
    u: np.ndarray          # retarded time / M
    H: np.ndarray          # complex (r/M) h, optimal orientation applied
    psi4: np.ndarray       # the (r Psi_4) M it came from, same clock
    f0: float              # fM of the integration clamp
    f_body: tuple          # (min, max) instantaneous fM over the record body
    f_psi4_peak: float     # resolved spectral peak of Psi_4, in fM
    drift: float           # |h| at the record's ends / at its peak; see below
    gate: float | None     # the ARMS coordinate-time cap, if any
    note: str

    @property
    def duration_M(self) -> float:
        return float(self.u[-1] - self.u[0])

    @property
    def dt_M(self) -> float:
        return float(np.median(np.diff(self.u)))

    def peak_index(self) -> int:
        return int(np.argmax(np.abs(self.H)))

    def duration_s(self, mass_msun: float) -> float:
        return self.duration_M * mass_msun * M_SUN_SEC

    def hz(self, f_M: float, mass_msun: float) -> float:
        """A dimensionless ``fM`` as Hz for a source of this total mass."""
        return float(f_M / (mass_msun * M_SUN_SEC))


def _fixed_frequency_integrate(y: np.ndarray, dt: float, f0: float) -> np.ndarray:
    r"""Twice-integrate ``Psi_4`` with the divisor clamped below ``f0``.

    ``y`` is complex ``(r Psi_4) M`` on a uniform grid of step ``dt`` (both in
    total-mass units), ``f0`` is in the same frequency units (``fM``).
    Returns complex ``(r/M) h``.
    """
    n = y.size
    win = tukey(n, alpha=2.0 * TAPER)
    spec = np.fft.fft(y * win)
    f = np.fft.fftfreq(n, d=dt)
    omega = 2.0 * np.pi * np.where(np.abs(f) < f0, f0, np.abs(f))
    return np.fft.ifft(-spec / omega**2)


def _resample_uniform(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Put a record on a uniform clock, which a glued series is not.

    The spiral's stream is three legs at two resolutions (``ARMS``), so its
    step changes mid-record; an FFT on it would read the seam as signal.
    """
    dt = float(np.median(np.diff(t)))
    if np.allclose(np.diff(t), dt, rtol=1e-6, atol=1e-12):
        return t, y
    grid = np.arange(t[0], t[-1] + 0.5 * dt, dt)
    out = CubicSpline(t, y.real)(grid).astype(complex)
    if np.iscomplexobj(y):
        out += 1j * CubicSpline(t, y.imag)(grid)
    return grid, out


def load_arm(name: str, pack: pathlib.Path | str | None = None) -> NRWaveform:
    """Build one :class:`NRWaveform` from the ``ARMS`` row called ``name``."""
    pack = pathlib.Path(pack or PACK_ROOT)
    try:
        row = next(r for r in ARMS if r[0] == name)
    except StopIteration:
        raise KeyError(f"no arm {name!r}; have {ARM_NAMES}") from None
    _n, knob, mode, rel, m, R0, t_max, note = row

    got = load(pack, rel, m)
    if got is None:
        raise FileNotFoundError(f"{name}: stream not packed ({rel})")
    t, series = got
    if t_max is not None:
        keep = t <= t_max + 1e-9
        t, series = t[keep], {r: v[keep] for r, v in series.items()}
    R = min(series, key=lambda r: abs(r - R0))
    t, y = trim_zeros_tail(t, np.asarray(series[R]))

    M = M_CODE[name]
    u = (t - R) / M                   # retarded time, in total masses
    psi4 = np.asarray(y, dtype=complex) * M
    u, psi4 = _resample_uniform(u, psi4)
    dt = float(u[1] - u[0])

    # The resolved spectral peak of Psi_4 -- bins 3-5 of these records, and
    # the one frequency in them that is NOT set by the record length (the
    # module docstring has the measurement).  It seeds the cycle-long window
    # the instantaneous frequency is averaged over.
    spec = np.abs(np.fft.fft(psi4 * tukey(psi4.size, alpha=2.0 * TAPER)))
    ff = np.fft.fftfreq(psi4.size, d=dt)
    pos = ff > 0
    f_pk = float(ff[pos][np.argmax(spec[pos])])

    # The clamp, measured off the record rather than chosen: the lowest
    # instantaneous frequency carried over the body, with a safety margin.
    # envelope_and_frequency and body() are the figures' own gate and their
    # own energy-weighted phase derivative, so the search and panel (c)
    # cannot disagree about what frequency a record carries.
    amp, freq = envelope_and_frequency(psi4, dt, f_pk)
    keep = body(amp, GATE) & np.isfinite(freq) & (freq > 0)
    if keep.sum() < 8:
        keep = np.isfinite(freq) & (freq > 0)
    f_lo, f_hi = float(np.nanmin(freq[keep])), float(np.nanmax(freq[keep]))
    # ...but never below ONE CYCLE PER RECORD.  A record of length T cannot
    # tell a wave at f < 1/T from a drift -- there is less than a cycle of it
    # -- so clamping below 1/T does not protect signal, it amplifies the
    # integration constants.  Measured on the fly-by, whose instantaneous
    # frequency genuinely falls to fM = 0.0098 as the pair separates while
    # its record resolves only 1/T = 0.0263: without this floor the clamp
    # sat at 0.0073, 98 % of the strain's power landed below half the
    # resolved Psi_4 peak, and |h| at the record's ENDS came out 0.83 of its
    # peak -- a pedestal with a wiggle on it, reported as a burst 100x the
    # article's amplitude.  With the floor it is 0.10.  This is the same
    # corner psi4_math._psd_psi4_to_strain settled on for the energy
    # integral (2026-09-16), applied as a clamp rather than a roll-off.
    f0 = max(F0_SAFETY * f_lo, 1.0 / (u[-1] - u[0]))

    H = _fixed_frequency_integrate(psi4, dt, f0) * SKY[mode]
    drift = float(max(abs(H[0]), abs(H[-1])) / np.abs(H).max())

    return NRWaveform(name=name, mode=mode, knob=knob, radius=float(R),
                      m_code=float(M), u=u, H=H, psi4=psi4, f0=f0,
                      f_body=(f_lo, f_hi), f_psi4_peak=f_pk, drift=drift,
                      gate=t_max, note=note)


def load_all_arms(pack: pathlib.Path | str | None = None,
                  names: list[str] | None = None) -> list[NRWaveform]:
    """Every packed arm, skipping (loudly) any whose stream is missing."""
    out = []
    for name in (names or ARM_NAMES):
        try:
            out.append(load_arm(name, pack))
        except (FileNotFoundError, KeyError) as exc:
            print(f"  {name:<18s} SKIPPED -- {exc}")
    return out


def template_timeseries(wf: NRWaveform, mass_msun: float, distance_mpc: float,
                        sample_rate: int, *, polarisation: str = "plus"):
    """``wf`` at a physical mass and distance, on the detector's clock.

    Returns a PyCBC ``TimeSeries`` whose epoch is set so that ``t = 0`` is the
    record's own peak: a matched-filter trigger time is then the time of the
    burst's peak in the data, not of some arbitrary end of the array.

    The mass enters twice, and both ways are exact for a scale-free record:
    the clock stretches as ``M`` and the amplitude grows as ``M/D``.
    """
    from pycbc.types import TimeSeries   # local: keeps the module importable

    t_sec = wf.u * mass_msun * M_SUN_SEC
    amp = (mass_msun * M_SUN_METER) / (distance_mpc * MPC_METER)
    h = {"plus": wf.H.real, "cross": -wf.H.imag}[polarisation] * amp

    dt = 1.0 / int(sample_rate)
    dt_rec = float(np.median(np.diff(t_sec)))
    if dt_rec < 0.5 * dt:
        # DOWN-sampling, and by a lot: at 30 Msun the spiral and fly-by
        # streams (dt = 0.005 M) carry 330 samples per detector sample, so
        # plain interpolation folds everything above 2 kHz back into the
        # band as if it were signal.  Band-limit first -- the records have
        # no physical content up there anyway, only the FFT's own noise
        # floor, and folding a noise floor into a template is how a search
        # acquires a bias no chi-squared will catch.
        spec = np.fft.rfft(h)
        spec[np.fft.rfftfreq(h.size, d=dt_rec) > 0.5 / dt] = 0.0
        h = np.fft.irfft(spec, n=h.size)
    grid = np.arange(t_sec[0], t_sec[-1], dt)
    h = CubicSpline(t_sec, h)(grid)
    t_sec = grid

    h = h * tukey(h.size, alpha=2.0 * TAPER)
    peak = int(np.argmax(np.abs(h)))
    return TimeSeries(h.astype(np.float64), delta_t=dt, epoch=-peak * dt)
