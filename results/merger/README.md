# Drainhole merger — packed campaign results

Two exotic-matter (phantom scalar) drainhole throats, given a gentle orbital push,
spiralling together in full 3+1 numerical relativity. This directory is the light
extract of that campaign: every number the analysis rests on, the movies, a thinned set
of stills, and enough provenance to rebuild any run. It is what survives if the machine
that produced it does not.

- The reasoning and the full argument: [`research/merger/Plan.md`](../../research/merger/Plan.md)
- The article in preparation: [`research/merger/article/research.tex`](../../research/merger/article/research.tex)
- The working run tree, **not in git** (~11 GB, on the machine that produced it):
  `runs/wormhole_merger/`, which carries its own README and a `NOTES.md` per stage
- Rebuild this directory: `bash research/merger/pack_results.sh`

## The result, in seven lines

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
4. The arm that lived longest measured the horizon **shrinking**, 1.07 at t = 51.5 down
   to 0.59 at t = 55.0, and accelerating. The natural reading — infalling phantom matter
   carrying negative energy across the horizon — survives every exclusion test run so
   far (damping the matter away pushes the budget the *other* way), but the energy-density
   sign at the horizon has not yet been measured directly (GPU_PLAN #13); until it is,
   the mechanism is stated as inference, the shrinkage as measurement.
5. Give the pair enough angular momentum that it never merges and the evolution is
   **healthy with no NaN at all**. The fly-by runs say so: `merge_orbit_flip_d12_p045`
   (clean to t = 60), its long rerun `..._p045_t200` (held to t ≈ 91), and
   `..._p035_t200` (closest approach 2.75, run to t = 73.9). The instability belongs
   to the merged core, not to the code.
6. And it is not a resolution artefact. A 25 % finer grid reproduces the inspiral to
   within 1.8 % and the waveform to within 4 % — and then dies of the same NaN
   1.55 units later. Refining postpones the failure by 3 %; reaching t = 60 that way
   would cost roughly 90× the compute. (Confirmed again on p = 0.15: a max_level 5
   restart bought +0.88 over the level-3 wall and still died mid-fusion.)
7. The result survived its credibility batch (2026-09-03/04): turn the core damping
   off and nothing claimed changes; change the slicing and the *physics* holds while
   the crash time moves 8.4 units (the wall is gauge, not an event); rerun a scout
   and it dies on the identical step (deterministic); and the same pipeline, fed
   vacuum black holes, recovers the textbook Kerr ringdown to a few percent.

## The paper's claims, and the runs behind each

Written claim-first so a paper subsection can be lifted straight from here:
what the text asserts, the runs that establish it, and where the numbers sit.
Runs overlap between claims — that is the point of the map. *(pack)* = has a
directory under `campaign/`; *(run tree)* = lives only in the gitignored
`runs/wormhole_merger/` tree on the production machine. As of 2026-09-04
two pack entries are snapshots of runs **still in flight** — the floor-ladder
reference rung `merge_twin_p012_cf08_t060_r05000` and the decisive from-t = 0
low-floor twin `merge_twin_p012_nodamp_cf10_t060`; both will be repacked at
their close-out. Every other pack entry is a finished run.

### The initial data is validated: a single throat holds 40 time units
- **Claim.** The grid represents each wormhole by folding its entire far
  universe into the ball inside the throat sphere (the other side's infinity
  lands on the throat's centre point) — the route the background survey said
  to avoid, because the published single-throat attempt (arXiv:2604.00071)
  died of it at t ~ 1.5. We used it anyway and measured it instead of
  assuming: refining the origin made every error *smaller*, a small lapse
  collar over the centre bought ~3.5x on origin survival, the mass was put in
  the lapse (drainhole) rather than the spatial metric (which crushes the
  throat), and a single static throat then held **40 time units with -0.36 %
  drift**, constraints exact at t = 0. This is the initial-data validation
  every merger run inherits.
- **Runs.** The Stage-1 ladder under `runs/wormhole_merger/01_single_throat/`
  *(run tree — see its NOTES.md)*: the lapse/collar/dissipation grid
  (`stage1_lapse5*`, `stage1_lapse6*`), the uniform-grid origin pair
  (`s1uni128`, `s1uni256`), and the long holds (`s15_*`, `s16ml3_*`).
- **Caveat.** The 40-unit window is a fuse, not stability: the known
  Ellis-Bronnikov growing mode (e-fold ~ 4.4, about one throat-light-crossing)
  is still growing at t = 40. Every production arm is budgeted to finish
  inside the fuse.

### Like-oriented throats repel; flipping one is what makes a binary
- **Claim.** Two identical throats push apart (5× gravity at a = 2, m = 1, the
  push scaling with throat *width*, not mass; pull/push ratio 1.50 measured vs
  1.5 predicted). Reversing one throat's scalar field turns the push into a
  pull — the only gravity-driven route to a merger.
- **Runs.** The Stage-2.5/2.6 control pairs under
  `runs/wormhole_merger/03_two_throats/` *(run tree — see its NOTES.md)*;
  every `merge_*flip*` run below is the attracting configuration in action.

### The p = 0.12 pair merges
- **Claim.** Inspiral to t ≈ 33, whirling double core, collapse at t ≈ 45, a
  genuine common trapped surface at t ≈ 51, and a gravitational-wave burst.
- **Runs.** `merge_orbit_flip_d12_r03000` *(pack)* — the discovery arm (its
  `__part1` streams are t = 0 → 30.5); `merge_headon_flip_d12` *(pack)* — the
  no-orbit version, merges sooner; `merge_twin_p012_plain_t100` *(pack)* — an
  independent from-scratch rerun 2026-09-02 that retraced the record (sep 2.06
  at t = 32.00 vs the original's 2.0) and closed to sep 0.81 by t = 44: the
  reproducibility twin.
- **Numbers.** `campaign/<run>/binary_throat_diagnostics.dat` (separation),
  `collapse_diagnostics.dat` (collapse), `horizon/` (the trapped surface).

### The merged object is a black hole that dissolves
- **Claim (measured).** The common trapped surface shrinks — 1.07 at t = 51.5
  down to 0.59 at t = 55, accelerating — on two independent damping schemes
  giving one dissolution curve. The run dies at t = 55 with the surface still
  shrinking: this is the **onset** of dissolution, not its endpoint, and the
  paper must not claim the completed disappearance.
- **Mechanism (inference, not yet measurement).** Phantom matter carrying
  negative energy across the horizon fits every exclusion test (deleting the
  matter by damping pushes the energy budget the other way), but the
  energy-density sign at the horizon is the still-unrun GPU_PLAN #13
  measurement. Until #13 lands, the paper states the shrinkage and *offers*
  the mechanism; it does not assert it.
- **Runs.** `merge_orbit_flip_d12_r04000` and `..._rw_r05000` *(pack)* — two
  independent damping schemes, one dissolution curve; `..._sg10_r05000`
  *(pack)* corroborates the death; the measurement itself is the offline scan
  in `horizon/`.
- **Say it as.** The merger produces a short-lived black hole that dissolves
  by swallowing its own exotic matter — written as **contingent** (GPU_PLAN
  §8 decision 7). Two gates before the hedge comes off: (1) the 2026-09-04
  floor ladder showed the collapsed-core state is floor-regularized (a
  relaxed χ-floor on the t = 50 state is instantly fatal), so horizon and
  dissolution numbers stand only if the from-t = 0 low-floor twin reproduces
  them; (2) "extinguished by negative-energy accretion" and "evaporates
  classically" are allowed only after #13 measures the sign. Nothing here is
  Hawking radiation either way.

### The instability belongs to the merged core, not the code
- **Claim.** Deny the merger and the evolution is healthy.
- **Runs.** `merge_orbit_flip_d12_p045` *(pack)* — clean to t = 60;
  `..._p045_t200` *(pack)* — the same fly-by held to t = 200, source of the
  six survival figures; `..._p035_t200` *(pack)* — a second fly-by (min sep
  2.75), though its inter-throat midpoint shows the slow lapse collapse of
  the freeze wall (last claim below), so "healthy" there needs the
  qualification.

### Resolution postpones the wall, never removes it
- **Claim.** The death time climbs +1.43 per refinement level, linearly over
  four rungs, no saturation and no cure; the NaN lands on each newly created
  finest level, so the blowup is a property of the continuum solution.
  Reaching t = 60 by refinement alone would cost ~10² × the compute.
- **Runs.** `merge_orbit_flip_d12_ml2` *(pack)* — level 2 dies at t = 9.4,
  before the throats meet; `..._r03000` (level 3, death 52.06) and `..._n160`
  *(pack)* — 25 % finer, same physics to 1.8 %, death 3 % later; the m4e
  refinement ladder, levels 4–7 with twins *(run tree —
  `runs/wormhole_merger/merger_fix/`, LAUNCHES.md and the ladder archives)* —
  pair-mean deaths 52.26 / 53.43 / 55.18 / 56.42, level-7 single arm 56.20;
  `..._p020_lvl5_t200` and `..._p025_lvl5_t200` *(pack)* — level 5 run
  from t = 0 dies at the level-3 wall (52.07 / 52.79): the +1.4/level gain
  belongs to the *restart* recipe (χ already clipped at the pits when a
  run starts deep), so depth must be added mid-run, not from birth.

### The interior freeze rescues the ringdown window
- **Claim.** Freezing the collapsed interior after the burst closes carries
  the evolution to t = 100 with flat constraints for 27+ units; the exterior
  is bit-identical to the unfrozen twin beyond r = 6, the two seam-radius
  twins agree to five digits at every shared waveform sample, and the
  late-engagement control moves the R = 14 waveform ≤ 0.003 % (m = 2) /
  0.022 % (m = 0).
- **Runs.** The M9b program *(run tree — `runs/wormhole_merger/merger_fix/`)*:
  `m9b_fill80_r05000` / `m9b_fillwide80_r05000` (the t = 80 twins),
  `m9b_fill100_r08000` / `m9b_fillwide100_r08000` (the t = 100 drains), plus
  the seam and late-engagement controls in the merger_fix archives.
  Figures in `figures/`.

### The recorded signal is a genuine gravitational wave
- **Claim.** Propagation at 0.889 of coordinate light matches the metric's
  own local light speed along the extraction path (14→30 crossing predicted
  ~19.5, measured 18.0); 1/R falloff holds; the (2,0) breathing and (2,2)
  whirl channels separate cleanly; the in-code mode integrals match an
  independent Simpson quadrature to 1e-8.
- **Runs.** The same M9b freeze arms *(run tree)*; the evidence is
  `figures/psi4_analysis_m9b_fillwide80*` and `figures/wave_speed_check.png`.

### Where the capture boundary sits in orbital momentum
- **Claim.** p = 0.20 and 0.25 are captured, p = 0.35 and 0.45 fly by — the
  boundary sits between 0.25 and 0.35 (50–70 % of circular). Whether a
  captured scout *completes* its merger is open: every one hits the t ≈ 53
  wall first, so "no completed merger at p ≠ 0.12" is untested, not
  established.
- **Runs.** `..._p020_t200`, `..._p025_t200`, `..._p035_t200`,
  `..._p045_t200` *(pack)*; `..._p020_nofill_t060` *(pack)* — p = 0.20 with
  damping off and in-code Weyl4: **hovered at sep 1.08 from t = 46 until the
  wall (52.08)** — captured but not fusing; the two lvl5 arms *(pack)* —
  the same answer at depth.  And the boundary is finer than "0.12 fuses,
  0.20 hovers": `..._p015_nofill_t060` and its insured rerun
  `..._p015_rr_t060` *(pack)* put **p = 0.15 on the fusing branch** —
  plateau at pit sep 0.816 (p012's was 0.815), dive to 0.70 with the core
  lapse *rising* (p012's endgame signature) — but the wall (53.35, the
  same step in both runs) cut it before the pits coincided.  So the fusing/
  hovering divide sits between 0.15 and 0.20.  The restart-refinement
  recipe was then tried and is **not enough**:
  `..._p015_lvl5_t060_r05000` *(pack)* — max_level 5 from the insured
  t = 50 seed — pushed the wall only +0.88 (h11 NaN at t = 54.23), the
  offline scan of its last plotfiles finds **no trapped surface** (1 % of
  rays at t = 54.0), and the (2,2) waveform was *still climbing* at death:
  3.14e-2, already 6 % above p012's complete peak.  p = 0.15 was wall-cut
  mid-fusion a third time; refinement alone cannot outrun the wall, and
  finishing p = 0.15 — and its full, larger signal — means the core-freeze
  continuation validated on p012.

### The Helfer correction: better initial data, worse evolution
- **Claim.** The correction removes the superposition's constraint defect at
  the throats but parks a fade-zone defect between them; at the default
  window (d/3 = 4) the orbit stalls at sep ≈ 4.7 and the run freezes —
  reproduced at levels 3, 4 and 5, so converged, not under-resolution.
  The halved window (2.0) did NOT clear it: the w2 twin tracked plain
  superposition exactly to t ≈ 14, then fell progressively behind and read
  sep 5.10 at the pre-registered t = 32 gate — above the 4.5 kill line and
  above even the wide-window run's 4.73 (plain: 2.06). Window placement was
  not the problem; the correction itself spoils the phantom binary's infall.
  Production therefore runs plain superposition (its +9.5 % initial-size
  artefact accepted).
- **Runs.** `merge_twin_p012_helfer_t100` vs `..._plain_t100` *(pack)* — the
  one-flag twins; `..._helfer_lvl4_t100` *(pack)* — stall reproduced to < 2 %
  in the lapse trace; `..._helfer_lvl5_t100` *(pack)* — stalled the same at
  production depth, stopped at t = 31.5; `..._helfer_w2_t060` *(pack)* —
  window halved to 2.0, killed by its pre-registered verdict (sep 5.10 > 4.5
  at t = 32), stopped by hand at t = 33.1.

### The freeze wall itself: lapse collapse at the midpoint, not the throats
- **Claim.** In every binary the lapse collapses at the inter-throat midpoint
  (where the opposite scalar profiles cancel), never at the throat cores (the
  pits hold lapse 0.05–0.24 throughout). If the midpoint reaches the 1e-10
  floor the evolution goes static without a NaN — the "zombie"; if it hovers
  above, the run dies of the h11 NaN instead. Mergers interrupt the collapse;
  stalls and fly-bys let it finish.
- **Runs.** The Helfer twins *(pack)* — the clean zombie; `..._p025_t200`
  *(pack)* — the NaN side of the race; `..._p035_t200` *(pack)* — a slow
  zombie with no Helfer correction at all, proving the wall is not
  Helfer-specific; the unmasked runs (`_nofill`, damping off) confirmed it
  on p = 0.15 and 0.20. The validation and the slice-probe evidence are
  written up in `research/merger/GPU_PLAN.md` §9.

### The wall time is gauge + resolution, not physics
- **Claim.** The t ≈ 52–53 death time must never be read as a physical event.
  Three independent handles each move it while the physics underneath holds:
  refinement moves it +1.4 units per level (the ladder above); halving the
  slicing's `lapse_coeff` (2 → 1) moves it **8.4 units earlier** — to
  t = 43.64 — while the blob still nucleates on schedule, capture and plunge
  proceed, and the pits close to 0.442; and at fixed gauge + resolution it is
  *deterministic*: the p015 rerun died at the same step (5335, t = 53.35) as
  its original. The crash is the 1+log slicing losing its
  singularity-avoidance race, not the singularity arriving.
- **Runs.** `merge_twin_p012_lc1_t060` *(pack)* — the one-knob gauge arm;
  `merge_orbit_flip_d12_p015_nofill_t060` + `..._p015_rr_t060` *(pack)* — the
  determinism pair; the m4e ladder *(run tree)* — the resolution axis.
- **Say it as.** Every claimed event (blob, capture, fusion, burst) completes
  *before* the wall of the run that claims it; the wall itself is quoted only
  as the limit of the numerical window.

### The core damping shapes nothing that is claimed
- **Claim.** Every scan/twin verdict was originally taken with
  CoreMatterDamping engaged from t ≈ 30. The damping-off twin shows this
  never mattered: at t = 32 the damped and undamped runs agree to 3 decimals
  in separation, midpoint lapse, |φ| and scalar activity (the files are
  verifiably different — max |Δφ| = 0.0056, so this is agreement, not a
  copy), and the wall moves only 52.06 → 51.53 (~1 %, the arm-pair noise
  floor). Damping neither causes the blob, nor the merger, nor the wall —
  and production can run clean (damping off) with its behaviour measured
  rather than assumed.
- **Runs.** `merge_twin_p012_nodamp_t060` vs `merge_twin_p012_plain_t100`
  *(pack)* — the one-knob pair.

### The vacuum BBH control recovers the known answer
- **Claim.** The same grid, gauge, extraction chain and orbit (d = 12,
  p = ±0.12, ADM mass 1 each), with black holes instead of throats, does
  everything textbook: merger at t ≈ 70, then a ringdown whose fitted QNM
  (period 28.8–29.7, damping time 23–27) matches a Kerr remnant of
  M ≈ 1.9 with modest spin (Schwarzschild reference 16.8 M / 11.2 M —
  spin shortens the period exactly as seen); both extraction radii agree to
  3–7 %. The instruments cross-validate: the independent plotfile consumer
  and the in-code stream match to 0.31 % of peak (correlation 0.999999).
  Boundaries hold for 150 units with Sommerfeld alone — χ scatter *falls*
  outward, no reflected ripples (the sponge exists only in the wormhole
  code path; the vacuum run needs none, by construction). And at the same
  detector (R = 14) the wormhole merger is **~2.3× louder** than the BBH —
  with an extra (2,0) breathing channel 5.5× the BBH's.
- **Runs.** `bbh_control_d12_p012_t150` *(pack)* — the control;
  `bbh_control_d12_p012` *(pack)* — its t = 100 predecessor;
  `merge_twin_p012_plain_t100` *(pack)* — the wormhole side of the
  comparison. Figures: `figures/bbh_t150_ringdown.*`,
  `figures/bbh_vs_wormhole_psi4.*`.

## `figures/` — the campaign figures (2026-09-02 → 04)

| file | what it shows |
| --- | --- |
| `bbh_t150_ringdown.{png,pdf}` | the BBH control's full (2,2) ringdown at R = 30 with the QNM fit (period 29.7, τ 27.1) and the Kerr known-answer comparison |
| `bbh_vs_wormhole_psi4.{png,pdf}` | same masses, same orbit, different object: wormhole vs BBH waveforms, envelopes (2.3× / 5.5×), PSD |
| `psi4_analysis_m9b_fillwide80.{png,pdf}` | six-panel analysis of the (2,0) breathing mode, full history t = 0–80 stitched across the restart chain: waveform at both radii, retarded-time overlay, PSD, propagation speed (0.889 of coordinate light — see the speed check below), spectrogram, strain vs Advanced LIGO |
| `psi4_analysis_m9b_fillwide80_m2.{png,pdf}` | same six panels for the (2,2) whirl mode — the channel that carries the plunge burst |
| `merger_ladder_psi4_R14/R30.png` | every campaign arm overlaid at each detector: the freeze arms run exactly under the unfrozen ladder arms wherever they overlap |
| `ladder_psi4_R14_lvl6.png` | the refinement-ladder arms alone at R = 14 |
| `merger_constraints_t80.png` | Hamiltonian and momentum L2 for both completed t = 80 freeze arms, t = 0–80: the spikes before t = 34 are regrid transients; the smooth bump is the collapse; after the freeze engages at 53 both norms sit flat for 27 units |
| `wave_speed_check.png` | why 0.889 c is not sub-luminal junk: the metric's own local light speed along the extraction path predicts a 14→30 crossing of ~19.5; the wave took 18.0. Constraint/gauge modes travel at √2 × light and are excluded |
| `seam_ring_rescaling.png` | why the freeze-arm frames *look* like the signal vanishes: a growing Ψ₄ artefact confined to the freeze seam hijacks the per-frame colour scale; the radiation field is bit-identical to the unfrozen twin beyond r = 6 |

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

## The stage-3 chain in detail

Nine runs (the 2026-09-02/03 scan, twin and wall runs are described in the
claim map above and carry rows in `summary.md`). The first five are one chain — each restarts from the previous one's
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
