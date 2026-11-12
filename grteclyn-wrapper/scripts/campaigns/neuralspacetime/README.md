# Matter-first pump studies

These tools preserve the pump experiments and saved-data measurements used by
the matter-first research. Run them from the repository root with the wrapper's
Python environment.

- `pump_ladder_queue.py`: bounded-duration pump comparisons.
- `pump_confine_queue.py`: confinement campaign arms.
- `score_evolving_geodesic.py`: reconstruct the evolving null-ray score from
  saved metric-stack slices.
- `score_confine_abs.py`: measure confinement from saved diagnostics.

The Python RL environment, PPO training and RL bridge gates were retired in
the stationary refactor. These four tools use the simulation's pump controls
and physical diagnostics without the Python RL package. Their former location
was `scripts/campaigns/rl/`; current callers use this directory directly.
Historical results retain their original source revision and manifests.

Launching a queue still requires its run-specific approval. Scoring commands
write derived data into the supplied run directories.
