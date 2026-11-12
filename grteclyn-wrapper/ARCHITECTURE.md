# Package boundaries and folder audit

The wrapper is the GRTeclyn application: evolution preparation, launchers,
consumers, analysis and research reproduction. `packages/stationary/` is an
independently buildable distribution, imported as `grteclyn_stationary`.
Its numerical and physical models have no imports from `grteclyn_workflows`.
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
live in `src/grteclyn_workflows/campaigns/stationary/`.

Build/install/export instructions are in [the package guide](packages/stationary/README.md).
Research launch recipes are in [STATIONARY_RESEARCH.md](STATIONARY_RESEARCH.md).

## Workflow namespace migration

The application distribution and command are `grteclyn-workflows`; imports use
`grteclyn_workflows`. The existing project directory and virtual environment stay
under `grteclyn-wrapper/`. There are no old-namespace shims.

`core` is now `evolution`. Physical `metrics` are now `diagnostics`, with stream
readers under `measurements`; objectives and incremental scoring live in
`search/scoring`. The plotfile consumer is `postprocessing`, while research plots
live in `plotting`. Waveform plotters share `plotting/waveforms`, and slice plotting
uses `plotting/slices`. Tests and executable references follow the new owners.

Nine generated PNG/PDF/EPS files were deleted from source on request. Plotting
defaults now write outside source. Existing result data and saved provenance were
not rewritten; current reproduction instructions point to the new modules.

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

| Directory | Purpose |
|---|---|
| `src/grteclyn_workflows/analysis/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/bondi_dipole/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/quantum_budget/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/wormhole_merger/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/wormhole_merger/pack/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/wormhole_merger/single_throat/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/wormhole_merger/two_throats/` | Analysis of saved research results. |
| `src/grteclyn_workflows/analysis/wormhole_merger/waves/` | Analysis of saved research results. |
| `src/grteclyn_workflows/campaigns/` | Checkout-specific campaign integration. |
| `src/grteclyn_workflows/campaigns/stationary/` | Checkout-specific campaign integration. |
| `src/grteclyn_workflows/cli/` | Command parsing and dispatch. |
| `src/grteclyn_workflows/cli/commands/` | Command parsing and dispatch. |
| `src/grteclyn_workflows/diagnostics/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/aggregation/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/io/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/measurements/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/probes/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/probes/ftl/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/diagnostics/types/` | Physical measurements and diagnostic readers. |
| `src/grteclyn_workflows/evolution/` | Simulation preparation and execution. |
| `src/grteclyn_workflows/grtresna/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/domain/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/fields/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/fit/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/io/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/matter/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/profiles/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/grtresna/solver/` | GRTresna bridge and grid conversion. |
| `src/grteclyn_workflows/gw_search/` | Gravitational-wave searches. |
| `src/grteclyn_workflows/gw_search/analysis/` | Gravitational-wave searches. |
| `src/grteclyn_workflows/gw_search/pipeline/` | Gravitational-wave searches. |
| `src/grteclyn_workflows/gw_search/strain/` | Gravitational-wave searches. |
| `src/grteclyn_workflows/gw_search/templates/` | Gravitational-wave searches. |
| `src/grteclyn_workflows/initial_data/` | Evolution seeds and initial constraints. |
| `src/grteclyn_workflows/packaging/` | Artifact path scrubbing. |
| `src/grteclyn_workflows/plotting/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/bondi_dipole/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/constraints/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/diagnostics/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/geometry_atlas/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/optimisation/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/radial/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/railgun/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/search/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/slices/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/spinning_wormhole/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/waveforms/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/wormhole_dynamics/` | Research plots and figures. |
| `src/grteclyn_workflows/plotting/wormhole_merger/` | Research plots and figures. |
| `src/grteclyn_workflows/postprocessing/` | Plotfile processing, extraction and frame rendering. |
| `src/grteclyn_workflows/postprocessing/extraction/` | Plotfile processing, extraction and frame rendering. |
| `src/grteclyn_workflows/postprocessing/frames/` | Plotfile processing, extraction and frame rendering. |
| `src/grteclyn_workflows/projection/` | Geometry-to-matter projection. |
| `src/grteclyn_workflows/search/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/atlas/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/geometry_atlas/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/optimize/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/pre_gpu/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/qd_search/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/scoring/` | Candidate search, validation and scoring. |
| `src/grteclyn_workflows/search/validation_tiers/` | Candidate search, validation and scoring. |

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

## Namespace migration validation — 2026-11-12

The renamed package was installed locally. Both wheels were then built and
extracted outside the checkout: commands resolve from the installed wheel,
`grteclyn_wrapper` cannot be imported, and diagnostic imports do not load search
modules. The installed constraint plotter produced PNG/PDF/EPS files under a
synthetic checkout's `runs/plots/`, with no figures written into installed source.

All **1,748 tests collect**. Selected checks: **1,137 passed, 13 skipped** (unique tests; reruns not counted).
This comprises 427 initial CPU regressions, 636 remaining regressions, 33
stationary packaging checks, 34 stationary integration checks, six workflow wheel
checks, and the command test rerun with the project Python on PATH. All 152 shell
scripts pass `bash -n`; internal imports resolve in the source, scripts and tests.
The lockfile is consistent. All 409 moved Python modules were compared with the
pre-rename source: 396 have identical ASTs after imports, docstrings and namespace
strings are normalized. The other 13 change package exports or plotting output
paths, not numerical or scoring calculations.

The broad CPU suite is **not fully green**. These failures also occur on the
pre-rename source (`aa3ae7296`):

- Missing rotating-wormhole parameter template in `test_grtresna_integration`.
- `test_consume_symmetry`: the odd-parity fixture has no `shift1` field.
- `test_preflight_symmetry`: its launch fixture omits plot cadence and Weyl4 output.
- `test_run_full_campaign`: HQ frame-default assertion and two-member CMA batch.
- `test_horizon_finder_guard`: charge-retention columns are not parsed.
- `test_proposed_extensions`: the dry-run QD archive remains empty.

These are seven failing tests in total. Six were rerun against an extracted
original checkout and reproduced the same errors; the missing-template failure
was already established on the original source. A separate command test passes
when subprocesses use the project Python rather than system Python.

The expensive self-gravitating profile-wiring scan was interrupted after 7.46
minutes; the remaining files were run separately. The full boson-star ODE suite
and the remaining stationary physics suite were not rerun for this namespace
change. No cluster or GPU evolution was launched, and no full old-versus-new
campaign-output equivalence is claimed.

Collection also exposed two indentation errors already committed in stationary
profile/continuation entry points. They were corrected, and their tests pass.
The earlier package extraction's aggregate pass count did not establish that all
of its entry points could be imported.

## Cluster reproduction — 2026-11-12

Six bounded before/after workflows passed on the first node's CPU in 178 seconds
(12:16:29–12:19:27 MSK), job `refactor-e2e-20261112-r2`. The baseline is
pre-extraction commit `2f1c4506`; new wheels were built from `bf4e3b2e6`, installed
outside the checkout and used with wrapper imports blocked during solver cases.
Both sides used Python 3.12.14, JAX/JAXlib 0.11.2, NumPy 2.4.6 and SciPy 1.17.1.
The cluster venv was also refreshed with both editable packages and the old
wrapper distribution removed; both CLI help checks pass, with dependencies unchanged.

- Spinning solves at J=0.25 (48x12) and J=1 (64x16), save/load, and SPINBG export:
  maximum field/table difference 3.20e-14; both pass the existing identity gates.
- A perturbed 96x12 spherical solution recovered with two Newton corrections,
  saved and reloaded, then checked with independent equations: identical outputs.
- Accepted and rejected two-field ring archives retain their validation verdicts
  and diagnostics, including independent Einstein/Klein–Gordon checks.
- A self-gravitating boson star solved from central amplitude 0.1: identical
  radial fields, frequency, mass and compactness.
- Archived evolution constraints parsed and plotted: identical metrics and PNG
  pixels. The generated plot was also inspected visually.

Fields, tables and ordinary observables use rtol=1e-10 and atol=1e-12. Residual
diagnostics must pass the original physical gates on both sides. The throat
area minimizer resolves positions only to approximately sqrt(float64 epsilon):
its coordinate differs by 6.25e-9, while the areas and field arrays agree under
the strict comparison. These differences are retained explicitly in the report;
no solver acceptance limit was changed. The first harness attempt omitted the
legacy plotter's checkout-root environment variable; the complete retry passed.

[Evidence](../results/software-validation/refactor-20261112/comparison.json)
includes input hashes, source revisions, dependencies, raw arrays and figures.
Recheck the archived comparison without a solve:

```bash
grteclyn-wrapper/.venv/bin/python \
  grteclyn-wrapper/scripts/validation/refactor_reproduction.py compare \
  --out results/software-validation/refactor-20261112
```

For a fresh run, use `scripts/validation/run_refactor_reproduction.sh` through
`scripts/ops/capped_job.sh`, with four CPU cores, 64 GiB address space and a
bounded timeout. The script builds both wheels, selects the original source
through Git, and exports `GRTECLYN_ROOT` for the application checks. This does
not rerun GPU solves, C++ time evolution, or every research campaign.


## Upstream integration — 2026-11-12

Merged 173 commits from GRTLCollaboration's `main` through `ed2e9a9d6`.
The C++ research examples now use `GRAmr`, `BHAmr`, the renamed level hooks,
and the separate gauge kernel. Matter sources carry the gravitational coupling
once; explicit research constructors retain their configured coupling and time.
Checkpoint retention, background-relative boundaries, chi regularisation,
shock-avoiding slicing, centered refinement boxes and the archived opt-in
determinant policy remain available. The legacy parameter reader is retained
because the research examples still use it. Extraction level separation stays
at 1 for archived flat-key campaigns; upstream's default is 1.5.

Validation used GCC 13.3, CPU AMReX `bac24575699e`, HDF5, no MPI or OpenMP:
19 C++ cases ran, 18 passed. The puncture-refinement test failed 24 coverage
assertions; an untouched upstream archive reproduced the same 24 failures,
with all 189 archived source/build/test files verified against Git. The new
13-assertion matter/gauge compatibility test passed. All eight examples passed
syntax compilation. Selected Python checks gave 138 passed, four skipped and
the previously documented incomplete preflight-fixture failure.
[Validation record](../results/software-validation/upstream-20261112.json).
No full example evolution or GPU build was performed for this upstream merge;
the earlier cluster reproduction establishes the Python refactor baseline.
