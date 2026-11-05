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

Workers enforce CUDA float64, the platform allocator, no preallocation,
Jacobian chunk 256, four CPU threads and 160 GiB through `capped_job.sh`.
Checkpoints remain off; fields, failed iterates and logs stay on persistent
storage. No evolution or new CMA search is dispatched. The original
exterior-ring rejection stays in the raw records; the separately authorized
throat-overlap assessment changes only that preference, retaining independent
equation, energy, surface, symmetry, quadrature and tidal checks.

Never modify an active worker on the cluster. Transport changes through Git
push/pull, then use a fresh output directory for an authorized rerun.
