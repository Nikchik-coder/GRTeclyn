#!/usr/bin/env python3
"""How often does noise alone do this?

Without an answer to that question a trigger is not evidence of anything,
however large its SNR.  The answer is measured, not modelled, by TIME
SLIDES: shift one detector's triggers against the other's by more than the
light-travel time and re-run the coincidence.  Any pair that survives is two
unrelated noise events that happened to line up -- exactly the accidental
coincidence whose rate is wanted -- and the shifted data has the same
glitches, the same non-stationarity and the same template bank as the real
thing, which no noise model would.

``N`` slides of ``T`` seconds of coincident livetime yield ``N*T`` seconds of
background, so a modest amount of data buys a long background.  That is what
makes this search reportable on one machine: the templates are short and
cheap, so the slides can run into the thousands.

THE FLOOR ON WHAT MAY BE CLAIMED
--------------------------------
:meth:`Background.far_of` counts ``(N_louder + 1) / T_background``.  The
``+1`` is the honest part.  A foreground event louder than every slide has
not been shown to have a vanishing false-alarm rate; it has been shown to be
louder than the background that was measured, and the smallest rate the
search may quote is one per its own background livetime.  Without the
``+1`` that event is reported at FAR zero -- infinite significance from a
finite experiment.
"""

from __future__ import annotations

import dataclasses

import numpy as np

__all__ = ["Background", "TimeSlideBackground"]

YEAR_S = 365.25 * 86400.0


@dataclasses.dataclass
class Background:
    ranks: np.ndarray           # sorted accidental-coincidence ranks
    livetime_s: float           # total slid livetime
    n_slides: int

    def far_of(self, rank: float) -> float:
        """False-alarm rate per year of ``rank``."""
        if self.livetime_s <= 0:
            return float("inf")
        louder = int(np.count_nonzero(self.ranks >= rank))
        return (louder + 1) / self.livetime_s * YEAR_S

    @property
    def floor_far_per_year(self) -> float:
        """The smallest FAR this background can support."""
        return YEAR_S / self.livetime_s if self.livetime_s > 0 else float("inf")

    def quantiles(self, qs=(50, 90, 99, 100)):
        return (np.percentile(self.ranks, qs) if self.ranks.size
                else np.full(len(qs), np.nan))


class TimeSlideBackground:
    """Accidental coincidences from non-zero time shifts.

    A :class:`..interfaces.BackgroundEstimator`.  Shifts run over
    ``+-k*step`` for ``k = 1..n_slides/2``.  Zero is excluded -- that is the
    foreground -- and ``step`` exceeds the coincidence window by two orders
    of magnitude, so no real signal can survive a slide.
    """

    def __init__(self, coincidence, n_slides: int = 400, step_s: float = 1.0):
        self.coincidence = coincidence
        self.n_slides = n_slides
        self.step_s = step_s

    def estimate(self, triggers_by_ifo: dict, livetime_s: float) -> Background:
        ifos = list(triggers_by_ifo)
        if len(ifos) != 2:
            raise ValueError(f"time slides need exactly two detectors, "
                             f"got {ifos}")
        a, b = triggers_by_ifo[ifos[0]], triggers_by_ifo[ifos[1]]
        ranks: list[float] = []
        used = 0
        for k in range(1, self.n_slides // 2 + 1):
            for sgn in (+1, -1):
                ranks.extend(c.rank for c in
                             self.coincidence(a, b, shift=sgn * k * self.step_s))
                used += 1
        return Background(ranks=np.sort(np.asarray(ranks, dtype=float)),
                          livetime_s=used * livetime_s, n_slides=used)
