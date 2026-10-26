# Launch reference

How every run in this pack was produced. Paths are repo-relative; run from the repository root.

**The authoritative record is per run, not this file.** Each `campaign/<group>/<run>/launch_config.sh` is the exact
script that produced that run, with every environment variable it was given. This document explains what those
variables mean and how the pieces fit together; where the two ever disagree, believe the run's own file.

---

## 1. What has to be built

Every run is a constraint solve followed by an evolution, on two codes with two parallelism models:

| stage | code | build ([`binaries.tsv`](binaries.tsv)) | hardware |
|---|---|---|---|
| initial data | GRTresna (Chombo, elliptic) | 9a85e6a, branch `fix/bondi-solve-matches-painter` of <https://github.com/Nikchik-coder/GRTresna> | CPU, 4 to 12 MPI ranks (`BONDI_GRTRESNA_RANKS`) |
| evolution | GRTeclyn, `Examples/RadialRecipe` (AMReX, CCZ4) | aa0dc4a1 with c12664fd | one GPU, a single rank |

```bash
# The constraint solver, from a GRTresna checkout at 9a85e6a
GRTRESNA_ROOT=<that checkout> bash grteclyn-wrapper/scripts/wormhole/build/build_grtresna_bosonstar.sh
# -> <that checkout>/Examples/BosonStarBH/Main_BosonStarBH3d.*.ex
```

The evolution executable is built per `grteclyn-wrapper/README.md` and handed to the launcher as `BONDI_BINARY`. The
solver additionally needs `CHOMBO_HOME` and its toolchain on `PATH`. The solve is the long pole on the fine grids (a
512³ solve took about an hour and 220 GB of memory), and a run's evolution claims its GPU only once its solve has
landed.

## 2. Launching one run

Every run follows the same shape. This is PM8, copied from `campaign/05_separation/PM8_L64_N128/launch_config.sh`:

```bash
REPO="$(git rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=0 \
RL_PUMP_TARGET_WIDTH=0.26748955019623744 BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GPU=1 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=8 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=4 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/PM8_L64_N128" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
```

Isolated stars use `run_single_selfgrav.sh`, with `BONDI_EXOTIC=1` selecting the negative-mass field; every pair uses
`run_pair_selfgrav.sh`.

The launcher writes `<run>/launcher.pid` as its stop handle and puts the run itself in `<run>/bondi_sg_pair_*/` (or
`bondi_sg_single_*/`), with the time series under `small_data/`, the plotfiles under `data/` and the solver's own
output under `grtresna/`.

## 3. The variables, and what they select

**Builds and initial data**

| variable | values used | meaning |
|---|---|---|
| `BONDI_BINARY` | `main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex` | the evolution executable, the same for every run |
| `GRTRESNA_ROOT` | the GRTresna checkout at 9a85e6a | which solver builds and runs the initial data |
| `BONDI_GRIDINIT` | unset, or a solved data file | evolve existing initial data and skip the solve. Set on the PM10 runs (the repaired solves of 2026-10-22), on M at N 256 (its own solve, stopped at its residual floor), and on PM10-rec and M-t1000 (the data of PM10 and M at N 192) |

**Grid and duration**

| variable | values used | meaning |
|---|---|---|
| `BONDI_NFULL` | `128`, `192`, `256` | evolution cells per side |
| `BONDI_LFULL` | `64`, `128` | side of the domain (`128` only for PM10-L128) |
| `BONDI_MAXLEVEL` | `0` | no mesh refinement in any run |
| `BONDI_STOP_TIME` | `200`, `400`, `1000` | end time: `400` for PM10-t400, `1000` for PM10-rec and M-t1000 |
| `BONDI_PLOT_INTERVAL` | `80`, `120`, `160`, `240`, `600` | steps between plotfiles; scaled with N, and wider on the two runs to t 1000 so the frame consumer keeps up |
| `BONDI_TREADMILL` and `BONDI_TREADMILL_*` | `1`; threshold `2.0`, check every `20` steps, ball `8.0`, fill `0` | PM10-rec only: the box follows the pair. Once the pair has drifted 2 units, the data shift back by 2 units, the trailing face is filled with the asymptotic 1/r tail, and the absorbing layer moves with the box; `treadmill.dat` records each shift |

**The configuration under test**

| variable | values used | meaning |
|---|---|---|
| `BONDI_SEP` | `8`, `10`, `12`, `16`, `20` | the initial separation d₀; for an isolated star, `0` puts it at the centre and `10` 5 units off centre |
| `BONDI_S0`, `BONDI_S1` | `0` or `1` per star | the field of each star: `0` positive mass (Φ₊), `1` negative mass (Φ₋). `0 1` is the mixed pair, `1 0` its exchange, `0 0` and `1 1` the same-sign pairs |
| `BONDI_S0_OMEGA`, `BONDI_S1_OMEGA` | see section 4 | each star's frequency, which sets its mass. `0.75` (Φ₊) and `0.7603` (Φ₋) are the reference stars, of equal and opposite mass to 0.4 % |
| `BONDI_OMEGA` | `0.75`, `0.7603` | isolated stars only: the star's frequency |
| `BONDI_EXOTIC` | `0`, `1` | isolated stars only: `1` for the negative-mass field |
| `BONDI_GRTRESNA_MAXIMAL_SLICING` | `1` | forces the solver's K = 0 path; set on the isolated stars and PP10 (rule 9 in `grteclyn-wrapper/README.md`) |
| `BONDI_EXTRA` | `rl_pump_target_amp=0.08 constraint_shells_dt=0.1` | raw `params.txt` overrides: the constraints in unit shells every 0.1 time units (`constraint_shells.dat`), and the target amplitude of the matter pump, which is off from t = 0 in every run (`rl_pump_stop_time = 0` in each `evolution_params.txt`) |
| `RL_PUMP_TARGET_WIDTH` | `0.26748955019623744` | the same pump's target width, fixed so that the launcher skips a star solve for it; no effect on the evolution |

**The elliptic solve**

| variable | values used | meaning |
|---|---|---|
| `BONDI_GRTRESNA_N` | `256`, `384`, `512` | solve grid, always twice the evolution grid on a domain twice its side, so the solved metric lands on the evolution grid without interpolation |
| `BONDI_GRTRESNA_DOMAIN_L` | `256` | PM10-L128 only: the solve domain for the doubled box |
| `BONDI_NL_TOL` | `0.002`, `0.000395`, `0.000125` | convergence gate, scaled as Δx⁴ from N 128 (`0.002 × (128/N)⁴`) |
| `BONDI_NL_STALL_TOL` | `4e-05`, `7.9e-06`, `2.5e-06` | give-up threshold when the residual stops improving; check which way a solve ended (rule 8 in `grteclyn-wrapper/README.md`) |
| `BONDI_GRTRESNA_RANKS` | `4`, `8`, `12` | MPI ranks for the solve; the result does not depend on them |
| `BONDI_GRTRESNA_TIMEOUT` | `21600`, `43200` | wall-clock limit in seconds |

**Diagnostics and output**

| variable | values used | meaning |
|---|---|---|
| `BONDI_SCRUTINY` | `1` | write the full diagnostic set (constraints, energy conditions, invariants, collapse watch) |
| `BONDI_SPONGE` | `1` | absorbing layer on; `BONDI_SPONGE_INNER` and `_OUTER` place it (`48` and `60` on the L 128 box) |
| `BONDI_RADII`, `BONDI_EXTRACTION_RADII` | `16 24 32 40` | PM10-L128 only: the Ψ₄ extraction spheres (the L 64 runs use the defaults, `8` and `16`) |
| `BONDI_PSI4_HIGHER_L` | `1` | PM10-L128 only: Ψ₄ modes beyond ℓ = 2 |
| `GRTECLYN_FRAMES` | `0`, `1` | render slices during the run (on for the runs the figures and videos draw) |
| `GRTECLYN_FRAMES_CACHE_SLICES` | `1` | also keep the raw slice arrays, so the frames can be redrawn later on one fixed colour scale |

`BONDI_GPU` selects the card and `BONDI_RUNS_DIR` the output directory; neither affects the physics.

## 4. What each run was given

| run | N | L | d₀ | fields | ω | stop | solve N | `NL_TOL` | initial data |
|---|---|---|---|---|---|---|---|---|---|
| `PM10_L64_N128` | 128 | 64 | 10 | 0/1 | 0.75 / 0.7603 | 200 | 256 | 0.002 | repaired 10-22 solve |
| `PM10_L64_N192` | 192 | 64 | 10 | 0/1 | 0.75 / 0.7603 | 200 | 384 | 0.000395 | repaired 10-22 solve |
| `PM10_L64_N256` | 256 | 64 | 10 | 0/1 | 0.75 / 0.7603 | 200 | 512 | 0.000125 | repaired 10-22 solve |
| `PM8_L64_N128` | 128 | 64 | 8 | 0/1 | 0.75 / 0.7603 | 200 | 256 | 0.002 | solve |
| `PM12_L64_N128` | 128 | 64 | 12 | 0/1 | 0.75 / 0.7603 | 200 | 256 | 0.002 | solve |
| `PM16_L64_N128` | 128 | 64 | 16 | 0/1 | 0.75 / 0.7603 | 200 | 256 | 0.002 | solve |
| `PM20_L64_N128` | 128 | 64 | 20 | 0/1 | 0.75 / 0.7603 | 200 | 256 | 0.002 | solve |
| `E0.64_L64_N128` | 128 | 64 | 20 | 0/1 | 0.850 / 0.859095 | 200 | 256 | 0.002 | solve |
| `E1.34_L64_N128` | 128 | 64 | 20 | 0/1 | 0.700 / 0.710478 | 200 | 256 | 0.002 | solve |
| `E1.57_L64_N128` | 128 | 64 | 20 | 0/1 | 0.675 / 0.686063 | 200 | 256 | 0.002 | solve |
| `R0.60_L64_N128` | 128 | 64 | 10 | 0/1 | 0.75 / 0.88 | 200 | 256 | 0.002 | solve |
| `R0.80_L64_N128` | 128 | 64 | 10 | 0/1 | 0.75 / 0.8040 | 200 | 256 | 0.002 | solve |
| `R1.33_L64_N128` | 128 | 64 | 10 | 0/1 | 0.81 / 0.7603 | 200 | 256 | 0.002 | solve |
| `MP10_L64_N128` | 128 | 64 | 10 | 1/0 | 0.7603 / 0.75 | 200 | 256 | 0.002 | solve |
| `PM10_L64_N128_t400` | 128 | 64 | 10 | 0/1 | 0.75 / 0.7603 | 400 | 256 | 0.002 | repaired 10-22 solve |
| `PM10-rec_L64_N192_t1000` | 192 | 64 | 10 | 0/1 | 0.75 / 0.7603 | 1000 | 384 | 0.000395 | PM10 N 192 data |
| `PM10_L128_N256` | 256 | 128 | 10 | 0/1 | 0.75 / 0.7603 | 200 | 512 | 0.002 | solve |
| `PP10_L64_N128` | 128 | 64 | 10 | 0/0 | 0.75 / 0.75 | 200 | 256 | 0.002 | solve |
| `MM10_L64_N128` | 128 | 64 | 10 | 1/1 | 0.7603 / 0.7603 | 200 | 256 | 0.002 | solve |
| `P_L64_N128` | 128 | 64 | centre | single, positive | 0.75 | 200 | 256 | 0.002 | solve |
| `M_L64_N128` | 128 | 64 | off centre | single, negative | 0.7603 | 200 | 256 | 0.002 | solve |
| `M_L64_N192` | 192 | 64 | off centre | single, negative | 0.7603 | 200 | 384 | 0.000395 | solve |
| `M_L64_N256` | 256 | 64 | off centre | single, negative | 0.7603 | 200 | 512 | 0.000125 | own solve, at its floor |
| `M_L64_N192_t1000` | 192 | 64 | off centre | single, negative | 0.7603 | 1000 | 384 | 0.000395 | M N 192 data |

"Solve" is a fresh solve on GRTresna 9a85e6a. The repaired 10-22 solves are the PM10 initial data solved on
2026-10-22 with the joined star lapse, their outermost face layer of χ and α then repaired by cubic extrapolation along
each face normal (the converter itself is fixed since e3992acf).

## 5. Running and stopping

Runs were launched by hand, one at a time, never from a self-driving queue: several solves at once saturate a node's
CPUs and starve the GPU evolutions that share it.

**Stopping is not `kill`.** Terminating a launcher's process group does not stop its solver ranks. Use the stop
script, which stops the orchestrator first and then sweeps the workers:

```bash
bash grteclyn-wrapper/scripts/campaigns/stop_campaign.sh runs/bondi/staging/<run>

# then verify that nothing of that run remains
grteclyn-wrapper/scripts/ops/sweep_ranks.py --match <run>
```

`sweep_ranks.py` walks the per-process `/proc` entries directly, for nodes where `ps`, `pgrep` and `nvidia-smi` report
nothing. Leftover `.nfs*` files in a run directory mean that processes are still alive. Always scope a stop to a named
run: the cards are shared, and a busy GPU is not necessarily one of these runs.

## 6. Reproducing the pack from finished runs

```bash
bash research/bondi_dipole/pack_runaway.sh
```

The packer lives with the paper's source on the repository's `trunk` branch (`research/` is not part of the
release line). It walks the run tree's groups (`runs/bondi/NN_group/`; a live run in `runs/bondi/staging/` is never packed), copies
each run's time series, parameter files and provenance, thins the rendered frames to one still per Δt = 10
(`FRAME_DT` overrides), derives the two-well tracking of the same-sign pairs, and scrubs machine-specific paths.
`CELLS_SKIP` and `FRAMES_SKIP` name what to leave out; the frames of the two runs to t 1000 are not packed by default.
