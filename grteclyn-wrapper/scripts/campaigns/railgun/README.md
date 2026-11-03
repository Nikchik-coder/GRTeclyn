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
- `pack_stationary.py` and `pack_evolution.py` archive completed studies.
- `verify_pack.py` checks the result inventory and immutable study checksums.
- `organize_runs.py` previews raw-run folder moves; `--apply` performs them.

The solver, initial-data conversion, origin check and physical-claims audit
live in `grteclyn_wrapper.optimisation.railgun`. In particular:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.audit_ring_claims
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.certify_ergoregion_core --help
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.certify_ergoregion_core \
  --config research/railgun/studies/evolution_ergoregion_372.json --dry-run
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.evolution_amr plan --n 96
grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/campaigns/railgun/verify_pack.py
```

The audit uses archived data on a CPU. The origin check starts GPU work and
requires the run-specific go. No command in this README grants that go.
