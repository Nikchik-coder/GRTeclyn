#!/usr/bin/env python3
r"""The template bank: five campaign waveforms times a mass ladder.

WHY THE BANK IS SMALL
---------------------
A compact-binary search has to cover masses AND spins AND (increasingly)
precession, which is why its banks run to :math:`10^5`-:math:`10^6`
templates.  Here the hypothesis is one numerically-evolved system per
channel, and the records are scale-free -- with the source's total mass as
the unit, strain scales as :math:`M/D` and frequency as :math:`1/M`.  So the
only bank dimension is the total mass, and the bank is five ladders of a few
dozen rungs.  That is the whole reason this search is tractable outside a
collaboration cluster.

HOW THE RUNGS ARE SPACED
------------------------
Not by eye, and not by "log-spaced, 20 of them".  The rungs are laid down by
bisection so that NEIGHBOURING TEMPLATES MATCH AT ``MIN_MATCH`` under the
detector noise curve the search will actually use (:func:`mass_ladder`).
That is the standard bank-placement criterion and it makes the bank's
worst-case loss a stated number -- with ``MIN_MATCH = 0.97`` the bank can
lose at most 3 % of amplitude, hence at most 9 % of detection volume, to a
signal that falls between rungs.

WHERE THE MASS RANGE COMES FROM
-------------------------------
From the records, not from the README's old guess.  That note reasoned from
a ringdown at :math:`f \approx 0.3/M` in code units and concluded that only
500-2000 :math:`M_\odot` could put a signal in band.  The campaign's records
do not carry ``0.3``: their resolved :math:`\Psi_4` band peaks sit at
:math:`fM = 0.028`-:math:`0.066` (``waveforms`` docstring), a factor of
5-10 lower, so the band that matters is a factor of 5-10 LIGHTER.
:func:`mass_range` puts each arm's own resolved peak inside
``[F_BAND_LO, F_BAND_HI]`` Hz, which lands every channel in roughly
20-400 :math:`M_\odot`: the intermediate-mass window, where the modelled
searches are thinnest and a short burst is least likely to have been
recovered by a chirp template.
"""

from __future__ import annotations

import dataclasses

import numpy as np

from grteclyn_wrapper.gw_search.templates.nr import (
    NRWaveform, load_all_arms, template_timeseries,
)

__all__ = ["BankTemplate", "MASS_LADDER_DOC", "MassLadderBank", "MATCH_S",
           "mass_ladder", "mass_range", "padded"]

MASS_LADDER_DOC = __doc__

MIN_MATCH = 0.97       # neighbouring rungs; <=3 % amplitude, <=9 % volume
F_BAND_LO = 40.0       # Hz: the arm's resolved Psi_4 peak must sit above...
F_BAND_HI = 400.0      # ...and below this, at the rung's mass
F_LOWER = 20.0         # Hz: matched-filter low-frequency cutoff


@dataclasses.dataclass(frozen=True)
class BankTemplate:
    """One (arm, mass) rung, with everything the ranking needs to explain it."""

    arm: str
    mode: str
    mass_msun: float
    waveform: NRWaveform

    @property
    def key(self) -> str:
        return f"{self.arm}@{self.mass_msun:.1f}"

    def duration_s(self) -> float:
        return self.waveform.duration_s(self.mass_msun)

    def f_peak_hz(self) -> float:
        return self.waveform.hz(self.waveform.f_psi4_peak, self.mass_msun)

    def f_lower_hz(self, floor: float = F_LOWER) -> float:
        """Where this template may be filtered from -- its own corner, in Hz.

        A record of length ``T`` measures nothing below ``1/T``: there is
        less than one cycle of it.  The fixed-frequency integration in
        :mod:`.nr` CLAMPS the divisor there rather than zeroing it, which is
        right for building a template but leaves real amplitude in a band
        the simulation never resolved.  Filtering down into that band
        harvests signal-to-noise from content that is integration constant,
        and it does it worst exactly where the detector is most sensitive.

        So each template is filtered from its own corner, never below.  The
        cost is real -- the fly-by at 125 Msun starts at 46 Hz rather than
        20, and loses the band underneath -- and it is the honest cost: what
        is lost was never measured.  The arms with clean integrations
        (``drift`` ~ 0.02-0.07: the collapsing throat and the BBH control)
        barely notice, and the three with pedestals (0.3-0.4) are the ones
        this protects.
        """
        corner_M = 1.0 / self.waveform.duration_M
        return max(float(floor), self.waveform.hz(corner_M, self.mass_msun))

    def series(self, sample_rate: int, distance_mpc: float = 1.0):
        return template_timeseries(self.waveform, self.mass_msun,
                                   distance_mpc, sample_rate)


def mass_range(wf: NRWaveform) -> tuple[float, float]:
    """The masses that put this arm's resolved peak in ``[F_BAND_LO, HI]``."""
    from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import M_SUN_SEC
    m_hi = wf.f_psi4_peak / (F_BAND_LO * M_SUN_SEC)
    m_lo = wf.f_psi4_peak / (F_BAND_HI * M_SUN_SEC)
    return float(m_lo), float(m_hi)


MATCH_S = 4.0          # FFT length the bank's matches are computed on


def padded(ts, n: int):
    """``ts`` zero-padded to ``n`` samples, peak kept where it was."""
    out = ts.copy()
    out.resize(n)
    return out


def _match(a, b, psd_for, f_lower: float, sample_rate: int) -> float:
    """Match between two rungs on a FIXED, long FFT.

    The natural length will not do.  A 30 Msun rung of the fly-by is 24
    samples -- 6 ms -- and at 4096 Hz that is a frequency resolution of
    170 Hz, which leaves two usable bins above the 20 Hz cutoff and makes
    the "match" a coin toss.  Both rungs are padded to ``MATCH_S`` seconds
    so the inner product is taken over a band that actually resolves the
    detector's noise curve, exactly as it will be during filtering.
    """
    from pycbc.filter import match
    n = int(MATCH_S * sample_rate)
    if max(len(a), len(b)) > n:
        n = 1 << int(np.ceil(np.log2(max(len(a), len(b)))))
    aa, bb = padded(a, n), padded(b, n)
    m, _ = match(aa, bb, psd=psd_for(n, 1.0 / sample_rate),
                 low_frequency_cutoff=f_lower)
    return float(m)


def mass_ladder(wf: NRWaveform, psd_for, sample_rate: int, *,
                min_match: float = MIN_MATCH, f_lower: float = F_LOWER,
                max_rungs: int = 200) -> list[float]:
    """Masses from ``mass_range(wf)`` spaced at ``min_match``.

    ``psd_for(n_samples, delta_t)`` supplies the noise curve.  Each new rung is
    found by bisecting in log-mass for the point where the match against the
    previous rung falls to ``min_match``, so the spacing is tight where the
    waveform changes fast and loose where it does not -- which a log grid
    cannot do, and which matters here because the low-mass end of every arm
    is the end that moves.
    """
    m_lo, m_hi = mass_range(wf)
    rungs = [m_lo]
    while rungs[-1] < m_hi and len(rungs) < max_rungs:
        m0 = rungs[-1]
        ref = template_timeseries(wf, m0, 1.0, sample_rate)
        lo, hi = m0, min(m0 * 4.0, m_hi)
        if _match(ref, template_timeseries(wf, hi, 1.0, sample_rate),
                  psd_for, f_lower, sample_rate) > min_match:
            rungs.append(hi)
            break
        for _ in range(24):
            mid = np.sqrt(lo * hi)
            cand = template_timeseries(wf, mid, 1.0, sample_rate)
            if _match(ref, cand, psd_for, f_lower, sample_rate) > min_match:
                lo = mid
            else:
                hi = mid
            if hi / lo < 1.002:
                break
        rungs.append(hi)
    return [m for m in rungs if m <= m_hi * 1.0001]


class MassLadderBank:
    """Every arm's mass ladder, flattened -- a :class:`.interfaces.TemplateSource`.

    Placement is deferred to :meth:`place` rather than done in ``__init__``,
    because it needs the noise model the search will actually run against
    and that is not known until the first block of data is conditioned.
    Iterating an unplaced bank is an error, not an empty bank: a search that
    silently filters nothing is worse than one that stops.
    """

    def __init__(self, arms: list[str] | None = None,
                 min_match: float = MIN_MATCH, f_lower: float = F_LOWER):
        self.arms = arms
        self.min_match = min_match
        self.f_lower = f_lower
        self._templates: list[BankTemplate] | None = None

    def place(self, noise, sample_rate: int, verbose: bool = True):
        """Lay the rungs against ``noise`` (a :class:`.interfaces.NoiseModel`)."""
        out: list[BankTemplate] = []
        for wf in load_all_arms(names=self.arms):
            rungs = mass_ladder(wf, noise.for_length, sample_rate,
                                min_match=self.min_match, f_lower=self.f_lower)
            out.extend(BankTemplate(arm=wf.name, mode=wf.mode,
                                    mass_msun=float(m), waveform=wf)
                       for m in rungs)
            if verbose:
                lo, hi = mass_range(wf)
                print(f"  {wf.name:<18s} {len(rungs):3d} rungs over "
                      f"{lo:6.1f}-{hi:6.1f} Msun  "
                      f"(f_pk M = {wf.f_psi4_peak:.4f}, "
                      f"drift {wf.drift:.2f}, T = {wf.duration_M:.0f} M)")
        self._templates = out
        return self

    def __iter__(self):
        if self._templates is None:
            raise RuntimeError("bank not placed; call place(noise, rate) first")
        return iter(self._templates)

    def __len__(self) -> int:
        return 0 if self._templates is None else len(self._templates)
