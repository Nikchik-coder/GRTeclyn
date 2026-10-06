"""Campaign waveforms as filters.

``nr`` turns a packed ``r Psi_4`` record into strain; ``bank`` lays the mass
ladder that record is filtered at.  Nothing here knows what a detector's
data looks like.
"""

from grteclyn_wrapper.gw_search.templates.bank import (
    BankTemplate, MassLadderBank, mass_range,
)
from grteclyn_wrapper.gw_search.templates.nr import (
    ARM_NAMES, NRWaveform, load_all_arms, load_arm, template_timeseries,
)

__all__ = ["ARM_NAMES", "BankTemplate", "MassLadderBank", "NRWaveform",
           "load_all_arms", "load_arm", "mass_range", "template_timeseries"]
