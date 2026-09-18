"""Detector data: where it comes from, what is done to it, how noisy it is.

Nothing here knows what a wormhole is.  Everything here satisfies one of
the ``strain``-side protocols in :mod:`..interfaces`, so a search can be
handed live O3 data, a simulated block, or a design-sensitivity projection
without any other module noticing.
"""

from grteclyn_wrapper.gw_search.strain.conditioning import StandardConditioner
from grteclyn_wrapper.gw_search.strain.gwosc import CACHE_DIR, GwoscStrainSource
from grteclyn_wrapper.gw_search.strain.noise import DesignNoise, WelchNoise

__all__ = ["CACHE_DIR", "DesignNoise", "GwoscStrainSource",
           "StandardConditioner", "WelchNoise"]
