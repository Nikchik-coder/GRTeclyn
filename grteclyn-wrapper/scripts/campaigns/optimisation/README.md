# Exotic-matter optimisation campaigns

Stationary code lives in `grteclyn_stationary`; shared numerical
algorithms live in `grteclyn_stationary.numerics`. Research decisions and results
are in [`research/optimisation/STATUS.md`](../../../../research/optimisation/STATUS.md).

`configs/` contains the fixed-area, potential and coupled ring--wormhole study
definitions. `run_signed_potential.sh` and `run_wormhole_ring.sh` dispatch the
potential and mixed-field studies. The `run_railgun_throat*` and
`run_railgun_matched_control*` launchers/workers perform bounded continuation
and validation. Run them from the repository root; preview-capable launchers
retain their default dry-run behavior and require `--run` for dispatch.

`build_binary.sh`, `launch_evolution.sh` and `preflight_campaign.json` are the
GRTeclyn evolution handoff. Stationary qualification and evolution have separate
acceptance checks and resource approvals. This directory replaces the former
operational files under `research/optimisation/studies/`.
