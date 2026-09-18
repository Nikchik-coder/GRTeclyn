#!/usr/bin/env python3
"""Two detectors, one signal.

A gravitational wave crosses the Earth in 10 ms and appears in both
detectors, in the same template, with consistent amplitude.  A glitch in
Hanford has no reason to be accompanied by anything in Livingston.  Demanding
coincidence is the single most effective cut in the whole search, and it is
what makes the time-slide background possible: slide one detector against
the other and every surviving coincidence is, by construction, accidental.

The window is the light-travel time plus timing error.  It is deliberately
NOT tuned down: a tighter window buys a little background at the cost of
throwing away real signals from sky positions near the detectors' plane, and
this search has no sky-position prior to defend a tighter one with.
"""

from __future__ import annotations

import dataclasses

import numpy as np

__all__ = ["Coincidence", "CoincidenceEngine"]

LIGHT_TRAVEL_H1L1_S = 0.010


@dataclasses.dataclass
class Coincidence:
    rank: float
    template: str
    arm: str
    times: dict          # ifo -> GPS
    stats: dict          # ifo -> single-detector statistic

    @property
    def dt_ms(self) -> float:
        a, b = list(self.times.values())[:2]
        return (a - b) * 1e3


class CoincidenceEngine:
    """Pair triggers across two detectors.  Ranking is injected."""

    def __init__(self, ranking, window_s: float = 0.015):
        self.ranking = ranking
        self.window_s = window_s

    def __call__(self, trig_a, trig_b, *, shift: float = 0.0
                 ) -> list[Coincidence]:
        """Pairs in the same template within the window, ``trig_b`` slid.

        Only the loudest partner per template per ``trig_a`` trigger is
        kept, so one loud glitch cannot manufacture a hundred coincidences
        and flood the background with copies of itself.
        """
        by_key: dict[str, list] = {}
        for t in trig_b:
            by_key.setdefault(t.template, []).append(t)

        out: list[Coincidence] = []
        for ta in trig_a:
            cands = by_key.get(ta.template)
            if not cands:
                continue
            times = np.fromiter((t.time + shift for t in cands), float,
                                len(cands))
            near = np.flatnonzero(np.abs(times - ta.time) <= self.window_s)
            if not near.size:
                continue
            tb = cands[near[int(np.argmax([cands[i].stat for i in near]))]]
            out.append(Coincidence(
                rank=self.ranking.network((ta.stat, tb.stat)),
                template=ta.template, arm=ta.arm,
                times={ta.ifo: ta.time, tb.ifo: tb.time},
                stats={ta.ifo: ta.stat, tb.ifo: tb.stat}))
        return out
