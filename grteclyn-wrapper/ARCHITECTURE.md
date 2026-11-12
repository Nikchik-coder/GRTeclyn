# Package boundaries and folder audit

The wrapper is the GRTeclyn application: evolution preparation, launchers,
consumers, analysis and research reproduction. `packages/stationary/` is an
independently buildable distribution, imported as `grteclyn_stationary`.
Its numerical and physical models have no imports from `grteclyn_wrapper`.
The wrapper depends on the solver through the uv workspace, with one copy of
all numerical routines and radial seed solvers.

## Solver extraction

The former flat stationary modules now have owners: `matter/` for equations,
potentials and boson seeds; `geometry/` for surfaces and physical diagnostics;
`studies/` for study orchestration and reports; `ringwormhole/` for coupled
studies; `validation/` for resolution and radial diagnostics; `exports/` for
background tables. `numerics/` remains physics-independent.
The GRTresna bridge imports radial boson/Q-ball solvers from the standalone
package's `profiles/`; it retains painting, grid conversion and MPI orchestration.
Checkout-specific pipeline dispatch, background comparisons and movie orchestration
live in `src/grteclyn_wrapper/campaigns/stationary/`.

Build/install/export instructions are in [the package guide](packages/stationary/README.md).
Research launch recipes are in [STATIONARY_RESEARCH.md](STATIONARY_RESEARCH.md).

## Removed code

- Python RL environments, PPO training, bridge/gate scripts, tests and training dependencies.
  Pump queues and scoring remain in `scripts/campaigns/neuralspacetime/`.
- The unused CMA adapter with a broken evaluation import and the duplicate spinning Newton solver.
- `scripts/lib/ftl_search_common.sh` and `scripts/lib/promote_common.sh`: deprecated
  redirects with no production callers. The smoke check now checks the actual
  QD/CMA shared-config imports.
- `scripts/campaigns/lib/watch_then_scalar_shell_ftl.sh`: unreferenced watcher
  hard-coded to two old named campaigns; general queue tooling remains.
- `scripts/campaigns/promote/_archive/eval118/bicomplex_diag.sh` and its orphan
  manifest: explicitly marked NO-GO and excluded from paper numbers.
- The study-plot forwarding module: implementation and CLI now share `studies/report.py`.

The misspelled plotting namespace `visualisation/constraines` is now `constraints`,
with callers and documentation updated. Retired source is recoverable from Git.
Saved result provenance and data archives are unchanged.

## Audit method and retention

The initial inventory covered 112 code directories and 787 Python/shell files.
The review checked module imports, script/module references in active code,
configuration and research writing, executable entry points, file purposes and
existing tests. A tool with no internal caller is not automatically dead: analysis,
figure reproduction, benchmarks and manual CLIs are entry points themselves.
Legacy-format readers remain where saved research data needs them.
This is a dependency/reference review, not an assertion that every historical
campaign has been rerun. The current directory inventory below includes config-only
and documentation-only folders; generated caches and runtime outputs are excluded.

## Source directories

| Directory | Ownership and disposition |
|---|---|
| `src/grteclyn_wrapper/analysis/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/bondi_dipole/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/quantum_budget/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/wormhole_merger/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/wormhole_merger/pack/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/wormhole_merger/single_throat/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/wormhole_merger/two_throats/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/analysis/wormhole_merger/waves/` | Keep: research analysis and symbolic extraction; stationary physics extracted. |
| `src/grteclyn_wrapper/campaigns/` | Wrapper integration only: requires checkout paths or evolution tooling. |
| `src/grteclyn_wrapper/campaigns/stationary/` | Wrapper integration only: requires checkout paths or evolution tooling. |
| `src/grteclyn_wrapper/cli/` | Keep: public evolution/search command dispatch. |
| `src/grteclyn_wrapper/cli/commands/` | Keep: public evolution/search command dispatch. |
| `src/grteclyn_wrapper/core/` | Keep: evolution configuration, runners, parameter contracts and scratch policy. |
| `src/grteclyn_wrapper/grtresna/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/domain/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/fields/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/fit/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/io/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/matter/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/profiles/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/grtresna/solver/` | Keep: MPI solver bridge and grid painting; shared radial solvers extracted. |
| `src/grteclyn_wrapper/gw_search/` | Keep: waveform templates, strain processing and search/validation tools. |
| `src/grteclyn_wrapper/gw_search/analysis/` | Keep: waveform templates, strain processing and search/validation tools. |
| `src/grteclyn_wrapper/gw_search/pipeline/` | Keep: waveform templates, strain processing and search/validation tools. |
| `src/grteclyn_wrapper/gw_search/strain/` | Keep: waveform templates, strain processing and search/validation tools. |
| `src/grteclyn_wrapper/gw_search/templates/` | Keep: waveform templates, strain processing and search/validation tools. |
| `src/grteclyn_wrapper/initial_data/` | Keep: evolution seeds, constraints and metric proposals. |
| `src/grteclyn_wrapper/metrics/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/aggregation/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/diagnostics/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/io/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/probes/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/probes/ftl/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/score/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/metrics/types/` | Keep: diagnostics, physical probes and search scoring. |
| `src/grteclyn_wrapper/packaging/` | Keep: source-path scrubbing for portable research artifacts. |
| `src/grteclyn_wrapper/projection/` | Keep: geometry-to-matter projection and post-load acceptance gates. |
| `src/grteclyn_wrapper/search/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/atlas/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/geometry_atlas/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/optimize/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/pre_gpu/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/qd_search/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/search/validation_tiers/` | Keep: matter-first CMA/QD/atlas search and validation; dead adapter removed. |
| `src/grteclyn_wrapper/visualisation/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/bondi_dipole/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/constraints/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/diagnostic/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/extract_wave/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/figures/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/geometry_atlas/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/optimisation/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/process_wave/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/process_wave/consume_plotfiles/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/process_wave/consume_plotfiles/extraction/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/process_wave/consume_plotfiles/frames/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/radial/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/railgun/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/search/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/spinning_wormhole/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/visualize/` | Keep: consumers and research figures; constraint namespace corrected. |
| `src/grteclyn_wrapper/visualisation/wormhole_merger/` | Keep: consumers and research figures; constraint namespace corrected. |

## Standalone solver directories

| Directory | Ownership and disposition |
|---|---|
| `packages/stationary/src/grteclyn_stationary/checks/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/commands/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/derivations/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/exports/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/geometry/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/matter/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/numerics/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/profiles/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/railgun/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/ringwormhole/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/search/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/spinning_wormhole/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/studies/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/validation/` | Portable solver distribution; no wrapper imports. |
| `packages/stationary/src/grteclyn_stationary/workflows/` | Portable solver distribution; no wrapper imports. |

## Script directories

| Directory | Ownership and disposition |
|---|---|
| `scripts/analysis/` | Keep: paper checks and reproducible offline analysis. |
| `scripts/analysis/bondi_dipole/` | Keep: paper checks and reproducible offline analysis. |
| `scripts/analysis/quantum_budget/` | Keep: paper checks and reproducible offline analysis. |
| `scripts/analysis/spinning_wormhole/` | Keep: paper checks and reproducible offline analysis. |
| `scripts/analysis/wormhole_merger/` | Keep: paper checks and reproducible offline analysis. |
| `scripts/benchmarks/` | Keep: explicit performance/load measurement entry points. |
| `scripts/build/` | Keep: GRTresna build tooling. |
| `scripts/campaigns/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/bondi_dipole/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/boson_star/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/cmaes/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/general_ftl/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/geometry_atlas/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/geometry_atlas/seeds/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/geometry_atlas/seeds/high_exotic/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/geometry_atlas/seeds/low_exotic/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/geometry_first/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/gw_beam/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/hq/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/lib/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/neuralspacetime/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/optimisation/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/optimisation/configs/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/promote/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/promote/bicomplex_cmaes_v1/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/promote/fgeo_max_cmaes_v1/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/promote/fgeo_max_cmaes_v2/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/promote/lib/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/qball_trajectory/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/qd/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/railgun/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/railgun/configs/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/ringwormhole/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/ringwormhole/configs/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/spinning_wormhole/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/spinning_wormhole/lib/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/splash/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/wormhole_merger/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/campaigns/wormhole_merger/lib/` | Keep: named campaign launchers/configurations and shared operational helpers. |
| `scripts/lib/` | Keep env.sh; remove deprecated forwarding scripts. |
| `scripts/ops/` | Keep: bounded jobs, Git checks and resource tools. |
| `scripts/plot/` | Keep: consumer draining, cached-frame rendering and movie tools. |
| `scripts/radial/` | Keep: RadialRecipe smoke, validation and promotion entry points. |
| `scripts/search/` | Keep: offline rescoring, projection and campaign assessment. |
| `scripts/validation/` | Keep: physical validation and independent diagnostic entry points. |
| `scripts/wormhole/` | Keep: published rotating-wormhole initial data, evolution and postprocessing. |
| `scripts/wormhole/build/` | Keep: published rotating-wormhole initial data, evolution and postprocessing. |
| `scripts/wormhole/id/` | Keep: published rotating-wormhole initial data, evolution and postprocessing. |
| `scripts/wormhole/postrun/` | Keep: published rotating-wormhole initial data, evolution and postprocessing. |
| `scripts/wormhole/run/` | Keep: published rotating-wormhole initial data, evolution and postprocessing. |
