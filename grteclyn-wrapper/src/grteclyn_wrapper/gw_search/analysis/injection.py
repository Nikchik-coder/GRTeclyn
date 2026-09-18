#!/usr/bin/env python3
"""Does the search actually find a signal that is there?

The validation in :mod:`.validation` tests the TEMPLATES -- that the
:math:`\\Psi_4 \\to h` chain reconstructs a waveform correctly.  It says
nothing about the pipeline wrapped around them.  A search can have perfect
templates and still recover nothing, and the failure is silent in the worst
way: an empty trigger list looks exactly like a quiet sky.

So: add a campaign waveform of known amplitude to real conditioned strain at
a known GPS time, run the ordinary search machinery over it, and check three
things.

1.  **It is found at all**, at the right time.  A template built with its
    peak at ``t = 0`` should report a trigger within a sample or two of where
    the injection was placed; a sign error, an epoch error or an off-by-one
    in the cropping shows up here as a constant offset, and nowhere else.
2.  **The recovered SNR matches the optimal one.**  The optimal SNR is
    computable in closed form from the template's norm and the injection
    distance, so the ratio recovered/optimal is a pure number that should sit
    just under 1 -- under, because the bank is discrete and the injected mass
    generally falls between rungs.  If it sits far under, the bank is spaced
    too loosely or the filter is losing band somewhere.
3.  **The chi-squared does not veto it.**  An injected signal IS consistent
    with its own template, so its reduced chi-squared should be of order 1
    and the re-weighted statistic should barely move.  If a real signal is
    vetoed, the veto is misconfigured and the whole search is insensitive --
    a failure that a background estimate will never reveal, because the
    background is made of glitches, and glitches being vetoed is what it
    looks like when everything is fine.

Point 3 is the one that matters most for THIS bank, because the templates are
short and the veto has few bins to work with (see :mod:`..pipeline.ranking`).
"""

from __future__ import annotations

import dataclasses

import numpy as np

__all__ = ["InjectionResult", "inject", "run_injections"]


@dataclasses.dataclass
class InjectionResult:
    arm: str
    mass_msun: float
    distance_mpc: float
    optimal_snr: float
    recovered_snr: float
    recovered_stat: float
    chisq_r: float
    dt_ms: float
    found: bool

    @property
    def efficiency(self) -> float:
        """Recovered over optimal: the bank's discreteness, made visible."""
        return (self.recovered_snr / self.optimal_snr
                if self.optimal_snr > 0 else 0.0)


def inject(strain, template, gps_time: float):
    """``strain`` with ``template``'s peak placed at ``gps_time``.

    The template carries a negative epoch so that its own peak sits at
    ``t = 0``; adding that epoch to the requested time is what makes "the
    injection is at ``gps_time``" mean the peak and not the array's start.
    """
    out = strain.copy()
    start = float(gps_time) + float(template.start_time)
    i0 = int(round((start - float(out.start_time)) / out.delta_t))
    if i0 < 0 or i0 + len(template) > len(out):
        raise ValueError("injection falls outside the block")
    out.data[i0:i0 + len(template)] += template.numpy()
    return out


def run_injections(strain, noise, bank, triggers, *, ifo: str = "H1",
                   target_snr: float = 20.0, n_per_arm: int = 3,
                   verbose: bool = True) -> list[InjectionResult]:
    """Inject one signal per (arm, mass) into ``strain`` and recover it.

    Each injection is run in a CLEAN COPY of the block and searched with the
    WHOLE bank, not just with the template that was injected: recovering a
    signal with its own template alone would test an inner product, not a
    search.

    The distance is CHOSEN PER INJECTION so that every one lands at
    ``target_snr``, rather than fixed.  A fixed distance does not test the
    pipeline, it tests the luminosity ordering: at 500 Mpc the collapsing
    throat arrives at optimal SNR 0.8 and "NOT FOUND" means only that it was
    never findable, while the spiral arrives at several hundred, where the
    chi-squared is dominated by per-mille template mismatch and no real
    search ever operates.  Equalising the SNR is what makes "found" and
    "vetoed" mean the same thing for every channel.
    """
    from pycbc.filter import sigma as pycbc_sigma
    from pycbc.filter.matchedfilter import make_frequency_series

    psd = noise.for_series(strain)
    mid = float(strain.start_time) + 0.5 * len(strain) * strain.delta_t

    by_arm: dict = {}
    for bt in bank:
        by_arm.setdefault(bt.arm, []).append(bt)

    out: list[InjectionResult] = []
    for arm, rungs in by_arm.items():
        picks = [rungs[int(round(f * (len(rungs) - 1)))]
                 for f in np.linspace(0.15, 0.85, n_per_arm)]
        for bt in picks:
            # sigma at 1 Mpc IS the distance at which this template rings
            # up SNR 1, so the distance for target_snr is just sigma/target.
            sigma1 = float(pycbc_sigma(
                make_frequency_series(
                    _resized(bt.series(int(strain.sample_rate), 1.0),
                             len(strain))),
                psd=psd, low_frequency_cutoff=bt.f_lower_hz()))
            distance_mpc = sigma1 / float(target_snr)
            tmpl = bt.series(int(strain.sample_rate), distance_mpc)
            optimal = float(target_snr)
            data = inject(strain, tmpl, mid)

            best = None
            for other in bank:
                got = triggers(data, other.series(int(strain.sample_rate)),
                               psd, ifo=ifo, key=other.key, arm=other.arm,
                               mass_msun=other.mass_msun,
                               f_lower=other.f_lower_hz())
                for t in got:
                    if abs(t.time - mid) < 0.05 and (best is None
                                                     or t.snr > best.snr):
                        best = t
            res = InjectionResult(
                arm=arm, mass_msun=bt.mass_msun, distance_mpc=distance_mpc,
                optimal_snr=optimal,
                recovered_snr=best.snr if best else 0.0,
                recovered_stat=best.stat if best else 0.0,
                chisq_r=best.chisq_r if best else float("nan"),
                dt_ms=(best.time - mid) * 1e3 if best else float("nan"),
                found=best is not None)
            out.append(res)
            if verbose:
                print(f"  {arm:<18s} M = {bt.mass_msun:6.1f} at "
                      f"{distance_mpc:8.1f} Mpc (optimal SNR "
                      f"{optimal:.0f}) -> recovered {res.recovered_snr:6.2f} "
                      f"({100 * res.efficiency:5.1f} %), chi2_r "
                      f"{res.chisq_r:6.2f}, newsnr {res.recovered_stat:6.2f}, "
                      f"dt {res.dt_ms:+7.2f} ms"
                      f"{'' if res.found else '   *** NOT FOUND ***'}")
    return out


def _resized(ts, n: int):
    out = ts.copy()
    out.resize(n)
    return out
