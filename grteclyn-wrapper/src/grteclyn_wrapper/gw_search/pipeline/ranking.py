#!/usr/bin/env python3
r"""How loud is this, really.

Matched-filter SNR :math:`\rho` is optimal for a signal in STATIONARY
GAUSSIAN noise.  Advanced LIGO data is neither.  Loud non-Gaussian
transients -- scattered light, blip glitches, and a long tail of things
with no name -- produce large :math:`\rho` against almost any template, and
they are far more common than signals.  Ranking on :math:`\rho` therefore
ranks on glitchiness.

:class:`NewSNR` is the standard repair (PyCBC's re-weighted SNR).  Allen's
:math:`\chi^2` test splits the template into ``p`` frequency bands chosen to
contribute equal shares of the expected SNR and asks whether the trigger's
SNR arrived spread across them, as a real signal's must, or dumped into one
band, as a glitch's does.  With :math:`\chi^2_r` the reduced statistic,

.. math::
    \hat\rho = \begin{cases}
      \rho & \chi^2_r \le 1\\
      \rho\,\big[\tfrac12\,(1 + (\chi^2_r)^{3})\big]^{-1/6} & \chi^2_r > 1
    \end{cases}

which leaves a consistent trigger alone and pushes an inconsistent one down
hard.  This is its own class because ranking is the part of a search most
likely to be revised, and revising it must not mean re-filtering the data.

A CAVEAT THAT IS SPECIFIC TO THESE TEMPLATES
--------------------------------------------
The veto's power grows with the number of independent frequency cells the
template has to offer, and this bank's templates are SHORT -- 5 ms to
125 ms.  :func:`..triggers.chisq_bins` scales the bin count with the
time-bandwidth product rather than fixing it at the CBC searches' 16, and
for the lightest rungs it returns as few as 4.  The veto is correspondingly
weaker here than in a binary-black-hole search, and the background rate is
correspondingly higher.  Nothing is hidden by this: the time-slide
background measures whatever the veto failed to remove, which is the whole
point of measuring it instead of assuming it.
"""

from __future__ import annotations

import numpy as np

__all__ = ["NewSNR"]


class NewSNR:
    """PyCBC's re-weighted SNR.  A :class:`..interfaces.RankingStatistic`."""

    name = "newsnr"

    def single(self, snr, chisq_reduced):
        from pycbc.events.ranking import newsnr
        return newsnr(snr, chisq_reduced)

    def network(self, singles) -> float:
        """Quadrature sum -- the network statistic for a coincidence.

        Correct because the per-detector statistics are independent under
        the noise hypothesis, and standard, so the rank is comparable with
        published ones.
        """
        return float(np.sqrt(sum(float(s) ** 2 for s in singles)))
