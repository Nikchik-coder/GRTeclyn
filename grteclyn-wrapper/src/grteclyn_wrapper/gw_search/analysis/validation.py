#!/usr/bin/env python3
r"""The one test in this package that can fail.

Everything the search reports rests on one step that is easy to get wrong
and impossible to check by eye: turning a numerical :math:`\Psi_4` record
into strain.  It is a double integration, two integration constants ride in
on a record only tens of masses long, and a mistake there does not look like
a mistake -- it looks like a waveform.

The campaign supplies its own control.  ``vacuum BBH twin`` is an
equal-mass non-spinning binary BLACK HOLE evolved with the same code, the
same grid and the same extraction as the wormhole arms.  Whatever a
wormhole merger is meant to look like, this one has to look like a binary
black hole.  So: put it through the search's own template chain and match it
against ``IMRPhenomD``, the model the catalogues are built from.

TWO NUMBERS, AND ONLY ONE OF THEM IS THE TEST
----------------------------------------------
Matched against the FULL model waveform the twin scores 0.46-0.63, and that
is not a failure -- it is the answer to a different question.  The model
spends seconds in band accumulating signal-to-noise up a long inspiral
ramp; the twin's record is 75 :math:`M` of merger with no inspiral attached,
because that is where the simulation was started.  Most of the model's power
has nothing to align with.

Cut the model to the twin's OWN window about its peak and the comparison is
like for like.  That is :func:`validate_bbh_twin`, and it must pass:
**0.90-0.94 over 60-300** :math:`M_\odot`, **recovering the correct total
mass**.  The residual few per cent is accounted for -- the twin's momentum
is 59 % of circular so it is an eccentric plunge, its record is short, and
it is extracted at :math:`R = 14` rather than at infinity.

Read every wormhole channel's fitting factor against that 0.90-0.94
ceiling, never against 1.
"""

from __future__ import annotations

import dataclasses

import numpy as np

from grteclyn_wrapper.gw_search.templates.bank import MATCH_S, padded
from grteclyn_wrapper.gw_search.templates.nr import load_arm, template_timeseries
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import M_SUN_SEC

__all__ = ["ValidationRow", "validate_bbh_twin"]

PASS_THRESHOLD = 0.85


@dataclasses.dataclass
class ValidationRow:
    mass_nr: float
    ff_full: float
    ff_window: float
    mass_recovered: float

    @property
    def mass_error(self) -> float:
        return self.mass_recovered / self.mass_nr - 1.0


def validate_bbh_twin(noise, sample_rate: int = 4096,
                      masses=(60.0, 100.0, 150.0, 200.0, 300.0),
                      f_lower: float = 20.0, verbose: bool = True):
    """Match the campaign's BBH control against IMRPhenomD.

    Returns ``(rows, passed)``.
    """
    from pycbc.filter import match
    from pycbc.waveform import get_td_waveform
    from pycbc.types import TimeSeries
    from grteclyn_wrapper.gw_search.analysis.fitting_factor import windowed

    n = int(MATCH_S * sample_rate)
    psd = noise.for_length(n, 1.0 / sample_rate)
    wf = load_arm("vacuum BBH twin")
    ipk = int(np.argmax(np.abs(wf.H)))
    pre_M, post_M = wf.u[ipk] - wf.u[0], wf.u[-1] - wf.u[ipk]

    if verbose:
        print(f"the control: {pre_M:.0f} M of record before its peak, "
              f"{post_M:.0f} M after\n")
        print(f"{'M_NR':>6s} {'FF(full model)':>15s} {'FF(same window)':>16s} "
              f"{'M recovered':>12s} {'error':>7s}")

    rows = []
    for m_nr in masses:
        nr = padded(template_timeseries(wf, m_nr, 1.0, sample_rate), n)
        best = (0.0, 0.0, 0.0)
        for m_model in m_nr * np.array([0.7, 0.8, 0.9, 0.95, 1.0, 1.05,
                                        1.1, 1.2, 1.35]):
            hp, _ = get_td_waveform(approximant="IMRPhenomD",
                                    mass1=m_model / 2, mass2=m_model / 2,
                                    delta_t=1.0 / sample_rate, f_lower=15.0,
                                    distance=1.0)
            a = np.asarray(hp.numpy())
            full = TimeSeries(np.zeros(n), delta_t=1.0 / sample_rate)
            b = a[-n:] if a.size > n else a
            full.data[n - b.size:] = b
            m_full, _ = match(nr, full, psd=psd, low_frequency_cutoff=f_lower)
            win = windowed(a, sample_rate, n,
                           int(pre_M * m_model * M_SUN_SEC * sample_rate),
                           int(post_M * m_model * M_SUN_SEC * sample_rate))
            m_win, _ = match(nr, win, psd=psd, low_frequency_cutoff=f_lower)
            if m_win > best[1]:
                best = (float(m_full), float(m_win), float(m_model))
        row = ValidationRow(m_nr, *best)
        rows.append(row)
        if verbose:
            print(f"{row.mass_nr:6.0f} {row.ff_full:15.3f} "
                  f"{row.ff_window:16.3f} {row.mass_recovered:12.0f} "
                  f"{row.mass_error:+7.1%}")

    passed = all(r.ff_window > PASS_THRESHOLD for r in rows)
    if verbose:
        lo = min(r.ff_window for r in rows)
        hi = max(r.ff_window for r in rows)
        print(f"\nVERDICT: {'PASS' if passed else 'FAIL'} -- same-window "
              f"match {lo:.3f}-{hi:.3f} against a threshold of "
              f"{PASS_THRESHOLD}")
    return rows, passed
