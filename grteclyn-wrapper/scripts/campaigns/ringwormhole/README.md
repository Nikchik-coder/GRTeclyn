# Ring–wormhole stationary campaign

Launchers, capped workers and run configurations (`configs/`) live here. The
current queue and research findings live in [research/ringwormhole](../../../../research/ringwormhole/STATUS.md).
All commands run from the repository root; omit `--run` for a CPU-only preview.
A run-specific go is required before GPU startup.

- `run_ergoregion108.sh GPU FRESH_OUT [--run]`: original direct CMA-seed
  throat insertion, three solves only.
- `run_ergoregion108_continuation.sh GPU FRESH_OUT [--run]`: physical
  continuation from the accepted weak ring, at most 32 attempts and three
  final validation solves.
- `run_ergoregion108_throat.sh GPU FRESH_OUT [--run]`: reanchor at the throat,
  at most eight attempts and three final solves. This dated retry is capped
  at 20 minutes and cannot outlive its original one-hour retry window.

- `run_spin_ring.sh GPU FRESH_OUT [--run]`: prepared independent-wormhole-spin
  plus co-rotating matter, and its ring-free same-area/same-total-J control;
  four J steps and three final grids per arm, 14 solves maximum. The two ends
  may be asymmetric. See `configs/spin_ring_co_rotating.json` and STATUS.
  A fourth argument names the original coupled output to complete its unstarted
  control arm only. This requires `RINGWORMHOLE_DEADLINE_UTC` set to the original
  approved deadline, refuses additional physical failures or an already claimed
  control, and consumes exactly the remaining seven solves. The counter-rotating
  diagnostic retains its original failed co-rotation classification.
- `run_spin_ring.sh GPU FRESH_OUT --run --flux`: directly pin geometric
  Killing flux at the specified xi=0 cut through -0.02/-0.04/-0.06/-0.08,
  at fixed scalar amplitude and true throat area. Every rung checks measured
  alignment, localization, independent equations, energy and tides before any
  refinement. Three-grid validation and a same-total-J ring-free control follow
  only if the rungs pass; 14 solves and one hour maximum, no automatic retries.
  The control's target is measured from the coupled solution; if its ladder
  exceeds the remaining budget, stop without a comparison claim. Config:
  `configs/spin_ring_flux.json`. The cut flux is not a unique object-spin split.
  Use `--dry-run --flux` in place of `--run --flux` for a CPU-only preview.

Workers enforce CUDA float64, the platform allocator, no preallocation,
Jacobian chunk 256, four CPU threads and 160 GiB through `capped_job.sh`.
Checkpoints remain off; fields, failed iterates and logs stay on persistent
storage. No evolution or new CMA search is dispatched. The original
exterior-ring rejection stays in the raw records; the separately authorized
throat-overlap assessment changes only that preference, retaining independent
equation, energy, surface, symmetry, quadrature and tidal checks.

Never modify an active worker on the cluster. Transport changes through Git
push/pull, then use a fresh output directory for an authorized rerun.
