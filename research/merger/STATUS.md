# Status — 2026-10-01 08:50 UTC (compacted; the full pre-compaction page is in GPU_PLAN.md ["2026-09-30 (~07 UTC) — STATUS.md compacted"])

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

## CRITICAL: the round scans under-read a deformed horizon (2026-10-01) — the head-on's horizon numbers need re-measuring

- **The flaw.** The consumer's round scan (`horizon.py`) and `ah_oriented_scan.py` report the outermost fully trapped
  ROUND sphere, which sits inside a deformed MOTS.
  - On the mode-3 head-on's t = 51–60 slices (HFL-ho), the round scan reads R 4–11 % low and the oriented scan 3–7 % low.
  - The 3D spectral finder there gives a steady R 4.7776 → 4.7735.
  - That finder has existed since 09-21 (it found the old spiral's MOTS that the scans missed) but stayed offline.
- **Fixed in the consumer (10-01).**
  - `--mots-spectral` runs the 3D finder on every plotfile before deleting it (~20 s warm). It is in every binary
    launch profile since 10-01 (the user's go): head-on (level 3, ±4.5) and orbit (level 2, ±6, ℓ ≤ 8); not bbh,
    chi or inflation.
  - Offline test on HFL-ho's 11 plotfiles: R matches to 8e-8.
  - End to end, MOTS-e2e passed (closed out 08:45, below): its rows at t = 51–55 equal the offline ones to 8e-8,
    the end-of-run drain's included.
  - A plotfile with no MOTS gets a row of nan.
  - Every consumer in a run dir also reads `./consumer_args.extra`, so the drain extracts what the watcher does.
  - The two live orbit runs have it since 08:24 / 08:25 UTC 10-01: their consumers were restarted on the first node
    with `--mots-spectral --mots-spectral-level 2 --mots-spectral-half 6 --mots-spectral-lmax 8 --mots-spectral-seeds
    5.0 3.5` (the user's word).
    - The window is level 2 at ±6, since level 2 covers −10..+8 about the centre at t = 49 and ±9 fell back to level 1.
    - SIGTERM stopped each consumer while idle. `restart_consumer.sh --check` was OK: frames 1400 / 1204 kept, every
      stream continuous.
    - Tested first on t = 49 (spiral) and t = 41 (fly-by): no common MOTS yet, as the round scan; a cold search takes
      ~1 min at level 1.
    - Each run dir's `consumer_args.extra` holds these flags. Every consumer started there reads it, including the
      end-of-run drain, so every plotfile gets the finder and none is left for an offline pass (the user, 10-01).
      The last 3 plotfiles stay on scratch as before.
- **The article defines the instrument since 10-02 (the user's ask: "grteclyn currently lacks true horizon
  finder and we need to justify our setup"):** new `sec:setup:mots` (after Diagnostics) -- the MOTS definition
  (theta_+ = 0, theta_- < 0, quasi-local vs the event horizon, the NEC caveat), the post-processing spectral
  Newton finder as the source of EVERY horizon number, star scans demoted to inner bounds/live monitor.
  Macros reused (clmFlowFinder*); not compiled on the nodes (no TeX) -- check both engines on the workstation.
  The Fig. 5/SVI rewrite plugs into this section when MOTS-ho1/2/3 land. First ho1 reading, 10-02 07:20 UTC:
  the finder holds the common MOTS from t = 18 (R 5.634, M 2.817, deform 0.104) -- 4 units before the round
  scan's t ~ 22 birth and 12 % larger than the caption's R 5.02.
- **Article to-do (the user, 10-02): the merger-race explanation.** Add the explanatory notes to the spiral
  section: (i) the two-wormhole setup ITSELF creates the inflationary kick -- solving the constraints with the
  companion present compresses each mouth (-0.4 % at d = 12, -1.2 % at d = 8), and by the seeded-single rule
  (fate opposite to the kick) a compression lands both mouths on the INFLATION branch, deterministically, at any
  momentum (the three d = 12 arms); (ii) the merging setup wins ONLY because the shorter separation makes
  contact (~2.3 e-folds of tau ~ 5.5 at d = 6) faster than the kick-seeded inflation -- the race, not a data
  fix. Ledger rows for the kick sizes and fold counts when written; SEED-csm (queued) pins the rule on solved
  data.
- **Paper numbers to re-measure, all the head-on's:**
  - **Fig. 5(a,b).** The gold line is the round scan. The caption's birth (t = 22, R 5.02, M_MS 2.69,
    `clmHeadonCsmMots*`) is round-scan; its end (t = 100, R 4.69, M_MS 2.373, `clmHeadonCsmEnd*`) is oriented-scan; its
    "~1 % wobble" (`clmHeadonCsmWobble`) is 3–11 % at t = 51–60.
  - **§VI and the abstract.** "Shrinks by a quarter" (`clmHeadonShrink`), R 4.17 (`clmHeadonRemnantRadius`,
    `clmRemnantRadiusMean`), M∞ 2.160 ± 0.006, the R slope, formation t ≈ 21.5–22 (`clmGwCensMotsTime`), the horizon's
    loss against E_GW (`clmHeadonGwShare`) and the rate drops (`clmHeadonRateDrop*`). These still read the superposed
    runs; the rewrite moves them to the mode-3 chain, measured with the 3D finder.
  - **Limitations.** The shape systematic (`clmShapeSyst*`: 34–44 % forming, 4 % rounded) becomes the measured
    scan-vs-MOTS offset.
- **Not affected:**
  - the single throats: their collapse horizons are round (0.1–0.5 %, at most 3 % on the quadrupole arms);
  - the moving-throat RESULT: it uses the throat radius;
  - the spiral's horizons: already from the 3D finder (the R0 verdict, the csm spiral's no-MOTS verdict).
- **The runs (MOTS-ho1/2/3, queued below; each needs the user's go).** The head-on chain replayed on the second node,
  27.5 GPU-h in all, with no plotfile kept.
  - Each uses the leg's packed params with only the stop and the name changed, and `headon-modes-prod` (with
    `--mots-spectral`, keep-last 3). Checkpoints are asked at launch.
  - Leg 1's `Chk03500` and leg 2's `Chk05000` exist only on the second node's scratch: keep them until MOTS-ho2/3 are
    done.

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
- Pack hygiene (the user, 10-02): the superseded superposed/Bowen–York runs LEFT the tracked pack — raw dir +
  pack extract moved (nothing deleted) to the untracked `runs/wormhole_merger/00_archive/superseded_2026-10-02/`.
  348 ledger rows frozen `manual` (values unchanged; unfreeze onto the reruns), Table I's counts kept (ARCHIVED
  notes in table1_groups.tsv). Still packed: singles, placement, ladder, gauge arms, Helfer twins, CS-1, BBH
  controls, the group aggregates. Figures 6/9/10/12/13 and the gallery's spiral+fly-by rows redraw only after
  their reruns. Details: GPU_PLAN "2026-10-02 (~06:00 UTC)".

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

## Live — first node (two H100s): card 0 MOTS-ho1 (since ~20:20 UTC 10-01), card 1 the boosted fly-by

**MOTS-ho1 `merge_headon_flip_d8_v1_L128_lvl5from0_mots_t035_csm` (the user's go 20:10 UTC 10-01):** leg 1 again
from t = 0 to 35 with the 3D finder on every plotfile (`headon-modes-prod`), for the head-on's true birth
(Fig. 5's R 5.02 / M_MS 2.69 are round-scan values, 3-11 % low). Leg 1's packed params with only stop 100 -> 35,
checkpoints OFF (nothing restarts from it; MOTS-ho2 uses the existing Chk03500) and the name;
`main3d_csmatch_5f988dbc`. ~13 h (2.7 u/h) -> done ~09:30 UTC 10-02. SPIRAL-lbf's scratch (91 GB) wiped 20:15 UTC
(`MANIFEST_CLEANUP_2026-10-01`).

Both consumers find the common MOTS with the 3D finder from t = 50 (spiral) and t = 43 (fly-by) on (restarted 08:24 / 08:25 UTC 10-01, and again 08:42 / 08:43 so that a plotfile with no MOTS gets a row of nan; CRITICAL above).

| card | run | t now | t end | speed | ETA |
|---|---|---|---|---|---|
| 1 | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` (FLYBY-lbf, the user's go 12:35 UTC 09-30: the old fly-by's params with p = 0.45 → 0.25, momentum model 1, the boosted shift, the per-throat lapse freeze and match tol 1e-5; max_level 5; checkpoints every 5 units keeping 3; in-code Ψ4 on the set's 24 × 37 grid, 21 modes; `main3d_boostpair_91ed17cd`, profile `orbit-modes-scan-prod`) | 67.2 (19:57 UTC 10-01; alive, no NaN; past periapsis — closest 2.33 at t ~ 47, separation 3.79 and rising: a scatter, not a plunge; no common MOTS (3D finder); launch checks 09-30: far sides to 9.4e-6, frame 0 as A's, 21 Ψ4 modes) | 100 | 2.2 u/h | t = 100 in ~15 h, ~11:00 UTC 10-02 |

**SPIRAL-lbf DIED at t = 71.78 (13:58 UTC 10-01, NaN in h11, level 2) — NO MERGER, the third d = 12 arm to
inflate instead.** Closed out 10-01 evening (`05_binary_spiral/lbf/`, movies to the trust window t <= 56.5 — the
L2 H criterion 2.5e-2 crossed at t = 56.3, the csm spiral's own cut): the trackers collapse onto the central pit
at t = 38.06, the 3D finder sees no common MOTS anywhere (±6 window valid to t ~ 61, nan rows to the end), and
the boost did not change the Bowen–York arm's verdict. Consumer drained to the end. **Its scratch (3 plotfiles +
3 checkpoints) awaits a prune from a session on the first node.** Card 0 there is free; MOTS-ho3 or the d8
production could take it (the user's go).

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

## Second node (one H100): D6-lvl6 live on card 0 (the merger's leg 2, evolving since ~06:21 UTC 10-02)

**D6-lvl6 `spiral_d6_p010_L128_lvl6from25_t060_lbf_csm_r02500` (the user's go 06:10 UTC 10-02): the merger's leg
through the wall.** Restart from leg 1's `Chk02500` (t = 25) with max_level 6, nothing else changed (template
diffed: names + max_level only); `orbit-modes-scan-prod`, the parent binary `main3d_boostpair_91ed17cd`;
checkpoints every 5 keeping 3 (the user's word). `Chk02500` also copied to leg 1's NFS run dir (the new
CLAUDE.md rule). Start verified 06:22 UTC: "restarting calculation from" Chk02500, every level advancing from
t = 25, card at 50.6 GB / 93 %, no NaN; level 6 appears at the first regrid. At the head-on lvl6 pace (~2.0 u/h)
t = 60 is ~17.5 h -> ~23:50 UTC 10-02. First new checkpoint (Chk03000, t = 30) expected ~08:50 UTC.

**Leg 1 `spiral_d6_p010_L128_lvl5from0_t060_lbf_csm` (RETIRED by hand at t = 26.26, 06:14 UTC 10-02): THE MERGER
HAPPENED ON IT.** Common MOTS from t = 13 (R 5.600, M_MS 2.800, deform 0.115) shrinking and rounding to t = 25
(R 4.946, deform 0.030); constraints flat (L2 Ham 4.4e-4 at the stop). The merged core's K runaway began t ≈ 25.8
(max|K| 0.87 at 25.0 -> 4.1 at 26.1, the head-on leg-1 death, 5 units later than the level-3 scout's 20.6);
stopped before the NaN so leg 2 restarts from the pre-spike Chk02500. Closed out and packed 10-02 07:00 UTC (`05_binary_spiral/merger_d6/`, trust t <= 25.5, movies to 25.5, K frames
kept as rendered); scratch pruned 07:05 UTC 10-02 on the user's word (~76G: Chk 1500/2000 + the 3 plotfiles; manifest logged); only Chk02500 kept (leg 2's restart source, NFS copy too).

**SCOUT-d8p closed out (19:30 UTC 10-01; `05_binary_spiral/scout_merger/`, frames kept; movies added ~20:05 UTC on the user's word, cut at t <= 19 — K at a fixed linear ±0.05, the other fields on the close-out symlog scales): THE FIRST
ORBITAL MERGER ON CLEAN DATA.** `spiral_d8_p010_lvl3_t040_lbf_csm` (MISNAMED d8: centers +-3 = d = 6; tangential p = 0.10, L = 64 level 3):
the 3D finder holds a common MOTS around both mouths from t = 12.5 (R 5.624, M_MS 2.812) to the last plotfile
t = 20.5 (R 5.120, M_MS 2.560), shrinking smoothly; separation 1.35 at t = 18.6. The run died at t = 20.61 (NaN in
K, level 3 — the merged core's K runaway from t ~ 19.3, the head-on-leg-1 class of death; constraints flat, L2 H
<= 1e-2). Trust window t <= 19.0. **The design point stands: d = 6, small tangential p merges** (the name says d8 -- a naming error, centers +-3 = separation 6; the records are corrected, the name kept as the identifier). Scratch (40 GB)
wiped 19:25 UTC. The natural next run: the level-5 production spiral on this design point (the user's go needed —
proposal below); MOTS-ho1/2/3 also still queued.
**SCOUT-d12pin closed out (12:55 UTC 10-01; `05_binary_spiral/scout_merger/`, no movies, frames kept): NO d = 12
MERGER AT ANY MOMENTUM.** `spiral_d12_pin025_lvl3_t040_lbf_csm` (the inward-momentum scout) was stopped by hand at
t = 33.86 with the verdict in, no NaN: the mouths inflate much faster than the gentle spiral's (R_min +4.7 % by
t = 8, +22 % by 16, +72 % by 24 — the closing pair deepens the companion kick seeding the tau ~ 5.5 mode), the
infall stalls at separation ~ 2.2 against the swelling throats, no common MOTS through t = 33. With the tangential
p = 0.12 and 0.25 arms this closes the d = 12 family: the ~20-unit approach always loses to the exponential.
Its scratch (41 GB) wiped 12:49 UTC (`MANIFEST_CLEANUP_2026-10-01`); its stop cut the drain's last mots row
(t = 33.5 would be nan anyway); manifest closed by hand (`run_manifest.py finish`, stop_campaign leaves "running",
which also blocks the pack for 30 min).

**SCOUT-d8p `spiral_d8_p010_lvl3_t040_lbf_csm` (the user's go 12:48 UTC): the collapsing-spiral design point.**
d = 8 (the head-on's separation, whose common MOTS at t = 22 beat +10 % inflation) with a small tangential twist,
p = 0.10 per mouth, the fly-by's clockwise sense. The d12 scout's params with only centers +-6 -> +-3, momentum ->
tangential 0.10, the name; same L = 64 level-3 grid, stop 40, checkpoints every 5 keeping 3, `orbit-modes-scan`
(3D finder, orbit window), `main3d_boostpair_91ed17cd`. ~3 h at the d12 scout's pace -> done ~16:00 UTC 10-01.
If it merges (common MOTS), the level-5 production follows (the user's go needed); if it inflates past contact,
p = 0.05 is the fallback scout. MOTS-ho1/2/3 stay queued behind it.
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

Node assignment (the user, 2026-10-02): MOTS-ho2 and ho3 restart from `Chk03500`/`Chk05000`, which live on the
SECOND node's scratch — they run there, back to back, once SPIRAL-d6-prod frees that card (~21:00 UTC 10-02).
Only MOTS-ho1 starts from t = 0, which is why it runs on the first node. The first node's card 1, after the
fly-by ends (~11:20 UTC 10-02), takes a checkpoint-free run instead — BBH-HEADON, A1-csm or PLACE-csm, on the go.

| id | run | what | how | GPU-h |
|---|---|---|---|---|
| D6-lvl6 | `spiral_d6_p010_L128_lvl6from25_t060_lbf_csm_r02500` | **LIVE on the second node's card 0 since ~06:21 UTC 10-02** (Second node, above). The merger's leg 2 through the wall: leg 1 hit the merged core's K runaway at t ≈ 25.8 | the head-on leg-2 pattern: restart from the parent's `Chk02500` (t = 25, before the spike), max_level 6. Template ready: `templates_scan/params_spiral_d6_p010_L128_lvl6from25_t060_lbf_csm.txt` (only the name, max_level 5→6, `amr.restart`; diffed). **First copy `Chk02500` into the parent's NFS run dir** (keep-3 is not an archive). Launch on the SECOND node, parent binary; checkpoints asked at launch (every-5 keep-3 proposed, the next leg needs them); needs the go | ~2.0 u/h at lvl6 (head-on leg 2): ~17 h for t = 25–60; a later lvl4 drop (template `lvl4fromCHK`, kept) once max\|K\| flattens |
| MOTS-ho3 | `merge_headon_flip_d8_v1_L128_lvl4from50_mots_t100_csm_r05000` | PAPER, REQUIRED (CRITICAL above): the head-on's true MOTS over t = 50–100 for Fig. 5(a,b) and its end values (t = 100) | leg 3 again from leg 2's `Chk05000` (max_level 4) to t = 100, leg 3's packed params with only the name changed; `headon-modes-prod` (`--mots-spectral`), keep-last 3; checkpoints asked at launch; its input checkpoint lives on the SECOND node's scratch — run it there (after SPIRAL-d6-prod) | ~7 (7.2 u/h) |
| MOTS-ho2 | `merge_headon_flip_d8_v1_L128_lvl6from35_mots_t050_csm_r03500` | PAPER, REQUIRED: the true MOTS over t = 35–50 (through the wall) | leg 2 again from leg 1's `Chk03500` (max_level 6) to t = 50, leg 2's packed params with only the stop (50) and the name changed; as MOTS-ho3 | ~7.5 (2.0 u/h) |
| MOTS-ho1 | `merge_headon_flip_d8_v1_L128_lvl5from0_mots_t035_csm` | **LIVE on the first node's card 0 since ~20:20 UTC 10-01** (Live, above). PAPER, REQUIRED: the birth (t ≈ 22, the caption's R 5.02 / M_MS 2.69, the formation time) and t = 0–35 | leg 1 again from t = 0 (max_level 5) to t = 35, leg 1's packed params with only the stop (35) and the name changed; as MOTS-ho3 | ~13 (2.7 u/h) |
| SPIRAL-lbf | `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` | THE PAPER RUN, FIRST (the user, 2026-09-30): the spiral on the boosted setup — the clean test of "inflates, no merger" | the csm spiral's template + momentum model 1, **no freeze** (the user's word; the pits move at v = 0.12, the runaway was a v = 0.41 problem), max_level 5, checkpoints every 5 keeping the newest 3 (the user's word; LAD-csm needs the t ≈ 50 one); its own verification A **PASSED**; **DONE — died t = 71.78, 10-01, no merger; closed out, trust t <= 56.5** (Live, above) | ~22 to t = 60, ~37 to t = 100 |
| SPIRAL-d6-prod | `spiral_d6_p010_L128_lvl5from0_t060_lbf_csm` | **LIVE on the second node's card 0 since ~19:50 UTC 10-01** (Second node, above). THE MERGER RUN (the merger scout, 10-01: common MOTS t = 12.5–20.5): the d = 6, p = 0.10 design point at production resolution, for the paper's orbital-merger section | the production box (L = 128, N = 256, max_level 5, the shared wave set) with the scout's initial-data block (d = 6: centers +-3, tangential p = 0.10, boosted-pair mode-3 solve); expect the head-on's leg structure through the wall (lvl6 restart) — plan the legs at launch; checkpoints every 5 keeping 3 | ~25–35 |
| SCOUT-d8p | `spiral_d8_p005/p010_lvl3_t040` | **DONE 10-01: the d = 6 scout (misnamed d8) MERGED — common MOTS t = 12.5–20.5; packed `05_binary_spiral/scout_merger/`.** Was: the collapsing-spiral design point (contact must beat the mouths' runaway; the head-on's d = 8 contact at t = 22 wins, d = 12's t ≈ 40 loses) | new setup, so level-3 scouts first (~2–3 h each, L = 64), then level 5 for the winner | ~5 + ~21 |
| FLYBY-lbf | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` | the fly-by rerun | **LIVE on the first node's card 1 since 12:37 UTC 09-30** (Live, above) | ~46 to t = 100 |
| LAD-csm | `ladder_csm_L{4,6,7}_r0XXXX` | **CANCELLED (the user, 10-02).** Was: the wall under refinement, mode-3 (Fig. 12a's rerun) | its restart point (the lb spiral's t ≈ 50 checkpoint) did not survive: `checkpoint_keep 3` pruned it during the run (only t ≈ 60–70 were left at death, past trust 56.5) and the 10-01 wipe removed those; a fresh checkpointed leg (~17 h) is not worth it — Fig. 12a stays on the superposed ladder. Lesson: copy any checkpoint a queued run needs off the keep-N rotation to NFS while the producer is live | — |
| SEED-csm | `single_eps_p1e1_t100_csm` | PAPER (the user, 10-02): the kicked single on SOLVED data — prove the ε kick is not the junk source (the seeded-throat verdicts §II.D/§IV.C are superposed-only) | `single_eps_p1e1_t100`'s packed params + the mode-3 constraint-solve block with the seed kept (`wormhole_seed_amplitude_A = 0.1`; preflight verifies the seed changes t = 0), only the name + `_csm` changed; L = 64, level 3, t = 100; checkpoints asked at launch; the mirror `m1e1` twin optional after | ~5 |
| BBH-HEADON | `bbh_headon_d8_L128_lvl5_t100` | the vacuum control for the head-on (the user, 2026-09-30): bare punctures at d = 8 from rest, t = 100, for Fig. 5 and the gallery/energy comparison | the csm head-on's setup (same box, grid, spheres, plot cadence) with the drainhole/scalar blocks swapped for bare punctures, as the d = 12 BBH controls; template from `bbh_control_d12_p012_t150`'s params with d and p changed; checkpoints asked at launch | ~30–50 (the head-on chain's class; vacuum punctures ride through a merger, so likely one leg) |
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
