# Drainhole merger — packed campaign results

Two exotic-matter (phantom scalar) drainhole throats, given a gentle orbital push,
spiralling together in full 3+1 numerical relativity. This directory is the light
extract of that campaign: every number the analysis rests on, the movies, a thinned set
of stills, and enough provenance to rebuild any run. It is what survives if the machine
that produced it does not.

- The reasoning and the full argument: [`research/merger/Plan.md`](../../research/merger/Plan.md)
- The article in preparation: [`research/merger/article/research.tex`](../../research/merger/article/research.tex)
- The working run tree, **not in git** (~1.6 GB, on the machine that produced it):
  `runs/wormhole_merger/`, which carries its own README and a `NOTES.md` per stage
- Rebuild this directory: `bash research/merger/pack_results.sh`

## The result, in five lines

1. Two identical throats **repel**. Reversing one throat's scalar field is the only
   gravity-driven way to make them fall together — no aimed momenta, no support cuts.
2. Flipped and pushed, they **merge**: collapse of the whirling double core at t ≈ 45,
   a genuine common trapped surface at t ≈ 51, and a gravitational-wave burst that
   survives every check made on it. (The "merged at t ≈ 30" this file used to claim
   was a false verdict of the old in-code horizon scan, which assumed a conformally
   flat metric — fixed in code 2026-09-01; see `research/merger/Plan.md`.)
3. Then the merged object **dies** — a NaN wherever un-damped phantom matter sits on
   collapsed geometry. Four arms, four different treatments, four deaths between
   t = 51.7 and t = 55.0.
4. The arm that lived longest measured why: the common horizon is **shrinking**, 1.07 at
   t = 51.5 down to 0.59 at t = 55.0, and accelerating. Phantom matter falling in
   carries negative energy across the horizon, and the horizon pays for it.
5. Give the pair enough angular momentum that it never merges and the evolution is
   **healthy to t = 60 with no NaN at all**. The instability belongs to the merged core,
   not to the code.
6. And it is not a resolution artefact. A 25 % finer grid reproduces the inspiral to
   within 1.8 % and the waveform to within 4 % — and then dies of the same NaN
   1.55 units later. Refining postpones the failure by 3 %; reaching t = 60 that way
   would cost roughly 90× the compute.

## Layout

```
campaign/<run>/                 one directory per run
  collapse_diagnostics.dat        lapse, chi, K and scalar-field extrema
  constraint_norms.dat            Hamiltonian and momentum L2
  binary_throat_diagnostics.dat   separation, per-throat position and minima,
                                  the in-code Theta scan
  throat_track.dat                the tracker that aims the refinement boxes
  psi4_*.dat                      the extracted waveform, two radii (R = 14, 30)
  evolution_params.txt            the exact input the run was given
  launch_banner.txt               what the launcher resolved: template, binary,
                                  GPU, restart checkpoint, consumer arguments
  run_tail.log, backtrace.txt     the last 200 log lines and where it aborted
  movies/                         the stitched .mp4s, one per field
  frames/                         thinned stills, where the pictures carry a result
  part1/, *__part1*.dat           the pre-restart episode of the same run
horizon/                        the offline Theta = 0 scan behind result 4
analysis/make_summary.py        builds the two summary tables from the above
summary.md, summary.csv         one row per run, generated -- do not hand-edit
```

The four evolution streams are written every step (dt = 0.01) and thinned here to
dt = 0.05 — **except the last time unit of each run, kept at full cadence**, because that
is where a dying run does everything interesting. The `psi4` streams are one row per
plotfile and are packed whole.

Not packed, and not recoverable from here: plotfiles, checkpoints, the full frame series
(~250 per field) and the slice caches (7–260 MB per run). Those live in the run tree.

## The runs

Nine runs. The first five are one chain — each restarts from the previous one's
checkpoint, changing exactly one thing, hunting the same failure. The rest are
independent probes. `summary.md` has the measured columns for all of them.

Reading a name: `merge_orbit_flip_d12_rw_r05000` is a **merge** run, throats on an
**orbit** (given tangential momentum) rather than dropped head-on, one throat's scalar
field **flipped** in sign, started **d = 12** apart, using the **r**adius **w**indow
damping, **r**estarted from checkpoint **05000**. `_pNNN` is a different tangential
momentum, `_nNNN` a different cell count, `_mlN` a different `max_level`, `_sgNN` a
different Kreiss–Oliger dissipation.

| run | what is different | ran to | what happened |
| --- | --- | --- | --- |
| `..._r03000` | **the main arm** — no damping | 52.06 | Inspiral to t ≈ 33, whirling double core, collapse at t ≈ 45, horizon at t ≈ 51 — then the phantom core blew up. Everything after this is an attempt to save it. |
| `..._r05000` | damping on, built-in thresholds (≈3 cells) | 52.09 | Bought 0.02 units. Aimed too deep to touch the matter that kills it. **Its streams were deleted before extraction — only the log survives.** |
| `..._r04000` | window widened 1000× (lapse 3e-2 → 1e-3) | 52.86 | Core cleaned to φ ≈ 1e-10 and it still died: 1+log slicing lets the sickest cells re-inflate their own lapse and climb out of a lapse-defined window. |
| `..._sg10_r05000` | dissipation σ 0.1 → 1.0 | 51.68 | Backfired — died *earlier*. The dissipation attacks the puncture structure itself. |
| `..._rw_r05000` | damping anchored in **radius**, not lapse | **55.00** | Longest survivor, and the one that caught the horizon dissolving. |
| `merge_headon_...` | dropped head-on, no orbital momentum | 44.00 | Merges harder and sooner, dies the same death. (Its "horizon at t = 29" was the old-scan artefact; true timing unverifiable — no metric in its plots.) |
| `..._p045` | momentum 0.45 instead of 0.12 | **60.01, clean** | Never merges: closest approach 3.95 at t = 40, then back out to 4.6. The healthy control. |
| `..._n160` | 160 cells per side instead of 128 | 53.61 | The convergence check, and the only undamped arm that ran t = 0 → death in one piece. Everything before the collapse converged; the death moved by 3 % and stayed. |
| `..._ml2` | `max_level = 2` instead of 3 | 9.42 | Dies before the throats meet. Three levels is the floor, not a luxury. |

Everything not named above is identical across all nine: two drainhole throats, scale
`a = 2`, ADM mass 1 each carried by the lapse, separation 12, box `L = 64`, `N = 128`,
`max_level = 3`, Sommerfeld boundaries, σ = 0.1, `stop_time = 60`.

## How these runs were launched

Every run went through one launcher,
[`grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh`](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh),
from the repository root, on a single node with four H100s. **The binary is never
invoked directly** — AMReX writes `parameters_and_version.txt` into the working
directory with the absolute output paths it was given, and that file reached a commit
that way once. The launcher clones the params template, rewrites its path keys to point
at node-local scratch, `cd`s into the (gitignored) run directory, registers a
`launcher.pid`, and starts the plotfile consumer sidecar beside the evolution.

Two frame sets were used. The first five runs asked for the six evolved fields; the
damping arms added the metric and the derived views, which is also when `h_ij`/`A_ij`
entered the plot list:

```bash
F6="--frames-fields chi K lapse phi Pi Weyl4_Re \
    --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices --frames-auto-zlim"

F12="--frames-fields chi chi_minus_1 K lapse shift1 phi Pi \
     Weyl4_Re Weyl4_Im Weyl4_Mag scalar_activity local_speed \
     --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices --frames-auto-zlim"

L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh
R=runs/wormhole_merger
```

### The four independent runs, one per card

Launched together, detached, 2026-08-31:

```bash
WHM_PARAMS=params_merge_orbit_flip.txt      WHM_NAME=merge_orbit_flip_d12 \
  WHM_GPU=0 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu0.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_headon_flip.txt     WHM_NAME=merge_headon_flip_d12 \
  WHM_GPU=1 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu1.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_orbit_flip_n160.txt WHM_NAME=merge_orbit_flip_d12_n160 \
  WHM_GPU=2 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu2.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_orbit_flip_p045.txt WHM_NAME=merge_orbit_flip_d12_p045 \
  WHM_GPU=3 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu3.log 2>&1 < /dev/null &
```

The `ml2` probe is the same orbit template with one knob, and it ran attached:

```bash
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12_ml2 \
  WHM_GPU=2 WHM_MAX_LEVEL=2 WHM_CONSUME_ARGS="$F6" bash $L
```

`WHM_MAX_LEVEL` rewrites `regrid_interval` to match — AMReX aborts if it does not
carry exactly `max_level` values.

### The restart chain

Only `params_merge_orbit_flip.txt` sets `checkpoint_interval` (1000 coarse steps, every
10 code units). The other three templates have it at `-1`, which is why `headon`, `n160`
and `p045` cannot be continued and why the whole damping investigation happens on the
orbit arm. Each restart names its **parent**; the launcher appends `_rNNNNN` itself, so
a continuation gets its own run directory and scratch and never clobbers the parent's
streams:

```bash
# r03000 -- the main arm resumed from the base run's newest checkpoint
CK=$(ls -d /tmp/grteclyn_scratch/merge_orbit_flip_d12/*Chk[0-9]* | sort -V | tail -1)
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 \
  WHM_GPU=0 WHM_RESTART="$CK" WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu0.log 2>&1 < /dev/null &

# r05000 -- damping on, thresholds left at the built-in defaults
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r03000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_r05000.log 2>&1 < /dev/null &

# r04000 -- the wide lapse window, written into the template before launch
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r03000/BinaryWormholeChk04000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_r04000.log 2>&1 < /dev/null &

# sg10 -- same window, dissipation raised; WHM_SIGMA appends _sg10 to the name
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_SIGMA=1.0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r04000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_sg10_r05000.log 2>&1 < /dev/null &

# rw -- the radius window, also a template edit; renamed by hand to keep it apart
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12_rw WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r04000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_rw_r05000.log 2>&1 < /dev/null &
```

**The three damping arms differ from each other by edits to the params template, not by
environment variables.** `core_damping_enabled`, the lapse thresholds and the radius
window were written into `params_merge_orbit_flip.txt` between launches, so the template
in git today is the *last* of them. The authoritative record of what each run actually
executed is its own `evolution_params.txt` in this pack — that is the cloned copy, taken
at launch.

### Four things that will cost you a day if you skip them

1. **No `env` prefix.** `setsid nohup env WHM_...=... bash $L` exits 0 in under a second
   and writes a zero-byte log. Variables go *before* the whole `setsid nohup` chain, as
   above.
2. **A printed PID proves nothing.** Four runs launched with a plain `&` from an editor
   session died when the editor restarted, losing 11, 11 and 3 code units on the arms
   that had no checkpoints. Detachment means the launcher is a session leader whose
   parent is init — check it, do not assume it:
   ```bash
   ps -eo pid,ppid,sess,args --no-headers | grep "[r]un_single.sh"
   # each launcher must show ppid = 1 and sess = its own pid
   ```
3. **Decide what to extract before launching.** The consumer deletes each plotfile once
   it has processed it (`--keep-last 3`), so anything not named in `WHM_CONSUME_ARGS`
   is gone with the plotfile. The five runs launched without `h_ij`/`A_ij` in
   `amr.plot_vars` can never be measured by the offline horizon finder — permanently.
   Frames also need `--frames-auto-zlim`: the preset colour ranges are black-hole
   values and wormhole frames come out blank without it.
4. **Dry-run first.** `WHM_DRYRUN=1` resolves the name, template, binary, scratch,
   restart checkpoint and consumer command, prints them, and touches nothing.

Stop a run with the campaign stopper, never by pattern-killing the binary — other
people's jobs share these cards:

```bash
bash grteclyn-wrapper/scripts/campaigns/stop_campaign.sh [--dry-run] runs/wormhole_merger/<run>
```

### After the run

```bash
# redraw every cached slice on one fixed colour scale, then stitch the movies
.venv/bin/python grteclyn-wrapper/scripts/plot/rerender_frames.py <run>/frames --movies

# the offline horizon scan (needs h_ij/A_ij in the plotfile)
.venv/bin/python grteclyn-wrapper/scripts/validation/ah_radial_scan.py <plotfile>

# rebuild this pack
bash research/merger/pack_results.sh                  # streams, movies, stills, tables
PACK_HORIZON=1 bash research/merger/pack_results.sh   # and re-run the horizon scan
```

Live frames are scaled per frame, so the colourbar moves; `rerender_frames.py` is what
makes a colour mean the same value in every frame of a movie.

## `horizon/` — the dissolution measurement

`horizon_dissolution.dat` is the radius of the outermost **fully trapped** coordinate
sphere around the merged core, from an offline scan of the plotfiles:

| t | r_AH | from |
| --- | --- | --- |
| 51.50 | 1.070 | `r04000` |
| 52.00 | 1.050 | `r04000` |
| 52.50 | 1.030 | `r04000` |
| 54.00 | 0.890 | `rw` |
| 54.50 | 0.830 | `rw` |
| 55.00 | 0.590 | `rw` |

Two independent damping schemes, one curve, accelerating toward zero at t ≈ 56. It is a
measurement, not a fit, and it was checked three ways: no NaN or inf cell appears in any
scan box, doubling both the angular and the radial sampling moves every crossing by
≤ 0.01, and the t = 51.5 value matches the in-code diagnostic's ≈ 1.0 at the same step.
Damping cannot be blamed for it — deleting negative-energy matter pushes the energy
budget toward horizon *growth*, not shrinkage.

`ah_radial_scan_output.txt` is the raw scanner output, including the per-ray statistics.
Those show the trapped region is strongly deformed — reaching past r = 2 along the poles
while pinching to ~0.6 at the equator — which is also why a purely radial in-code proxy
loses sight of it.

Regenerate with `PACK_HORIZON=1 bash research/merger/pack_results.sh`, which needs
plotfiles that the consumer sidecar deletes as a run proceeds; only the last few of each
arm still exist. Without that flag the committed copy is left alone.

## Reading these files without being fooled

- **The last row of a dead run is the crash, not the spacetime.** `max|K|` of 3648 and an
  L2 Hamiltonian of 4.4 in the `rw` arm are the NaN arriving. `summary.md` quotes the row
  half a unit earlier for exactly this reason; do the same.
- **Separation can glitch to ~0 for a single row.** When the throats swap sides both
  finders can latch onto the same one; `p045` reads 0.06 at t = 38.46 between neighbours
  of 4.06. Its true closest approach is 3.95 at t = 40, and both trackers agree on it.
  `make_summary.py` drops rows that disagree with both neighbours by more than half.
- **The θ/AH columns (13–18) of every `binary_throat_diagnostics.dat` in this pack are
  tainted.** All were written by the pre-2026-09-01 scan, which assumed a conformally
  flat metric; wherever one scan sphere encloses two wells it produces false trapped
  verdicts — the t ≈ 30 "fusion" on the merger arms, and continuous trapping out to
  r = 6.2 over t ≈ 42–60 in `p045`, a run with no collapse anywhere. Trust only the
  offline scan (`horizon/`), which needs `h_ij` and `A_ij` in the plotfiles: only
  `r04000`, `rw` and `sg10` were launched with them, so the undamped main arm can never
  be checked this way. That is permanent. The in-code scan computes the full-metric
  expansion since 2026-09-01; streams written after that date are trustworthy.
- **Waveforms across a restart.** The interior of a restart restores exactly; the outer
  boundary does not, and the error walks inward at roughly the speed of light. Do not
  read `psi4` at R = 30 across a restart boundary without allowing for it.
- **The first ~5 time units are gauge settling.** Nothing measured there means what it
  appears to mean.
