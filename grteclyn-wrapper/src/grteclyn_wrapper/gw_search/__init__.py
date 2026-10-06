"""Matched-filter search of public LIGO data for the campaign's waveforms.

Layers, outermost first.  Each one depends only on the layer below it and on
:mod:`.interfaces`; none depends on :mod:`.cli`.

``cli``          entry points; the only module that prints for a human.
``analysis``     what the templates MEAN -- fitting factors, and the
                 validation of the Psi_4 -> h chain against IMRPhenomD.
``pipeline``     the search: filter, veto, rank, coincide, slide.
``templates``    campaign waveforms as filters, and the mass ladder.
``strain``       detector data: source, conditioning, noise model.
``interfaces``   the protocols the above are wired together with.

The article's Sec. V is written from what ``cli`` prints.
"""

from grteclyn_wrapper.gw_search import interfaces

__all__ = ["interfaces"]
