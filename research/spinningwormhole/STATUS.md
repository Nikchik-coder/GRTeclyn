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

All clock times Moscow (UTC+3, decided 2026-10-16); older prose entries are UTC.
Schedule below from 08:39 MSK 10-17 (speeds measured 21:43 → 08:39). Card 0/1 = 1st node; 2nd node has one card.

| ✓ | run | recipe | stop | node | gpu | where / when | ends in | ETA (MSK) |
|---|---|---|---|---|---|---|---|---|
| ☑ | 0c static anchor | slow | 85 | 1 | – | DONE, `00_paper_runs/` | finished | finished |
| ☑ | 0.5c | slow | 85 | 1 | 1 | DONE (died 130.0, window t ≤ 80 clean), `00_paper_runs/` | finished | finished |
| ☐ | 0.9c | fast | 150 | 2 | 0 | ran clean to t 150 (packed `00_paper_runs/`) — **RERUN REQUIRED**: no throat-size record (ran before the throat measure; the horizon finder found nothing; plotfiles gone) → rerun `spin_hold_L64_ml3_ve090a_spdrv1_sig04_t150_thr`, same params, ~9 h | rerun | – |
| ☐ | **1st** 0.21c triplet N 192 | slow | 85 | 1 | 1 | DIED 78.66 ≈ 12:10 MSK (NaN, post_timestep) late in the throat collapse, before its stop: R −1 % at 56, 2.98 at 78; χ on the 1e-8 floor at 75.7, K > 0.1 at 76.4 (the N 128's sequence 9.3 later); trust 75; packed `00_paper_runs/`; 1st-node scratch prune needs a session there | died | died |
| ☑ | **1st** 0.21c triplet N 128 | slow | 85 | 1 | 0 | DONE t 85 ≈ 04:35 through the throat collapse (R −1 % at 47, 2.53 at 85; trust 66), `00_paper_runs/` | finished | finished |
| ☐ | **1st** 0.21c triplet N 96 | slow | 85 | 1 | 0 | FAILED, not finished: died 64.83 ≈ 00:30 at the end of the throat collapse (R −1 % at 43); pulled from the paper folders 10-17, archived in `drainhole/00_archive/failed_2026-10-17/` | failed | failed |
| ☐ | 0.7c | fast | 150 | 2 | 0 | DIED 135.85 ≈ 11:06 MSK (NaN in K, level 3): the lapse collapsed to its 1e-10 floor at t 102.4, K > 0.1 at 105.8, Ham ×2 at 127.5; the throat holds in the window (MOTS R 6.870–6.873 over t 0–83) — the slicing breaks, not the throat; trust 102; packed `00_paper_runs/` 10-17 ≈ 11:50, 2nd-node scratch pruned | died | died |
| ☐ | **0.7c extra run**: slow recipe `ve070a_spdrv1_t100` | slow | 100 | 1 | 0 | LIVE since 12:45 MSK 10-17 — the 0.7c on the 0.5c's settings (min_chi 1e-8, σ 0.1; params = the 0.5c's with the ve070 background, diff-proven), no checkpoints. Question: does the 0.7c hold or slowly collapse like the 0.5c? (On the fast recipe its centre stayed pinned near the 1e-4 floor, K ≈ 0.035 drained the lapse e-fold ~15 to its floor at 102.) | ~6 h | ≈ 10-17 18:45 |
| ☑ | 0.99c stretch (σ 0.4 rerun) | fast | 150 | 2 | 0 | DONE clean t 150 ≈ 12:19 MSK: Ham flat 3.93e-2, Mom 1.50e-3, lapse 8.1e-3, K 2.2e-3; MOTS R 181.76 → 181.72; `00_paper_runs/`; 2nd-node scratch prune (7.1 GB) needs a session there | finished | finished |
| ☐ | 0.9c fast triplet N 96 (t 150 window) | fast | 150 | 1 | 0 | evolution reached t 150 ≈ 12:30 MSK (no NaN); consumer draining its last 73 plotfiles (frames 2× until the N 96 repair, see below) — **RERUN REQUIRED**: throat measure only from t 79 → rerun `spin_hold_L64_N96_ml3_ve090a_spdrv1_sig04_t150_thr`, ~3.5 h | drain | ≈ 10-17 14:20 |
| ☐ | 0.9c fast triplet N 192 (t 150 window) | fast | 150 | 1 | 1 | NOT STARTED — on the spline binary, after the decision on the spline checks' outer-level finding (see Constraints); solo on a card, ~67 GB of 80; hold profile with throat spheres, ψ4 14/18/30 | ~34 h | – |
| ☑ | spline t = 0 checks: 0.9c and 0.2c × N 96/128/192 | as the triplets | 0.5 | 1 | 0, 1 | DONE 13:47 MSK 10-17 (all six to t 0.5, `03_t0_checks/t0spline_*`): the table is fixed, the outer levels are not — see Constraints | finished | finished |
| ☐ | kick 0.9c, amplitude A1 | fast + seed | 150 | 2 | 0 | when the 2nd node frees ≈ 13:40 (~8.5 h run) | – | – |
| ☐ | kick 0.9c, amplitude A2 (×10) | fast + seed | 150 | 2 | 0 | after kick A1 (~8.5 h run) | – | – |
| ☐ | kick 0.7c, amplitude A1 | fast + seed | 150 | 1 | 1 | after the 0.9c N 96 (~8.5 h run) | – | – |
| ☐ | 0.95c stretch | fast | 150 | – | – | optional, only if the 0.99c curve wants the point | – | – |
| – | clamp validation (methods) | σ04 + mc4 + dt005 @ 0.5c | 100 | 1 | 0 | DIED 81.1 (NaN in K — the dt 0.05 instability, delayed 22 → 64 by σ0.4+floor); clamp validated in the clean window (ψ4@14 0.9 %, throat R 0.3 % vs parent); `06_dt_ladder/` | finished | finished |

**Throat check (10-17 ≈ 10:00 MSK) — the fast throats hold their size.** Areal throat radius (MOTS, or the
min over coordinate spheres of sqrt(A/4π) from the full metric of the live plotfiles):
0.5c 4.961 → 4.881 at t 80 (−1.6 %, slow shrink from t ≈ 45; 4.79 at 110) · 0.7c 6.873 → 6.871 at t 83 (MOTS, ≤ 0.05 %; after its
slicing breaks at 102 both measures drift: sphere R 7.41 at 109 → 6.81 at 125 → 7.75 at 135, MOTS 6.79–6.99 at 123–134) · 0.9c 18.476 at t 24–31 (N 96; equatorial circumference 23.82 flat to t 40;
later times from the N 96 rerun's plotfiles on node 1, TBD) · 0.99c 181.76 → 182.4 at t 120 (≤ 0.3 %, a long
marginal tube, R within 2 % from r 2.4 to 8). No fast throat shrinks: the 0.9c is stable to 150.
`throat_geometry.dat` is NOT a throat measure on the fast runs: its rays start at r = 0.6, inside the χ-floored
core, and the minimum lands there (0.9c from t ≈ 45, 0.99c from t = 0; the polar ray on the 0.7c too) — the
"0.9c 23.8 → 5.9 / 0.99c 101 → 76" readings are that core, as is the lapse → 0.001; the 0.9c N 96-vs-N 128
throat-ray comparison (0.6 % / 11 %) is void. The 0.7c's late |K| growth was the breakdown: it died at
t 135.85 (see the matrix; trust 102).
From 10-17 ≈ 10:40 MSK the consumer writes the throat per plotfile (`--throat-spheres` → `small_data/throat_spheres.dat`,
in the hold profile): live on the 0.99c (consumer restarted), in the 0.7c and 0.9c N 96 rerun drains, on every
future launch (the 0.9c N 192). Spinning paper runs differ by spin: static + 0.21c collapse (τ ≈ 5–6); 0.5c
shrinks slowly (−1.6 % by t 80); 0.7c holds its size (MOTS to t 83) but its slicing breaks from t ≈ 102 (NaN 135.85); 0.9c and 0.99c hold flat.

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
| `spin_hold_L64_ml3_ve050a_spdrv1_sig04_mc4_dt005_t100` | 0.5c | 64 | 0.4 | 0.05 | 1e-4 | 1.0 | DIED 81.1 (NaN in K): dt 0.05 K instability delayed (0.1 at 64.5) not cured; clamp validated t ≤ 70 (ψ4 0.9 %, throat 0.3 % vs parent) | 70 |
| `spin_hold_L64_ml3_ve090a_spdrv1_sig04_t150` | 0.9c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | CLEAN t 150: Ham flat (1.07e-2 → 1.17e-2 over 60 → 150); its all-nan MOTS rows were the finder's 400-step cap, not physics (the fast N 96 finds the throat surface, R 18.46, with 700–1200 steps; this run's plotfiles are gone) — the paper 0.9c run | 150 |
| `spin_hold_L64_ml3_ve070a_spdrv1_sig04_t150` | 0.7c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | DIED 135.85 (NaN in K; lapse floor 102.4), packed; the paper 0.7c run (fast recipe, 0.9c params + background swap); horizon rows nan at t 16–25 (the throat's θ_in mean stays ~1e-5, its max flips sign at noise level and the strict finder dropped it); consumer restarted 21:13 MSK with `--mots-spectral-untrapped --mots-spectral-warm-flow --mots-spectral-steps 1500`, rows again from t 26 (R 6.8704) | 102 |
| `spin_hold_L64_N96_ml3_J100_full_spdrv1_t85` | 0.21c | 64 (N 96) | 0.1 | 0.02 | 1e-8 | 1.0 | J=1 triplet N 96: FAILED 64.83 at the collapse end (not finished); R −1 % at 43; τ ≈ 5.4–6.6; archived 10-17, out of the paper folders | 58 |
| `spin_hold_L64_ml3_J100_full_spdrv1_t85` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | J=1 triplet N 128: through the collapse to 85; R −1 % at 47, 2.53 at 85; τ ≈ 4.7–5.8 | 66 |
| `spin_hold_L64_N192_ml3_J100_full_spdrv1_t85` | 0.21c | 64 (N 192) | 0.1 | 0.02 | 1e-8 | 1.0 | 0.2c (J=1) triplet N 192: DIED 78.66 late in the collapse (the collapse is the result: kept, 10-17); R −1 % at 56, 2.98 at 78; τ ≈ 5.5–6.5 | 75 |
| `spin_hold_L64_N96_ml3_ve090a_spdrv1_sig04_t100` | 0.9c | 64 (N 96) | 0.4 | 0.02 | 1e-4 | 1.0 | fast triplet N 96, SUPERSEDED (stopped at 100; the triplet window is 150): CLEAN t 100; MOTS t 24–26 only (its throat-ray comparison is void, see Throat check) | 100 |
| `spin_hold_L64_N96_ml3_ve090a_spdrv1_sig04_t150` | 0.9c | 64 (N 96) | 0.4 | 0.02 | 1e-4 | 1.0 | fast triplet N 96 rerun to 150: LIVE | tbd |
| `spin_hold_L64_ml3_ve099a_spdrv1_t150` | 0.99c | 64 | 0.1 | 0.02 | 1e-4 | 1.0 | stopped 50.4 (feasibility answered: Ham flat 3.94e-2, K flat, chi on the 1e-4 floor); paper 0.99c = σ 0.4 rerun | 50 |
| `spin_hold_L64_ml3_ve099a_spdrv1_sig04_t150` | 0.99c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | the paper 0.99c: clean t 150 (Ham 3.93e-2 flat, MOTS R 181.76 → 181.72) | 150 |

What the ledger says, four lines:
- sigma ≥ 0.2 kills the spin far-side puncture on the 1e-8 floor at any dt (0.4 by t ≈ 22, 0.2 slowly); the min_chi 1e-4 floor removes that failure mode.
- sigma 0.1 caps every slow run at the interior interface knee, Ham ×2 at 78–85, box-independent; the drive does not cure it.
- ONE-RECIPE verdict (died 81.1): sigma 0.4 + floor 1e-4 do NOT cure the dt 0.05 K instability at 0.5c, only delay it (K > 0.1 at 64.5 vs 22). dt 0.02 everywhere; the two-regime recipe is final. The probe doubles as the clamp methods check: physics unchanged vs the unclamped parent in the clean window.
- dt alone never killed a spin run; dt 0.05 needs sigma ≥ 0.3 (static) and the floor (spin).

## LIVE

| run | node/card | t @ 08:39 MSK | stop | speed (21:43 → 08:39) | ETA (MSK) |
|---|---|---|---|---|---|
| 0.9c fast N 96 rerun `L64_N96_ml3_ve090a_spdrv1_sig04_t150` | 1st, card 0 → freed | 150 done ≈ 12:30 | 150 | consumer drain | ≈ 10-17 14:45 (drain) |
| 0.7c extra run, slow recipe `L64_ml3_ve070a_spdrv1_t100` | 1st, card 0 | 16.4 @ 13:48 | 100 | 15.8 t/h | ≈ 10-17 19:05 |

**Constraints on every level (checked 10-17, `constraint_norms_levels.dat`, r < 0.125 masked).** 0.2c: only the finest level (|x| < 4, around the throat) converges, order 3–4 from t ≈ 1 (Ham 3.7/2.7, Mom 3.5/3.7 at t 20); levels 0–2 GROW with N (order −0.4 to −4). 0.9c: no level converges (order −0.3 to −1.8 at t ≤ 2.4 for all three; N 96 → N 128 at most +1 through t 150). Likely causes, to be tested: the background table's bilinear interpolation (the atan map thins its points at large radius, and finite-difference second derivatives of a piecewise-bilinear field grow like (Δ_table/h)² as the grid refines) on the outer levels; on the 0.9c's finest level, the χ floor (1e-4) clipping the core out to r ≈ 0.6, beyond the r < 0.125 mask. Until fixed, the fast triplet's convergence rests on the throat size and the lapse, not the constraints. **Confirmed 10-17 ≈ 13:45 (CPU check on both tables, equatorial row):** 4th-order FD second derivatives of the linearly interpolated f and nu_bar get WORSE with N on every level (order −0.8 to −2.8); a C2 cubic spline of the same table converges (order +4.2 near the throat). Fix = spline interpolation in RotatingBackgroundTable, then a t = 0 constraint check at N 96/128/192, then the triplets on the fixed data.

**Spline checks (10-17, done 13:47 MSK; binary faadc95e, `03_t0_checks/t0spline_*`, both tables, N 96/128/192 to t 0.5).** The table is fixed: on CPU the spline's Cartesian 4th-order second derivatives (xx, zz, xz) of f, nu_bar and phi converge at order +4.0 on levels 1–3 (bilinear −0.9 to −1.8). On the GPU at t = 0, Mom converges on levels 1–3 (order +2.2 to +3.7; bilinear −0.7 to −1.2 on levels 1–2), Ham on levels 1–2 is 5–100× lower, and level-3 Ham converges N 96 → 128 (+3.2/+3.3) but flattens N 128 → 192 (+0.5/+0.75). **Not fixed: a second, table-independent source on levels 1–2.** Ham there still grows with N at t = 0 (order −1.4 to −1.6, both tables), and Mom there grows from the first step on (order ≈ −2, both interpolations, spline 6–120× lower). A −1.5 order fits a fixed jump on a surface (the coarse–fine boundaries are the suspect; unproven). Level 0 is identical bilinear vs spline (order −0.4, the box boundary). On the 0.9c, level 3 after the first step is the χ-floored core (Ham 3e-4, Mom 1.8e-3, the same both ways): its mask r < 0.125 is too small (the floor reaches r ≈ 0.6).

**0.9c throat may be INFLATING after t ≈ 40 (10-17).** The N 96's throat measure (outermost minimum of the coordinate-sphere areal radius) reads R 20.98 at t 79 → 21.68 at t 103, against 18.49 at t 0 (+13 → +17 %); the minimum moved out in coordinates (r 1.76 → 6.7) and the region inside it bulged (R ≈ 28 at r ≈ 2). Caveat: this measure overestimates a deformed throat (up to 9 % over the horizon finder on the 0.7c); the 0.99c reads flat with it (182.4 → 183.0). The "0.9c holds flat to 150" above rests on t ≤ 40 only — open until the fixed-data triplet with a proper surface finder.

**N 96 frames were drawn 2× (found 10-17, renderer fixed ≈ 13:00 MSK).** yt's SlicePlot through a plane exactly on a cell face (z = 32 on the N 96 grids) summed the cells on both sides: every field in the N 96 runs' frames and slice caches is exactly 2.000× the plotfile (0.2c N 96, 0.9c N 96 `_t100` and `_t150`). The evolution data and every number from them are unaffected (t = 0 throat rays agree with N 128/192 to 0.03 %); N 128/192 frames are right. The consumer now slices a millionth of a cell off the face; live consumers pick it up per batch. Frames rendered before the fix stay 2× until repaired.

0.9c triplet window = t 150 (the fast recipe's stop, as its N 128 member). 10-17: the N 96 reruns to 150 on card 0
(launched 09:11 MSK, t = 0 Ham bit-identical to the `_t100` run, frame 0 identical, ψ4 14/18/30); the N 192 to 150
aborted at start beside it (Arena out of memory at 64 GB of 80; run dir in `drainhole/00_archive/aborted_2026-10-17/`,
6.7 GB scratch pruned) and was relaunched solo on card 1 at 12:23 (67.3 GB of 80). The N 96 rerun's consumer lags the
solo run (plotfile every ~1.3 min); the drain finishes after the run. The solo N 192 was stopped 10-17 ≈ 13:30 MSK at t 4.67 by decision (bilinear table data): run dir moved out of the paper runs to `drainhole/00_archive/aborted_2026-10-17/…_t150_bilinear`, 27 GB scratch pruned, registry row removed; the N 192 is not started on the fixed data.

Closed out 10-17 ≈ 08:45 MSK (packed to `00_paper_runs/`, 16 files each; scratch pruned, 14.3 GB):
- J=1 N 96 DIED 64.83 (NaN) at the end of the throat collapse (FAILED, not finished; pulled from the paper
  folders 10-17 and archived); J=1 N 128 ran to 85
  through it. The collapse is in every member, onset later with N (MOTS R −1 % at
  t 43 / 47 / 56 for N 96 / 128 / 192), growth time similar (τ ≈ 5–6.5 from the
  MOTS deficit, window-dependent) — a resolution-seeded onset, rate set by the
  physics. Members agree on R to 0.1 % only to t 30 (N 96) / 37 (N 128).
- 0.9c fast N 96 `_t100` CLEAN t 100 (superseded: the triplet window is 150, rerun live): Ham flat 9.3e-3 → 9.6e-3 (the throat-ray
  comparison with the N 128 is void: see Throat check). MOTS only t 24–26 (R 18.476): from
  t 27 the lmax-6 surface stalls at rms θ_out 2–3e-3, later the flow hits the inner
  floor. The fast N 192 template should carry the three MOTS flags and lmax 8 (test first).

0.9c `ve090a_spdrv1_sig04_t150` FINISHED CLEAN t = 150 ≈ 15:05: Ham flat
(1.07e-2 → 1.17e-2 over t 60 → 150), max|K| flat 2.0e-2 (its "no MOTS" was the finder's 400-step cap: the fast N 96
finds the throat surface at R 18.46) — the
stability claim delivered, trust full 150. Moved + packed `00_paper_runs/`;
scratch pruned (7.1 GB). The paper 0.7c run launched ≈ 15:15 on its card from the
0.9c params (background swap only, diff-proven).

0.5c drive `ve050a_spdrv1_t150` FINISHED-DEAD: NaN (h11, L3) at t = 130.0. Clean
through the Ham ×2 knee (~83); then Ham 0.157@110 → 0.367@120, max|K| > 0.1 at
t ≈ 110, lapse pinned 1e-10 by 128 — the slow recipe going unphysical long, as
the two-regime split predicted. Trust 80; moved + packed `00_paper_runs/`;
scratch pruned (7.1 GB).

Notes: every live run no-checkpoint, spdrv binary, full frames, keep-last 3.
psi4 radii 14/18/30 on every run — baked into the hold profile 2026-10-16 after
the triplet went up on the old 14/30 default; the three J=1 members' consumers
were restarted with --radii 14 18 30 at t <= 5 (earlier rows 2-radius, read by
row width, nothing physical lost: waves start at the ~64 collapse). The node-2
pair (0.7c, 0.99c) still runs 14/30 — fast end, stability claim, no waveform
quoted; restart needs a node-2 session if R=18 is wanted there.
The packed 0.99c σ 0.1 probe's psi4 is 3-radius (14/18/30) from t = 22 only — the consumer was killed by a
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

Current queue (2026-10-16 ~19:45 MSK; the PAPER RUN MATRIX above is the
authority — this is the launch order on freed slots). Every launch waits for
its go; no queued run writes or needs checkpoints.

| next free slot | run | needs |
|---|---|---|
| node 2 now (a session there; nothing to kill) — or node 1 card 0 after the 0.7c extra run (≈ 18:25) | **0.9c N 128 + N 96 throat reruns** (`…_t150_thr`): same params as the packed runs (templates diff-proven: paths only), hold profile (throat spheres, ψ4 14/18/30), no checkpoints; both on one card (39 GB) ≈ 12 h | go given 10-17 |
| node 2, free since ≈ 12:19 MSK (0.7c died, 0.99c done) | kick 0.9c A1, then A2 (×10) | kick templates: seed amplitude A1 = merger seed scale |
| node 1 gpu 1, after fast N 192 | kick 0.7c A1 | same template, ve070 background |
| anywhere, only if the 0.99c curve wants it | 0.95c stretch | background fam_a_ve095 |

**Kick (perturbed-stability) study — planned 2026-10-16.** As in
Evstafyeva–Siemonsen–East (arXiv 2508.11527): the fast-end holds are so far
stable only against truncation error, so rerun the stable 0.9c (A1 and ×10)
and 0.7c (A1) with the Gaussian scalar seed (`spinning_seed_amplitude/width/
radius`, constraint-compatible as in the merger paper's kick), fast recipe,
stop 150. Discriminators: ring-down back to the hold vs triggered collapse;
ψ4 response at R 14/18.

**Convergence: two triplets on the L64 production box** (policy 2026-10-16;
both LIVE or done — see the matrix): slow at the J = 1 rung (N 96/128/192,
licenses the fast rungs via the published O(J²) rate), fast at 0.9c
(N 96/128/192 to t 150 — the recipe's stop, as the paper 0.9c run, which is the middle member). The L128 N 256 run
keeps the model-check and box-independence roles; the L128 N 192 rerun and the
155 GB N 384 are DROPPED.

Everything below this line is the 10-13/10-15 planning record (launch freeze,
L128-box policy, L128 triplet ladders) — SUPERSEDED by the two-regime L64
recipe and the matrix above; kept for the paper trail only.

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
