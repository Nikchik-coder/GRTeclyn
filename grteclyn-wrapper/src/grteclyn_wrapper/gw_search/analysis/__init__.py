"""What the search means, as opposed to what it found.

``fitting_factor`` answers "would the modelled searches have recovered
this"; ``validation`` answers "is the Psi_4 -> h chain that makes these
templates right at all" -- both without any data.  ``injection`` answers the
third question, which needs data: given correct templates, does the PIPELINE
find a signal that is really there?  An empty trigger list looks the same
whether the sky is quiet or the search is broken, and only an injection
tells those apart.
"""

from grteclyn_wrapper.gw_search.analysis.fitting_factor import (
    BBH_BANK, FitResult, fitting_factor, survey,
)
from grteclyn_wrapper.gw_search.analysis.injection import (
    InjectionResult, inject, run_injections,
)
from grteclyn_wrapper.gw_search.analysis.validation import validate_bbh_twin

__all__ = ["BBH_BANK", "FitResult", "InjectionResult", "fitting_factor",
           "inject", "run_injections", "survey", "validate_bbh_twin"]
