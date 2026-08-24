# Launch reference

How every cell in this pack was produced. Paths are repo-relative; run from the
repository root.

**The authoritative record is per cell, not this file.** Each
`campaign/<cell>/launch_config.sh` is the exact script that produced that cell,
with every environment variable it was given. This document explains what those
variables mean and how the pieces fit together; where the two ever disagree,
believe the cell's own file.

---

## 1. What has to be built

```bash
# Constraint solver — GRTresna, complex scalar matter with per-lump sign
bash grteclyn-wrapper/scripts/wormhole/build/build_grtresna_bosonstar.sh
# -> GRTresna/Examples/BosonStarBH/Main_BosonStarBH3d.*.ex
```

The GRTeclyn evolution executable (`RadialRecipe`) is built per
`grteclyn-wrapper/README.md`. The solver additionally needs `CHOMBO_HOME` and
its toolchain on `PATH`.

**Two codes, two parallelism models.** Every cell is a constraint solve followed
by an evolution:

| stage | code | hardware | parallelism |
|---|---|---|---|
| initial data | GRTresna (Chombo, elliptic) | CPU | **32 MPI ranks** (`BONDI_GRTRESNA_RANKS=32`) |
| evolution | GRTeclyn (AMReX, CCZ4) | one GPU | single rank |

The solve is the long pole on the fine rungs — a `512³` solve takes about four
hours — which is why cells were launched while a card was still busy: the
evolution only claims the GPU once the solve has landed.

## 2. Launching one cell

Every cell follows the same shape. This is the finest runaway rung, copied from
`campaign/runaway_pair_d10_L64_N256_lev0/launch_config.sh`:

```bash
REPO="$(git rev-parse --show-toplevel)"
cd "${REPO}"

GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 \
BONDI_GPU=0 BONDI_STOP_TIME=200 BONDI_NFULL=256 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=160 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.000125 BONDI_NL_STALL_TOL=0.0000025 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_GRTRESNA_N=512 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=32 \
BONDI_GRTRESNA_TIMEOUT=43200 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/runaway_pair_d10_L64_N256_lev0" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
```

Single-star cells use `run_single_selfgrav.sh` with `BONDI_EXOTIC=1` selecting
the phantom sector; everything else is a pair and uses `run_pair_selfgrav.sh`.

The launcher writes `<cell>/launcher.pid` as its stop handle and puts the run
itself in `<cell>/bondi_sg_pair_*/` (or `bondi_sg_single_*/`), with time series
under `small_data/`, plotfiles under `data/`, and the solver's own output under
`grtresna/`.

## 3. The knobs, and what they select

**Grid and duration**

| variable | values used | meaning |
|---|---|---|
| `BONDI_NFULL` | `128`, `192`, `256` | evolution cells per side — the resolution ladder |
| `BONDI_LFULL` | `64`, `128` | box side in code units (`128` only for the wave-zone cell) |
| `BONDI_MAXLEVEL` | `0`, `1` | mesh refinement. **`0` everywhere** except the one `amrcheck_*` cell that exists to show refinement changes nothing |
| `BONDI_STOP_TIME` | `200`, `400`, `1000` | end time; `400` only for the long pair run, `1000` only for the extended lone-phantom control |
| `BONDI_PLOT_INTERVAL` | `80`, `120`, `160`, `400` | steps between plotfiles (scaled so every cell writes a comparable number). `400` on the `t = 1000` cell: at the default cadence the frame consumer falls behind the GPU and the scratch tree grows without bound |
| `BONDI_CHECKPOINT_INTERVAL` | unset, `40000` | rolling checkpoint. Set only on the `t = 1000` cell, which is five times longer than anything else in the campaign |

**The configuration under test**

| variable | values used | meaning |
|---|---|---|
| `BONDI_SEP` | `8`, `10`, `12`, `16`, `20` | separation of the two stars; `0` for a centred single star |
| `BONDI_S0`, `BONDI_S1` | `0` or `1` per lump | sector of each star: `0` canonical, `1` phantom. `0 1` is the runaway, `1 0` its mirror, `0 0` and `1 1` the same-sign nulls |
| `BONDI_S0_OMEGA`, `BONDI_S1_OMEGA` | `0.75`, `0.7603`, `0.8040`, `0.81`, `0.88` | each star's frequency, which sets its mass. `0.75` canonical and `0.7603` phantom are the mass-matched pair (`\|M\| = 0.014350` both); the others build the mass ladder |
| `BONDI_OMEGA` | `0.7603` | single-star cells only — the lone star's frequency |
| `BONDI_EXTRA` | unset, `eta=2.0` | raw `params.txt` overrides, for evolution-gauge knobs (`eta`, `shift_Gamma_coeff`, `lapse_power`) that the environment cannot otherwise reach. Defaults to empty, so every other cell reproduces bit-for-bit |
| `BONDI_GRTRESNA_MAXIMAL_SLICING` | `1` | forces the `K = 0` path. Required on any **all-canonical** cell, because the solver picks that path by itself whenever a lump carries negative energy — see rule 9 in `grteclyn-wrapper/README.md` |
| `BONDI_EXOTIC` | `0`, `1` | single-star cells only: which sector the lone star belongs to |

**The elliptic solve**

| variable | values used | meaning |
|---|---|---|
| `BONDI_GRTRESNA_N` | `256`, `384`, `512` | solve grid — always `2×` the evolution grid |
| `BONDI_NL_TOL` | `0.002`, `0.000395`, `0.000125`, `0.0002` | convergence gate, scaled as `dx⁴` off the base rung (`0.002 × (128/N)⁴`). `0.0002` is off-schedule: the deep-solve twin tightens the base rung `10×` at fixed grid, to separate solve error from grid error |
| `BONDI_NL_STALL_TOL` | `4e-05`, `7.9e-06`, `2.5e-06`, `4e-06` | give-up threshold when the residual stops improving. **Check which door the solve left by** — `converged`, `stalled` and the iteration cap are not the same thing; see rule 8 in `grteclyn-wrapper/README.md` |
| `BONDI_GRTRESNA_RANKS` | `32` | MPI ranks for the solve |
| `BONDI_GRTRESNA_TIMEOUT` | `21600`, `43200` | wall-clock ceiling in seconds |

**Same-sign pairs keep the flat `0.002` gate at every resolution.** Their solve
residual floors near `5.4e-04 %` — the outer boundary condition is genuinely
wrong for a box carrying net `2M` — so the `dx⁴` schedule would never be met and
the cell would burn its timeout. This is a documented exception, not an
oversight.

**Diagnostics and output**

| variable | values used | meaning |
|---|---|---|
| `BONDI_SCRUTINY` | `1` | write the full diagnostic set (constraints, energy conditions, invariants, collapse watch) |
| `BONDI_SPONGE` | `1` | absorbing layer on; `BONDI_SPONGE_INNER` / `_OUTER` place it (`48`/`60` on the `L = 128` box) |
| `BONDI_RADII`, `BONDI_EXTRACTION_RADII` | `8, 16`; `16, 24, 32, 40` | ψ₄ extraction shells — the wider set only on the wave-zone cell |
| `BONDI_PSI4_HIGHER_L` | `1` | wave-zone cell only: modes beyond `l = 2` |
| `GRTECLYN_FRAMES` | `0`, `1` | render slices during the run |
| `GRTECLYN_FRAMES_CACHE_SLICES` | `1` | also cache the raw slice arrays, so frames can be redrawn later on one fixed colour scale. **Always set this when frames are on** — without it the plotfiles are gone and the movies cannot be rescaled |

`BONDI_GPU` selects the card and `BONDI_RUNS_DIR` the output directory; neither
affects physics.

## 4. What each cell was given

Twenty-seven of the thirty-one cells carry a launch record. The four `stability_canonical_w*` cells
predate the campaign's staging layout and reuse cached initial data, so they
have no `launch_config.sh` — their configuration is in their `metadata.json`.

| cell | `N` | `L` | sep | `S0`/`S1` | stop | solve `N` | `NL_TOL` |
|---|---|---|---|---|---|---|---|
| `runaway_pair_d08_L64_N128_lev0` | 128 | 64 | 8 | 0/1 | 200 | 256 | 0.002 |
| `runaway_pair_d10_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `runaway_pair_d12_L64_N128_lev0` | 128 | 64 | 12 | 0/1 | 200 | 256 | 0.002 |
| `runaway_pair_d16_L64_N128_lev0` | 128 | 64 | 16 | 0/1 | 200 | 256 | 0.002 |
| `runaway_pair_d10_L64_N192_lev0` | 192 | 64 | 10 | 0/1 | 200 | 384 | 0.000395 |
| `runaway_pair_d10_L64_N256_lev0` | 256 | 64 | 10 | 0/1 | 200 | 512 | 0.000125 |
| `control_lone_canonical_L64_N128_lev0` | 128 | 64 | — | single | 200 | 256 | 0.002 |
| `control_lone_phantom_L64_N128_lev0` | 128 | 64 | off-centre | single, exotic | 200 | 256 | 0.002 |
| `control_pair_pp_d10_L64_N{128,192,256}_lev0` | 128/192/256 | 64 | 10 | 0/0 | 200 | 256/384/512 | 0.002 |
| `control_pair_mm_d10_L64_N{128,192}_lev0` | 128/192 | 64 | 10 | 1/1 | 200 | 256/384 | 0.002 |
| `control_mirror_mp_d10_L64_N128_lev0` | 128 | 64 | 10 | 1/0 | 200 | 256 | 0.002 |
| `massscale_pair_d10_w0804_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `massratio_w088_r060_d10_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `massratio_heavyphantom_d10_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `amrcheck_pair_d10_L64_N128_lev1` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `wavezone_pair_d10_L128_N256_lev0` | 256 | 128 | 10 | 0/1 | 200 | 512 | 0.002 |
| `longrun_pair_d10_t400_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 400 | 256 | 0.002 |
| `runaway_pair_d20_L64_N128_lev0` | 128 | 64 | 20 | 0/1 | 200 | 256 | 0.002 |
| `deepsolve_pair_d10_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | **0.0002** |
| `gaugetwin_pair_d10_eta2_L64_N128_lev0` | 128 | 64 | 10 | 0/1 | 200 | 256 | 0.002 |
| `control_lone_phantom_t1000_L64_N128_lev0` | 128 | 64 | off-centre | single, exotic | **1000** | 256 | 0.002 |
| `control_pair_mm_d10_L64_N128_lev0_frames` | 128 | 64 | 10 | 1/1 | 200 | 256 | 0.002 |

The last two rows of the runaway series are the two referee-response cells of
2026-08-24. Their launch records name a fresh elliptic solve rather than a
reused `initial_data.gridinit`: the archived gridinit files had been pruned from
the staging tree, and the solve is deterministic at fixed settings, so both
re-solved and both landed on the same `converged` door at NL iteration 12 of 50
that every archived cell used.

`chase03c_pair_d10_L64_N128_lev0` and `nomill_left_pair_d10_L64_N128_lev0` are
in the pack but belong to the 0.3c follow-up rather than this campaign; see
`research/bondi_dipole/docs/CHASE_TO_03C.md`.

The mass ladder's frequencies are the part not visible in that table:
`massscale_*` sets `S1_OMEGA=0.8040`, `massratio_w088_r060` sets `0.88`, and
`massratio_heavyphantom` reverses the ordering with `S0_OMEGA=0.81` against the
matched phantom.

## 5. Running and stopping

Cells were launched by hand, one at a time, and never from a self-driving queue.
The reason is practical: several elliptic solves at 32 ranks each will saturate
the node's CPUs and starve the GPU evolutions sharing it, so solves are spaced
out rather than fired together.

**Stopping is not `kill`.** Terminating a launcher's process group does *not*
stop the work — after three solves were "stopped" that way, 133 solver ranks
were still running at full tilt and the GPU evolutions sharing the node stayed
starved. Use the sanctioned path, which kills the orchestrator first and then
sweeps the workers:

```bash
bash grteclyn-wrapper/scripts/campaigns/stop_campaign.sh runs/bondi/staging/<cell>

# then verify — nothing of that cell may remain
grteclyn-wrapper/scripts/ops/sweep_ranks.py --match <cell>
```

`sweep_ranks.py` exists because the usual tools are unavailable on this node:
`/proc/stat` and `/proc/loadavg` are broken, so `ps`, `top`, `pgrep`, `pkill`
and `free` all fail or return nothing, and `nvidia-smi` reports no PIDs. It
walks the per-PID `/proc` entries directly. Leftover `.nfs*` files in a run
directory are the tell-tale of processes that are still alive.

Always scope a stop to a named cell. Cards on this node are shared, and a busy
GPU is not necessarily one of these runs.

## 6. Reproducing the pack from finished runs

```bash
bash research/bondi_dipole/pack_runaway.sh
```

It walks the staging tree, copies each cell's time series, parameter files and
provenance, thins the rendered frames to one still per `dt = 10`
(`FRAME_DT` overrides), derives the two-lump tracking for same-sign cells, and
scrubs machine-specific paths. `CELLS_SKIP` and `FRAMES_SKIP` name what to leave
out; the long run's frames are skipped by default because it is twice the length
of every other cell and no number is read off its stills.
