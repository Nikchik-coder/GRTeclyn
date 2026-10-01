# Status — 2026-10-01 07:25 UTC (compacted; the full pre-compaction page is in GPU_PLAN.md ["2026-09-30 (~07 UTC) — STATUS.md compacted"])

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes; keep it this size.**

## RESULT (in the paper since 2026-09-30): a moving wormhole collapses under its own unstable mode

`single_boost_p045_lbf_t050` (one exact Lorentz-boosted drainhole, momentum model 1, p = 0.45, v = 0.41, L = 64,
level 3, the per-throat slicing freeze; packed `campaign/02_moving_throat/exact_boost/`): the throat holds while
moving (R_min at most +2.0 %, t = 29), falls 1 % below its start at t = 36.8 (the resting level-3 throat: t = 44),
collapses on the resting throat's own mode (τ = 5.5–5.7 against 5.88; same branch — level 3 collapses) and dies at
t = 44.67 (NaN in h11, χ at the pit on its floor: numerical, inside the collapse). Gauge and boundary ruled out.
- **In the paper (2026-09-30):** Sec. III "The throat in motion" + Fig. 2(d); the boosted setup is
  Sec. II "Throats with momentum" + Fig. 1 (`boost_contraction`). Every number is a ledger row (`clmBoost*`).
- **Level 4 agrees (the twin `single_boost_p045_lbf_ml4_t060`, closed out 05:10 UTC 10-01; packed beside it):** it
  collapses too, although the resting level-4 throat inflates. R_min peaks at +1.4 % (t = 30), falls 1 % below its
  start at t = 40.4 (level 3: 36.8), and reaches −11.4 % at t = 48 and −30.1 % at 53. τ = 5.0–5.7 over t = 44–53.
  It dies at t = 53.43 (NaN in h11, level 4). The onset comes ~4 units later. Not cited yet; citing it is the
  user's call.

## CRITICAL: the momentum setup (2026-09-29) — every p > 0 run so far was a round throat at rest

A throat with momentum is the exact drainhole Lorentz-boosted: squashed along the motion by
1/γ = m/√(m² + p²) (9 % at p = 0.45), its scalar moving (Π ≠ 0), its own K_ij, lapse and shift. Every old p > 0
run used Bowen–York K_ij on round, conformally flat data with the scalar at rest — the black-hole recipe. The
mismatch reads as a −ε kick growing as p² that inflates the throats: p = 0.45 reaches +10 % by t = 20.2
(ε_eff ≈ −1.8 %), p = 0.12 is ε_eff ≈ −0.15 %.
- **The fix:** `wormhole_momentum_model = 1` (dc34eb51, exact boost, model 0 unchanged and warning) + the
  per-throat slicing freeze (`core_freeze_track_throats = 1`; the collar lapse broke the boost instead) + the
  boosted-pair solve for (w, W) with the companion's K_ij/Π cut inside each throat (91ed17cd).
- **Verified:** the solve is idle on a lone boosted throat (|w| ≤ 5e-7, far side to 4e-7); the rest pair
  reproduces the model-0 mode-3 solve to ~1e-5; the p = 0.25 flipped pair on the production grid PASSES at t = 0
  (far sides to 1e-5, R_min +0.09 %, shell Ham ≤ 7.8e-5); its L = 64 level-3 twin ran clean to t = 20, no NaN
  (its Ham "spikes" are the level-0 norm's pit cells — see Traps); the measured t = 0 axis ratios sit on 1/γ to
  6e-5 at every p (the shape set, below).
- **Overturned:** the p = 0.45 fly-by (`merge_orbit_flip_d12_p045_L128_lvl5_t100_csm`, stopped t = 64.98, not
  packed, frames kept) and §VII.A's capture boundary. **Clean:** the head-on and the rest pairs (p = 0).
  Every p > 0 result waits for a rerun on boosted data.
- p = 0.45 is extreme (v = 0.41 per mouth, 0.70 relative); binary production stays at p ≤ 0.35 unless a clean
  rerun places the capture boundary above that.

## CRITICAL: superposed initial data (2026-09-28) — every binary before the csm campaign

The superposition is not a solution: each mouth 9–15 % oversize (one-body mass 1.149 at d = 8, 1.094 at d = 12),
M_ADM misses the interaction energy. No binary number is final until remeasured on mode-3 data
(`constraint_solve_puncture_mode = 3`, name token `csm`).
- **RULE for every rerun:** the old run's packed `evolution_params.txt` with ONLY the initial-data block changed
  (checkpoints only on the user's word; plot variables for the frame set are output-only). Diff before launching.
- Rest pairs rerun and closed out (`03_two_throats/csm/`, five runs to t = 15, clean): pull/push
  **1.463 ± 0.023** (superposed 1.518; fixed potential 1.500 — the headline; fixed charge −0.667 excluded);
  force-law δ = 2.65 (superposed 3.56). In the paper.
- Framing rule (the user): the old constraint state is barely mentioned; mode 3 improving the constraints is the
  headline, and the old campaign becomes the systematics study.

## The plan, in order (the user, 2026-09-28)

1. **Energy check** — done: the pair acts at fixed scalar potential (Sec. II D; `t0_matching/energy_scan.tsv`).
2. **Rest pairs + head-on** — rest pairs done (above); the head-on runs as legs 1–3 (second node, below).
3. **The orbits on mode-3 boosted data**: spiral p = 0.12 (+ level-4 twin), fly-by p = 0.25 (live since 12:37 UTC 09-30) and
   p = 0.45, boundary p = 0.35. The lvl5 spiral rerun runs on the first node's card 0 since
   11:55 UTC 09-30 (its verification A passed).
4. **Single throats on clean data** (12–25 h, settles the regrowth question).
5. **Rewrite** (once the production runs are in):
   - initial-data story once, in order: superposition (one line) → Helfer correction (tested, stalled, not
     adopted; no reruns; twins stay in Table I systematics) → mode 3 as the headline;
   - every binary number from mode-3 runs; old campaign = systematics; CS-1 = old-vs-clean table;
   - new definitions (each wormhole's mass, the pair's mass, p in true units);
   - boosted-setup section + validation figure — **DONE 2026-09-30** (Sec. II, Fig. 1);
   - moving-throat section — **DONE 2026-09-30** (Sec. III, Fig. 2(d));
   - boosted single throats section (inflation/collapse vs p, ε_eff ladder) once the probes are closed out;
   - withdraw §VII.A's capture boundary until p = 0.35/0.45 rerun on fixed data;
   - branch-selection finding: every companion is a −ε kick (−0.4 % at d = 12, −1.2 % at d = 8, same in
     superposed and mode-3 data); a merger is a race against contact (head-on MOTS t = 22 beats +10 % at t ≈ 23;
     the spiral's contact t ≈ 40–45 loses); design rule for a collapsing spiral: d = 8, small p. Open before the
     text states the mechanism: which piece carries −ε (tail gradient vs tide; cheap t = 0 test in GPU_PLAN);
   - re-measure Sec. II D's solve paragraph on mode-3 data (t = 0-only start on CS-1's grid, the paper's only
     per-level constraint number); the scalar energies (`clmGwScalar*`) are partly near-field and change;
   - every extractor/figure that moves to csm runs: `CSM_SWITCHOVER.md`.
6. **Longer GW runs** with farther spheres — proposed, not queued (flat-space ℓ = 1 fit is the estimator;
   free: extra scalar radii on the reruns, output only).

Constraint norms are not a paper problem: the logged ℋ is the base-grid box average (discretisation floor of the
smaller matched throats), every paper claim is relative, and the mode-3 reruns' norms match or better their
superposed twins (checked 09-28/09-29; details in the archive).

## Live — first node (two H100s): card 0 the boosted spiral, card 1 the boosted fly-by (both production)

| card | run | t now | t end | speed | ETA |
|---|---|---|---|---|---|
| 0 | `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` (SPIRAL-lbf, the user's go 06:38 UTC 09-30: the csm spiral's params with only momentum model 1, the boosted shift and match tol 1e-5 changed; **no freeze**; max_level 5; checkpoints every 5 units keeping 3; `main3d_boostpair_91ed17cd`, profile `orbit-modes-prod`) | 2.22 (13:17 UTC 09-30; alive, no NaN; mouths R_min 3.8784 / 3.8783 at t = 1 / 2; level-0 L2 H 1.66e-3 (the csm spiral: 1.30e-3 at t = 2), L2 M 8.3e-6) | 100 | 2.1–2.2 u/h (16.7 s per coarse step, the csm spiral's start) | t = 60 in ~22 h, ~10:30 UTC 10-01; t = 100 in ~32 h (~20:30 UTC 10-01) if it speeds up after t ≈ 35 as the csm spiral did (to 4 u/h), ~48 h (~12:15 UTC 10-02) at the present pace; first rolling checkpoint (t = 5) ~14:40 UTC |
| 1 | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` (FLYBY-lbf, the user's go 12:35 UTC 09-30: the old fly-by's params with p = 0.45 → 0.25, momentum model 1, the boosted shift, the per-throat lapse freeze and match tol 1e-5; max_level 5; checkpoints every 5 units keeping 3; in-code Ψ4 on the set's 24 × 37 grid, 21 modes; `main3d_boostpair_91ed17cd`, profile `orbit-modes-scan-prod`) | 0.74 (13:17 UTC 09-30; alive, no NaN; the solve as its verification A: far sides to 9.4e-6, mouths R_min 3.8807; frame 0 as A's; 21 in-code Ψ4 modes written; level-0 L2 H 1.5e-3, L2 M 1.7e-5) | 100 | 2.17 u/h (16.6 s per coarse step) | t = 100 in ~46 h, ~11 UTC 10-02, if the throats stay apart (sooner if they merge) |

- Its verification A (`t0_v2_spiral_d12_p012_L128_lvl5_lb_csm`, the rerun's template stopped at t = 0.5;
  finished 07:17 UTC 09-30): **PASS** — solve converged (22 Newton passes, 2 matching rounds), far sides the
  isolated throat's to 4e-6 (one-body a 2.0000, m 1.0000), mouths R_min 3.8780 each (isolated 3.8772, +0.02 %;
  the p = 0.25 pair's +0.09 % × p²), throat-shell Ham rms 7.8e-5 / 2.9e-5 / 5.1e-5 on levels 3 / 4 / 5 (the
  fly-by pair's floor), axis ratio 0.9919 / 0.9914 at r_c = 1 / 1.55 against 1/γ = 0.9929 (0.10–0.15 % flatter,
  the p = 0.25 pair's × p²), no NaN, frame 0 as the csm spiral's. **Packed 12:06 UTC** without movies
  (`05_binary_spiral/verify_p012/`); its scratch (two plotfiles, 21 GB) wiped 12:14 UTC on the user's word.

The fly-by's gate (the user, 19:18 UTC 09-29: "we need to be sure this time the fly-by is correct, only after
that we can launch") was lifted by the user's go at 12:35 UTC 09-30. Its verification state at launch:
- A (its own t = 0 on the production grid): **PASS** (far sides to 1e-5, mouths +0.09 %, shell Ham ≤ 7.8e-5;
  the solved pair is 0.4–1 % flatter than 1/γ, ∝ p², the solve's interaction — real, not resolution).
- e2e (one boosted throat to t = 50): **PASS** — no gauge runaway; dies at t = 44.67 of its own level-3 collapse
  (the RESULT above), not the boundary.
- B (the pair on the L = 64 level-3 grid to t = 20): ran clean, no NaN; the Ham spikes are the level-0 norm's
  pit cells (artefact). **Open:** B's mouths inflate (+3.6 % at t = 20 against the rest pair's +0.6 % at t = 15
  — the throats' own mode, kicked by the companion), and its infall matches the old p = 0.45 fly-by's exactly,
  so B does not decide plunge vs fly-by. Both packed `06_binary_flyby/verify_p025/`.

Recently closed out on this node (packed; scratch wiped 06:01 UTC 09-30, `MANIFEST_CLEANUP_2026-09-30`, no
checkpoint left): the csm spiral `v2_spiral_d12_p012_L128_lvl5from0_t100_csm` (stopped t = 60.40 by
`dump_and_stop`: **it does not end in a merger** — anti-trapped surfaces, no MOTS at t = 53–58.9, max|K| falling;
trust window 57; `05_binary_spiral/csm/`); the three mode-3 momentum probes (`single_{rest,boost_p012,boost_p045}_csm_t050`,
stopped t ≈ 32–33); the exact-boost e2e chain (`02_moving_throat/exact_boost/`; the `lb` and collar `lbc` arms
died at t = 26.1 / 37.6, not packed, frames kept); the t = 0 solve tests (`t0_*_lbcs*`); the shape set (below).

## Second node (one H100): free since 06:50 UTC 10-01 — its next launch waits for the user's go

**HFL-ho closed out (07:25 UTC 10-01; `04_binary_headon/first_law/`, no movies, frames kept).**
`merge_headon_flip_d8_v1_L128_lvl4from50_hfl_t060_csm_r05000` reached t = 60 (06:50 UTC) with no NaN, and every
stream is bit-identical to leg 3's.
- **The first law:** the common MOTS (spectral finder, level 3) is steady over t = 51–60: R 4.7776 → 4.7734
  (t = 58) → 4.7735, while it rounds. The measured ΔR −0.00411 lies between the phantom-only prediction (−0.00704)
  and flux plus shear (−0.00252); the late regrowth comes from the shear.
- **Both scans under-read it there:** the round scan by 11 → 4 %, the oriented scan by 7.4 % (t = 55) and 3.2 %
  (t = 60). Fig. 5(a,b)'s gold line and its end values rest on them. MOTS-ho (queued, below) would settle it; the
  user's call.
- Its 11 plotfiles (60 GB) stay on scratch on the user's word. Details in GPU_PLAN ["2026-10-01 (07:25 UTC)"].

**The level-4 twin closed out (05:10 UTC 10-01):** `single_boost_p045_lbf_ml4_t060` died at t = 53.43 (23:51 UTC 09-30, NaN in h11, level 4; stop 60).
It collapsed like the level-3 run (RESULT, above). Closed out 05:10 UTC 10-01: filed to `02_moving_throat/exact_boost/`,
no movies (as the level-3 run), trust window t ≤ 53; its three plotfiles (8.8 GB) wiped 05:04 UTC.

**NOISE-1 closed out (17:50 UTC): the level-1 noise is under-dissipation.** `merge_headon_flip_d8_v1_L128_lvl4from50_sig03_t080_csm_r05000`
(leg 3 again from `Chk05000` with σ 0.1 → 0.3) reached t = 80, no NaN, and has no level-1 noise: (3,2) at R = 20
1.0e-5 against leg 3's 2.9e-4 over t = 75–80; the K ring 7.5e-6 against 1.0e-4 at t = 80; L2 H 1.01e-4 and falling
against 1.37e-4 and rising; the rebuilt level-1 constraint 2–7e-5, flat (leg 3 at t = 100: 1e-2). Waves on R = 36/44
and the remnant's MOTS unchanged. Packed in `campaign/08_convergence/` (`VALIDATION.md`), no movies; its plotfiles
wiped 17:48 UTC on the user's word.


**The mode-3 production head-on (legs 1–3) is done, validated and packed** (13:06 UTC 09-30,
`campaign/04_binary_headon/csm/`; tables in leg 3's `VALIDATION.md`; movies per leg and the three legs as one film
t = 0–100 in `runs/.../04_binary_headon/csm/headon_csm_L128_stitched_t0_t100/movies/`).
- Chain: leg 1 (level 5, t = 0–35; died at t = 38.845 at the merged core, as the uncheckpointed run) → leg 2
  (level 6 from Chk03500, through the wall, stopped by hand at t = 50.80) → leg 3 (level 4 from Chk05000, t = 100
  at 11:25 UTC, no NaN). Seams continuous (norms to 1.4 % / 0.1 %, in-code Ψ4 identical on the overlaps).
- Result: common MOTS first at t = 22 (R 5.02, M_MS 2.69), found every unit t = 36–100; R 4.25–4.70, M_MS
  2.29–2.39; at t = 100 R 4.69, M_MS 2.373 by the oriented scan (M_ADM 2.357). The ringdown swings repeat the
  superposed run's (r Ψ4 (2,0) at R = 10: +0.0240, −0.0207, +0.0126, −0.0066 at t = 28.8, 44.2, 63.0, 81.7).
- **Caveat (new, see Traps): numerical noise on the level-1 cube from t ≈ 65**, the late rise of L2 H. In-code Ψ4:
  R ≤ 20 good to t ≈ 80, R = 28 to t ≈ 90, R = 36 / 44 to t = 100. Remnant and MOTS untouched. No trust-window
  row (the limits are per sphere); the films run to t = 100 on the user's word and show the speckle from t ≈ 85.
- Scratch on this node: the chain's plotfiles wiped 13:38 UTC 09-30 and NOISE-1's 17:48 UTC, both on the user's
  word (`MANIFEST_CLEANUP_2026-09-30`); the twin's 05:04 UTC 10-01 at its close-out (`MANIFEST_CLEANUP_2026-10-01`).
  Left: leg 1's `Chk03500` (26 GB) and leg 2's `Chk05000` (28 GB), MOTS-ho's inputs, plus HFL-ho's 11 plotfiles
  (60 GB, kept on the user's word 10-01). 557 GB free at 07:25 UTC 10-01.

## The production set (shared box; the user, 2026-09-28 09:00 UTC)

L = 128, N = 256, max_level 5, tagging_L 64, sponge 48/64, plots every 1.0, mode-3 data. Status: **head-on**
(p = 0, clean of the momentum issue) done to t = 100 as legs 1–3 (`main3d_csmatch_5f988dbc`); **spiral** live as the
boosted rerun (the Bowen–York one stopped at t = 60.40, closed out); **fly-by** live as the p = 0.25 lbf rerun (the Bowen–York
one stopped at t = 64.98, overturned). Templates in `runs/wormhole_merger/templates_scan/`.

**Wave settings, the same in every run of the set (the user, 2026-09-30; checked 12:25 UTC against each run's
`params.txt`, manifest and output headers):**
- in-code Ψ4 (`Weyl4_mode_*.dat`, every coarse step): spheres 20/28/36/44, 24 × 37 points, 21 modes (l = 2–4,
  every m);
- consumer (every plotfile, 1.0): scalar modes l = 0–2 and the python Ψ4 l = 2 modes on spheres 14/20/30/44.
- Head-on, all three legs: these plus its old spheres (in-code Ψ4 also at 10/14/18, consumer also at 10/18), the
  same in each leg, t = 0–100 covered (legs 2–3's restart files carry no header; columns as leg 1's).
- The spheres against the grid (head-on, merged): R ≤ 20 lies inside the level-1 cube, R = 28 (and the consumer's
  R = 30) cuts its corners, R = 36 / 44 are on level 0 — the last two are the clean ones late (Traps).
- Spiral (live): exactly the shared set.
- Fly-by (live, launched with the fix): radii the shared set. **Fixed 12:27 UTC:** its template had no angular-grid or mode lines, so
  the in-code Ψ4 would have run on the code defaults (2 × 5 points, three l = 2 modes), as the overturned p = 0.45
  fly-by did; the head-on's and the spiral's lines are added (output only). Its verification A predates the fix
  (initial data only, unaffected).

## Done — the boosted shape set (t = 0; packed `campaign/02_moving_throat/contraction_t0/` + `boost_contraction_t0.tsv`)

| p | v | 1/γ | measured axis ratio |
|---|---|---|---|
| 0 | 0 | 1.00000 | 1.00000 |
| 0.12 | 0.119 | 0.99288 | 0.99288 |
| 0.25 | 0.243 | 0.97014 | 0.97015 |
| 0.35 | 0.330 | 0.94386 | 0.94387 |
| 0.45 | 0.410 | 0.91192 | 0.91195 |

The paper's Fig. 1 (`plot_boost_contraction`); residual < 6e-5 at every p and three contour levels.

## Queued — mode-3 follow-ups (the user, 2026-09-28 ~11 UTC; nothing launches without the go)

Fig. `fig:spiral_ladder` panel (b) (slicing/gauge) is done on superposed data and is not rerun; panel (a), the
ladder, reruns on mode-3 data. Note 2026-09-29: the spiral's every-5 checkpoints were wiped with the first
node's scratch (06:01 UTC 09-30), so LAD-csm needs a fresh checkpointed leg or restarts from a rerun's.

| id | run | what | how | GPU-h |
|---|---|---|---|---|
| SPIRAL-lbf | `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` | THE PAPER RUN, FIRST (the user, 2026-09-30): the spiral on the boosted setup — the clean test of "inflates, no merger" | the csm spiral's template + momentum model 1, **no freeze** (the user's word; the pits move at v = 0.12, the runaway was a v = 0.41 problem), max_level 5, checkpoints every 5 keeping the newest 3 (the user's word; LAD-csm needs the t ≈ 50 one); its own verification A **PASSED**; **LIVE on the first node's card 0 since 11:55 UTC 09-30** (Live, above) | ~22 to t = 60, ~37 to t = 100 |
| SCOUT-d8p | `spiral_d8_p005/p010_lvl3_t040` | IF the clean spiral again fails to merge: the collapsing-spiral design point (contact must beat the mouths' runaway; the head-on's d = 8 contact at t = 22 wins, d = 12's t ≈ 40 loses) | new setup, so level-3 scouts first (~2–3 h each, L = 64), then level 5 for the winner | ~5 + ~21 |
| FLYBY-lbf | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` | the fly-by rerun | **LIVE on the first node's card 1 since 12:37 UTC 09-30** (Live, above) | ~46 to t = 100 |
| LAD-csm | `ladder_csm_L{4,6,7}_r0XXXX` | the wall under refinement, mode-3 (Fig. 12a's rerun) | restart from a checkpointed spiral leg at t ≈ 50, max_level 4/6/7, ~10–15 units per arm; convergence rules (no frames, `WHM_MOVIES=0`, `08_convergence`) | ~15–25 |
| BBH-HEADON | `bbh_headon_d8_L128_lvl5_t100` | the vacuum control for the head-on (the user, 2026-09-30): bare punctures at d = 8 from rest, t = 100, for Fig. 5 and the gallery/energy comparison | the csm head-on's setup (same box, grid, spheres, plot cadence) with the drainhole/scalar blocks swapped for bare punctures, as the d = 12 BBH controls; template from `bbh_control_d12_p012_t150`'s params with d and p changed; checkpoints asked at launch | ~30–50 (the head-on chain's class; vacuum punctures ride through a merger, so likely one leg) |
| MOTS-ho | `merge_headon_flip_d8_v1_L128_lvl4from50_mots_t100_csm_r05000` (+ `..._lvl6from35_mots_t050_csm_r03500`) | the head-on's true horizon for Fig. 5(a,b) and its end values: on HFL-ho's slices both scans under-read the MOTS by 3–11 % (GPU_PLAN 10-01 07:25 UTC) | leg 3 again from `Chk05000` to t = 100 (and leg 2 again from `Chk03500`, t = 35–50, level 6), each the packed params with only the stop and the name changed; every plotfile kept (~275 + ~100 GB) for `headon_first_law.py`; no checkpoints; leg 1 from t = 0 (~13 h) only to re-read the birth at t = 22 | ~7 (+ ~7.5) |
| A1-csm | `ctrl_rest_a1_csm` (then, optional, `ctrl_rest_a15_csm` / `ctrl_rest_a3_csm`) | restore Fig. 4(a)'s width arm on matched data (the a = 1 arm left the panel 09-30: no matched twin) and put clmNarrowPairRatio — and with the optional twins the §V.B width ladder clmALadder* — on mode 3 | the old run's packed `evolution_params.txt` with ONLY the constraint-solve block and the name changed (the rest-pair rule), t = 15, L = 64 level 3; checkpoints asked at launch; re-measure into `matched_rest_displacement.dat` and redraw Fig. 4(a) | ~1 each (the csm rest pairs' class: 18 u/h alone) |
| PLACE-csm | `place_d{6..48}_step1_csm` (the 18 one-step probes) | the matched placement curve for Fig. 4(d,e), now captioned as superposed-only: expected flat at R⋆ = 3.8895 (the matched pairs read 3.876–3.878 at t = 0), which would draw the clean-data contrast under the superposed excess; re-measures or retires clmMouthTauFlybyPlaced/SeedFlybyPlaced (CSM_SWITCHOVER) | the superposed probes' params (`04_binary_headon/placement/place_d*_step1`) with only mode 3 + names; initial data plus one step, scanned at t = 0; no frames beyond the default t = 0 set | < 1 total (minutes per probe) |
| CONV-csm | `v2_spiral_d12_p012_L128_lvl4from0_t100_csm` | spiral burst/energy, level 4 vs 5 | the spiral template, max_level 4, from t = 0 | ~8–10 |
| EGW-p06 | `merge_orbit_flip_d12_p060_lvl5_t040_csm` | E_GW(p) above the fly-by (turnover) | fly-by template, p = 0.60, stop ~40; junk ∝ p², read the Newton passes at start | ~8–12 |
| EGW-p09 | `merge_orbit_flip_d12_p090_lvl5_t040_csm` | E_GW(p) far side of the peak | same, p = 0.90 | ~8–12 |

Also waiting: p = 0.35/0.45 boundary reruns (step 3), clean-data single throats (step 4), the spiral freeze
continuation (from a checkpoint ≥ 55 of the rerun, fill armed from ITS core profile). The old-data convergence
queue (CONV-1..8) is **cancelled** (step 3's twins replace it); templates and launch lines in the GPU_PLAN
archive. Checkpoints: asked per run at launch, never on by default.

## Verdicts (the paper's wording; every binary verdict is on superposed data and stands only until its mode-3 rerun)

- **Single throat**: unstable fixed point, one exponential mode within 2.5 % (level 4) of the matched
  González–Guzmán–Sarbach rate; truncation noise picks the branch. Collapse horizon shrinks 40 %; the 9–11 %
  "regrowth" is numerical. Inflation (F4, quotable to t = 218): keeps growing, anti-trapped, Shinkai–Hayward
  rate in proper time; the late slowdown is the slicing. **New (2026-09-30): a moving throat collapses on the
  resting throat's mode (the RESULT above; in the paper), at levels 3 and 4 (the twin, 10-01).** (§III–IV)
- **Seeded throat**: fate opposite to the kick; ε = ±0.1 both collapse and die at the origin. (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻²; **mode-3 rerun done: ratio
  1.463 ± 0.023 = fixed potential, δ = 2.65 — in the paper. Fig. 4(a–c) draws the matched pairs since 09-30**
  (abstract and caption quote the ledger's 1.462 ± 0.022; the a = 1 arm left panel (a) — no matched twin;
  (d)/(e) stay on the superposed placement probes, the superposition systematic itself). (§V)
- **Head-on**: common MOTS from t = 22 around both throats; never bounces; shrinks toward the pair's Bondi
  mass. **Mode-3 chain done (t = 100, closed out 09-30): MOTS at t = 22 with R 5.02 (superposed 5.56), there to
  the end (R 4.69, M_MS 2.373 against M_ADM 2.357); the same ringdown swings. **The FIGURES read the mode-3
  chain since ~14:30 UTC 09-30** (the user): Fig. 5 is the three-leg composition (new caption: the h11 NaN at
  t = 38.845, the seams, the settle onto 2 M_ADM = 4.71), the wave figures (gallery / ligo / heavy_seeds, one
  ARMS row) read the glued `04_binary_headon/csm/.../SERIES` stream (M_ADM 2.3573, ARMS gate t = 76, level-1
  noise draw gates 80/90/100), and heavy_seeds (b) gains the head-on burst at 1e5 Msun; 16 ledger rows
  re-measured, 14 added, 1108 rows, 0 problems. §VI's TEXT still reads the superposed runs
  (`CSM_SWITCHOVER.md`; the rewrite is plan step 5).** (§VI)
- **Spiral**: every "spiral" is a plunge; common MOTS 5.4 units before the NaN; the wall is censored.
  **Mode-3 caveat: the csm rerun (Bowen–York momentum) does not end in a merger — the verdict waits for the
  boosted-setup rerun.** (§VII)
- **Fly-by / capture**: p = 0.45 scatters; p ≤ 0.25 merges, p ≥ 0.35 does not — **withdrawn pending boosted
  reruns (CRITICAL above).** (§VII.A)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂; the
  scalar channel is comparable and negative-energy; the horizon switches it off. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, none expected. (§IX)
- **Astrophysics**: LISA is the headline (burst SNR 61–500 at 10⁵–10⁶ M⊙, z = 20), LIGO the null channel; the
  deposit cannot be Λ. (§X)

**Plan vs paper**: the paper is the current word (1094 ledger rows, 0 problems, 2026-09-30). Where older
GPU_PLAN entries disagree (regrowth as physics, "no horizon ever forms" for the spiral, the ×7.8 fly-by
growth), the paper wins.

## Traps (each has cost a run)

- **Level-1 noise (found 2026-09-30 on the head-on chain):** fine-scale noise grows on the level-1 refinement
  cube (±20 about the tracked throats), doubling every ~6 units, equal to the smooth field in the outer ring by
  t ≈ 80. **Cause: the dissipation** — at σ = 0.3 it does not grow (NOISE-1, 09-30; the physics unchanged); σ = 0.1
  lets it. Whether the live runs restart at σ = 0.3 before t ≈ 60 is the user's call (not queued). It is what a late
  rise of the logged L2 H can be (check where the constraint sits
  before blaming the core or the boundary: `ham_level_map.py` in the head-on's `validation/` rebuilds Ham from a
  plotfile's metric on any level). A wave sphere inside level 1 (R ≤ 20) or across its corners (R = 28, and the
  consumer's R = 30) is contaminated late; read the symmetry-forbidden modes ((3,2), (2,1)) as the monitor. The
  live spiral and fly-by run the same grid and dissipation: expect it there from t ≈ 65–80.

- **The constraint norm is level 0 only** (Δx = 0.5, nothing masked): a moving pit spikes it while the fine
  solution is clean (verification B: 99.99 % of the norm from four pit cells). Mask the pit cells or read the
  finest level before calling a moving-pit run unconstrained.
- AMReX ignores keys nothing reads: old binaries run new params without the new physics (preflight refuses).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the interval (preflight refuses).
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows that are not horizons; size a horizon hunt's box from
  a wide radial θ_out profile first (the finder says LEFT THE BOX).
- The round scan misreads a moving throat (+0.2–0.4 % that is not there): every moving throat needs the
  shifted-ellipsoid fit.
