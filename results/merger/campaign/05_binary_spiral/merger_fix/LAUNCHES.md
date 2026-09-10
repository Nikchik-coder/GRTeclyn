# merger_fix — launch record

Runs validating and then rescuing the merger after the 2026-09-01 horizon-scan fix
(Plan.md, checkpoints M2–M8). Everything here follows the launch conventions in
`results/merger/README.md` ("How these runs were launched"); this file records only
what differs.

## val_ahfix_r04000 (M2+M3 merged) — launched 2026-09-01

The original Chk03000 (t = 30) no longer exists on scratch, so the validation
restarts from the surviving `merge_orbit_flip_d12_r03000/BinaryWormholeChk04000`
(t = 40) instead and runs to the natural NaN death ≈ 52.06. One run now covers
both gates:

- **M2 (specificity):** the fixed scan must stay silent over t = 40–50.9 — the
  two-wells-in-one-sphere regime where conformal flatness fails O(1). Cross-check
  offline on this run's own plotfiles (h_ij/A_ij are in the plot list).
- **M3 (sensitivity):** first genuine trapped surface at t ≈ 51.06, r ≈ 1.0,
  agreeing with the offline scanner's 1.07 at t = 51.5 to ~10 %. The old scan
  reported NOTHING over 40–52 — it missed the real horizon too.
- **Regression:** evolution columns must be bit-identical to r03000's streams
  (the kernel change is diagnostic-only). Verified at t = 40.01–40.03 at launch:
  separation/chi/lapse identical to every printed digit.

Template: `templates/params_val_ahfix.txt` = `params_merge_orbit_flip.txt` (the
rw-era copy) with exactly two edits:

- `checkpoint_interval = -1` (no checkpoints — short validation run, per request)
- `core_matter_damping = 0` (undamped, reproducing r03000's own segment)

Launch (repo root, GPU 0, detached, verified ppid = 1). **Every path absolute** —
the launcher `cd`s into the run directory before exec'ing and passes `WHM_EXE`
and `WHM_RUNS_DIR` through verbatim, so a relative value dies there with
`No such file or directory` (exit 127) or `Couldn't open file: …/params.txt`:

```bash
R=<repo root>
WHM_PARAMS=$R/runs/wormhole_merger/merger_fix/templates/params_val_ahfix.txt \
WHM_NAME=val_ahfix WHM_GPU=0 \
WHM_RUNS_DIR=$R/runs/wormhole_merger/merger_fix \
WHM_EXE=$R/Examples/BinaryWormholeMerger/main3d.gnu.MPI.CUDA.ex \
WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r03000/BinaryWormholeChk04000 \
WHM_CONSUME_ARGS="--frames-fields chi chi_minus_1 K lapse shift1 phi Pi \
  Weyl4_Re Weyl4_Im Weyl4_Mag scalar_activity local_speed \
  --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices --frames-auto-zlim" \
setsid nohup bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh \
  > runs/wormhole_merger/merger_fix/detached_gpu0_val.log 2>&1 < /dev/null &
```

Binary: `main3d.gnu.MPI.CUDA.ex` rebuilt 2026-09-01 01:23 with the full-metric
θ kernel (commit 04c9d89c). Speed at launch ≈ 10 code units/h → death ≈ 75 min.

Checkpoints that still exist for later steps (M4+):
`merge_orbit_flip_d12_r04000/BinaryWormholeChk05000` (t = 50) — note its state
carries r04000's lapse-window damping history from t = 40 on.

### Result — both gates PASS (2026-09-01)

Died as expected: `NaN in GRAMRLevel::post_timestep`, component K, level 3, at
t = 51.7075 (r03000 died 52.06). Ran t = 40 → 51.71 in 39 min at 18.2 units/h.

| gate | criterion | measured | verdict |
|---|---|---|---|
| M2 specificity | no common trapping over the two-well regime | silent t = 40 → 51.02, min θ = +0.158 | PASS |
| M3 sensitivity | trapped surface t ≈ 51.1 ± 0.5, r ≈ 1.0, ≤ 10 % from offline | first θ < 0 at t = 51.03, r = 1.0625; sustained from 51.47 | PASS |
| second source | offline `ah_radial_scan.py` on this run's own plotfiles | fully-trapped shell r = 1.110 (t = 50.5), 1.090 (51.0), **1.070 (51.5)** | agrees to 0.7 % |
| regression | evolution untouched by the diagnostic fix | bit-identical to r03000 through t ≈ 44.9 | PASS |

The old scan found **nothing** anywhere in t = 40–52 — it missed this horizon
entirely. The fixed scan finds it within 0.03 units of the offline scanner and
within one cell (dx = 0.03125) of its radius.

Two measurements that change the plan:

- **Post-floor trajectories are not run-to-run reproducible.** The streams are
  bit-identical from the restart until χ first touches min_chi at t ≈ 44.9, then
  decohere (sep 0.477 vs 0.569 at t = 48) and the deaths differ by 0.35 units.
  Floor clipping plus non-deterministic GPU reductions; the *physics* repeats
  (horizon ≈ 51, death ≈ 52), the trajectory does not. No convergence or overlap
  claim may be stated tighter than that.
- **r_AH(t) is shrinking from the moment it forms**: 1.110 → 1.090 → 1.070 over
  t = 50.5 → 51.5, i.e. ≈ 0.04 per code unit. Linear extrapolation crosses
  r = 0.95 at t ≈ 54.5. That is the measured lifetime of the M4 seal, and it is
  the freeze hypothesis' first evidence against: the horizon is not frozen, it
  is already contracting before any damping exists.

## m4_sealed (M4) — launched 2026-09-01 02:44

Template `templates/params_m4_sealed.txt`, seven edits off the validation clone:

| key | value | why |
|---|---|---|
| `core_matter_damping` | 1 | engage the cure |
| `core_damping_lapse_start` | **0.0** | **disables the lapse window** — see below |
| `core_damping_radius_start` | 0.95 | zero weight at and outside 0.95 |
| `core_damping_radius_full` | 0.80 | full weight inside 0.80 |
| `core_damping_radius_from_time` | 51.2 | engage only after certification |
| `checkpoint_interval` | 500 | every 5 units — this one is a long run |
| `stop_time` | 66.0 | far enough for the R = 14 record (M7) |

**Why the lapse window must be off.** `CoreMatterDamping::operator()` combines the
two windows as `w = max(w_lapse, w_radius)`, and the lapse branch is live whenever
damping is enabled. Leaving `lapse_start = 3e-2` would damp every cell below that
lapse *wherever it sits*, so the damped region would no longer be bounded by a
constant radius and the causal-seal proof (r_AH(t) − r_damp,max > 0) would have
nothing constant to compare against. With `lapse_start = 0` the test `lapse <
lapse_start` is false for every physical lapse (floored at 1e-10), the lapse
branch never fires, and r_damp,max is exactly 0.95 by construction.

**Why it restarts from Chk04000 (t = 40), not Chk05000 (t = 50).** Chk05000 carries
r04000's lapse-window damping through the collapse at t = 44–47 — the very burst
M7 is meant to record. Restarting at t = 40 undamped, with the radius window gated
to t = 51.2, gives a clean collapse *and* a sealed core afterwards. Cost is 11
extra code units, ≈ 36 min.

Launched exactly as the validation run above, with `params_m4_sealed.txt`,
`WHM_NAME=m4_sealed` and the same F12 consumer arguments. Verified detached
(ppid = 1, session leader), restarting from Chk04000, first row t = 40.02 with
separation 9.2280144126e-01 — identical to r03000 and to the validation run.
Pass criterion: alive and NaN-free past t = 56; it runs to stop_time = 66, which
also delivers M7's R = 14 record if it survives.

The campaign prune sweep does not touch this run: its guard requires
`$CAMPAIGN/<name>` to exist, and `merger_fix` runs live one level deeper. That
also means nothing was pruning them, so a second sweep scoped to `merger_fix`
with `KEEP_OTHER=1` runs alongside this run and keeps only its newest
checkpoint. It exits when the run does. This is the stop-gap; the permanent fix
is `checkpoint_keep` below, which this run is too old to have.

## Checkpoint retention (`checkpoint_keep`) — added 2026-09-01

A checkpoint here is 9.7 GB and this run writes one every 5 code units, so a
clean pass to t = 66 would leave ~50 GB of state nobody restarts from. New
parameter, default 0 = keep every one (nothing archived changes):

```
checkpoint_keep = 1     # keep only the newest; 2 is the cautious setting
```

`GRAMR::checkPoint()` writes the checkpoint through AMReX as before, then calls
`CheckpointRetention::prune()` (own header, `Source/GRTeclynCore/`). Because the
prune runs *after* the write returns, a run killed mid-write never reaches the
delete and still has its previous checkpoint — which is why keeping one is safe
here. Two more guards: a directory is a candidate only if it contains a
`Header` (never half-deletes one being written), and the checkpoint the run was
restarted from is never deleted. Scope is the run's own `amr.check_file`
prefix, so a co-tenant's checkpoints on the same scratch disk are not
candidates.

**Verified end to end**, not just built: `ckptkeep_smoke` (GPU 1, 32³ single
level, `checkpoint_interval = 2`, `checkpoint_keep = 1`,
`templates/params_ckptkeep_smoke.txt`) wrote eight checkpoints and deleted seven,
each one immediately after its successor was complete:

```
CHECKPOINT: file = .../BinaryWormholeChk00002
[checkpoint_keep] removed .../BinaryWormholeChk00000 (keeping newest 1)
```

One checkpoint on disk at the end (Chk00015). Its `run.log` is the evidence;
the scratch was deleted afterwards.

Set in `templates/params_m4_sealed.txt`; it takes effect on the next launch.
The live run keeps the binary it started with, preserved as
`main3d.gnu.MPI.CUDA.ex.pre_ckptkeep` (renaming keeps the running inode;
linking over it would fail with ETXTBSY).

Scratch cleanup at the same time: `merge_orbit_flip_d12_r04000/…Chk05000`
(t = 50, 9.7 GB) deleted — it carries the lapse-window damping through the
collapse, so no step of the plan restarts from it, and that arm's streams are
already packed in `results/merger/campaign/merge_orbit_flip_d12_r04000`.
`merge_orbit_flip_d12_r03000/…Chk04000` (t = 40) is kept: it is the parent of
M4 and of any M4b/M5 relaunch.

### m4_sealed result — FAIL, and the failure is the measurement (2026-09-01)

Died `NaN in GRAMRLevel::post_timestep`, component **h11**, level 3, at
**t = 51.6925** — 0.015 units before the undamped validation death (51.7075).
The certified seal bought zero time. The damping itself engaged and worked
where it reached: `collapse_diagnostics.dat` shows |phi|max falling
0.82 → 0.57 at exactly t = 51.2, then stalling (two e-folding times at
tau = 0.25 for 1.5x total decay), while |Pi|max grew 0.64 → 0.74 to the end.
The surviving driver sits where the window weight is small or zero — the ring
r ≈ 0.95–1.3. In-code scan near death: r_AH 1.0625 (51.5) → 1.0000
(51.65–51.69), the contraction accelerating ≈ 8× over its birth rate. Offline
scan on this run's own Plt05050/05100/05150 before pruning them: shells
1.110 / 1.090 / 1.070 at 50.5 / 51.0 / 51.5 — identical to the validation
run's curve, 0.7 % from the in-code scan; rays trapped only 27–30 %, shell
mean radius 1.63, equator max 2.3 (strongly aspherical). No NaN pollution in
the final stream rows. Death analysis: two sources per claim (in-code scan +
offline scan; run.log abort + stream tails).

## m4b sweep — four arms, four GPUs (launched 2026-09-01)

All restart from `m4_sealed_r04000/BinaryWormholeChk05000` (t = 50 — clean:
that run's damping never fired before its 51.2 gate), engage damping at
t = 50.0 (certification-gating is measured too late; publishability comes
back through M6 overlap instead), **checkpoints off** (`checkpoint_interval
= -1`, per request), stop_time 66. Launched exactly as m4_sealed, one
template and GPU each:

| arm | GPU | template | window (full/zero) | tau |
|---|---|---|---|---|
| m4b_wide | 0 | `params_m4b_wide.txt` | radius 1.00 / 1.30 | 0.25 |
| m4b_combo | 1 | `params_m4b_combo.txt` | lapse 3e-2→1e-3 + radius 1.00 / 1.30 | 0.25 |
| m4b_fast | 2 | `params_m4b_fast.txt` | radius 1.00 / 1.30 | **0.05** |
| m4b_sledge | 3 | `params_m4b_sledge.txt` | radius 2.00 / 2.50 | 0.25 |

Verified at launch: all four detached (setsid, distinct launcher pids), all
four GPUs at ~98 %, first stream rows t = 50.07 bit-identical across arms.
Chk05000 (9.7 GB) is the sweep's restart parent and is kept until the sweep
concludes; M4's three death-window plotfiles (7.2 GB) were pruned after the
offline scan above was recorded.

### Wave-1 result (2026-09-01): rate is the control variable

| arm | died | NaN | verdict |
|---|---|---|---|
| m4b_wide | 51.94 | h11, L3 | ring window bought 0.25 units |
| m4b_combo | 51.94 | h11, L3 | identical to wide — lapse window added nothing |
| m4b_sledge | 51.91 | h11, L3 | whole-object window changed nothing — size falsified |
| m4b_fast | **52.42** | h11, L3 | tau 0.05 outlived every tau 0.25 arm and the undamped arm |

The three tau = 0.25 deaths are inside the 0.35-unit reproducibility scatter
of each other: window shape, size and lapse-selection are all irrelevant at
that rate.  The one arm that differed only in tau lived 0.5 units longer.
Frames from m4b_fast at t = 52.0 (0.4 before its death) image the mechanism:
phi cleaned white inside r ~ 1 with saturated crescents pinned at the window
edge, wrong-sign K pockets (K ~ -0.07) wrapped around the bar ends at
r ~ 1-2 exactly where the crescents sit (the rw re-inflation loop,
photographed), and Weyl4 showing the whirling bar radiating a clean
quadrupole spiral -- the collapse signature is emitted and in flight.

## m4b wave 2 -- rate pushed and crossed (launched 2026-09-01)

Same restart (m4_sealed Chk05000, t = 50), same engagement (t = 50.0), same
checkpoints-off, same consumer args; three arms on the freed GPUs:

| arm | GPU | template | window (full/zero) | tau |
|---|---|---|---|---|
| m4b2_vfast | 0 | `params_m4b2_vfast.txt` | radius 1.00 / 1.30 | **0.02** |
| m4b2_fastsledge | 1 | `params_m4b2_fastsledge.txt` | radius 2.00 / 2.50 | 0.05 |
| m4b2_fastcombo | 3 | `params_m4b2_fastcombo.txt` | lapse 3e-2→1e-3 + radius 1.00 / 1.30 | 0.05 |

If all three die at ~52-53, post-collapse matter surgery is falsified across
the whole (window, rate) plane and wave 3 goes at the gauge: freeze the lapse
in the damping zone (targets the imaged K-pockets directly), and/or damp
*through* the collapse from r03000's Chk04000 -- which is how rw actually got
to 55.00 (its restart parent had been lapse-damped from t = 40 on, through
the collapse; publishability then rests on the M6 overlap over the burst).

**RESULT (2026-09-01): all three dead within 8 minutes -- the plane is
exhausted.**

| arm | died | NaN | reading |
|---|---|---|---|
| m4b2_vfast | 51.88 | **K**, level 3 | tau 0.02 gave back all of tau 0.05's gain and switched the death component: too-violent removal shocks the gauge itself |
| m4b2_fastsledge | **52.55** | h11, level 3 | nominal record among damped arms; +0.13 over fast is inside the +-0.35 scatter |
| m4b2_fastcombo | 52.42 | h11, level 3 | identical to fast -- lapse selection adds nothing at the winning rate |

Sources per arm: run.log NaN-diagnostic line + amrex Abort, and the final
clean rows of binary_throat_diagnostics.dat (no NaN pollution). GPUs verified
idle (0 MiB, 0 %) and no stray main3d/run_single processes after the wave.

Verdict: the rate axis is non-monotonic with its peak measured at tau ~= 0.05
(~51.9 at 0.25, 52.42 at 0.05, 51.88 at 0.02); coverage and lapse selection
are flat at every rate. Best achievable ~= 52.5 vs the t = 66 target. Wave 3
(gauge attack, per above) is designed in research/merger/Plan.md and awaits an
explicit go-ahead -- it needs new code (lapse-freeze flag) and/or a new
restart chain from Chk04000. Both restart parents are kept in scratch until
that decision: m4_sealed's Chk05000 (t = 50) and r03000's Chk04000 (t = 40).

## m4c wave 3a -- lapse-source taper (launched 2026-09-01, go-ahead given)

New module `Examples/BinaryWormholeMerger/CoreLapseFreeze.hpp` (default-off
flag `core_lapse_freeze`), built into a fresh binary (previous saved as
`main3d.gnu.MPI.CUDA.ex.pre_freeze`). It tapers the Bona-Masso SOURCE of the
lapse: d/dt alpha = advec - (1 - W(r)) * c * alpha^p * (K - 2 Theta), with
W a C^2 quintic smootherstep (full inside core_freeze_radius_full, zero at
core_freeze_radius_start, engaging at core_freeze_from_time).  Advection is
left intact so no lapse-vs-shift shear boundary forms; the add-back is
computed from the same solution array the gauge RHS read, so the
cancellation is term-exact.  `core_freeze_shift = 1` additionally scales the
shift and B RHS by (1 - W) -- the Gamma-driver guard, off unless stated.

Wave 3b (damp through the collapse from Chk04000) was VETOED before launch:
matter damping during t = 44-51.5 alters the stress-energy that sources the
burst, so it would fail the M6 overlap by construction.  The extraction
radius also stays at R = 14 (proposal to add a nearer sphere declined --
same radius; Psi4 comes off the plotfiles, where the radius is a post-hoc
choice anyway).

Same restart (m4_sealed Chk05000, t = 50), engagement t = 50.0, checkpoints
off, same consumer args; four arms:

| arm | GPU | template | matter damping | freeze (full/zero) | shift guard |
|---|---|---|---|---|---|
| m4c_freeze | 0 | `params_m4c_freeze.txt` | tau 0.05 ring | 1.00 / 1.30 | off |
| m4c_freezewide | 1 | `params_m4c_freezewide.txt` | tau 0.05 ring | 2.00 / 2.50 | off |
| m4c_freezeonly | 2 | `params_m4c_freezeonly.txt` | none | 2.00 / 2.50 | off |
| m4c_freezeshift | 3 | `params_m4c_freezeshift.txt` | tau 0.05 ring | 2.00 / 2.50 | on |

Read-out: freezeonly isolates the gauge fix (if it survives, the scalar was
never the killer); freeze vs freezewide tests whether the taper must cover
the imaged pockets (r ~ 1-2) or only the ring; freezeshift pre-deploys the
guard.  Every freeze arm is publishable only through the M6 overlap -- the
window is not strictly inside the trapped surface.

**First result: m4c_freezeshift died at t = 50.24 (NaN in K), 0.24 units
after engagement -- the fastest death on record.  The Gamma-driver guard is
fatal, not protective: scaling the shift/B RHS by (1 - W) strangles the
shift mid-collapse.  `core_freeze_shift` stays off everywhere.  GPU 3 free;
the three guard-less arms run on.**

**RESULT (2026-09-01): all four dead.  Gauge-source surgery falsified.**

| arm | died | NaN | reading |
|---|---|---|---|
| m4c_freezeshift | 50.24 | K | shift guard fatal in 0.24 units |
| m4c_freezewide | 52.03 | **h12** | first off-diagonal death; pocket coverage irrelevant |
| m4c_freeze | 52.04 | h11 | taper + matter < matter alone (fast 52.42): taper mildly harmful |
| m4c_freezeonly | **52.12** | h11 | == undamped baseline (r05000 52.09): slicing source is NOT the killer |

The -0.4 shift of freeze vs its exact matter-only twin (fast) proves the
taper engaged; freezeonly's dead-match with the undamped baseline proves
cancelling the Bona-Masso source changes nothing.  The K -> lapse
re-inflation loop is not the load-bearing mechanism -- h_ij blows up at the
bar ends regardless of the slicing source.

The t ~ 52 wall has now survived every interior intervention (resolution,
dissipation, matter deletion at every window and rate, slicing-source
cancellation, shift freezing).  Causal arithmetic: full burst at radius R
needs survival to ~ 51.5 + R; the all-time record 55.0 gives R ~ 3.5 --
near zone.  Remaining moves are formulation-level (true excision, another
slicing family) or the M8 pivot (publish the convergent wall).  All GPUs
verified idle; both scratch checkpoints kept pending the campaign decision.

## m4d wave 4 -- dt and sigma, the last interior knobs (launched 2026-09-01)

User-proposed dt_multiplier = 0.02 and sigma = 0.1 are ALREADY the campaign
baseline (checked in every template), so wave 4 tests the live directions:
dt lower (unmeasured axis) and sigma lower (the measured trend points down:
1.0 died 51.68, 0.1 died 52.09).  Same restart (Chk05000), engagement 50.0,
checkpoints off, same consumer args; four arms:

| arm | GPU | template | change | matter |
|---|---|---|---|---|
| m4d_dt001_fast | 0 | `params_m4d_dt001_fast.txt` | dt_multiplier 0.01 | tau 0.05 ring |
| m4d_dt001_plain | 1 | `params_m4d_dt001_plain.txt` | dt_multiplier 0.01 | none |
| m4d_dt0005_fast | 2 | `params_m4d_dt0005_fast.txt` | dt_multiplier 0.005 | tau 0.05 ring |
| m4d_sig002_fast | 3 | `params_m4d_sig002_fast.txt` | sigma 0.02 | tau 0.05 ring |

Wall ETA: dt001 arms run ~2x slower (wall at ~20 min), dt0005 ~4x slower
(~40 min), sig002 normal (~8-10 min).  If deaths land at 52.0-52.6 again,
the wall is timestep-independent and the interior-knob space is exhausted
in full.

RESULT (all four dead, all inside the wall band):

| arm | death | NaN | speed cu/h | twin | shift |
|---|---|---|---|---|---|
| m4d_dt001_plain | 52.261875 | h11 | 9.10 | undamped r05000 52.09 | +0.17 |
| m4d_sig002_fast | 52.26625 | h22 | 18.07 | m4b_fast 52.42 | -0.15 |
| m4d_dt001_fast | 52.06625 | h11 | 9.12 | m4b_fast 52.42 | -0.35 |
| m4d_dt0005_fast | 52.0253125 | K | 4.58 | m4b_fast 52.42 | -0.39 |

Reproducibility scatter is +-0.35, so NOTHING here is a signal.  dt001_plain
is the clean isolated dt measurement (halved dt, no other change): +0.17.
Quartering dt cost 4x the wall time and moved the death 0.39 EARLIER.  The
blowup is dt-converged -- refining the integrator reproduces it instead of
removing it, which is what a continuum/spatial feature looks like and what a
CFL instability does NOT look like.  Sigma is flat at the low end too.
Interior-knob space is exhausted in full.

Scratch: the four m4d dirs pruned after read-out (28 GB, plotfiles only --
diagnostics, frames and params live under runs/).  /tmp back to 20 GB: the
two restart checkpoints plus _cache.

## m4e wave 5 -- extra AMR levels ADDED ON RESTART (prepared 2026-09-01)

User's question: can we restart a checkpoint with a higher max_level?  Yes,
and it is the cheap version of the resolution ladder.  Verified in the AMReX
source before writing the templates:

  * Amr::restart takes the max_level >= mx_lev branch and fills dt_level,
    level_steps and level_count for every level above the checkpoint's; the
    new levels' Geometry comes from the inputs file (already built by
    InitAmr), and n_cycle is set to the ref_ratio, so dt_level[4] =
    dt_level[3]/2 is well defined.  Sub-cycling is on, so the
    "same dt at all levels" error check is skipped.
  * checkInput has no level-dependent obstacle here: blocking_factor 16 is a
    power of 2, max_grid_size 32 is even and divisible by it, N = 128 is
    divisible by 16, ref_ratio 2 everywhere.
  * GRTeclyn reads regrid_interval with getarr(..., 0, max_level), i.e. it
    needs max_level entries -- the baseline's four are enough for max_level 4
    but NOT for 5, so the templates carry six.
  * The tagger is geometric, not threshold-based (tagging_type = 2,
    FixedGridsTagger half-width L*2^-(l+2) about each tracked throat), so the
    new level materialises deterministically at the first level-3 regrid --
    within regrid_int[3] = 16 level-3 steps = 0.01 code units of the restart.

Box arithmetic with L = 64: tagging on level 3 gives a level-4 cube of
half-width 2 at dx = 0.03125; tagging on level 4 gives a level-5 cube of
half-width 1 at dx = 0.015625.  Half-width 2 lands exactly on the r ~ 1-2
bar ends where h11/h22/K blow up.  Both boxes are 128 cells across, so
blocking factor and proper nesting are satisfied with room to spare.

| arm | template | max_level | finest dx | matter |
|---|---|---|---|---|
| m4e_lvl4_plain | `params_m4e_lvl4_plain.txt` | 4 | 0.03125 | none |
| m4e_lvl4_fast | `params_m4e_lvl4_fast.txt` | 4 | 0.03125 | tau 0.05 ring |
| m4e_lvl5_plain | `params_m4e_lvl5_plain.txt` | 5 | 0.015625 | none |

Same restart (Chk05000, t = 50), stop_time 66, checkpoints off, same
consumer args.  Cost: cell-updates per unit time scale as N_cells * 2^l, so
level 4 alone costs about 2x what level 3 costs and level 5 about 4x --
expect roughly 9 cu/h for the lvl4 arms and 4 cu/h for lvl5, i.e. ~20 min
and ~45 min to reach the wall.  Cheap enough to run all three at once.

Read-out: m4e_lvl4_plain against undamped r05000 (52.09) is the clean
measurement -- same physics, same dt, twice the resolution where the shock
forms.  Compare the gain against n160's +1.55, which bought only 1.25x
refinement AND paid the 1/dx^2 initial-data noise penalty.

LAUNCHED 2026-09-01 on GPUs 0/1/2, detached (setsid, launcher ppid = 1),
restart Chk05000, same command shape as the wave-4 block above.

Verified at launch -- the mechanism works exactly as the source said:

  * all three restarted cleanly from a max_level = 3 checkpoint (restart
    read ~4.1-4.2 s), no abort, no parameter complaint;
  * "Level 4 step" lines appear on all three arms and "Level 5 step" on
    m4e_lvl5_plain, i.e. the extra levels really were created from the
    geometric tagger within a hair of the restart, not merely declared;
  * speed 5.4-5.8 code units/h for the lvl4 arms (about 3x the baseline
    cost, close to the predicted 2x) and 3.7 for lvl5 (about 5x).

Wall ETA from t = 50: ~27 min for the lvl4 arms, ~40 min for lvl5.  Monitor
bfsgk74p4 (persistent) emits one TERMINAL line per arm plus WAVE5_ALL_DONE.

### wave 5 results, first two arms

| arm | died | NaN in | on level | its twin | shift |
|---|---|---|---|---|---|
| m4e_lvl4_plain | **53.0956** | h11 | 4 (the new one) | undamped `r05000` 52.09 | **+1.01** |
| m4e_lvl4_fast | **53.7538** | h11 | 4 (the new one) | `m4b_fast` 52.42 | **+1.33** |

The resolution axis is REAL: both shifts clear the +-0.35 reproducibility
scatter by a wide margin, and they are the first knob in the whole campaign
to do so.  Two further facts matter more than the sign:

  * the NaN MOVED ONTO the newly created finest level in both arms.  The
    failure sharpens into the fine grid instead of being smoothed away by
    it -- the signature of a feature the solution actually has, not of an
    under-resolved artefact.
  * refinement and matter deletion STACK better than additively: deletion
    alone bought +0.33 (52.09 -> 52.42), one extra level alone bought +1.01,
    and the two together bought +1.66 (52.09 -> 53.75).

Exchange rate: about one code unit of survival per factor-of-two in grid
spacing at the failure site.  Reaching the extraction window at t = 66 needs
+14 from the undamped baseline, i.e. of order 2^14 refinement.  Open axis,
hopeless slope -- unless the ladder is super-linear, which is exactly what
the lvl5 and lvl6 arms measure.

## m4e wave 5b -- the missing corner of the square (launched 2026-09-01)

Wave 5 ran three of the four (level x damping) cells and PREDICTED the
fourth from the wave-4 estimate that deletion is worth +0.33 on its own.
The measured stacking above falsifies that prediction, so the corner had to
be measured.  User asked for max_level 6 as well; the six regrid_interval
entries already in the wave-5 templates are exactly enough for it (GRTeclyn
reads max_level entries), and the geometric tagger gives a level-6 cube of
half-width 0.5 at dx = 0.0078125 -- still 128 cells across, so blocking
factor and proper nesting hold with the same room to spare as before.

| arm | GPU | template | max_level | finest dx | matter |
|---|---|---|---|---|---|
| m4e_lvl5_fast | 0 | `params_m4e_lvl5_fast.txt` | 5 | 0.015625 | tau 0.05 ring |
| m4e_lvl6_fast | 3 | `params_m4e_lvl6_fast.txt` | 6 | 0.0078125 | tau 0.05 ring |

Templates built by lifting the M4b FAST block verbatim into the lvl5 plain
template, then bumping max_level for the lvl6 copy; verified afterwards that
each differs from its parent ONLY in the intended lines.  Same restart
(Chk05000, t = 50), stop_time 66, checkpoints off, same consumer args.

Verified at launch: both restarted cleanly from the max_level = 3 checkpoint,
no abort; m4e_lvl5_fast at 3.8 code units/h with level 5 live, and
m4e_lvl6_fast reached "Level 6 step" within a hair of the restart, so the
mechanism carries three levels above the checkpoint, not just one.

Read-out: the damped ladder is now four points -- 52.42 (lvl3), 53.75
(lvl4), lvl5, lvl6.  Linear in doublings confirms the hopeless-slope
reading and closes resolution as a cure; super-linear would reopen it.

Monitor b795b060w (persistent): LEVEL6 line, one TERMINAL per arm,
WAVE5B_ALL_DONE.

### wave 5 result: the undamped ladder is SUPER-LINEAR

| level | finest dx | died | NaN in | on level | gain over previous rung |
|---|---|---|---|---|---|
| 3 (baseline `r05000`) | 0.0625 | 52.09 | h11 | 3 | -- |
| 4 (`m4e_lvl4_plain`) | 0.03125 | 53.10 | h11 | 4 | **+1.01** |
| 5 (`m4e_lvl5_plain`) | 0.015625 | **55.60** | h11 | 5 | **+2.50** |

m4e_lvl5_plain is the campaign's ALL-TIME SURVIVAL RECORD and the first
record that is clean: no matter damping anywhere in the run, nothing altered
but the grid.  The previous record (rw, 55.00) damped through the collapse
that sources the burst and is waveform-tainted; this one is not.

Three facts, in order of importance:

  * **Each doubling buys ~2.5x what the last one bought** (+1.01 then +2.50).
    This inverts the morning's conclusion.  Refinement is not a runway-buyer
    priced out of reach -- it is a candidate CURE.  Two-point ratio 2.48
    projects level 6 to ~61.8 and level 7 to ~77.2; both are extrapolations
    from two increments and must be measured, not believed.
  * **The NaN moved onto level 5**, the newest finest level, exactly as it
    moved onto level 4 before.  The physical reading is unchanged -- the
    shock is a real feature that sharpens into whatever grid resolves it --
    but it is now being OUTRUN by refinement rather than merely delayed.
  * The damped ladder is behind but tracking: m4e_lvl5_fast passed its own
    lvl4 twin's 53.75 and is still running at the time of writing.

## m4e wave 6 -- level 7 undamped (launched 2026-09-01, user go-ahead)

Card 2 freed by the lvl5_plain death; launched immediately rather than
waiting ~5 h for the level-6 verdict, because if the trend holds this is the
arm that actually reaches the signal.

| arm | GPU | template | max_level | finest dx | matter |
|---|---|---|---|---|---|
| m4e_lvl7_plain | 2 | `params_m4e_lvl7_plain.txt` | 7 | 0.00390625 | none |

Template built from the lvl6 plain copy; regrid_interval extended to SEVEN
entries (GRTeclyn reads max_level entries -- six would have aborted).  The
geometric tagger gives a level-7 cube of half-width 0.25, still 128 cells
across, so blocking factor and nesting hold as at every other rung.

**Binary: `main3d.gnu.MPI.CUDA.ex.pre_fill`** -- deliberately the SAME binary
every other rung of the ladder ran on.  The production binary is mid-rebuild
with the new default-off CoreFreezeFill module; using the old one keeps the
ladder a single-variable experiment and costs nothing.

Cost: expect ~1 code unit/h and ~59 GB of card memory (measured 52 GB at
level 6, ~7 GB per level).  From t = 50 to the projected wall ~62 is ~12 h;
to stop_time 66 is ~16 h.

Monitor bvcaqso7b (persistent): LEVEL7 creation line, then TERMINAL.

### wave 5b result: the damped ladder decelerates, and damping crosses over

| level | undamped | damped | damping's effect |
|---|---|---|---|
| 3 | 52.09 | 52.42 | **+0.33** |
| 4 | 53.10 | 53.75 | **+0.65** |
| 5 | **55.60** | 54.76 | **-0.84** |

m4e_lvl5_fast died 54.763125, NaN h11 on level 5.  Damped increments +1.33
then +1.01 (decelerating) against undamped +1.01 then +2.50 (accelerating).
Matter deletion was compensating for an under-resolved region; once the grid
resolves it, the deletion is an unphysical perturbation that costs time.
The clean no-surgery route wins outright -- and needs no M6 overlap caveat.

### box-coverage caveat found while sizing the next launch

The tagger's boxes are 160^3 cells at EVERY level (125 grids of 32^3), so
their half-widths halve as levels are added:

  level 3 -> 5.0    level 5 -> 1.25    level 7 -> 0.3125
  level 4 -> 2.5    level 6 -> 0.625   level 8 -> 0.15625

The imaged blowup ring is at r ~ 1-2.  So in the lvl6/lvl7 runs the finest
grid AT r ~ 1 is still level 5's dx = 0.015625 -- the same as the lvl5 run.
Adding levels 6+ refines only the deep interior.

Sharp prediction, decided by the running lvl6_plain: dies near 55.6 (same as
lvl5_plain) => the failure sits at r ~ 1, the ladder is finished, and the
next axis is WIDER fine boxes (a tagger change), not deeper ones.  Dies near
the super-linear projection ~62 => the failure is genuinely inside r = 0.625
and deeper levels keep paying.

**Level 8 is on hold until lvl6_plain reports** -- it would refine r < 0.16.

### memory measured across the ladder (81559 MiB cards)

  level 5: 43895 MiB    level 6: 51903 MiB    level 7: 57479 MiB

~6-8 GB per added level (each new level is the same 160^3 box), so the card
ceiling is ~level 9-10, not 8-9 as first estimated.  Host RAM 3 of 976 GB.
Scratch steady at 68 GB (keep-last-3 bounds it); disk 619 GB of 1.8 TB.

---

## Level 6 verdict (2026-09-01): the ladder saturates

`m4e_lvl6_plain_r05000` — **NaN t = 56.13484375**, `rank=0 level=6 component=1
name=h11`, aborted in `GRAMRLevel::post_timestep`, immediately after a
`REGRID with lbase = 4`.

Clean ladder, all four rungs from the same Chk05000 parent, same binary
(`main3d.gnu.MPI.CUDA.ex.pre_fill`), one variable changed:

| level | dx | death | gain |
| --- | --- | --- | --- |
| 3 | 0.0625     | 52.09     | — |
| 4 | 0.03125    | 53.10     | +1.01 |
| 5 | 0.015625   | 55.60     | +2.50 |
| 6 | 0.0078125  | **56.13** | +0.53 |

The super-linear projection made from the first three rungs (level 6 ≈ 61.8,
level 7 ≈ 77.2) is falsified by 5.7 units. The sequence is saturating toward
t ≈ 56. Level 5 was the outlier.

**The box-coverage prediction, recorded before the result, was right.** Fine
boxes are 160^3 cells at every level, so half-widths halve per level (level 6
reaches r = 0.625) while the imaged blowup ring sits at r ~ 1-2. Adding levels
refines a ball the failure has already left. Level 8 stays cancelled.

**Damping's sign flips back.** `m4e_lvl6_fast` was still running past 56.18 when
its undamped twin died at 56.13, so the level-5 "damping costs 0.84" crossover
does not repeat. Series: +0.33, +0.65, -0.84, >=+0.05 against a +-0.35
reproducibility floor. Read it as zero, not as a trend.

**Consequences.** Level 7 is now a ~20 h confirmation of the asymptote (projected
~56.3), not a route to the signal — flagged to the user as a candidate to stop
and reassign. M9b (CoreFreezeFill, built and verified, default-off) is promoted
from insurance to the primary route. The surviving refinement idea is *wider*
fine boxes at r ~ 1-2 (a tagger change, parked as M4f), not deeper ones.

Ladder waveform figure regenerated with the level-6 stream:
`runs/wormhole_merger/merger_fix/plots/ladder_psi4_R14_lvl6.png`. Gap to the
start of the target window across the ladder: 6.50 -> 5.00 -> 2.50 -> **2.00**.

### ...and 34 minutes later the damped arm overturned it

`m4e_lvl6_fast_r05000` — **NaN t = 56.7065625**, same signature (`level=6
component=1 name=h11`). That is +1.95 over its level-5 sibling: its own largest
gain, while the clean arm had just posted its smallest.

Both single-arm readings were wrong. Arm-pair means:

| level | clean | damped | mean | gain |
| --- | --- | --- | --- | --- |
| 3 | 52.09 | 52.42 | 52.26 | — |
| 4 | 53.10 | 53.75 | 53.43 | +1.17 |
| 5 | 55.60 | 54.76 | 55.18 | +1.76 |
| 6 | 56.13 | 56.71 | 56.42 | +1.24 |

Least squares over the four rungs: **+1.425 per level**, increments scattering by
+-0.3 — the reproducibility floor. Projections: level 7 = 57.88, level 8 = 59.31,
level 9 = 60.73. Window start (58) at level 7.1; window end (66) at level 12.7,
against a memory ceiling near level 9-10 (level 7 measured 57.5 GB of 81.5).

Damping by level: +0.33, +0.65, -0.84, +0.58 — mean +0.18, signs alternating,
against a +-0.35 floor. Zero. The level-5 crossover is withdrawn.

**Three laws in one day from four levels** — super-linear (from clean L5),
saturating (from clean L6), accelerating (from damped L6) — each falsified within
hours. Recorded in Plan.md's traps table: never extrapolate a ladder increment
from one arm.

**Level 7 recommendation reversed.** Under saturation it was a 20 h confirmation
worth stopping; under the linear fit it discriminates 57.9 from 56.3 and would be
the first arm to touch the window start. Left running.

## m9b wave 6 -- the smooth interior fill, first two arms (launched 2026-09-01)

User's call after reading the ladder: refinement "bought some time but it won't
be enough and this approach is a dead end -- we need to isolate the violent part
properly to make it to t = 64".  Correct on the arithmetic: +1.43/level reaches
t = 64 at level ~12 against a memory ceiling near 9.  M9b is promoted from
insurance to the route.

Both templates are `params_m4e_lvl5_plain.txt` plus one four-line block; verified
by diff that they differ from the parent ONLY in that block, and from each other
ONLY in the two radii.

| arm | GPU | radius_full | radius_start | from_time | contamination reaches R = 14 |
| --- | --- | --- | --- | --- | --- |
| m9b_fill | 1 | 1.3 | 1.8 | 53.0 | 53 + (14 - 1.8) = **65.2** |
| m9b_fillwide | 3 | 1.5 | 2.0 | 53.0 | 53 + (14 - 2.0) = **65.0** |

Target window is 58-65.5, so both keep the collapse arrival (58-61) clean by
~4 units and the whole window clean bar its last few tenths.

WHY max_level 5 AND NOT 3, since the core is frozen anyway (asked at launch).
The freeze cannot help a run that dies before it engages: level 3 dies at
52.09/52.42, i.e. ~0.8 BEFORE t = 53; level 4 at 53.10/53.75 is inside the
+-0.35 floor of the engagement time, a coin flip.  Level 5 (55.60/54.76) clears
it by ~2 units.  Refinement is no longer buying signal -- it is buying the
survival needed to reach the switch-on, plus margin.

Engaging EARLIER to let a coarse grid reach it fails twice: the collapse is
still sourcing the burst until 51.5 (freezing before that deletes signal), and
engaging at 51.5 puts contamination at R = 14 at 63.7, inside the window.

Real saving available later, and it is the user's point in the right place: once
the fill is proven the frozen core no longer needs fine cells, yet the geometric
tagger keeps refining it.  Moving the fine boxes off the dead zone is worth ~3x
speed and costs nothing physically -- build it AFTER these arms show the freeze
holds.

Watch t = 53.0-53.5: CoreLapseFreeze's partial freeze died 0.24 units after
switch-on, so the blend zone fails fast if it fails.  Past 55.6 is new ground.

Monitor bedwx0b4o (persistent): ENGAGED-OK, PAST-RECORD, one TERMINAL per arm,
M9B_ALL_DONE.

## m9b wave 7 -- the freeze arms extended to t = 80 (launched 2026-09-01)

The t = 66 arms COMPLETED -- first runs in campaign history to reach their stop
time.  Both hit t = 66.0 with zero NaN; the R = 14 window 58-65.5 is on disk in
full.  The waveform is bit-identical between the two skins and bit-identical to
the unfrozen level-5/6/7 arms over every shared time, so the fill is invisible
at the detector, as the causal budget said it must be.  What the window shows,
though, is a smooth decaying tail, not a distinct burst -- either the phantom
dissolution radiates no sharp feature, or the arrival estimate is off.  Hence:

**User: "we need to run this for longer / 65 is too early / relaunch for t = 80"**
(explicit "yes launch" given for the detached pair).

Why 80 is the right number: the R = 30 sphere sees the collapse over
t = 73-80.5, and freeze contamination cannot reach R = 30 until
53 + (30 - 2.0) = 81.0 at the earliest (wide skin).  So the outer detector
gives a SECOND, fully causally-clean measurement at an independent radius --
the cross-check R = 14 cannot give itself.

No checkpoints existed from the t = 66 pair (checkpoint_interval = -1), so
these restart from the same Chk05000 parent and re-run the whole span:

| run | template | gpu | skin (full/start) | stop | new vs t=66 twin |
| --- | --- | --- | --- | --- | --- |
| m9b_fill80_r05000 | params_m9b_fill80.txt | 0 | 1.3 / 1.8 | 80.0 | stop_time, checkpoint_interval 1000, checkpoint_keep 1 |
| m9b_fillwide80_r05000 | params_m9b_fillwide80.txt | 1 | 1.5 / 2.0 | 80.0 | same three lines |

Verified by diff: each new template differs from its completed t = 66 parent in
exactly those three settings, and the two new twins differ from each other in
exactly the two radii.  checkpoint_keep = 1 is the in-binary rolling retention
committed this morning (ad9b18a5, CheckpointRetention.hpp): prunes only after
the new checkpoint is complete, never touches the restart parent, scoped to
this run's own prefix -- so /tmp stays clean without any sidecar.  (A duplicate
shell pruner was started and deleted when the user pointed back at the commit.)

Launched detached via launch_m9b80.sh (user's explicit permission), restart
parent /tmp scratch m4_sealed_r04000/Chk05000.  Both verified up: restart line
in run.log, checkpoint_keep/core_freeze_fill/stop_time all echoed in
parameters_and_version.txt, cards 0-1 at 98 %.  ETA at ~4.3 cu/h: ~16:00-16:30.

Watchpoints (monitor blsus2490): freeze switch-on 53.0-53.5 (fast-failure
window), 56.9 = past every unfrozen death, 73.0 = R30 window opens, 80 = done.

Also today, closing the ladder: m4e_lvl7_plain died at 56.20 (h11, level 7) --
BELOW level 6's 56.71.  The ladder turned over; linear extrapolation is dead
along with the saturating one.  Refinement is finished as a route, exactly as
the user called it.  And m4e_lvl5_dt001 died at 55.96 vs the 55.60 full-dt
twin: +0.36 on a +/-0.35 floor = no effect; the wall is dt-converged at depth.

## m9b wave 7b -- the late-freeze control (launched 2026-09-01)

**The user's physics worry, verbatim intent:** the current signal is just the
spiral; in black-hole physics most of the energy is released at merger, so the
freeze at t = 53 might be blocking the most violent event.  The causal answer
(window 58-65.2 carries the TRUE core history through t = 53.2; output had been
falling for ten units when we froze) does not close the case for source times
PAST 53.  This arm does, by measurement.

**Design: one variable = the freeze time.**  `m9b_late6_r05000`, card 2.
Template params_m9b_late6.txt diffs against the running fill80 arm in exactly
two physics lines: max_level 6 (the grid must survive unfrozen to the later
engagement -- level 5 dies at 55.2 +/- 0.35, so 55.5 needs level 6, whose
unfrozen deaths are 56.13/56.71) and core_fill_from_time 55.5.  Same skin
1.3/1.8, same stop 80, same rolling checkpoint retention (keep 1).

**The test:** 2.5 more units of real core history reach the detector.  If the
58-65 waveform matches the from_time=53 arms, nothing radiative was being cut
through source-time 55.5 and the decaying tail is the genuine collapse
signature.  If it moves, the user was right and we chase engagement later on
finer grids.  Causal windows for this arm: R = 14 clean to 55.5 + 12.2 = 67.7;
R = 30 clean to 55.5 + 28.2 = 83.7 > 80, so the outer window 73-80.5 is clean
here too.

Verified up: restart from Chk05000, all four key params echoed
(max_level 6, from_time 55.5, keep 1, stop 80), card 2 at 99 %.  Level-6 speed
~2 cu/h -> t = 80 in roughly 14 h (early tomorrow).  Watchpoints (monitor
bhkekfri9): 56.1 = engagement survived, 57.1 = past both unfrozen level-6
deaths, 65.6 = R14 window complete, 73 = R30 window opens.

## Wave 8 (2026-09-01, ~21:30): continue both freeze arms to t = 100

**Why.**  Wave 7's completed t = 80 arms measured the propagation speed:
R = 30 lags R = 14 by 18.0 over 16 coordinate units (correlation 0.9998),
i.e. 1.125x slower than coordinate light.  Rerunning the arrival arithmetic
with the measured speed moves the R = 30 collapse window from the assumed
73-80.5 to 76.1-83.6 -- so stop 80 cut off the outer window ~4 units early.
The waveform itself also demands more time: with data to 80 the R = 14 signal
passes through a node at t ~ 66 and rises to a SECOND PEAK at ~ 75, which, if
real, must reappear at R = 30 near t ~ 93 with 1/R amplitude.

**How.**  `m9b_fill100_r08000` (card 0) and `m9b_fillwide100_r08000` (card 1),
restarted from each arm's rolling-retention survivor Chk08000 (verified valid,
t = 80.000 exactly, both restarts clean).  Template diff against the 80
templates: stop_time 80 -> 100, nothing else.  Same rolling checkpoint
retention (keep 1) -- verified live on wave 7: 5 prunes logged per arm,
exactly one Chk held at all times, restart parent never touched.

**Caveats recorded.**  (1) R = 30 sits INSIDE the sponge layer (ramps 24->32;
~13x base dissipation at r = 30): timing and shape only, no absolute
amplitudes.  (2) The R = 30 tail past 84.5 and the R = 14 data past 66.5 are
outside the causal freeze-contamination ceilings; the seam-radius twins and
the late6 engagement-shift test are the contamination discriminators there.

**Watchpoints:** 83.6 = R30 collapse window complete, 93 = second-peak arrival
at R30, 100 = stop.
