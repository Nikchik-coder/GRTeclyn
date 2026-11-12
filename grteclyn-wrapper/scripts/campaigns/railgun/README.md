# Scalar-ring campaign scripts

Run commands from the repository root, using `grteclyn-wrapper/.venv/bin/python`.
The current study definitions and run instructions are in
[research/railgun](../../../../research/railgun/RUNNING.md).

- `run_ergoregion_*.sh` and `run_max_candidate_validation.sh` run bounded
  stationary searches and validation after their separate launch approvals.
- `build_binary.sh`, `launch.sh` and `launch_long.sh` build and launch
  GRTeclyn evolutions through the shared preflight and consumer.
- `launch_ergoregion.sh` prepares the strongest-ring, L=64, six-level
  evolution from independently sampled initial data at every AMR level.
  It preserves the approved card assignment and requires checkpoints OFF.
- `run_ergoregion_sequence.sh CONFIG CARD STEM BINARY`, inside a capped job,
  requires a completed, hash-matched centre qualification before export.
  Card 0 runs N96 then N128; card 1 runs N192. Each member has a 48-hour
  ceiling including export, and the queue stops if the preceding member
  fails or ends before t=50. Checkpoints remain OFF.
- `run_full_spectral_recovery.sh CARD OUT`, after a separate bounded go,
  runs regressions and three stationary solves retaining all metric and
  dragging coefficients, then the unchanged centre certificate. It does
  not launch evolutions itself. The v2 archive preserves every coefficient
  through refinement, geometry and common-point comparisons.
- `audit_cartesian_curvature.py SOURCE` independently evaluates saved
  curvature away from the axis using extended precision. Its single-field
  replacement comparisons diagnose an error; they do not alter or qualify
  the saved solution. Exact rotating-flat and Schwarzschild tests check it.
- `pack_stationary.py` and `pack_evolution.py` archive completed studies.
- `verify_pack.py` checks the result inventory and immutable study checksums.
- `organize_runs.py` previews raw-run folder moves; `--apply` performs them.

The solver, initial-data conversion, origin check and physical-claims audit
live in `grteclyn_stationary.railgun`. In particular:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_stationary.railgun.audit_ring_claims
grteclyn-wrapper/.venv/bin/python -m grteclyn_stationary.railgun.certify_ergoregion_core --help
grteclyn-wrapper/.venv/bin/python -m grteclyn_stationary.railgun.certify_ergoregion_core \
  --config grteclyn-wrapper/scripts/campaigns/railgun/configs/evolution_ergoregion_372.json --dry-run
grteclyn-wrapper/.venv/bin/python -m grteclyn_stationary.railgun.evolution_amr plan --n 96
grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/campaigns/railgun/verify_pack.py
```

The audit uses archived data on a CPU. The origin check starts GPU work and
requires the run-specific go. No command in this README grants that go.

- `run_weak_ergoregion_pilot.sh CARD STEM BINARY off`, after its separate
  go, runs targeted GPU tests and the accepted 1.081-dragging source through
  three independently certified exports and t=2 evolutions. N96 then N128
  use card 0; N192 uses card 1. It preserves the L64/AMR6 comparison and
  never automatically extends to t=50.
