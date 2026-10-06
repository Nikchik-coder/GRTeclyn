#!/usr/bin/env python3
"""Noise power spectra: what the inner products are weighted by.

Two implementations of :class:`..interfaces.NoiseModel`, and the difference
between them is the difference between two claims Sec. V has to keep apart:

``WelchNoise``
    the spectrum measured from the block being searched.  Everything the
    search REPORTS -- triggers, ranks, false-alarm rates, the horizon at
    which the data excludes a source -- is weighted by this, because it is
    what the detector was actually doing at that GPS second.

``DesignNoise``
    the Advanced LIGO design curve.  Used for bank placement in the
    no-data paths and for PROJECTIONS ("what would this channel look like
    at design sensitivity"), never for a statement about O3.  Quoting a
    design-curve horizon as a search result is the standard way to
    overstate a null result by a factor of a few.
"""

from __future__ import annotations

__all__ = ["DesignNoise", "WelchNoise"]

PSD_SEG_S = 8.0


class WelchNoise:
    """Welch-median PSD of the block, truncated for time-domain filtering."""

    def __init__(self, seg_s: float = PSD_SEG_S, f_lower: float = 15.0):
        self.seg_s = seg_s
        self.f_lower = f_lower
        self._last = None
        # for_length is called once per match, and bank placement runs tens
        # of thousands of matches on a handful of distinct FFT lengths.
        # Re-interpolating the spectrum each time made placement the most
        # expensive step in the whole search, by an order of magnitude.
        self._cache: dict = {}

    def for_series(self, series):
        from pycbc.psd import interpolate, inverse_spectrum_truncation
        psd = interpolate(series.psd(self.seg_s), series.delta_f)
        psd = inverse_spectrum_truncation(
            psd, int(self.seg_s * series.sample_rate),
            low_frequency_cutoff=self.f_lower, trunc_method="hann")
        self._last = psd
        self._cache.clear()      # a new block is a new spectrum
        return psd

    def for_length(self, n_samples: int, delta_t: float):
        """The most recent measured spectrum, re-binned.

        Falls back to the design curve only if nothing has been measured
        yet, and says so, because a bank silently placed on a design curve
        and then run on real data is a bank with the wrong spacing.
        """
        if self._last is None:
            print("  [noise] no measured PSD yet -- placing on the design "
                  "curve; re-place once a block is conditioned")
            return DesignNoise(self.f_lower).for_length(n_samples, delta_t)
        key = (int(n_samples), float(delta_t), id(self._last))
        if key not in self._cache:
            from pycbc.psd import interpolate
            self._cache[key] = interpolate(self._last,
                                           1.0 / (n_samples * delta_t))
        return self._cache[key]

    @property
    def lost_s(self) -> float:
        """Seconds a filter must crop at each end for this PSD truncation."""
        return self.seg_s


class DesignNoise:
    """Advanced LIGO zero-detuned high-power design sensitivity."""

    def __init__(self, f_lower: float = 15.0):
        self.f_lower = f_lower
        self._cache: dict = {}

    def for_series(self, series):
        return self.for_length(len(series), float(series.delta_t))

    def for_length(self, n_samples: int, delta_t: float):
        key = (int(n_samples), float(delta_t))
        if key not in self._cache:
            import pycbc.psd
            self._cache[key] = pycbc.psd.aLIGOZeroDetHighPower(
                n_samples // 2 + 1, 1.0 / (n_samples * delta_t), self.f_lower)
        return self._cache[key]

    @property
    def lost_s(self) -> float:
        return PSD_SEG_S
