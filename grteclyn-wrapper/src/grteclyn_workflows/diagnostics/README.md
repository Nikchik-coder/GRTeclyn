# Physical diagnostics

This package reads simulation outputs and computes physical measurements.
`measurements/` owns diagnostic stream readers, `probes/` owns physical probes,
`types/` defines their records, `io/` reads and serializes data, and
`aggregation/` builds episode summaries. `catalog.py` registers measurements.

Search objectives and prefix scoring live in `grteclyn_workflows.search.scoring`.
They consume diagnostics; diagnostic imports do not load the search drivers.

```python
from grteclyn_workflows.diagnostics import read_episode_metrics
from grteclyn_workflows.search.scoring import score_episode
```
