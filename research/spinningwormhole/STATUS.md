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

Confirmed if the GPU 1 template run lands clean at t = 150 (≈ 19:00 UTC 10-16):
- **Grid**: L = 64, N = 128 base, max_level 3 (dx 0.5 → 0.0625), sponge 24–32
- **dt_multiplier = 0.02** (the ladder closed: 0.035 and 0.05 die on L128 spin data)
- **TWO REGIMES (realised 2026-10-16 ~12:30 UTC), two recipes, both proven:**
  - **≤ 0.5c (the collapse/shrink end): σ 0.1, min_chi 1e-8, stop 85.** Everything
    that collapses does so by t ≈ 64 (static 61, 0.21c 64; 0.5c never collapses,
    its shrink trend is measured inside t ≤ 78) — the σ 0.1 interface knee at
    78–85 costs nothing here, and the throat stays unclamped for the quoted τ.
  - **0.7c+ (the stability end): σ 0.4, min_chi 1e-4, stop 150.** The claim IS
    long-time stability; σ 0.1 recipes NaN here, and floor + σ 0.4 holds the 0.9c
    FLAT past t = 90 (Ham +2 %). σ 0.4 is safe because the floor forbids the χ
    depth it kills.
- **sponge_drive_strength = 1.0** (physics-neutral absorber; makes L64 viable past t ≈ 64)
- **2–3 L64 runs per card** (~25 GB each) is the campaign throughput. The window-extension
  probes for the slow end (σ 0.2, dt 0.05, ml4) are MOOT under the two-regime split; the
  ONE-RECIPE probe stays only as the clamp-validation methods check (verdict ≈ 17:05 UTC).
- **ψ4 radii 14, 18** (both outside the drive shell; 30 = in-shell reference only)
- spdrv binary, full frame set, no checkpoints, consumer keep-last 3; movies and quotes
  cut at each run's trust window
- Stable (non-collapsing) spins radiate nothing (checked 0.5c/0.7c: ψ4 deviations at the
  noise floor, no R = 14 → 30 propagation); the two-radius check matters for collapsing arms

## PAPER RUN MATRIX (2026-10-16) — the final list, checked off as they land

Paper runs live in `runs/spinning_wormhole/drainhole/00_paper_runs/` and pack to
`results/spinningwormhole/campaign/drainhole/00_paper_runs/`: new members launch
with `--subdir drainhole/00_paper_runs`; already-finished qualifying runs mv
there (run dir + repack, old pack git-rm'd) at their close-out.

**SLOW recipe (≤ 0.5c)**: L64 N128 ml3, σ 0.1, min_chi 1e-8, dt 0.02, drive 1.0,
**stop 85** (brackets the 78–85 knee; the paper quotes t ≤ 80), ψ4 R 14/18.
**FAST recipe (0.7c+)**: same grid, σ 0.4, min_chi 1e-4, dt 0.02, drive 1.0,
**stop 150**.

Schedule below from 15:30 UTC 10-16. Card 0/1 = 1st node; 2nd node has one card.

| ✓ | run | recipe | stop | where / when | ends in | ETA (UTC) |
|---|---|---|---|---|---|---|
| ☑ | 0c static anchor | slow | 85 | DONE, `00_paper_runs/` | – | – |
| ☑ | 0.5c | slow | 85 | DONE (died 130.0, window t ≤ 80 clean), `00_paper_runs/` | – | – |
| ☑ | 0.9c | fast | 150 | DONE (clean t 150), `00_paper_runs/` ≈ 15:10 | – | – |
| ☐ | **1st** 0.21c triplet N 192 | slow | 85 | LIVE card 1 since 14:58, 4.3 t/h measured | ~19 h | ≈ 10-17 10:45 |
| ☐ | **1st** 0.21c triplet N 128 | slow | 85 | card 0 when the probe ends (~4.9 h run) | – | – |
| ☐ | **1st** 0.21c triplet N 96 | slow | 85 | card 0 after N 128 (~1.5 h run) | – | – |
| ☐ | 0.7c | fast | 150 | LIVE 2nd node since ≈ 15:15, shared from 15:30 (~9.5 t/h) | ~15 h | ≈ 10-17 06:30 |
| ☐ | 0.99c stretch (σ 0.4 rerun) | fast | 150 | LIVE 2nd node since 15:30, shared with the 0.7c (~9.5 t/h) | ~16 h | ≈ 10-17 07:30 |
| ☐ | 0.9c fast triplet N 96 | fast | 100 | card 1 after the J=1 N 192 (~1.8 h run) | – | – |
| ☐ | 0.9c fast triplet N 192 | fast | 100 | card 0 after the J=1 members (~23 h run) | – | – |
| ☐ | kick 0.9c, amplitude A1 | fast + seed | 150 | 2nd node when a slot frees (~8.5 h run) | – | – |
| ☐ | kick 0.9c, amplitude A2 (×10) | fast + seed | 150 | 2nd node after kick A1 (~8.5 h run) | – | – |
| ☐ | kick 0.7c, amplitude A1 | fast + seed | 150 | card 1 after the 0.9c N 96 (~8.5 h run) | – | – |
| ☐ | 0.95c stretch | fast | 150 | optional, only if the 0.99c curve wants the point | – | – |
| – | clamp validation (methods) | σ04 + mc4 + dt005 @ 0.5c | 100 | LIVE card 0 solo, 32 t/h; stays `06_dt_ladder/` | ~0.8 h | ≈ 16:15 |

Campaign total ~34 h if the queue runs back-to-back. Kick templates
(A1 = merger seed scale, A2 = ×10) still to be built; every launch waits
for its go. ETAs only for launched runs.

Remaining ☐ ≈ 100 card-hours on THREE cards (both first-node + the second
node's) ≈ 1.4 days once the current probes clear; second-node launches run
from a session on that node. Kick amplitudes fixed at template time (A1 = the merger
seed's scale, A2 = ×10), constraint-compatible Gaussian scalar seed.

## RUN LEDGER — every arm so far

All N 128 base, max_level 3. drv = sponge_drive_strength. Outcomes frozen in
`runs_registry.tsv` / `trust_windows.tsv`; family (b) (the ve0xxb probes) is the
dropped campaign, postmortem at the bottom.

| run | data | L | sigma | dt | floor | drv | outcome | trust |
|---|---|---|---|---|---|---|---|---|
| `static_hold_L64_ml3_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | – | Step 0 anchor, clean t 100 | 64 |
| `static_hold_L64_ml3_dt002ctl_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | – | bit-exact twin of Step 0 | 100 |
| `static_hold_L64_ml3_dt005_t070` | static | 64 | 0.1 | 0.05 | 1e-8 | – | interface mode ×61 by t 15; stopped 45 | – |
| `static_hold_L64_ml3_dt0035_t070` | static | 64 | 0.1 | 0.035 | 1e-8 | – | same mode, later; stopped 62 | – |
| `static_hold_L64_ml3_dt005_sig02_t045` | static | 64 | 0.2 | 0.05 | 1e-8 | – | FAIL: mode only postponed | – |
| `static_hold_L64_ml3_dt005_sig03_t045` | static | 64 | 0.3 | 0.05 | 1e-8 | – | clean 45, gentlest working KO | – |
| `static_hold_L64_ml3_dt005_sig04_t045` | static | 64 | 0.4 | 0.05 | 1e-8 | – | clean 45, mode killed | – |
| `static_hold_L64_ml3_dt002_sig04_t100` | static | 64 | 0.4 | 0.02 | 1e-8 | – | constraints 400–40,000× below ctl; collapse 4 u early | 100 |
| `static_hold_L64_ml3_spdrv1_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | drive is a clean absorber; echo story falsified | 64 |
| `spin_hold_L64_ml3_J025_t100` | 0.1c | 64 | 0.1 | 0.02 | 1e-8 | – | clean t 100 | 64 |
| `spin_hold_L64_ml3_J100_t100` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | – | collapse; tau 6.8 vs static 5.8 | 57 |
| `spin_hold_L64_ml3_J100_full_t100` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | – | exact-data collapse; died 70.64 at its end | 64 |
| `spin_hold_L64_ml3_ve050a_t100` | 0.5c | 64 | 0.1 | 0.02 | 1e-8 | – | clean t 100; Ham ×2 at 84.5 | 64 |
| `spin_hold_L64_ml3_ve070a_t100` | 0.7c | 64 | 0.1 | 0.02 | 1e-8 | – | DIED 42.36, far-side puncture | 40 |
| `spin_hold_L128_ml3_ve050a_t100` (B1) | 0.5c | 128 | 0.1 | 0.02 | 1e-8 | – | clean t 100; Ham ×2 at 78.8 | 78 |
| `spin_hold_L128_ml3_J100_full_t100` (N 256) | 0.21c | 128 | 0.1 | 0.02 | 1e-8 | – | model check PASSES (tau 6.78 = L64's); GW burst 500× floor | 67 |
| `spin_hold_L128_ml3_ve050a_sig04_dt005_t100` | 0.5c | 128 | 0.4 | 0.05 | 1e-8 | – | DIED 47.85, puncture floored from t 20 | 20 |
| `spin_hold_L128_ml3_ve050a_sig04_dt0035_t060` | 0.5c | 128 | 0.4 | 0.035 | 1e-8 | – | floored 22.3; stopped 26.4 | – |
| `spin_hold_L128_ml3_ve050a_sig04_t100` | 0.5c | 128 | 0.4 | 0.02 | 1e-8 | – | DIED 46.47: sigma kills at ANY dt | 15 |
| `spin_hold_L64_ml3_ve070a_minchi4_t100` | 0.7c | 64 | 0.1 | 0.02 | 1e-4 | – | RESCUE PASS, clean t 100, chi heals | 64 |
| `spin_hold_L64_ml3_ve050a_spdrv1_t150` | 0.5c | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | DIED 130.0 (NaN h11): K > 0.1 at 110, lapse pinned 128 — slow recipe breaks long; paper 0.5c run, quotes t ≤ 80 | 80 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig02_t100` | 0.5c | 64 | 0.2 | 0.02 | 1e-8 | 1.0 | stopped 23.9 (two-regime decision; chi already on the dt005 decay curve — sigma-driven, dt-independent) | 25 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig02_dt005_t100` | 0.5c | 64 | 0.2 | 0.05 | 1e-8 | 1.0 | stopped 44.5: slow puncture decay | 20 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig04_mc4_dt005_t100` | 0.5c | 64 | 0.4 | 0.05 | 1e-4 | 1.0 | LIVE; the ONE-RECIPE candidate | tbd |
| `spin_hold_L64_ml3_ve090a_spdrv1_sig04_t150` | 0.9c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | CLEAN t 150: Ham flat (1.07e-2 → 1.17e-2 over 60 → 150), no MOTS ever — the paper 0.9c run | 150 |
| `spin_hold_L64_ml3_ve070a_spdrv1_sig04_t150` | 0.7c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | LIVE; the paper 0.7c run (fast recipe, 0.9c params + background swap) | tbd |
| `spin_hold_L64_ml3_ve099a_spdrv1_t150` | 0.99c | 64 | 0.1 | 0.02 | 1e-4 | 1.0 | stopped 50.4 (feasibility answered: Ham flat 3.94e-2, K flat, chi on the 1e-4 floor); paper 0.99c = σ 0.4 rerun | 50 |

What the ledger says, four lines:
- sigma ≥ 0.2 kills the spin far-side puncture on the 1e-8 floor at any dt (0.4 by t ≈ 22, 0.2 slowly); the min_chi 1e-4 floor removes that failure mode.
- sigma 0.1 caps every slow run at the interior interface knee, Ham ×2 at 78–85, box-independent; the drive does not cure it.
- sigma 0.4 + floor 1e-4 holds the 0.9c flat past t = 90 — the ONE-RECIPE probe is testing that combo + dt 0.05 at 0.5c; pass = one recipe at every spin, stop 150, 2.5× faster.
- dt alone never killed a spin run; dt 0.05 needs sigma ≥ 0.3 (static) and the floor (spin).

## LIVE

| run | node/card | t @ 15:25 | stop | speed | ETA (UTC) |
|---|---|---|---|---|---|
| triplet N 192 `L64_N192_ml3_J100_full_spdrv1_t85` | 1st, card 1 (solo) | ~2 | 85 | 4.3 t/h measured | ≈ 10-17 10:45 |
| ONE-RECIPE `..._sig04_mc4_dt005_t100` | 1st, card 0 (solo from ~15:10) | 71.6 | 100 | ~32 t/h | ≈ 16:15 |
| 0.7c `ve070a_spdrv1_sig04_t150` | 2nd node (shared 15:30) | 4.5 | 150 | ~9.5 t/h shared | ≈ 10-17 06:30 |
| 0.99c `ve099a_spdrv1_sig04_t150` | 2nd node (shared) | 0 (launched 15:30) | 150 | ~9.5 t/h shared | ≈ 10-17 07:30 |

0.9c `ve090a_spdrv1_sig04_t150` FINISHED CLEAN t = 150 ≈ 15:05: Ham flat
(1.07e-2 → 1.17e-2 over t 60 → 150), max|K| flat 2.0e-2, no MOTS ever — the
stability claim delivered, trust full 150. Moved + packed `00_paper_runs/`;
scratch pruned (7.1 GB). The paper 0.7c run launched ≈ 15:15 on its card from the
0.9c params (background swap only, diff-proven).

0.5c drive `ve050a_spdrv1_t150` FINISHED-DEAD: NaN (h11, L3) at t = 130.0. Clean
through the Ham ×2 knee (~83); then Ham 0.157@110 → 0.367@120, max|K| > 0.1 at
t ≈ 110, lapse pinned 1e-10 by 128 — the slow recipe going unphysical long, as
the two-regime split predicted. Trust 80; moved + packed `00_paper_runs/`;
scratch pruned (7.1 GB).

Notes: every live run no-checkpoint, spdrv binary, full frames, keep-last 3.
0.99c psi4 is 3-radius (14/18/30) from t = 22 only — the consumer was killed by a
wrong-flag restart ~11:44 and hand-rebuilt ~11:50; earlier rows are 2-radius and
the header names 2, so read `psi4_mode_l2_all/l2m0.dat` by row width. B1's final
Chk10000 sits in its `nfs_chk/` (t = 100 restart point). The L128 N 192/384
verification members are DROPPED — the triplet moved to the L64 production
box (convergence policy, QUEUED).

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

**History**: one row per arm in the RUN LEDGER above; packed in
`drainhole/06_dt_ladder/`.

**Adoption state (2026-10-16)**: the one-knob sigma 0.4 + dt 0.02 check on L128
spin data DIED t = 46.47 — verdict 2 does NOT transfer to spin data on the 1e-8
floor. The surviving path is sigma 0.4 + min_chi 1e-4 (+ dt 0.05): the
ONE-RECIPE probe.

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

**Kick (perturbed-stability) study — planned 2026-10-16, launches later on the go.**
As in Evstafyeva–Siemonsen–East (arXiv 2508.11527: ultracompact spinning boson
stars show no instability to tμ ~ 1e4 under truncation-error AND imposed
perturbations): our fast-end holds are so far stable only against truncation
error, so rerun the stable 0.9c (and 0.7c) with the Gaussian scalar seed at 2–3
amplitudes (`spinning_seed_amplitude/width/radius`, currently 0 in every hold),
applied constraint-compatibly as in the merger paper's kick. Fast-end recipe
(σ 0.4, min_chi 1e-4, dt 0.02, drive 1.0), stop 150. Discriminators: ring-down
back to the hold vs triggered collapse/migration; the ψ4 response at R 14/18.

**Convergence policy (2026-10-16, revised same day): ONE Richardson triplet,
ON THE PRODUCTION BOX.** The triplet moves to L = 64 at the J = 1 rung with the
production slow-end recipe (σ 0.1, 1e-8, drive 1.0, dt 0.02, stop 85):
**N 96 / 128 / 192** — the same dx₀ ladder (0.667/0.5/0.333) the L128 plan
used, with production N 128 as the middle member (~1.6 + 5 + 24 h, one card).
The finished L128 N 256 run keeps its two roles — the O(J²) model check and
the box-independence cross-check (milestones match L64 to 0.05 u) — but is no
longer the formal triplet; **the L128 N 192 rerun and the N 384 member
(155 GB, MPI over both cards) are DROPPED.** Fast-end: a FULL second triplet at 0.9c, N 96/128/192 on the fast recipe to
t ≈ 100 (~2.7 + 29 h; the N 128 member is the paper 0.9c run itself), so the
σ 0.4 + clamp recipe carries its own convergence order rather than borrowing
the slow triplet's. Every other run: production N 128 with its regime's
triplet error bar.

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
