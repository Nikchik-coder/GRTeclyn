"""The search itself: filter, veto, rank, coincide, slide, report.

``Search`` in :mod:`.search` is the only orchestrator, and it is written
against :mod:`..interfaces` alone -- it never imports a detector, a noise
curve or a waveform.
"""

from grteclyn_wrapper.gw_search.pipeline.background import TimeSlideBackground
from grteclyn_wrapper.gw_search.pipeline.coincidence import (
    Coincidence, CoincidenceEngine,
)
from grteclyn_wrapper.gw_search.pipeline.ranking import NewSNR
from grteclyn_wrapper.gw_search.pipeline.search import Search, SearchResult
from grteclyn_wrapper.gw_search.pipeline.triggers import Trigger, TriggerGenerator

__all__ = ["Coincidence", "CoincidenceEngine", "NewSNR", "Search",
           "SearchResult", "TimeSlideBackground", "Trigger", "TriggerGenerator"]
