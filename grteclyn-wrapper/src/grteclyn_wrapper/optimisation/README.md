# `grteclyn_wrapper.optimisation`: campaign M's solver

Exact rotating Ellis–Bronnikov wormholes held open by an exotic scalar **with a potential**, and the search for the
design that needs the least exotic matter at a fixed throat size and spin. Plan:
[`research/optimisation/Minimal Exotic Wormhole Search.md`](../../../../research/optimisation/Minimal%20Exotic%20Wormhole%20Search.md);
what ran, what it showed and what is next: [`research/optimisation/STATUS.md`](../../../../research/optimisation/STATUS.md).

## Layout

| path | holds |
|---|---|
| `matter_equations.py` | the matter problem: the field forms (the imposed rows and the unimposed monitors, through the step-4 layer field chi and the step-5 winding field zeta) and `MatterCollocationProblem`, with the J, R_e and area pins |
| `potentials.py` | scalar potentials in the solver's normalization; every one is a kink ψ²(ψ − ψ₋)²Q(ψ) |
| `exoticity.py` | the bill X = \|VIQ\|/R_e, the throat, NEC along rays, the tidal tensor at the throat |
| `solver/newton.py` | damped Newton: equilibrated dense LU, Armijo backtracking, chord steps; on the host, or the whole solve on the card when the Jacobian arrives there |
| `solver/jacobian.py` | the exact dense Jacobian of a jitted residual: `jax.jacfwd`, or `chunked_jacfwd` in column blocks |
| `solver/device.py` | where jax runs: CPU by default, a CUDA card on request, float64, the XLA thread cap |

Scripts, in [`grteclyn-wrapper/scripts/optimisation/`](../../../scripts/optimisation/):
- `pipeline.py` and `pipeline.toml`: the campaign's runnable stages;
- `first_matter_solve.py`: the V ≠ 0 kink ladders;
- `scan_potential.py`: the step-3 shape and γ scans and the open rays;
- `cloud_solve.py`: the step-4 layer-field ladders (the mini-boson-star cloud);
- `winding_solve.py`: the step-5 winding-field ladders (spin carried by the matter phase);
- `check_chi_star.py`: the step-4 J = 0 cross-check against the published dressed star;
- `optimize_potential.py`: the step-6 4-knob (m, q₁, q₂, q₃) Nelder–Mead search at pinned J and R_e;
- `stability_screen.py`: the radial stability column — re-solves each potential at J = 0 on the member's R_e pin
  and runs `stability_radial.growth_rate` on the flattened 1D background;
- the gates: `validate_matter_v0.py` (V = 0 against the published solver), `check_matter_pins.py`, `check_tidal.py`,
  `check_matter_n_row.py`, `check_growth_rate.py` (the drainhole rate 0.390 for the stability screen);
- `diagnose_matter_v0.py`;
- `derive_matter_equations.py`: the symbolic proof that the forms are Einstein + KG;
- `derive_radial_perturbation.py`: the symbolic derivation and transcription check of the radial perturbation rows
  (`optimisation/stability_radial.py`).

Tests: `grteclyn-wrapper/tests/optimisation/`.

## Two dependency rules

`tests/optimisation/test_layout.py` checks both.

1. **Nothing outside this package imports it.** `develop`, the public release line, ships without it. This package
   reads the published spinning package (`analysis/spinning_wormhole`: its spectral pieces, `Solution`, and the V = 0
   `CollocationProblem` as the validation reference), never the other way round. That is why the spinning package
   keeps its own published, CPU-only `newton.py`; `solver/newton.py` is the copy that grew the CUDA path.
2. **`solver/` imports nothing from `grteclyn_wrapper`.** The numerics stay physics-free, so the folder can be lifted
   out whole. Importing it starts no jax: the switches below must be set first.

## Running

On the GPU node only: JAX is in the node's venv, not the workstation's. Every job goes through
`grteclyn-wrapper/scripts/ops/capped_job.sh`: one runaway process restarts the whole node container.

```bash
PY=grteclyn-wrapper/.venv/bin/python
$PY grteclyn-wrapper/scripts/optimisation/pipeline.py list                  # stages and their state
$PY grteclyn-wrapper/scripts/optimisation/pipeline.py run <stage>           # CPU, through capped_job.sh
$PY grteclyn-wrapper/scripts/optimisation/pipeline.py run <stage> --gpu N   # card N; refuses a busy card
```

GPU switches. Solver jobs run on a card by default (2026-10-28: the solves are ~25× faster there; the
no-GPU-without-the-go rule is the evolutions', not the solver's). The cards are shared, so check `nvidia-smi`
first.
- `--gpu CARD` and `--jac-chunk` on `first_matter_solve.py` call `solver.device.select_device`. It sets
  `JAX_PLATFORMS=cuda`, `CUDA_VISIBLE_DEVICES` and `XLA_PYTHON_CLIENT_ALLOCATOR=cuda_async` (2026-10-28: the
  default grow-only pool fragments across a ladder's solves and OOM'd every m > 0 Jacobian at 180x36).
- `WH_JAC_CHUNK` sets the Jacobian's column block: 1024 by default on a card, unchunked on the CPU.
