# Campaign extracts — the Bondi dipole runaway (revision)

Since 2026-10-23 this folder holds only runs on the fixed code: fourth-order time integration (c12664fd) and the
fixed initial data (the joined star lapse, the matched solve, the converter's face layer). The v1 cells were evolved
with first-order time integration; they moved, with their guide and registry, to the untracked
`runs/bondi/00_archive/superseded_2026-10-23/results_campaign/`, and the published v1 pack stays in the tag
`v1.0-bondi-dipole`.

One folder per question, one folder per cell, in the same groups as the run tree (`runs/bondi/NN_group/<cell>/`);
`../runs_registry.tsv` lists every cell. Packed by `research/bondi_dipole/pack_runaway.sh`, which is safe to re-run
and scrubs absolute paths. Plotfiles, the initial-data file, frames and movies stay in the gitignored run tree.

| folder | cells |
|---|---|
| `04_runaway/` | PM10 carried to t 400 (`PM10_L64_N128_t400`) and PM10 in the L 128 box (`PM10_L128_N256`), both with frames |
| `05_separation/` | the mixed pair at d0 8 and 12 (`PM8_L64_N128`, `PM12_L64_N128`) to t 200 |
| `09_convergence/` | PM10 (`PM10_L64_N128`, `PM10_L64_N192`, `PM10_L64_N256`) and M (`M_L64_N128`, `M_L64_N192`) to t 200; M at N 256 joins when it finishes |

The other groups (`01_star_family/` … `08_late_separation/`) come back as their reruns finish; the list and its
state are in `research/bondi_dipole/STATUS.md`, "Runs for the revision".

## How to read a cell name

`PM10_L64_N192` = the run labelled PM10 in the paper's Table I (the mixed pair, stars 10 apart), evolution box of
side `L = 64` with `N = 192` cells per side, no mesh refinement. A stop time other than the paper's is appended
(`PM10_L64_N128_t400`); `M_L64_N128` is the lone negative-mass star, 5 units off the centre. The initial data are
filed as `<name>_initial_data` under `runs/bondi/11_initial_data/`. The initial data are solved in a box of side 128
with the same cell size, so the solved metric lands on the evolution grid without interpolation. `evolution_params.txt` records
`N_full` and `max_level` but not the evolution `L`; `launch_config.sh` is the authoritative record of the grid.

## Files in a cell

| file | what it is |
|---|---|
| `sector_dynamics.dat` | the main stream: per-sector core position, peak, momentum, gauge |
| `sector_barycenters.dat` | whole-sector centroid and rms radius, an independent tracker |
| `confinement.dat`, `shell_profiles.dat`, `areal_radius.dat`, `boundary_flux.dat`, `ftl_timeseries.dat` | the consumer's other streams |
| `collapse_diagnostics.dat` | lapse, `chi`, `K`, downsampled to `dt = 0.5` |
| `constraint_norms.dat`, `energy_conditions.dat`, `curvature_invariants.dat` | likewise downsampled |
| `constraint_shells.dat` | the L2 of Ham and Mom (and the signed mean of Ham) in 33 unit shells about the centre, downsampled to `dt = 0.5`; the convergence figures read it |
| `psi4_*.dat` | extracted wave content |
| `Ham_and_Mom_errors.txt` | the elliptic solve's convergence history (cells that solved their own data) |
| `evolution_params.txt`, `grtresna_params.txt` | what was evolved, what was solved |
| `launch_config.sh` | the exact environment the cell was launched with |
| `frames/` | runs with frames only: stills every 10 time units per field, thinned from the run's frame set (`FRAMES.md`) |

Every `.dat` carries its own `#` header naming the columns.
