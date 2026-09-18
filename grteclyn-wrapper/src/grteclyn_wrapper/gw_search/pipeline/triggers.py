#!/usr/bin/env python3
"""Filtering one template through one block, and clustering what comes out.

Single responsibility: this module turns (strain, template, noise) into a
list of :class:`Trigger`.  It does not decide what is significant -- that
needs a background, which needs every block -- and it does not decide how to
rank, which is :mod:`.ranking`'s job and is injected.
"""

from __future__ import annotations

import dataclasses

import numpy as np

__all__ = ["Trigger", "TriggerGenerator", "chisq_bins"]


@dataclasses.dataclass
class Trigger:
    """One clustered maximum, with the provenance to explain it later."""

    ifo: str
    template: str
    arm: str
    mass_msun: float
    time: float          # GPS of the TEMPLATE'S PEAK, not of the array
    snr: float
    chisq_r: float
    stat: float          # the ranking statistic's single-detector value
    sigma: float         # Mpc at which this template would ring up SNR 1


def chisq_bins(template, f_lower: float, sample_rate: int) -> int:
    """Bin count from the template's time-bandwidth product.

    A fixed count (16, in the CBC searches) presumes a template with seconds
    of structure.  These span 5 ms to 125 ms, two orders of magnitude, so
    the count follows ``sqrt(T * Delta f)`` -- how many genuinely
    independent frequency cells the template has -- clipped to ``[4, 16]``.
    Asking for more bins than the template can fill does not strengthen the
    veto; it just divides noise into smaller pieces.
    """
    dur = len(template) * template.delta_t
    bw = max(0.5 * sample_rate - f_lower, 1.0)
    return int(np.clip(int(np.sqrt(dur * bw)), 4, 16))


class TriggerGenerator:
    """Matched filter + chi-squared veto + clustering, for one block."""

    def __init__(self, ranking, f_lower: float = 20.0,
                 snr_floor: float = 5.0, psd_seg_s: float = 8.0):
        self.ranking = ranking
        self.f_lower = f_lower
        self.snr_floor = snr_floor
        self.psd_seg_s = psd_seg_s

    def __call__(self, strain, template, psd, *, ifo: str, key: str,
                 arm: str, mass_msun: float, f_lower: float | None = None,
                 cluster_s: float | None = None) -> list[Trigger]:
        """Filter, cluster, then veto ONLY the survivors.

        The order matters for cost, and the cost decides how much background
        the search can afford.  ``power_chisq`` over a whole block is ten
        or more FFTs per template; at 120 templates and two detectors that
        is minutes per block, and it computes a veto for the ~2 million
        samples that were never candidates.  Clustering on SNR first and
        evaluating the veto at the few surviving maxima is what the
        production pipelines do, and it turns minutes into seconds.

        The one thing it costs: a loud glitch can now mask a quieter but
        cleaner trigger inside the same cluster window, where clustering on
        the vetoed statistic would have kept the cleaner one.  The window is
        a few template lengths -- milliseconds here -- so this is a real but
        small effect, and it is stated rather than hidden.
        """
        from pycbc.filter.matchedfilter import (
            make_frequency_series, matched_filter_core,
        )
        from pycbc.filter import sigma as pycbc_sigma

        f_lower = self.f_lower if f_lower is None else max(f_lower,
                                                           self.f_lower)
        from pycbc.types import zeros
        from pycbc.vetoes.chisq import (
            power_chisq_at_points_from_precomputed, power_chisq_bins,
        )

        t = template.copy()
        if len(t) > len(strain):
            return []
        # The template was built with its PEAK at t = 0 (negative epoch), so
        # this turns an SNR-series index into the GPS time of the burst's
        # peak rather than of the array's start.
        peak_offset = -float(t.start_time)
        t.resize(len(strain))

        # Transform ONCE and pass the frequency series everywhere: the
        # filter, the veto's bin edges and the norm all want the same
        # htilde, and power_chisq_bins in particular MISREADS a TimeSeries
        # -- it infers the FFT length as 2*(len-1), which for a time-domain
        # argument is twice the real one, and indexes off the end of its own
        # sigma-squared series.
        htilde = make_frequency_series(t)
        # corr_out must be a full-length buffer: the veto's shift_sum walks
        # the whole correlation, and matched_filter_core will otherwise hand
        # back a series the veto cannot index the same way (this is exactly
        # how pycbc.vetoes.power_chisq calls it).
        corra = zeros((len(htilde) - 1) * 2, dtype=htilde.dtype)
        snr_ts, corr, snr_norm = matched_filter_core(
            htilde, strain, psd=psd, low_frequency_cutoff=f_lower,
            corr_out=corra)
        rho = np.abs(snr_ts.numpy()) * snr_norm

        # Both ends of the block are corrupt: the PSD truncation rings for
        # psd_seg_s, and the template itself wraps around by its own length.
        pad = self.psd_seg_s + len(template) * template.delta_t
        npad = int(round(pad * float(strain.sample_rate)))
        if 2 * npad >= rho.size:
            return []
        valid = np.zeros(rho.size, dtype=bool)
        valid[npad:rho.size - npad] = True

        idx = np.flatnonzero(valid & (rho > self.snr_floor))
        if not idx.size:
            return []

        win = int(round((cluster_s
                         or max(4.0 * len(template) * template.delta_t, 0.1))
                        * float(strain.sample_rate)))
        keep = []
        while idx.size:
            i = idx[int(np.argmax(rho[idx]))]
            keep.append(int(i))
            idx = idx[np.abs(idx - i) > win]
        keep = np.array(sorted(keep))

        nbins = chisq_bins(template, f_lower, int(strain.sample_rate))
        bins = power_chisq_bins(htilde, nbins, psd, f_lower)
        # UNNORMALISED snr here, with snr_norm passed alongside.  PyCBC's
        # own power_chisq feeds it matched_filter_core's raw output and the
        # norm separately, and the expression inside squares the norm once.
        # Passing the normalised series as well double-counts it: measured on
        # an injection of the filter's own template, the reduced chi-squared
        # came out 28.7 where it must be ~1, and the veto was demoting a
        # perfect signal from SNR 19.6 to newsnr 4.1.  A search with this bug
        # finds nothing and reports a quiet sky.
        chisq = power_chisq_at_points_from_precomputed(
            corr, snr_ts.numpy()[keep], snr_norm, bins, keep)
        chisq = np.asarray(chisq, dtype=float) / (2 * nbins - 2)

        sig = float(pycbc_sigma(htilde, psd=psd,
                                low_frequency_cutoff=f_lower))
        stat = self.ranking.single(rho[keep], chisq)
        times = np.asarray(snr_ts.sample_times)[keep] + peak_offset

        return [Trigger(ifo=ifo, template=key, arm=arm, mass_msun=mass_msun,
                        time=float(times[j]), snr=float(rho[keep[j]]),
                        chisq_r=float(chisq[j]), stat=float(stat[j]),
                        sigma=sig)
                for j in range(keep.size)]
