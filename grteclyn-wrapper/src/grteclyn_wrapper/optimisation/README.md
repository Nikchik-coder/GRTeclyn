# `grteclyn_wrapper.optimisation`: campaign M's solver

Exact rotating Ellis–Bronnikov wormholes held open by an exotic scalar **with a potential**, and the search for the
design that needs the least exotic matter at a fixed throat size and spin. Stationary extension experiments resumed on 2026-10-30: richer positive potentials, ordinary and rotating
bosonic matter, and fixed-area shape/asymmetry trials. No 3+1 evolutions are part of this batch.
Stability labels remain withdrawn pending repair of the radial screen. Plan:
[`research/optimisation/Minimal Exotic Wormhole Search.md`](../../../../research/optimisation/Minimal%20Exotic%20Wormhole%20Search.md);
what ran, what it showed and what is next: [`research/optimisation/STATUS.md`](../../../../research/optimisation/STATUS.md).

## Layout

| path | holds |
|---|---|
| `matter_equations.py` | the matter problem: the field forms (the imposed rows and the unimposed monitors, through the step-4 layer field chi and the step-5 winding field zeta) and `MatterCollocationProblem`, with the J, R_e and area pins |
| `potentials.py` | scalar potentials in the solver's normalization; every one is a kink ψ²(ψ − ψ₋)²Q(ψ) |
| `exoticity.py` | the bill X = \|VIQ\|/R_e, the throat, NEC along rays, the tidal tensor at the throat |
| `handoff.py` | a saved solve (optimize_potential.py .npz) as the evolution's background table: SPINBG_V1 plus the 7th column B and the `potential_coeffs` header line |
| `solver/newton.py` | damped Newton: equilibrated dense LU, Armijo backtracking, chord steps; on the host, or the whole solve on the card when the Jacobian arrives there |
| `solver/jacobian.py` | the exact dense Jacobian of a jitted residual: `jax.jacfwd`, or `chunked_jacfwd` in column blocks |
| `solver/device.py` | where jax runs: CPU by default, a CUDA card on request, float64, the XLA thread cap |

`exploration.py` provides matched stationary trials from saved optimiser fields. Physical size is
recomputed from the fields and sigma, avoiding the old radius-metadata ambiguity. Ordinary clouds
use an amplitude pin with frequency as an unknown, like winding clouds. Both asymptotic mass gaps
must permit a localized mode.

Scripts, in [`grteclyn-wrapper/scripts/optimisation/`](../../../scripts/optimisation/):
- `explore_extensions.py`: bounded trials from a saved NPZ (`--stages potential,cloud,winding,shape,asymmetry`).
  Positive Bernstein controls enrich the potential while exactly embedding the starting cubic.
  Shape and asymmetry hold area and J; other trials hold R_e and J. Every stage refines its best
  trial and matched reference; failed constraints or a gain comparable to grid drift never count
  as confirmed. JSONL records include failures, physical radii, phantom-only X/X_A, J bookkeeping,
  lapse and spectral tails. NPZs are diagnostic, not evolution exports. No stability penalty is used.
- `pipeline.py` and `pipeline.toml`: the campaign's runnable stages;
- `first_matter_solve.py`: the V ≠ 0 kink ladders;
- `scan_potential.py`: the step-3 shape and γ scans and the open rays;
- `cloud_solve.py`: the step-4 layer-field ladders (the mini-boson-star cloud);
- `winding_solve.py`: the step-5 winding-field ladders (spin carried by the matter phase);
- `check_chi_star.py`: the step-4 J = 0 cross-check against the published dressed star;
- `optimize_potential.py`: the step-6 4-knob (m, q₁, q₂, q₃) search at pinned J and R_e (Nelder–Mead or
  CMA-ES; `--stability` is refused while the radial screen is under repair). Opt-in:
  `--pin area` holds throat area so oblateness is free (score $X_A = |{\rm VIQ}|/R_A$);
  `--free-J` adds $J$ as a fifth knob. Defaults omit both, so existing 4-knob jobs are
  unchanged. New bests must pass inexpensive checks of all imposed equations,
  unused constraints, spin and radius on three grids. `best_screened.npz` is
  provisional: it evaluates the same polynomial at new nodes. The default
  `--refine-best final` independently re-solves the finalist; only a PASS on
  all three grids and <=1e-6 relative bill drift writes `best_clean.npz`,
  containing the finest solved fields. `--refine-best each` instead re-solves
  every new best. Failed screens receive a death penalty. Failed final
  refinement exits 2, without a validated result or an automatic evolution.
  Physical stability remains unassessed. Outputs require a fresh prefix;
- `python -m grteclyn_wrapper.optimisation.resolution`: standalone residual
  screening of a saved candidate; `--method refine` performs full re-solves.
  Every grid's fields and diagnostics are retained for comparison;
- `grid_check.py`: grid convergence of solved potentials at the member's J (one walk-in, then each finer grid
  seeded by spectral interpolation, one R_e pin for all), to tell under-resolution from the round-off floor;
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
