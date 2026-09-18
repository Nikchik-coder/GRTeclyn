#!/usr/bin/env python3
"""The contracts the search is assembled from.

Everything below is a ``Protocol``: a shape, not a base class.  Nothing in
this package inherits from anything here, and nothing imports a concrete
implementation in order to talk to one.  The point is the last of the five
SOLID letters -- **dependency inversion**: :class:`~.pipeline.search.Search`
is written against these names only, so the pieces it drives can be swapped
without editing it.

That is not architecture for its own sake.  It is the difference between a
search you can believe and one you cannot:

* swapping :class:`StrainSource` for a source that returns coloured noise
  with a known signal added is how the pipeline gets tested end to end
  without the network, and how its recovered SNR is checked against the
  optimal one;
* swapping :class:`NoiseModel` between the live Welch estimate and the
  aLIGO design curve is how a *projection* ("what would this look like at
  design sensitivity") is told apart from a *measurement* ("what is in O3
  data"), which are the two different claims Sec. V has to make;
* swapping :class:`BackgroundEstimator` is how the time-slide count is
  raised without touching the filtering, and the background count is the
  only thing that sets the smallest false-alarm rate the search may quote.

**Open/closed**, the second letter, is what :class:`TemplateSource` buys.  A
new radiating channel is a new row in the campaign's ``ARMS`` table and
nothing else: no module here learns its name, and the bank, the filter, the
coincidence and the ranking are untouched.
"""

from __future__ import annotations

from typing import Iterator, Protocol, Sequence, runtime_checkable


@runtime_checkable
class StrainSource(Protocol):
    """Where detector data comes from."""

    def segments(self, start: float, end: float,
                 ifos: Sequence[str]) -> list[tuple[float, float]]:
        """Intervals in ``[start, end)`` where every detector in ``ifos`` was
        observing and passed the data-quality cut."""

    def fetch(self, ifo: str, start: float, end: float, sample_rate: int):
        """``[start, end)`` of strain for one detector, as a PyCBC series."""


@runtime_checkable
class Conditioner(Protocol):
    """Raw strain to filterable strain."""

    def __call__(self, series, sample_rate: int | None = None): ...


@runtime_checkable
class NoiseModel(Protocol):
    """The noise power spectrum the inner products are weighted by."""

    def for_series(self, series):
        """PSD matching ``series`` bin for bin."""

    def for_length(self, n_samples: int, delta_t: float):
        """PSD for an FFT of ``n_samples`` at ``delta_t`` -- the bank's
        placement and the fitting factors need this, and they never hold a
        strain series to ask it from."""


@runtime_checkable
class Template(Protocol):
    """One filter, and enough provenance to explain a trigger."""

    key: str
    arm: str
    mass_msun: float

    def series(self, sample_rate: int, distance_mpc: float = 1.0): ...


@runtime_checkable
class TemplateSource(Protocol):
    """A bank: something to iterate templates out of."""

    def __iter__(self) -> Iterator[Template]: ...
    def __len__(self) -> int: ...


@runtime_checkable
class RankingStatistic(Protocol):
    """How loud is this, really.

    Kept separate from trigger generation because it is the part most likely
    to be argued about, and because ranking is where a search's sensitivity
    is actually won or lost.  A change here must not require a re-filter.
    """

    def single(self, snr, chisq_reduced):
        """Per-detector statistic; array in, array out."""

    def network(self, singles: Sequence[float]) -> float:
        """Combine per-detector statistics into the coincidence rank."""


@runtime_checkable
class BackgroundEstimator(Protocol):
    """Accidental-coincidence distribution, and the livetime it took."""

    def estimate(self, triggers_by_ifo: dict, livetime_s: float): ...
