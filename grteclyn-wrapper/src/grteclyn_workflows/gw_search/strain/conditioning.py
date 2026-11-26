#!/usr/bin/env python3
"""Raw strain to filterable strain.

One class, because conditioning is one decision repeated: high-pass below
the seismic wall, match the sample rate, then throw away the seconds the
filter itself corrupted.  It is separate from the data source so that
simulated data goes through exactly the same treatment as real data -- an
injection test that conditions its noise differently from the search is
testing a pipeline that does not exist.
"""

from __future__ import annotations

__all__ = ["StandardConditioner"]


class StandardConditioner:
    """High-pass, resample, crop.  A :class:`..interfaces.Conditioner`.

    ``highpass_hz`` sits below anything filtered on and above the red wall
    that carries more power than the entire band above it.  Suppressing that
    wall in the time domain BEFORE the PSD is estimated -- rather than
    leaning on the PSD weight alone -- is what keeps the FFT's dynamic range
    honest.  ``crop_s`` then removes the ring the high-pass leaves at each
    end, which is otherwise the loudest thing in the block and triggers on
    every template in the bank.
    """

    def __init__(self, highpass_hz: float = 15.0, crop_s: float = 4.0,
                 fir_order: int = 512):
        self.highpass_hz = highpass_hz
        self.crop_s = crop_s
        self.fir_order = fir_order

    def __call__(self, series, sample_rate: int | None = None):
        out = series.highpass_fir(self.highpass_hz, self.fir_order)
        if sample_rate is not None and int(sample_rate) != int(out.sample_rate):
            from pycbc.filter import resample_to_delta_t
            out = resample_to_delta_t(out, 1.0 / int(sample_rate))
        if self.crop_s > 0:
            out = out.crop(self.crop_s, self.crop_s)
        return out

    @property
    def lost_s(self) -> float:
        """Seconds of livetime this conditioner destroys per block."""
        return 2.0 * self.crop_s
