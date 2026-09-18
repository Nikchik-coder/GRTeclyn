#!/usr/bin/env python3
r"""Would the modelled searches have found these signals?

The LVK catalogues are built by filtering the data against banks of
quasi-circular binary-black-hole templates.  A source whose waveform is not
in the bank is not thereby invisible -- it is recovered by whichever bank
template happens to resemble it, at reduced signal-to-noise.  The number
that quantifies that loss is the **fitting factor**

.. math::  \mathrm{FF} = \max_{\lambda \in \mathrm{bank}}\;
           \max_{t_0,\phi_0}\; \langle s\,|\,h(\lambda)\rangle

-- the best normalised overlap the bank can achieve against the signal
:math:`s`.  Recovered SNR is ``FF`` times optimal, and since detection
volume goes as the cube of SNR, a channel recovered at ``FF`` is seen in a
fraction ``FF^3`` of the volume a matched template would reach.  ``FF = 0.9``
is the conventional line for "adequately covered"; below it, a dedicated
search is buying real sensitivity.

TWO NUMBERS, AND THEY ANSWER DIFFERENT QUESTIONS
------------------------------------------------
:func:`fitting_factor` reports both, because quoting one without the other
is how this comparison is usually got wrong:

``ff_bank``
    against the FULL bank template, inspiral and all.  This is the honest
    search answer -- it is what the pipeline would actually recover -- and
    it is low for every campaign channel largely because these records are
    short bursts with no inspiral ramp, while the bank template spends
    seconds in band accumulating SNR the burst never supplies.

``ff_window``
    against the same bank template CUT to the signal's own window about its
    peak.  This isolates MORPHOLOGY from duration: it asks whether the burst
    looks like the merger-ringdown of a binary, setting aside that it has no
    inspiral attached.

The control that calibrates both is the campaign's own vacuum binary-black
-hole twin, which IS a black-hole merger and must score high on
``ff_window``.  It does: 0.90-0.94 over 60-300 :math:`M_\odot`, recovering
the correct total mass.  That is the validation of the whole
:math:`\Psi_4 \to h` chain in :mod:`.waveforms` -- the residual few per cent
is the twin's own eccentricity (momentum 59 % of circular), its 75 :math:`M`
record and its finite extraction radius.  Any wormhole channel's score is
read against that ceiling, not against 1.
"""

from __future__ import annotations

import dataclasses
import functools

import numpy as np
from scipy.signal.windows import tukey

from grteclyn_wrapper.gw_search.templates.bank import MATCH_S, padded
from grteclyn_wrapper.gw_search.templates.nr import (
    NRWaveform, load_all_arms, template_timeseries,
)
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import M_SUN_SEC

__all__ = ["BBH_BANK", "FitResult", "fitting_factor", "survey", "windowed"]

# A quasi-circular bank in the shape of the ones the catalogues use: total
# mass, mass ratio, aligned effective spin.  Coarse on purpose -- the point
# is where the MAXIMUM over the bank lands, and the fitting factor is a flat
# function of the bank near its own peak.
BBH_BANK = dict(
    total_mass=np.geomspace(20.0, 500.0, 22),
    mass_ratio=(1.0, 2.0, 4.0),
    chi_eff=(-0.5, 0.0, 0.5, 0.9),
)
APPROXIMANT = "IMRPhenomD"
F_LOWER = 20.0
WINDOW_TAPER = 0.24


@dataclasses.dataclass
class FitResult:
    arm: str
    mass_msun: float
    ff_bank: float
    ff_window: float
    best_total_mass: float
    best_mass_ratio: float
    best_chi_eff: float

    @property
    def volume_fraction(self) -> float:
        """Fraction of the optimal detection volume the bank would reach."""
        return float(self.ff_bank ** 3)


@functools.lru_cache(maxsize=4096)
def _bbh(total_mass: float, q: float, chi: float, sample_rate: int):
    """One bank waveform, cached.

    The survey walks the same few hundred bank points once per (arm, mass),
    so without this the SAME waveform is regenerated tens of times -- and
    generating a 20 Msun template from 15 Hz is by far the most expensive
    operation in the module.  Caching turns the survey from hours into
    minutes and changes no number.
    """
    from pycbc.waveform import get_td_waveform
    m1 = total_mass * q / (1.0 + q)
    m2 = total_mass / (1.0 + q)
    hp, _ = get_td_waveform(approximant=APPROXIMANT, mass1=m1, mass2=m2,
                            spin1z=chi, spin2z=chi, delta_t=1.0 / sample_rate,
                            f_lower=15.0, distance=1.0)
    return np.asarray(hp.numpy())


def _as_series(a, sample_rate, n):
    from pycbc.types import TimeSeries
    ts = TimeSeries(np.zeros(n), delta_t=1.0 / sample_rate)
    if a.size > n:
        a = a[-n:]
    ts.data[n - a.size:] = a
    return ts


def windowed(a, sample_rate, n, n_pre, n_post):
    ip = int(np.argmax(np.abs(a)))
    lo, hi = max(0, ip - n_pre), min(a.size, ip + n_post)
    seg = a[lo:hi] * tukey(hi - lo, alpha=WINDOW_TAPER)
    from pycbc.types import TimeSeries
    ts = TimeSeries(np.zeros(n), delta_t=1.0 / sample_rate)
    ts.data[:seg.size] = seg[:n]
    return ts


def fitting_factor(wf: NRWaveform, mass_msun: float, psd, sample_rate: int,
                   *, bank: dict | None = None,
                   f_lower: float = F_LOWER) -> FitResult:
    """Maximise the overlap of one arm at one mass over the whole BBH bank."""
    from pycbc.filter import match

    bank = bank or BBH_BANK
    n = int(MATCH_S * sample_rate)
    nr = padded(template_timeseries(wf, mass_msun, 1.0, sample_rate), n)

    ipk = int(np.argmax(np.abs(wf.H)))
    pre_M, post_M = wf.u[ipk] - wf.u[0], wf.u[-1] - wf.u[ipk]

    best = FitResult(wf.name, mass_msun, 0.0, 0.0, 0.0, 0.0, 0.0)
    for M in bank["total_mass"]:
        n_pre = int(pre_M * M * M_SUN_SEC * sample_rate)
        n_post = int(post_M * M * M_SUN_SEC * sample_rate)
        for q in bank["mass_ratio"]:
            for chi in bank["chi_eff"]:
                a = _bbh(float(M), float(q), float(chi), sample_rate)
                m_full, _ = match(nr, _as_series(a, sample_rate, n), psd=psd,
                                  low_frequency_cutoff=f_lower)
                if m_full > best.ff_bank:
                    m_win, _ = match(nr, windowed(a, sample_rate, n,
                                                   n_pre, n_post),
                                     psd=psd, low_frequency_cutoff=f_lower)
                    best = FitResult(wf.name, mass_msun, float(m_full),
                                     float(m_win), float(M), float(q),
                                     float(chi))
                else:
                    m_win, _ = match(nr, windowed(a, sample_rate, n,
                                                   n_pre, n_post),
                                     psd=psd, low_frequency_cutoff=f_lower)
                    if m_win > best.ff_window:
                        best = dataclasses.replace(best,
                                                   ff_window=float(m_win))
    return best


def survey(psd, sample_rate: int, masses=(60.0, 100.0, 150.0, 200.0, 300.0),
           arms=None, verbose: bool = True) -> list[FitResult]:
    """Every arm at every mass, against the bank."""
    out = []
    for wf in load_all_arms(names=arms):
        for m in masses:
            r = fitting_factor(wf, m, psd, sample_rate)
            out.append(r)
            if verbose:
                print(f"  {r.arm:<18s} M = {m:5.0f}  FF(bank) = {r.ff_bank:.3f} "
                      f"[vol {100 * r.volume_fraction:5.1f}%]  "
                      f"FF(same window) = {r.ff_window:.3f}  "
                      f"best: M = {r.best_total_mass:5.0f}, q = "
                      f"{r.best_mass_ratio:.0f}, chi = {r.best_chi_eff:+.1f}")
    return out
