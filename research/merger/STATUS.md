# Status — 2026-09-30 12:15 UTC (compacted; the full pre-compaction page is in GPU_PLAN.md ["2026-09-30 (~07 UTC) — STATUS.md compacted"])

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
- Caveat that stands: one resolution (level 3). A level-4 twin (~8 GPU-h) is in GPU_PLAN with its cost.

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
3. **The orbits on mode-3 boosted data**: spiral p = 0.12 (+ level-4 twin), fly-by p = 0.25 (queued, gated) and
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

## Live — first node (two H100s): card 0 the boosted spiral (the paper run); card 1 free

| card | run | t now | t end | speed | ETA |
|---|---|---|---|---|---|
| 0 | `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` (SPIRAL-lbf, the user's go 06:38 UTC 09-30: the csm spiral's params with only momentum model 1, the boosted shift and match tol 1e-5 changed; **no freeze**; max_level 5; checkpoints every 5 units keeping 3; `main3d_boostpair_91ed17cd`, profile `orbit-modes-prod`) | 0 (launched 11:55 UTC 09-30; the solve as A's, evolving since 12:13 UTC, card at 56 GB) | 100 | ~2.7 u/h expected (the csm spiral's average) | t = 60 in ~22.5 h, ~10:30 UTC 10-01; t = 100 in ~37 h, ~01 UTC 10-02 |

- Its verification A (`t0_v2_spiral_d12_p012_L128_lvl5_lb_csm`, the rerun's template stopped at t = 0.5;
  finished 07:17 UTC 09-30): **PASS** — solve converged (22 Newton passes, 2 matching rounds), far sides the
  isolated throat's to 4e-6 (one-body a 2.0000, m 1.0000), mouths R_min 3.8780 each (isolated 3.8772, +0.02 %;
  the p = 0.25 pair's +0.09 % × p²), throat-shell Ham rms 7.8e-5 / 2.9e-5 / 5.1e-5 on levels 3 / 4 / 5 (the
  fly-by pair's floor), axis ratio 0.9919 / 0.9914 at r_c = 1 / 1.55 against 1/γ = 0.9929 (0.10–0.15 % flatter,
  the p = 0.25 pair's × p²), no NaN, frame 0 as the csm spiral's. **Packed 12:06 UTC** without movies
  (`05_binary_spiral/verify_p012/`); its scratch (two plotfiles, 21 GB) wiped 12:14 UTC on the user's word.

Queued on card 1: **`merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm`** — the fly-by rerun
(old fly-by's params, p = 0.45 → 0.25, momentum model 1, per-throat freeze, match tol 1e-5, checkpoints every
5 units keeping 3, build 91ed17cd, profile `orbit-modes-scan-prod`). **Gate (the user, 19:18 UTC 09-29): "we
need to be sure this time the fly-by is correct, only after that we can launch."** Verification state:
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

## Live — second node (one H100): free since 11:27 UTC 09-30 — the head-on chain is complete, close-out due

Leg 3 (`merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000`: leg 2's Chk05000 down-stepped to
max_level 4, no checkpoints, profile `headon-modes-prod`) **reached t = 100 at 11:25 UTC 09-30**, exit 0, no
NaN; common MOTS to the end (R 4.65, M_MS 2.37 at t = 100). Its plotfiles and leg 2's `Chk05000` (28 GB) are
still on the second node's scratch.

- Leg 2 (`..._lvl6from35_..._r03500`, level 6 through the wall): **stopped at t = 50.80** (04:25 UTC 09-30, the
  user's word) — 12 units past leg 1's death, NaN-free; `Chk05000` (t = 50, 28 GB) kept, the rest wiped.
- Leg 1 (level 5 from t = 0, checkpointed): **died at t = 38.845** as the uncheckpointed run did (one-step
  overflow at the merged core inside the common MOTS; clean outside to the end); `Chk03500` was leg 2's start.
- **Legs 1–3 are closed out together now that leg 3 has ended** (checklist in CLAUDE.md; the dead first run is archived
  out of the pack in `00_archive/superseded/`).
- The head-on chain for the paper: superposed scout → CS-1 (same grid, one knob) → mode-3 big box; its common
  MOTS forms at t = 22 with R ≈ 5.0, ~10 % smaller than superposed, as the mode-3 mouths are.

## The production set (shared box; the user, 2026-09-28 09:00 UTC)

L = 128, N = 256, max_level 5, tagging_L 64, sponge 48/64, Ψ4 at 20/28/36/44, scalar at 14/20/30/44 (+ the
head-on's old spheres), plots every 1.0, mode-3 data, binary `main3d_csmatch_5f988dbc`. Status: **spiral** ran
and stopped at t = 60.40 (closed out; its p = 0.12 is Bowen–York momentum, so it reruns under the boosted setup
once verified); **fly-by** stopped at t = 64.98 (overturned, above; reruns as p = 0.25 lbf, queued); **head-on**
(p = 0, clean of the momentum issue) runs as legs 1–3. Templates in `runs/wormhole_merger/templates_scan/`;
launch lines in the GPU_PLAN archive.

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
| FLYBY-lbf | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` | the fly-by rerun | queued on card 1, gated (Live, above) | ~30–46 |
| LAD-csm | `ladder_csm_L{4,6,7}_r0XXXX` | the wall under refinement, mode-3 (Fig. 12a's rerun) | restart from a checkpointed spiral leg at t ≈ 50, max_level 4/6/7, ~10–15 units per arm; convergence rules (no frames, `WHM_MOVIES=0`, `08_convergence`) | ~15–25 |
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
  resting throat's mode (the RESULT above; in the paper).** (§III–IV)
- **Seeded throat**: fate opposite to the kick; ε = ±0.1 both collapse and die at the origin. (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻²; **mode-3 rerun done: ratio
  1.463 ± 0.023 = fixed potential, δ = 2.65 — in the paper.** (§V)
- **Head-on**: common MOTS from t = 22 around both throats; never bounces; shrinks toward the pair's Bondi
  mass. The mode-3 legs reproduce it ~10 % smaller. (§VI)
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
