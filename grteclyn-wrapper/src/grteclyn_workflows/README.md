# GRTeclyn workflows

`grteclyn_workflows` prepares and runs GRTeclyn evolutions, processes their outputs,
and supports research analysis. Install it from this project with `uv sync`.
The console command is `grteclyn-workflows`; the module command is
`python -m grteclyn_workflows`.

The independent stationary solver is `grteclyn_stationary`, built from
[`packages/stationary`](../../packages/stationary/README.md). Workflows can use
that solver; the solver never imports this package.

## Source layout

- `evolution/`: checkout configuration, initial parameter contracts, run directories,
  binary execution and consumer commands.
- `initial_data/`: seed geometries and initial constraint preparation.
- `grtresna/`: the GRTresna MPI bridge, field painting and grid conversion.
- `postprocessing/`: plotfile watching, physical extraction and per-run frame rendering.
  Run it with `python -m grteclyn_workflows.postprocessing`.
- `diagnostics/`: measurements, physical probes, diagnostic readers and episode aggregation.
- `search/`: candidate searches, scheduling, validation and `scoring/` objectives.
- `analysis/`: research-specific analysis of saved results.
- `plotting/`: figures from diagnostics and results, grouped by subject.
- `gw_search/`: gravitational-wave templates, strain processing and searches.
- `projection/`: geometry-to-matter projection and acceptance checks.
- `campaigns/`: checkout-specific integration with stationary studies.
- `packaging/`: portable artifact path scrubbing.
- `cli/`: command parsing and dispatch.

## Common imports

```python
from grteclyn_workflows.evolution.config import resolve_example
from grteclyn_workflows.diagnostics import read_episode_metrics
from grteclyn_workflows.search.scoring import score_episode
```

Source directories contain code and documentation. Generic plotters write to
`runs/plots/` by default; campaign tools use each run's output directory. Curated
figures stay under `results/`. Pass an explicit output path when reproducing them.

The distribution, command and import namespace were renamed from
`grteclyn-wrapper` / `grteclyn_wrapper`. The repository project directory remains
`grteclyn-wrapper/`, which owns the existing virtual environment and scripts.
There are no old import aliases. Reinstall the project after pulling this change.
See [ARCHITECTURE.md](../../ARCHITECTURE.md) for the folder inventory.
