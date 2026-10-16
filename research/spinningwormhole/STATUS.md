# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

**Folders** (decided 2026-10-13; no flat folders): `runs/spinning_wormhole/<family>/<NN_study>/`
mirrors `results/spinningwormhole/campaign/<family>/<NN_study>/`; a triplet sits in a per-spin
folder; superseded runs go to `<family>/00_archive/`. Shared: `backgrounds/ bin/ logs/
manifests/ smoke/ templates/`. Now:
- `drainhole/`: `01_static_hold/`, `02_spin_hold/` (the O(J²) holds), `03_t0_checks/`
  (v_e 0.5, N 96/128/192), `04_fast_spin_hold/` (v_e 0.5, 0.7, J = 1);
- `symmetric_massless/`: `00_archive/L64_A1_superseded/`, `01_t0_checks/L64_ladder/` (the
  morning's v_e 0.5–0.99 checks) and `01_t0_checks/L128_A1/<spin>/` (A1: N 128/192/256
  per spin), `03_spin_hold/<spin>/` (the A3 holds; the probes first).

Launch through `logs/queue_worker.sh <gpu> logs/spin_queue.txt` (each line: template, name,
target folder, fg|bg) or `launch.sh --subdir <family>/<NN_study>[/<spin>]`; pack with
`pack_run.sh <family>/<NN_study> <run dir>`.

## FINAL PAPER-RUN SETTINGS (decided 2026-10-16; template = the L64 0.5c drive run)

Confirmed if the GPU 1 template run lands clean at t = 150 (≈ 13:40 UTC 10-16):
- **Grid**: L = 64, N = 128 base, max_level 3 (dx 0.5 → 0.0625), sponge 24–32
- **dt_multiplier = 0.02** (the ladder closed: 0.035 and 0.05 die on L128 spin data)
- **σ = 0.1 at every spin** (σ 0.4 kills the spin far-side puncture at any dt)
- **min_chi**: 1e-8 up to 0.5c; **1e-4 for the fast spinners** (0.7c+ — the far-side
  rescue floor is the enabler there, proven on 0.7c to t = 100)
- **sponge_drive_strength = 1.0** (physics-neutral absorber; makes L64 viable past t ≈ 64)
- **stop_time = 85** (decided 2026-10-16): the quotable window dies at the interface-mode
  knee (~75–85, box-independent: B1 Ham ×2 at 78.8, the L64 parent at 84.5; the drive run
  tracks the parent to 1 % through t = 72, so the growth is interior, not the echo) —
  stop just past it, bracket the ×2 point for the trust row. **2–3 L64 runs per card**
  (~25 GB each) is the campaign throughput. A σ 0.2 probe (untested middle filter) may yet
  move the knee — pending its go.
- **ψ4 radii 14, 18** (both outside the drive shell; 30 = in-shell reference only)
- spdrv binary, full frame set, no checkpoints, consumer keep-last 3; movies and quotes
  cut at each run's trust window
- Stable (non-collapsing) spins radiate nothing (checked 0.5c/0.7c: ψ4 deviations at the
  noise floor, no R = 14 → 30 propagation); the two-radius check matters for collapsing arms

## LIVE

**σ adoption check `spin_hold_L128_ml3_ve050a_sig04_t100` DIED t = 46.47
(NaN in post_timestep), ~08:10 UTC 10-16 — σ 0.4 FAILS on L128 spin data
even at dt 0.02. The speed-up program on the L128 spin holds is CLOSED:
production stays σ 0.1 + dt 0.02.** One knob vs B1 (σ 0.1 → 0.4, dt
kept): χ_min followed B1's 1.5e-6 track to t ≈ 15, decayed and hit the
1e-8 floor at t = 22.34 — within 0.05 units of the dt 0.035 arm (22.3)
and ~2 of dt 0.05 (~20). The floor-hit time is set by σ, not dt: the
stronger filter itself kills the far-side puncture sector (B1 at σ 0.1
holds 1.5e-6 to t = 100); the L64 static-ladder pass and the σ-kick
head-to-head (static data) do not transfer. Runs on the min_chi 1e-4
rescue floor are unaffected so far (the 0.9c hold below: χ_min rising,
2.9e-4 at t = 33). max|K| 0.44 → 52.6 in the final steps. Packed,
registry + trust rows written, scratch pruned, 2026-10-16 ~08:45 UTC.
Both first-node cards now carry two runs each (~50 GB/card).

**dt 0.05 + σ 0.2 probe `spin_hold_L64_ml3_ve050a_spdrv1_sig02_dt005_t100`
STOPPED BY HAND t = 44.5 (no NaN), ~12:05 UTC 10-16 — FAILS the puncture
discriminator.** χ_min on the healthy 1.5e-6 track to t ≈ 20, then monotone
decay (4.9e-7 at t = 40, halving every ~5 units, floor extrapolates to
t ≈ 65–70) while Ham/Mom still sat flat at baseline: the σ 0.4 death in slow
motion — the filter kills the far-side puncture long before the constraints
feel it. Matches the static ladder's dt005_sig02 floor rung and the L128
dt005 σ04 death. dt 0.05 is dead at any production σ WITHOUT the rescue
floor; whether σ 0.2 alone kills is the dt 0.02 arm's verdict (t = 25–40
window ≈ 12:45–14:30 UTC). Packed, registry + trust rows written, scratch
pruned ~12:05 UTC. Its card-0 slot went to the one-recipe probe below.

**Prior rung for the record: `spin_hold_L128_ml3_ve050a_sig04_dt0035_t060`
FAILED the discriminator** — stopped by hand at t = 26.4, ~06:30 UTC
10-16; χ_min floored at t = 22.3, max|K| runaway 3e-3 → 9e-2 over
t = 20–26. Packed, registry row written, scratch pruned, ~06:40 UTC.

| **L64 long-run test** `spin_hold_L64_ml3_ve050a_spdrv1_t150` (`drainhole/07_sponge_fix/`; the packed L64 0.5c hold rerun with the damping sponge, stop_time 150 — does L64+drive stay clean past its old t = 64 window and the t ≈ 128 crossing? σ 0.1 kept for direct comparison to the parent through t = 100; psi4 R = 14 is the trusted sphere (R = 30 sits in the drive shell); per-level norms on; no checkpoints; spdrv binary; first attempt REFUSED — the packed params' scrubbed relative table path; absolute path fixed in the template) | first GPU node, card 1 | launched 05:10 UTC 10-16, t = 0 byte-identical to the parent (Ham 2.1412059709e-03); t = 76.0 at 09:32 | 150 | ~7.8 t/h shared (17.8 solo) | t = 150 ≈ 19:00 UTC 10-16 (recovers when the σ 0.2 probe ends) |
| **σ 0.2 probe** `spin_hold_L64_ml3_ve050a_spdrv1_sig02_t100` (`drainhole/06_dt_ladder/`; its go 2026-10-16 — the untested middle filter: does σ 0.2 spare the far-side puncture (0.4 kills it by t ≈ 22 at any dt) while slowing the interface-mode knee (Ham ×2 at 78–85 on every 0.5c hold at σ 0.1)? One knob vs the live σ 0.1 drive run, stop 100; second run on a shared card — both slow; no checkpoints; spdrv binary) | first GPU node, card 1 (shared with the t150 run) | launched ≈ 09:25 UTC 10-16, t = 0 byte-identical (Ham 2.1412059709e-03 — σ doesn't touch initial data); t = 1.0 at 09:32 | 100 | ~7.8 t/h shared | χ_min discriminator (t = 25) ≈ 12:45 UTC; t = 100 ≈ 22:15 UTC 10-16 |
| **ONE-RECIPE probe** `spin_hold_L64_ml3_ve050a_spdrv1_sig04_mc4_dt005_t100` (`drainhole/06_dt_ladder/`; its go 2026-10-16 — σ 0.4 + min_chi 1e-4 + dt 0.05 at 0.5c: every pair is proven (floor+σ0.4 holds the 0.9c flat to t = 92; dt005+σ04 clean on static data; the dead L128 2.5× package ran on the 1e-8 floor). If it survives past t ≈ 48, holds Ham/Mom flat past 85 AND matches the parent's ψ4/exotic-matter numbers at close-out, the whole campaign unifies on this recipe at every spin — stop 150, no 85 cap, 2.5× faster. Also the revived slow-end floor-validation rung; no checkpoints; spdrv binary) | first GPU node, card 0 (shared with the 0.99c) | launched ≈ 11:57 UTC 10-16, t = 0 byte-identical (Ham 2.1412059709e-03) | 100 | ~19.5 t/h shared | survives-t≈48 gate ≈ 14:25 UTC; t = 100 ≈ 17:05 UTC 10-16 |
| **Max-spin probe, 0.99c** `spin_hold_L64_ml3_ve099a_spdrv1_t150` (`drainhole/04_fast_spin_hold/`; its go 2026-10-16 — "what max c can we run": the top of the family-(a) catalogue, v_e 0.9899, J 16215, M_ADM 127.3, D 0.3396, areal R_e 254.7 at coordinate throat η ≈ 1.29; the final paper-run recipe — σ 0.1, dt 0.02, min_chi 1e-4, drive 1.0, stop 150; preflight t = 0 L2_Ham 1.47e-3, CLEANER than 0.9c's 6.3e-3 (the phantom shrinks toward extremality faster than the metric steepens); spdrv binary; no checkpoints. R = 18 APPENDED at t = 22: a wrong-flag-order restart_consumer call killed the consumer ~11:44, hand-rebuilt ~11:50 with --radii 14 18 30, no row gap — but psi4_mode_l2_all/l2m0 rows before t = 22 carry R = 14/30 only and the header still names 2 radii: read those files by row width) | first GPU node, card 0 (shared with the dt005 probe) | launched ≈ 09:16 UTC 10-16, t = 0 Ham matches preflight; t = 5.1 at 09:32, χ_min ON the 1e-4 floor (engaged as designed, the 0.9c's pattern) | 150 | 17.3 t/h solo, ~9 t/h shared | t = 150 ≈ 21:30 UTC 10-16 (shares card 0 with the one-recipe probe until ≈ 17:05) |
| **0.9c fast-end hold** `spin_hold_L64_ml3_ve090a_spdrv1_sig04_t150` (`drainhole/04_fast_spin_hold/`; family (a) at v_e 0.90, the ve070a-minchi4 L64 grid with the three knobs together — min_chi 1e-4 rescue floor, σ 0.4, damping sponge drive 1.0; ψ4 R = 14 is the trusted sphere; no checkpoints; χ_min lifts off the floor and rises, 2.9e-4 at t = 33, max|K| 1.8e-2) | second GPU node | launched ≈ 06:36 UTC 10-16, t = 33.2 at 08:30 UTC | 150 | ~17.6 t/h | t = 150 ≈ 15:10 UTC 10-16 |
**Speed-recipe test `spin_hold_L128_ml3_ve050a_sig04_dt005_t100` DIED
t = 47.85 (NaN in K, level 3) — the 2.5× package is DEAD on production spin
data.** It tracked B1 to t ≈ 20, then χ_min crashed to the 1e-8 floor (B1
holds 1.5e-6 throughout) and max|K| jumped 40×; K runaway at the end. With
the L64 static ladder clean at dt 0.05 + σ 0.3–0.4, this isolates dt as the
killer on the L128 drainhole: **dt stays 0.02; the surviving speed-up is
σ 0.4 alone** (the second node's head-to-head: constraints 400–40,000×
below control at t = 100, a ~4-unit σ kick to collapse times). Owed before
adoption: the one-knob σ 0.4 + dt 0.02 check on L128 spin data. Packed,
registry row written, scratch pruned, 2026-10-16 ~04:55 UTC.

**Sponge-fix arm `static_hold_L64_ml3_spdrv1_t100` REACHED t = 100, 0 NaN —
the damping sponge WORKS as an absorber, and FALSIFIES the echo story.**
One knob (drive A = 1) vs the packed static hold: throat identical to
4 digits, global Ham/Mom identical, the 12–16 ring |K| identical at every
time — while |K| falls TWO DECADES across the 24–32 shell (0.27 → 0.003 at
t = 100), so the drive engages hard. Conclusion: the t ≈ 60+ growth that
set every L64 t_max = 64 window is NOT a boundary echo (an echo crosses the
shell twice, e⁻¹² with the drive) — it is the collapse itself radiating K
outward (the horizon forms at t ≈ 61). For non-collapsing holds the box
wall is therefore the true limit only where a run outlives the crossing
time, and **the drive guarantees absorption there: adopt
`sponge_drive_strength = 1.0` for any run intended past t ≈ L** (the L128
t = 128+ holds the 0.5c/0.7c trends need). Packed, registry + trust rows
written, scratch pruned, 2026-10-16 ~04:55 UTC. Both cards idle; nothing
launches without the go.

**Verification rung N 256 `spin_hold_L128_ml3_J100_full_t100` FINISHED
≈ 20:20 UTC 10-15: reached t = 100 clean, 0 NaN — THE MODEL CHECK PASSES.**
τ(ΔR ∈ [0.01, 0.3]) = 6.78 vs the L64 acceptance run's 6.8 (static 5.8);
milestones −1 % / −10 % at t = 46.85 / 61.82 vs L64's 46.9 / 61.8 — box-
and resolution-independent to 0.05 time units. Full collapse with a
detached horizon at t ≈ 64 (static ≈ 61), throat −44 % by t = 96, ridden
cleanly to t = 100. Trust window t ≤ 67 (Ham ×2 at 67.1; the τ window and
the detachment inside). Registry + trust row written; pack + movies follow
the consumer drain. The formal triplet still needs the N 192 rerun and
N 384 — both behind the freeze.

**B1 `spin_hold_L128_ml3_ve050a_t100` FINISHED ≈ 12:15 UTC 10-15: reached
t = 100 clean, 0 NaN** — packed, registry + README + trust window (t ≤ 78)
done, movies rendering. MOTS R −1 % at t = 71 (static twin: t = 44), −3.14 %
at t = 100, no horizon; L2_Ham ×2 off plateau at t = 78.8 (the slow level-2
interface mode), far-side χ on the 1e-8 floor from t = 91.9. Final Chk10000
copied to the run's `nfs_chk/` (a t = 100 restart point if the hold is ever
extended toward the t ≈ 120 return); scratch pruned. **Card 0 is free and
stays idle — the launch freeze above holds until the σ verdict.**

| run | node/card | t | stop | speed | ETA |
|---|---|---|---|---|---|
**Verification rung N 192 STOPPED by hand ~19:50 UTC 10-15 at t = 1.6 on the no-launch order** (it had launched 19:30 under the earlier rung go, minutes before the freeze; clean while it ran). Its registry row records it; it reruns from t = 0 when the rung gets its go. Card 1 idle. Its 5.2 GB scratch dir awaits the prune word.

**Rescue probe `spin_hold_L64_ml3_ve070a_minchi4_t100` FINISHED ≈ 15:30 UTC
10-15: RESCUE PASS — reached t = 100, 0 NaN** (the parent died t = 42.36).
One knob, min_chi 1e-8 → 1e-4: the floor is pinned only t = 0–3.17, then
χ_min lifts off and rises to 1.0e-3 by the end — the far side heals, not
just clamps. L2_Ham flat at 3.4e-3 the whole run (never ×2); throat frozen,
R_eq −0.016 % over t = 0–100 (0.5c shrinks −2.9 % on this grid — the
slowdown trend continues to 0.7c, below detection). Trust window t ≤ 64
(L64 boundary return). Packed, registry + README + trust row written,
scratch pruned (~19 GB). **B2 (v_e 0.7, L = 128 ×3) is unblocked at the
data level — min_chi 1e-4 goes into its templates; launches stay frozen.**
**The dt × σ study FINISHED overnight 10-15→10-16** (all three arms clean,
0 NaN, packed, scratch empty; close-out 04:55 UTC 10-16). Second node's
card 0 is idle; the two adoption runs (confirmation hold at (0.3, 0.05) to
t = 100 on L64, and the L128 one-knob check) are proposed and await the
go. Verdicts and history: **SPEED-UP RESEARCH** below.

## SPEED-UP RESEARCH (dt × σ) — goes fully to the article

**RESULT (study complete 2026-10-16; the L128 rungs decided it the same
day).** Four verdicts:
1. **L64-static speed-up (OVERRULED for production by verdict 4):
   sigma = 0.3, dt_multiplier = 0.05** — 2.5×
   today's (0.1, 0.02) and cleaner than it (level-2 masked Ham at 0.3–0.5
   of the dt 0.02 control, falling; startup max|K| offset ×1.51 decays to
   ×1.11 by t = 45). **Sigma 0.3 is the floor**: the 0.2 rung FAILED —
   it only slows the mode (level-2 Ham ×29 at t = 40, ×69 at t = 45,
   ψ4 ×10 and rising; breakout postponed past the window, not removed).
2. **Trust-window fix: sigma 0.4 at the production dt 0.02 erases the
   late constraint growth.** At t = 100 the masked Ham norms sit at
   2.4e-5 / 4.1e-5 / 7.9e-4 of the sigma-0.1 control on levels 1/2/3
   (composite 2.5e-3 of it): the interface mode IS the late growth that
   ended every trust window (B1: ×2 at t = 78.8). Cost, measured on the
   hold: the collapse milestone comes ~4 time units earlier (max|K| > 0.1
   at t = 57.9 vs 61.97 — the sigma-induced initial kick is larger), so
   collapse-time comparisons across sigma values need matched sigma.
3. **Binary regression: the levnorm binary is bit-exact** — the dt 0.02
   control twins the packed Step 0 hold to all printed digits over the
   full t ≤ 100 record, same collapse milestone t = 61.97.
4. **The fast dt DIES on production L128 spin data — production dt stays
   0.02.** dt 0.05 + sigma 0.4 NaN'd at t = 47.85 (chi_min to the 1e-8
   floor from t ≈ 20; B1 holds 1.5e-6 throughout); the in-between rung
   dt 0.035 crashed the same way, floor at t = 22.3 — a puncture/gauge-
   sector failure sigma cannot fix, distinct from the L64 interface
   mode. **The adopted speed-up is verdict 2 alone: sigma 0.4 at
   dt 0.02** (one-knob adoption check live on the first node).

**The finding.** The dt ceiling was never hard CFL (local speeds ≤ 0.95;
the KO+RK4 bound allows dt_mult ~0.23 at sigma 0.1) — it is a weak AMR
interface-mode instability: a grid-scale checkerboard pinned to the fixed
nested coarse–fine box edges (square halos in K; shells r ≈ 5–7.5 fastest,
level-3 box corners at 4√3 ≈ 6.9), dissipation-starved at sigma 0.1 and
radiating into the wave zone long before breakout (ψ4 ×373 at t = 10,
×8,600 at t = 15 at dt_mult 0.05). One mode at every dt, a growth-rate
ladder, not a threshold: e-fold ~0.8 at dt_mult 0.1, breakout t ≈ 28–30 at
0.05, t ≈ 43 at 0.035, e-fold ~9 (slow but present) at the production
0.02. The composite constraint norm is blind to it until breakout (level-0
volume dominates); the per-level masked norms (debt item 2) flag it by
t = 10. Stronger KO kills it where it lives.

**History, one line per arm** (all on the L64 static hold, levnorm binary
`main3d_levnorm_73793542`, packed in `drainhole/06_dt_ladder/`):
- Merger-era evidence: dt_mult 0.1 NaN at t = 16; 0.05 drifted after
  t ≈ 30; 0.02 clean to 100 — cause unknown, every hold paid ~7 h.
- `dt005_t070`: localized the mode (level-2 Ham ×61 at t = 15, max|K|
  1.37 at t = 40); stopped by plan at t = 45.
- `dt0035_t070`: unstable too, later (left the reference t ≈ 43, ×41 by
  t = 55); stopped by hand at t = 62.
- `dt002ctl_t100`: bit-exact vs the packed Step 0 hold (binary regression
  clean); carries the slow mode itself (level-2 e-fold ~9).
- `dt005_sig04_t045`: sigma 0.4 kills the checkerboard at the bad dt;
  clean to 45, offset ×1.68 → ×1.07.
- `dt005_sig03_t045`: clean to 45 and cleaner than 0.4 — level-2 at
  0.3–0.5 of control; the gentlest working KO so far.
- `dt005_sig02_t045`: the floor rung FAILS — 0.2 only postpones breakout;
  the floor is 0.3.
- `dt002_sig04_t100`: the sigma-default / trust-window test PASSES —
  constraints 400–40,000× below control at t = 100; collapse ~4 units
  earlier (the sigma kick).
- `sig04_dt005_t100` (L128 spin, first node): the 2.5× package on
  production data DIED t = 47.85 — chi_min to the 1e-8 floor from
  t ≈ 20, NaN in K level 3; a puncture-sector failure, not the
  interface mode.
- `sig04_dt0035_t060` (L128 spin): the in-between rung crashes the same
  way — chi_min floored at t = 22.3, max|K| runaway; stopped at
  t = 26.4. dt stays 0.02.

**Owed before adoption**: the sigma 0.4 + dt 0.02 one-knob check on L128
spin data — LIVE on the first node (card 0, t = 100 ≈ 12:20 UTC 10-16).
The L64 confirmation hold at (0.3, 0.05) is moot for production (dt 0.02
fixed by verdict 4); it stays available only as a numerics cross-check.

**2026-10-14 ~21:53 UTC the node container was killed externally** (and once
before, 23:44 UTC 10-13, which is what stopped B1): scratch wiped, both
first-launch runs gone, no checkpoints survived (they lived on scratch only).
What each had shown by then:

- **B1 first launch (killed, not a death): clean to t = 46.70, zero NaN.**
  MOTS R 4.9612 → 4.9573, **−0.08 % by t = 46**, where the static twin
  (`single_hold_L128_t100`) was already −1 % by t = 44 — the spin is slowing
  the collapse ~10× at mid-time, matching the L64 result. χ_min steady
  1.5e-6, lapse_min 0.17, all smooth. 47 frames + 363 MB slice cache to
  t = 46 survive on NFS (`..._t100_killed_t46/`), so movies to t ≈ 46 are
  makeable. Relaunched from t = 0 on the same template, 05:00 UTC 10-15.
- The family (b) probe ladder died the same morning — the full story is in
  **CAMPAIGN A — DROPPED** at the bottom; it no longer gates the plan.

The B1 production member (its go 2026-10-13): the v_e 0.513 drainhole on plain
L128 N256 ml3 (`params_spin_hold_ve050a_L128_N256.txt`), full-box frames
(zoom 128, cache 2048), rolling checkpoints every t = 10 keep 3 (asked). Its
static twin on this exact layout is the merger's `single_hold_L128_t100`:
the question is whether the L64 result (collapse slows with spin) holds with
the clean t = 100 baseline. Earlier today (final packing 19:50 UTC): every previous run packed,
scratch empty. Closed out: in `drainhole/04_fast_spin_hold/` v_e 0.7
(died t = 42.36, far-side puncture), v_e 0.5 (finished; 14 movies to t = 64) and
J = 1 on exact data (died t = 70.64 at the end of a collapse); in
`symmetric_massless/` the 21 A1 runs (`01_t0_checks/L128_A1/`) and the three puncture
probes (`03_spin_hold/`). The six L = 64 A1 runs are superseded
(`symmetric_massless/00_archive/`, not packed).

**Frames over the whole box** (decided 2026-10-13): launch with `--zoom 128
--coord 64 --center 64 64 64` and `GRTECLYN_FRAMES_BUFF_CAP=2048`, so the live frames,
the preflight's frame 0 and the slice cache cover ±64 at one pixel per finest cell
(2048² at N = 256); zooming is done later, when the frames are redrawn from the cache
(`rerender_frames.py` needs a window option for that, not yet written).

## QUEUED

**LAUNCH FREEZE (2026-10-15, ~12:00 UTC): no new run starts until the
slow-interface-mode / sigma question on the second node is settled** (the
σ = 0.4 + dt 0.02 head-to-head vs the σ = 0.1 control, verdict expected
tomorrow morning). The triplet members would otherwise bake today's σ = 0.1
into the production curve while the fix is being measured. Cards freed by
finishing runs (B1 ≈ 12:15 UTC, the ve070a rescue probe ≈ 13:20 UTC) stay
idle; systematics passes still run.

**FIRST AFTER THE FREEZE (decided 2026-10-15): the v_e ≈ 0.2 verification
triplet** (`spin_hold_L128_ml3_J100_full_*`, the J = 1 exact point) — before
any other ladder rung, because it is the one rung the published O(J²) rate can
check: if the nonlinear τ there does not meet the perturbative prediction,
the model is wrong and the fast rungs are worthless. The B1 rung's N 192/384
members and everything faster run only after this rung passes. Order within
the rung: N 256 (production grid, ~7 h) first, then N 192 (~2.2 h), N 384
last (needs the junk-shell templates). All start from t = 0 — no queued run
restarts from any checkpoint. Launches still wait on the σ verdict, the go,
and the per-member checkpoint answer.

**SCOPE (decided 2026-10-15, supersedes the 10-13 order): the paper is the
drainhole's.** Campaign A (the symmetric family (b) evolutions A2–A4) is
DROPPED: four one-knob probes all die at t ≈ 23–24 at the far-side
positive-mass end, knob-independently (the postmortem at the bottom), and a
paper that introduces the symmetric case only to abandon it mid-story is
worse than one that never promises it. Family (b) stays in the paper as
theory and as the solver's validation only — the Step 2 gates, the A1
t = 0 ladder (21 runs, every quantity against Kleihaus–Kunz/CKK) and the
t = 0 convergence figures. No family (b) evolution is queued; the
postmortem section keeps everything needed to return to it.

**Every run from now on is on L = 128, clean to t = 100** (decided 2026-10-13).
The sponge (extra Kreiss–Oliger dissipation in r 24–32; the merger's
`Source/Grids/SpongeZone.hpp`) removes only grid-scale noise: the outgoing gauge
pulse (λ ~ 8 ≫ Δx 0.5) passes it, reflects off the faces and is back at the
throat by t ≈ 64 on L = 64, which ends every L64 hold's trust window (in ve050a,
K enters the frame window from t ≈ 60). The layout is the merger's own
`single_hold_L128_t100`: the L64 Step 1 grid's base Δx and nested boxes
(tagging_L 64: ±16/8/4, max_level 3) in a box twice as wide, sponge 48–64, so the
return comes at t ≈ 120–128. **Triplets are N = 192 / 256 / 384** (dx0 0.667 /
0.5 / 0.333; finest Δx 0.0833 / 0.0625 / 0.0417): dx0 = 1 is too coarse for any
evolution, so the coarsest member keeps dx0 ≤ 2/3 and the production grid is
dx0 = 0.5 (corrected 2026-10-13; the A1 N = 128 members stand as t = 0 checks
only, and the old L = 64 at N = 128 was this same dx0 0.5). From the measured
14.1 t/h and 46 GB at N = 256: ~2.2 / 7.1 / ~36 h to t = 100 (N⁴), ~45 GPU-h a
triplet; N = 384 scales to ~155 GB, over the 81.5 GB card, so those members
need both cards (MPI) or their own decision.

*Phase B: drainhole, family (a) — THE HEADLINE*

**The spin ladder (agreed 2026-10-15): five rungs in v_e, every rung a
triplet, one τ(v_e) curve.** Rationale per rung — 0 is the anchor every
"spin slows collapse by X" divides by; ≈ 0.2 sits inside the source
paper's perturbative O(J²) domain, the one rung where the nonlinear rate
checks against a published number (the validation that licenses the fast
rungs, which have none) — and the J = 1 exact point (v_e 0.2100) IS that
rung (L64 already measured τ 6.8 vs static 5.8 there, i.e. where the
slowdown turns on); 0.5 is the production line; 0.7 and 0.9 (then
0.95/0.99 stretch) are the fast end, behind the far-side rescue.
Intermediate rungs (0.35, 0.6) only if the curve bends oddly between
neighbours. ~25 GPU-h a triplet (junk-shell N 384) → ~100 GPU-h for the
four new rungs, ~2–2.5 days on both cards.

**FOR THE ARTICLE (noted 2026-10-16): the rotating collapse EMITS A REAL
GRAVITATIONAL WAVE — the second headline observable.** At the outer
extraction sphere (R = 30), the 0.21c collapse (`spin_hold_L128_ml3_
J100_full_t100`) shows an l = 2, m = 0 burst of |ψ₄| = 3.0e-2 arriving at
t = 81 — horizon formation (t ≈ 64) plus the light-travel time (~17). The
static (spherical) collapse at the same radius reads 6.0e-5 — spherical
collapse cannot radiate, so that is the numerical floor: **the spinning
burst is 500× above it**, and 10⁴× above the run's own quiet-phase noise;
B1 (0.5c, no collapse) stays quiet. The GW burst is measurable per ladder
rung alongside τ (`psi4_mode_l2m0.dat` in every pack). Later: a few
larger-box runs to show the burst is not near-zone extraction (R = 30 on
L = 128 is base-grid; raise extraction_levels or the radius there).

**FOR THE ARTICLE (noted 2026-10-15): the exotic-matter trend is the
physics behind the ladder — don't forget the τ(v_e) vs D/M(v_e) figure.**
From the family (a) tables themselves (D = the phantom scalar charge, the
source of the exotic matter; values read off the solver legs, no new runs
needed):

| v_e | D (scalar charge) | M_ADM | D/M |
|---|---|---|---|
| 0.06 | 2.23 | 1.01 | 2.22 |
| 0.51 | 2.00 | 1.87 | 1.07 |
| 0.70 | 1.72 | 3.31 | 0.52 |
| 0.90 | 1.07 | 11.7 | 0.09 |
| 0.96 | 0.67 | 32.0 | 0.02 |

Two effects compound: D shrinks monotonically with spin while M_ADM grows
(rotational energy), so the exotic fraction D/M collapses a hundred-fold
across the family — at 0.7c the wormhole is already half as "exotic" per
unit mass as at 0.5c, and by 0.95c the phantom field is a trace
ingredient; in the extremal limit the family approaches extremal Kerr with
the scalar switching off entirely. Rotation progressively replaces exotic
matter as what holds the throat open. This makes the stability result
physically coherent rather than mysterious: the phantom field both
sustains the throat and drives its collapse, and the faster the spin, the
less of it there is — at 0.7c (exotic fraction halved vs 0.5c) the
collapse is already below detection. The correlation plot τ(v_e) against
D/M(v_e) is the paper's physical-mechanism figure once the ladder runs;
the D, M_ADM columns are in `results/spinningwormhole/solutions/<leg>/
<leg>.tsv` (tracked 2026-10-15).

**FOR THE ARTICLE (noted 2026-10-16): the exotic matter is MEASURED ON THE
GRID, at t = 0 and in time — collapse swallows it, the spinning survivors
keep it.** The scalar charge is fit from the equatorial φ frame slices
(closed form φ = D/(η₀√4π)·[arctan(η/η₀) − π/2], annulus r = 4–22). At
t = 0 the grid reproduces the solver's D to ~2×10⁻⁴ at all four spins
(static 2.2358/√5, 0.21c 2.2014, 0.51c 2.0010, 0.70c 1.7194) — the
pipeline carries exactly the right charge, and the decrease with spin
stands on the evolved grids themselves. In time (quoted to each trust
window): the static hold drains D 2.24 → 1.39 (−38 %) by t = 64 and the
0.21c collapse 2.20 → 1.61 (−27 %) by t = 67, max|φ| falling with it —
the horizon swallows the phantom, the merger paper's head-on panel (e)
picture (grid max|φ|, max|Π|); past trust both continue to ~0, consistent
but unquotable. B1 (0.51c, no horizon) and 0.70c (frozen throat) stay
flat: max|φ| −2.5 % over 78 units and −6 % (settled by t = 40), the slow
±15–20 % wobble of the fitted D there is the coordinate annulus feeling
the gauge, not matter moving. Paper figure when wanted: D(t) + max|φ|,
max|Π| per hold, cut at trust. **No extra plotfile retention is needed**:
everything reads the frame slice caches (phi_z, Pi_z, kept forever),
unlike the merger campaign, where plotfiles were consumed live for the
3D MOTS horizon numbers; the fit reruns from the caches in minutes.

| rung | run | needs | waiting on |
|---|---|---|---|
| v_e = 0 | static ×3: N 256 EXISTS (the merger's `single_hold_L128_t100`), run N 192 / 384 | templates written (`params_static_hold_L128_N*.txt`) | its go |
| v_e ≈ 0.2 (the published-domain rung) | `spin_hold_L128_ml3_J100_full_t100` ×3 — **the J = 1 exact point IS this rung**: its table meta reads v_e = 0.2100 (eta0 2, family a), and the freshly built `fam_a_ve020` came out at v_e 0.1984, J 0.936 — the same background twice (found 2026-10-15, one triplet saved) | table + templates exist (`params_spin_hold_J100_full_L128_N*.txt`, levnorm keys wired); L64 run already measured τ 6.8 here. `fam_a_ve020.spinbg` (2049×129, err 3.9e-8) stays on disk as an optional same-rung cross-check from a different solver leg | **FIRST after the freeze** (the model-verification rung, decided 2026-10-15), its go |
| v_e = 0.5 | **N 256 DONE** (reached t = 100 clean 12:15 UTC 10-15, trust window 78, packed); N 192/384 AFTER the 0.2 verification rung passes | templates written (`params_spin_hold_ve050a_L128_N{192,384}.txt`, levnorm keys wired); N 384 needs the junk-shell layout (below) or both cards | the 0.2 rung's verdict, then its go + checkpoint policy per member (N 256 ran every t = 10 keep 3 + NFS keeper) |
| v_e = 0.7 | B2 `spin_hold_L128_ml3_ve070a_t100` ×3 | the far side to clear t = 100: the min_chi 1e-4 rescue probe is LIVE on card 1 (the drainhole's χ does clamp to the floor, so the knob engages here — unlike family (b)) | the probe's verdict (≈ 13:30 UTC vs the old t = 42.36 death), its go |
| v_e = 0.9 (stretch 0.95 / 0.99) | B3 ×3 per spin | tables exist; expect a resolution wall before 0.99 and say so | B2, its go |

**Junk-shell layout for the N = 384-class members** (agreed 2026-10-13, not yet
templated): same L = 128 box, but the outer r > 32 shell stays one level
coarser (tagging_L 128, max_level 4, base dx0 = 2× the interior) — the
wormhole keeps its full resolution, the startup pulse dies in the 48–64 sponge,
return still t ≈ 128. Params-only (no code change). It cuts the finest triplet
member from ~36 h / 155 GB (impossible on one card) to ~16 h / ~70 GB, a
triplet to ~25 GPU-h. The production N = 256 member gains little (~7 h either
way), so it runs plain.

**Every quoted run is a triplet** (decided 2026-10-13; the stability protocol in
`SpinningWormhole.md`, after Evstafyeva, Siemonsen & East, arXiv:2508.11527):
L128 ml3 at N = 192 / 256 / 384 (finest Δx 0.0833 / 0.0625 / 0.0417; dx0 never
1). A growth is physical only if its τ converges to a nonzero value, the
finest-level constraints converge while it grows, and the throat's areal radii
or MOTS grow with it. N 192 / 384 costs are N⁴ estimates from the measured
14.1 t/h at N = 256.

**Per-level masked constraint norms are wired into every queued triplet
member** (2026-10-15): all six templates (`params_spin_hold_ve050a_L128_N*`,
`params_spin_hold_J100_full_L128_N*`) now carry `constraint_norms_levels = 1`
+ `constraint_norms_mask_radius = 0.125` (commit 73793542), so each run writes
`constraint_norms_levels.dat` — one Ham/Mom pair per AMR level plus a
hierarchy-wide pair, masked outside r = 0.125. The keys need the levnorm
binary: these launches pass `--binary
runs/spinning_wormhole/bin/main3d_levnorm_73793542_2026-10-15.ex` (the smoke
pin does not read them; preflight would refuse). Why: B1's level-0 norms grow
late (Ham 5.0e-4 → 6.3e-3 by t = 91, doubling ~5 units), and the dt-ladder
analysis identified it as the SLOW interface mode near level 2 (e-fold ~9 at
dt 0.02 in the control — the fast dt ≥ 0.035 checkerboard's quiet sibling),
not the throat and not the far-end floor. The per-level file makes that
attribution native to every triplet member. **Sigma stays 0.1 in the queued
templates for now**: the σ = 0.4 + dt 0.02 head-to-head vs the σ = 0.1
control (launching ≈ 13:00 UTC on the second node, verdict tomorrow morning)
directly measures whether a default σ raise flattens the late growth and
extends the trust window; if it does, raising σ in these templates is the
one-knob follow-up.


## NOW: STEP 3, TEST THE FAST-SPIN TABLES

The question the solver was built for: **does fast spin fix the instability?**
The O(J²) holds could not tell (their push was the data's own J⁴ error); the
full tables are exact to ~1e-10.
1. **t = 0 checks: PASS** (07:03–07:50; `*/0N_t0_checks/`, `t0_checks.py`).
   v_e 0.5, 3 grids: constraints converge at 4th order
   inside the throat; outside they grow as 1/dx² (Ham) and 1/dx (Mom), the
   fingerprint of the tables' fixed ~2e-7 bilinear error, 10⁴× below the
   O(J²) holds' push; throat radii converge to the table (R_eq −5e-5 at
   N = 192). Family (b) to v_e 0.99: throat radii within 0.1 %, constraints
   at the static hold's level.
2. **The drainhole at v_e 0.5 and 0.7** (the earlier holds' L64 grid, to
   t = 100). 0.7: died at its far-side puncture (t = 42.36), throat frozen.
   0.5: the throat shrinks, the static hold's sign, but slowly (MOTS R
   −0.61 % at t = 64, −2.9 % at 100; e-fold time ~5 at t 40–50, then a
   steady rate); no horizon, where the static hold's detached at t ≈ 61.
   Both are cut by the L64 boundary return (t ≈ 64), hence L = 128 above.
3. **J = 1 on exact data: the push vanishes.** The throat collapses on the
   static hold's mode (R_eq −1 % at t = 46.9, −10 % at 61.8; τ 6.8 against the
   static hold's 5.8 by the same measure) and the run dies inside the collapse
   at t = 70.64. The O(J²) hold's inflation was its data's error. With 0.5
   (−0.5 % by t = 64) the collapse slows with spin: the headline to confirm on
   L = 128 (B1).
4. **A1, family (b) on L = 128: PASS** (21 runs, v_e 0.24–0.99 × N 128/192/256;
   `L128_A1/<spin>/t0conv_<spin>_L128_checks.txt`). Throat radii converge to the
   table (R_eq −7e-5 to −9e-4 at N = 256); Ham/Mom 4th order inside the throat,
   1/dx² and 1/dx outside (the tables' interpolation); the 3D ADM mass integral
   equals the table metric's on the same grid to ≤ 1e-12, extrapolated M within
   2e-5–7e-4 of the table's (0.7 % at 0.99), J within 2e-3 (0.24) to 2e-5 (0.99).
5. **The family (b) holds died at the far-side puncture** at every knob
   setting — campaign A dropped 2026-10-15 (the postmortem below).

## NUMERICS DEBT (Step 0 of `SpinningWormhole.md`; items 1 + 2 in work 2026-10-15, second node's card)

This file carried the list until ca71ceed compacted it away; restored because
every item is still open:
1. **Why Δt = 0.02 Δx — SOLVED 2026-10-15**: a weak AMR interface-mode
   instability (grid-scale checkerboard on the nested box edges),
   dissipation-starved at sigma 0.1; stronger KO kills it and buys 2.5×.
   The full finding, verdicts and arm history: **SPEED-UP RESEARCH** above.
2. **Constraint norms level 0 only — DONE 2026-10-15** (commit 73793542,
   binary `main3d_levnorm_73793542_2026-10-15.ex`): `constraint_norms_levels
   = 1` writes `constraint_norms_levels.dat` — one masked L2_Ham/L2_Mom pair
   per level (cells no finer level covers, `makeFineMask`) plus a
   hierarchy-wide pair, puncture excluded inside `constraint_norms_mask_radius`
   (default 0.125, t0_checks.py's innermost shell edge). Historic level-0
   file untouched; smoke-tested on the ml3 grid (t = 0 value bit-identical to
   the packed Step 0 hold, speed unchanged 17.8 t/h). Adopt in production
   templates at the next binary bump.
3. **Constraint-solved seeds.** The Π shell seed violates the constraints in
   proportion to its amplitude (`SimulationParameters.hpp:50`); perturb Π,
   then re-solve the constraints. Dormant until a seeded spinning run is
   queued: every current hold runs seed_amplitude 0.
4. **Waveform extrapolation in 1/R**: absent; matters least under the
   stability-only plan.

## DONE

- **Step 0** (2026-10-11): the static hold twins the merger's `single_hold`:
  collapse, τ 5.27, trust window t ≤ 64.
- **Step 1** (2026-10-12): the O(J²) holds at J = 0.25 / 1 inflate (τ 5.8 / 5.6);
  their push grew as J⁴, the data's error, not the spin.
- **Step 2** (2026-10-13): full solver, both families to v_e 0.99, every gate
  green; CKK's eq. (12) is wrong; tables in `runs/spinning_p3/tables/`
  (error ≤ 1e-7 to v_e 0.9).

## CAMPAIGN A — DROPPED 2026-10-15 (postmortem, kept in case we return)

Not part of any evolution plan; nothing here is queued. The record of why
the symmetric family (b) holds cannot run, and what was already tried, so a
return does not repeat it.

**The wall.** Family (b) is mirror-symmetric: its compactified far end is a
genuine positive-mass puncture (M ≈ 2.5) at the grid centre. Every hold dies
there in a K runaway (χ → floor, |K|max explodes ~30× in one coarse step,
NaN in h11 or K on the finest level), with the throat unmoved. The drainhole
differs in kind: its far end is the repulsive/negative-mass side (stationary
lapse 0.21 ≈ gauge equilibrium), which is why B-campaign runs are not behind
this wall (the slow v_e ≤ 0.51 holds ran clean; the fast ve070a death is a
different, floor-engaged variant under its own rescue probe).

**The probe ladder — four one-knob probes, N ≥ 192, all ve085b, all dead at
t ≈ 23–24** (templates `params_spin_hold_L128_N192_ve085b_lapse1*.txt`; runs
kept in `symmetric_massless/03_spin_hold/ve085b/`, frames + slice caches on
NFS):
1. √χ initial lapse (pre-collapsed punctures), ml3: died t = 22.87 —
   cleared the old t ≈ 4 window (~6×), insufficient.
2. max_level 4 on the puncture (dx 0.0417, satisfying the BH rule
   dx ≲ M/40): died t = 23.76 — +0.9 units for 2× resolution. Resolution
   ruled out.
3. eta 1 → 0.2 (shift damping ~1/(2M_punc)): died t = 23.24 — EARLIER.
   Gauge-parameter tuning ruled out.
4. min_chi 1e-4 on the ml4 grid: died t = 23.76, the parent's time to the
   step, with χ_min 2.2e-3 the whole run — the floor never engaged. Floor
   ruled out.
   (A fifth, min_chi 1e-4 on ml3, was killed by hand at t = 9.13
   pre-verdict — under-resolved, no information.)

**Conclusion.** The death time is knob-independent across lapse, resolution,
shift damping and floor: it tracks the initial data, not the numerics. The
far-side positive-mass end collapses on its own timescale (~23 at N192-class
grids) and the moving-puncture gauge family cannot ride through THIS
puncture (plausibly because it is a compactified image of infinity carrying
the scalar field, not a vacuum Schwarzschild end). What a return would need:
excision/turducken at the far puncture, a qualitatively different gauge, or
different data (a family (b) slice whose far end is regularized) — code or
theory work, not params.

**What the paper keeps from A** (validation, not evolution): Step 2 solver
gates (both families to v_e 0.99, CKK eq. (12) corrected); A1 t = 0 ladder
— 21 runs, v_e 0.24–0.99 × N 128/192/256, every Kleihaus–Kunz Fig. 1
quantity and M/J against the tables (`L128_A1/`); the t = 0 convergence
figures. The clean t < 23 windows of the probes exist on NFS if ever needed,
but are quoted nowhere.

**Shelved rationale** (for a return): Azad et al.'s mode-crossing test lived
on family (b) — second mode and crossing only for C ≤ 0.2, spins at
10/20/33/50 % of limiting J/A, crossing predicted at J/A ≈ 0.013 (33 %),
static Ellis anchor τ ≈ 1.7 at η0 = 2. The A2 static (massless far side,
NOT behind the wall) ×3, A3 ×4 spins ×3, A4 ×3 ×3 run lists and templates
are in git history at 2998819f.

## RULES

Merger launch discipline: go first, checkpoints asked per run, full frame set,
STATUS pushed at every launch/stop. Ψ4 radii in the box's wave zone (L = 64:
12 / 16 / 20, decided 2026-10-12; L = 128: inside r 48, set with the A2
templates).
