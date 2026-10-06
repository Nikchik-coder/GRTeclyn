# Status — 2026-10-06 ~05:30 UTC (last compacted 2026-10-01)

Current state only; the map is in [`../../MAP.md`](../../MAP.md). The old diary GPU_PLAN.md was deleted 2026-10-06
(the user: too big, out of date); the GPU_PLAN headings quoted below are in `git show 94e7df53:research/merger/GPU_PLAN.md`.
**Update this page whenever a verdict or the queue changes; keep it this size.**

## LIVE NOW (2026-10-06 06:23 UTC) — the first node: DAMP-off on card 1, card 0 idle; the second node idle

| run | node / card | t at 06:23 UTC | stop | speed | ETA | checkpoints |
|---|---|---|---|---|---|---|
| DAMP-off `merge_orbit_flip_d12_p045_L128_lvl4_t070_nodamp_lbf_csm` | first / 1 | 53.52 | 70 | 6 u/h since the pass (4.4 before it) | ~2.8 h → ~09:10 UTC 10-06 | none (the user) |

- **P060-EXT STOPPED t = 109.4 (05:04 UTC 10-06; the user: "its dead") — NO common MOTS at level 5 either, t =
  61–109:** the spectral flow stalls at rms θ_out 1.6–3e-2 on all 49 plotfiles, no trend to 0. The level-1 cube
  fills with grid-scale K noise (the user's eye at t = 109): L2 Ham > 1e-3 from 83.8 (the lvl4 chi leg: 83.7), >
  1e-2 from 100.9, 3.1e-2 at the stop — level 5 does not move it; trust t ≤ 80 (trust_windows.tsv). The core itself
  stays calm (max|K| ≈ 0.52, min lapse 0.034–0.042; the lapse minimum splits off-centre to y ≈ ±0.44 at t ≈ 105,
  past the trust window). CLOSED OUT 05:20 UTC: filed and packed `06_binary_flyby/`, no movies (stopped, past
  trust), 0 problems; plotfiles and Chk10000/10500 pruned; its stop checkpoint `Chk10940` wiped 05:28 UTC (the user
  declined the resume to t = 115).
- **T0-1THROAT `t0_single_boost_p045_L128_lvl4_lbf_csm` DONE t = 0.5 (card 0, 05:05–05:13 UTC; the user's go "do
  both"): ONE exact-boost throat, p = 0.45, on P045-T100's box with its mode-3 solve. THE SOLVE IS IDLE on it (20
  Newton passes, max |w| ≤ 1.2e-5 per level, c = c_superposed, σ = 1, far side 4e-6 off), the face estimate prints
  M_ADM_face = 1.000014, and the t = 0 plotfile's full ADM surface integral (level 0, R = 20–56, a + b/R + c/R²)
  reads 1.0967 = γm (1.0966): the data carry the motion energy, the printout drops it. Filed
  `02_moving_throat/exact_boost/`, no movies, scratch pruned. (Its drain looped on a `--watch` I put in
  `--consume-args`; killed by PID once both plotfiles were done — never pass `--watch` there.)
- **THE BOOSTED PAIRS' MASS, FIXED (10-06, the user's "do both"):** the solve's `M_ADM_face = M_bg + 2<r w>` counts
  each throat's rest mass σm; the exact-boost background integrates to γσm (+ the shift's 2s·asinh(γv)/γv), so it
  left out Σ(γ−1)σm. Corrected ADM masses (`results/merger/analysis/boosted_adm_mass.py` → `boosted_adm_mass.tsv`,
  from the pack; `run_tree.boosted_adm_mass`): d6 merger 2.3634 → 2.3709, p025 2.1783 → 2.2332, p045 2.0776 →
  2.2536, p060 1.9120 → 2.2286 (p090 1.3419 → 2.1066). The code now prints and writes `M_ADM_boost` (from the next
  build; the pinned binaries print the old face only). Paper: E/M at p = 0.25/0.45/0.60 3.85/9.0/4.9e-2 →
  3.75/8.3/4.2e-2 (outer 3.95/8.2e-2), boundary/scatterer 2.3 → 2.2, boundary/plunge 1.8 → 2.0, fly-by gallery 9.0 →
  8.3e-2 (outer 4.9e-2), envelope 1.3 → 1.4e-1, |E_φ| 5.1 → 4.7e-2, merger mass 2.363 → 2.371; Sec. II.C states how
  a moving pair's mass is taken and the face estimate's offset (2.8 % low where both apply, clmBoostFaceBias).
  Search: the ladders scale with the mass, so templates, triggers, horizons and injections are unchanged (labels
  only); the fitting factors re-run (bank max 0.81 → 0.80, fly-by 0.63–0.80, window max 0.995). Figs psi4_ligo and
  heavy_seeds redrawn; `egw_momentum` removed (the user: not needed). LISA rows re-measured on the current channels
  (task 2; frozen → auto): all three ≥ 8 from 3e4 to 6e6 M⊙, fly-by + merger SNR 103–394, the fly-by and head-on
  hold 8 to 8e6, and at 1e7–1e8 ONLY THE PLUNGE still reaches 8, to ≥ 4e7 (sentence rewritten); (fM)_peak 0.04–0.07,
  band 0.4–70 mHz, Ω_GW 1e-13–1e-12 at ~7 mHz, PLS threshold n ≳ (6–36)e-4 Mpc⁻³. Claims check: 886 rows, only the
  10 local-archive LookupErrors. OPEN: even corrected, the moving pairs weigh ~flat in p (2.23 / 2.25 / 2.23) where
  2γm′ + E_b(rest, d = 12) predicts ~2.34 / 2.47 / 2.61; the solve is idle on one throat, so it is the pair
  (velocity-dependent interaction or the boosted superposition's companion terms). The model-free test is a t = 0
  ADM surface integral of one pair's plotfile (P045 rebuild to t = 0.5, ~40 GPU-min; needs the go).
- **DAMP-off** (the user's go ~17:25 UTC 10-05, "Required" below; launched 17:35): P045-T100's params with ONLY
  `core_matter_damping` 1 → 0, the stop (100 → 70; P045-T100's trust 67.6) and the names changed; binary
  `main3d_boostpair_91ed17cd`; NO checkpoints (the user: "None, as P045-T100"; the inherited lines are off).
  Preflight PASS. Started by effect: the ~35-min mode-3 solve gave M_ADM 2.077626359 and far sides 1.249e-6, P045-T100's
  to every digit; frame 0 matches P045-T100's (the mouths at ±6; the renderer's newer style); the consumer's t = 0
  rows landed (no common MOTS, as expected); card 1 at 57 GB. Pending: the keep-last pruning (from t = 3).
- **O3B-NEW DONE 21:17 UTC 10-05 (the same go; the first node's CPU): the LIGO search on every wormhole channel of the
  paper — throat, head-on, d = 6 merger, p = 0.45 fly-by and now the p = 0.60 plunge — plus the vacuum twin: 2.25 h,
  154 templates, NO candidate; background 20 231 accidentals over 469 days (floor 1 per 469 days); horizons
  (SNR 8, optimal) fly-by 5.1 / head-on 3.0 / merger 2.7 / plunge 1.7 / twin 1.3 / throat 0.15 Gpc; injections
  18/18 at 92–123 %, none vetoed; same-window FF 0.893–0.996 (twin 0.935–0.951). The validation found and fixed
  seven defects (7fcb7990), among them the HEAD-ON AXIS: both head-ons fall along x, so the z-based (2,0) held a
  quarter of the power — every head-on amplitude ×2, energy ×4 since (the user: "fix everywhere"; the vacuum head-on
  5.6e-4 now meets the published 5.5e-4). Sec. IX, ledger (884 rows; 10 problems = the local 00_archive
  duplicates) and figures updated; GPU_PLAN ["2026-10-05 (~21 UTC) — O3B-NEW"]. My CPU jobs throttled this
  24-CPU container 19:48–20:16 UTC (both live runs slowed); pinned with taskset since.

- **P09-LVL5 `merge_orbit_flip_d12_p090_L128_lvl5from40_chi1e4_t100_lbf_csm_r04000` DIED t = 45.28 (~14:07 UTC
  10-05): h11 NaN on level 4, the SAME instant as the lvl4 chi leg (45.27).** Level 5 changed the core, not the
  death: max|K| stayed calm (1.23 → 1.44 over t = 44–45.27; lvl4 0.78 → 1.77 → 172), min lapse 8.3e-3 and χ_min
  1.2e-4 at the centre, and the NaN shows first on level 4, not on the level-5 core — lvl4's K runaway was a
  symptom. No common MOTS t = 41–45. Trust t ≤ 45.1. Filed `06_binary_flyby/`, closeout without movies. It ran
  from p09's `Chk04000` (t = 40, re-staged to scratch; the user moved the restart off the mid-runaway Chk04500),
  launched 12:48 UTC on the user's go with checkpoints every 5 keep 3; first checkpoint `Chk04500` (t = 45, lvl5)
  written 14:03. NEXT (PROPOSED, no go): a `nan_autopsy = 1` restart from that Chk04500 (~10 GPU-min) names the
  cell and field that go first. E_GW(p = 0.90) stays unmeasured.
- **BBH-d6 `bbh_control_d6_p010_t100` DONE 14:44 UTC 10-05: reached t = 100, no NaN (~50 u/h after the merger);
  filed `07_bbh_control/`, closeout with movies (it will be cited beside the d6 merger).** Was (the same go; launched 12:48): the d = 6 merger's vacuum twin for the gallery's merger row — bare
  punctures at ±3, tangential Bowen–York p = ±0.10 in the merger's clockwise sense, bare mass 0.9282 (per-hole ADM
  1.00 by the d12 controls' Brill–Lindquist rule; the code's O(P²)-corrected boosted punctures, valid for
  |P| < 0.3 m), on the BBH controls' box (L = 64, N = 128, level 5, spheres 14/20/26/30): BBH-HEADON's params with
  d, p, the mass and the checkpoint lines changed. NO checkpoints: `amr.check_int = -1` +
  `amr.checkpoint_files_output = 0` (verified: none written). `WHM_PREFLIGHT=static`, as BBH-HEADON. Started by
  effect: frame 0 eyeballed against BBH-HEADON's, Ψ4 rows landing, keep-last 3 pruning, card 1 at 62 GB.
- **Storage (the first node, 05:28 UTC 10-06):** scratch 1.1T free, CLEAN: only DAMP-off 18G (3 plotfiles, in
  policy). Today: the 76G of leftovers wiped at 04:53 (the user's "wipe them"; P09-LVL5's Chk04500 copied to NFS
  first), P060-EXT's and T0-1THROAT's close-out prunes, and P060-EXT's stop checkpoint Chk10940 at 05:28 (the user:
  "wipe"); MANIFEST_CLEANUP_2026-10-06. The second node was not listed from here (05:35 UTC 10-05: only the HFL
  cell, 60G).

## RUNS FOR THE PAPER (the full read of 2026-10-05, late; nothing launches without the go)

The paper was read end to end: the superposition / Bowen–York / workaround wording is out (Sec. II states the
solved, matched, boosted data as the method), duplicates are cut, the d = 6 chain is "the merger" everywhere
(text and figures), the run matrix (Table III) lost the Bowen–York probes, the GRTresna bridge, the unused CS-1 scout and the
Bowen–York convergence arms (96 runs, 476 GPU-h; BBH-d6 joined the vacuum controls). Ledger 907 rows, 0 problems.
**No more GPU runs after DAMP-off (the user, 2026-10-06 06:20 UTC): CONV-lbf-w, HARM-oct, the optional rows and the
flat-in-p mass rebuild are declined.** **Required:** DAMP-off — the text quotes numbers that rest on it (started ~17:30 UTC 10-05 on the user's go: LIVE
NOW, top; O3B-NEW DONE 21:17 UTC 10-05). **Recommended:** CONV-lbf-w — no
quoted number waits on it, but the paper has no wave-zone resolution test on current data and a referee will ask.
**Optional:** SOLVE-t0 — the d = 8 shell number it would restore is no longer in the paper. (Classified 10-05 late,
after the shortening pass.)

| id | what | why the paper needs it | how | cost |
|---|---|---|---|---|
| O3B-NEW | DONE 21:17 UTC 10-05 (LIVE NOW, top) | Sec. IX now quotes the search on the current channels plus the plunge (154 templates, 2.25 h, no candidate) | — | CPU hours |
| DAMP-off | the p = 0.45 fly-by with `core_matter_damping = 0` | the orbital runs damp the scalar where the lapse collapses; on both scatterers that is the grid centre between the mouths from t ≈ 34–36, during the dipole arch the scalar channel quotes (\|E_φ\| = 0.56 E_GW). The twin shows whether the arch and E_GW move. The 09-0x damping-off arms (merge_twin_p012_nodamp_t060: fields equal to 3 decimals at t = 32, wall 51.53 vs 52.06; the damped/undamped ladder rungs) tested the superposed p = 0.12 merger's wall, behind a horizon — never a scatterer, where the damping acts outside any horizon | P045-T100's params with only the damping off and the name; level 4, stop 70 (trust 67.6); no checkpoints (the user, at launch) | ~15 GPU-h (P045-T100 averaged 4.8 u/h) |
| CONV-lbf-w | the wave-zone test on exact-boost data | CONV-csm-w resolved the wave zone (0.01–0.15 % of peak) on the Bowen–York `_csm` arm, which the paper no longer cites | the CONV-csm-w recipe (`extraction_levels 0 1 0 0`, the R = 28 ball, 77.6/80 GB) on P045-T100's params, t = 0–40 | ~11 GPU-h, a whole card |
| SOLVE-t0 | the mode-3 d = 8 head-on at t = 0 | Sec. II quoted the d = 8 throat-shell Hamiltonian from the pre-matching (mode-0) check, now cut; the paper keeps only the boosted pair's mode-3 per-level number | t = 0 only on CS-1's grid, `constraint_solve_t0_check.py` | CPU minutes |
| HARM-oct (referee 1, recommended) | the ε = −10⁻² inflating throat in harmonic slicing, octant, to t ≈ 45 | the referee asks whether 1+log shapes the inflation; F2/F3 (harmonic, 09-25) kept α_neck ≈ 0.45 and grew R_neck 3.81 → 9.89 by t = 46 (1+log: 12.2 only by t = 90), F6 (zero shift) matched R_neck to 3 digits — but all were wiped, so nothing is quotable; their grid died at t ≈ 46.6 on the level-5 box faces | F3's template from `templates_scan/` (`lapse_coeff`/`lapse_power` harmonic), the full consumer (`inflation-octant`), stop 45; quote the neck's proper-time onset rate against F4's H R₀ | ~1 GPU-h |
| SIGN-d (referee minor 2, optional) | flipped rest pairs at d = 14/16/18 (and the d = 12 pair at level 4) | the pull/push ratio 1.462 ± 0.022 is one d, one resolution; whether it tends to 3/2 (point charges, d → ∞) or carries a near-zone offset needs the ladder | ctrl_flip_d12_csm's params with d changed (and max_level 4 for the twin); t = 15; sign_rule.py | ~1–2 GPU-h (L = 64, level 3) |
| KRETSCH (referee 4, optional) | curvature invariants at a dying core | is the K wall / cell NaN a curvature singularity or a slicing effect? The paper says only "a coordinate blow-up read on the slice"; the plotfiles at every death are pruned | a restart of a dying leg from its last checkpoint with plotfiles every step over its last unit (fold into the P09 autopsy if that goes); offline: R = 8π(Π² − \|Dφ\|²) and the Weyl invariants I, J from E_ij, B_ij at the core | ~1 GPU-h + CPU |
| PALETTE (referee minor 1, no GPU) | greyscale-safe accent | GOLD #c69214 and FAINT #a5a29a print as the same grey (luma 0.58 vs 0.64; gold on white 2.8:1) | darken GOLD (e.g. luma ≤ 0.45) or add a line-style cue wherever gold sits beside faint grey; re-render every figure, label audits, show the images | CPU |

Analysis only (no GPU), optional: E_GW(p = 0.12) on SPIRAL-lbf's packed streams (a fourth point for Sec. VIII D's
energy sequence).

Referee ideas checked on the packed data (2026-10-05, late; the scalar ringdown and the memory sentence are IN the paper since, on the user's "yes"):
- **Scalar ringdown (computed, preliminary):** after the head-on's common MOTS the ℓ = 1 scalar dipole rings at
  ω = 0.122–0.124 on R = 10 (0.122 on R = 14 from t = 45): the Schwarzschild ℓ = 1 scalar QNM of the final MOTS mass
  2.389 is 0.1226 (1 %); damping 0.037 against 0.041 (10 % slower). Fit: damped cosine on the x-dipole of the SERIES
  scalar_modes.dat, t = 35/40/45–95. The d = 6 merger's dipole gives no stable fit (0.07–0.16).
- **Memory (computed 09-27 on the superposed data; geometry, so it carries over):** the negative-energy dipole
  ENHANCES the (2,0) memory, never reverses it — per unit energy an equatorial dipole projects −(2/5)√(5/16π), an
  m = ±2 GW flux +(4/7)√(5/16π). On the current fly-by: +0.7 × |E_φ|/E_GW ≈ 0.34 (arch) to 0.39 (whole record) of
  the GW memory. `results/merger/analysis/scalar_memory_angmom.py` still points at the superposed runs (rerun on
  csm/lbf = a path edit). A direct DC offset in the near-zone (2,0) is not readable on these records (ωR ≈ 1–3).
- **3D MOTS shapes:** feasible here — `mots_spectral_alm.jsonl` exists for the head-on legs and the d = 6 legs.
- **Phantom flow (ρ, J on z = 0) and embedding diagrams:** need the χ/φ/Π/α/β slice caches in `runs/` on the
  workstation; the packs carry no field slices or areal-radius profiles. The (2,0)-memory sign is no longer needed: the memory aside left the paper in the shortening pass.

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
- **DONE (in Sec. VII B; 10-05 wording: an EFFECTIVE inward kick read off the seed ladder — each mouth starts in
  the isolated shape, Table I).** Article to-do (the user, 10-02): the merger-race explanation. Add the explanatory notes to the spiral
  section: (i) the two-wormhole setup ITSELF creates the inflationary kick -- solving the constraints with the
  companion present compresses each mouth (-0.4 % at d = 12, -1.2 % at d = 8), and by the seeded-single rule
  (fate opposite to the kick) a compression lands both mouths on the INFLATION branch, deterministically, at any
  momentum (the three d = 12 arms); (ii) the merging setup wins ONLY because the shorter separation makes
  contact (~2.3 e-folds of tau ~ 5.5 at d = 6) faster than the kick-seeded inflation -- the race, not a data
  fix. Ledger rows for the kick sizes and fold counts when written; SEED-csm (queued) pins the rule on solved
  data.
- **DONE (10-05): Fig. 5 and §VI read the finder; the abstract's area loss is the finder's (clmHeadonCsmShrinkArea);
  the shape systematic became the measured scan-vs-MOTS offset (Sec. III C).** Paper numbers to re-measure, all the head-on's:
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

## Done 10-05 (the old diary's last open items)

- **DONE 10-05 ~12:20 UTC on the second node (it has the run tree): the matched width table and Fig. 4(d).**
  `results/merger/analysis/matched_rest.py` now reduces `ctrl_rest_a{1,15,3}_csm` too: the packed
  `campaign/03_two_throats/matched_rest_displacement.dat` gained `dsep_like_a1/a15/a3` (a = 2 is
  `dsep_like_d12`; the first five columns are byte-identical). Fig. 4 is (a)–(d): (d) is the width ladder
  (`plot_width_ladder`), δd at t = 11.5 = 0.1623/0.3250/0.4791/0.7583 for a = 1/1.5/2/3, log-log fit a^1.40
  against the point-charge a². Sec. V B's width sentence is back (n = 1.2–1.4 over t = 8–11.5; 7 rows
  clmALadder*/clmWidthExponent*, extractors `single_matched_aladder`/`_width_exponent`).
- **DONE 10-05 ~11:00–12:35 UTC (GPU_PLAN has the entries): E_GW(p = 0.60) and the Sec. VIII waves update.** The
  radii passthrough reads the header-less restart streams; the glued p060 record (t = 0–80) gives E/M = 4.9e-2 at
  R = 20, so the turnover reads 3.85e-2 / 9.0e-2 / 4.9e-2 at p = 0.25 / 0.45 / 0.60. Sec. VIII gained the plunge,
  the turnover and the vacuum head-on control (its (2,0) bell 21x quieter, 28 units later); new Fig.
  `egw_momentum`; the gallery re-fed (d6 merger, p045 scatterer, p060 plunge row, the BBH head-on overlay).
  E_GW(p = 0.90) stays unmeasured (P09-LVL5 died at the lvl4 instant, 10-05); E_GW(p = 0.12) is pending analysis on the d12 p012 spiral's packed streams
  (SPIRAL-lbf, `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` — mode-3 solve + exact boost, NOT the superposed or
  the Bowen–York `_csm` twin; EGW-p012 dropped, the user 10-05).
- **What a session without `runs/` can do** (a cloud container has git only): read the pack. Anything that
  reads raw run output — `frames/_slice_cache`, unthinned `data/*.dat`, scratch plotfiles or checkpoints — is a
  lab-node task, and its product lands in the pack as a reduced table its figure and ledger read (as here).

## The plan, in order (the user, 2026-09-28)

1. **Energy check** — done: the pair acts at fixed scalar potential (Sec. II D; `t0_matching/energy_scan.tsv`).
2. **Rest pairs + head-on** — rest pairs done (above); the head-on runs as legs 1–3 (second node, below).
3. **The orbits on mode-3 boosted data** — run, except the p = 0.90 merger and p = 0.35: spiral p = 0.12 (no
   merger, died t = 71.78; its level-4 twin CONV-csm agrees on where trust ends), fly-by p = 0.25 and p = 0.45
   (scatters, no wall), p = 0.60 and 0.90 (plunges; the boundary sits in (0.45, 0.60)); the d = 6, p = 0.10 design
   point merges (the d6 chain, t = 0–100). The p = 0.90 lvl5 continuation (P09-LVL5) died at t = 45.28, the lvl4 instant (top).
4. **Single throats on clean data** (12–25 h, settles the regrowth question) — not queued: no further
   single-wormhole runs (the user, 10-02, at SEED-csm).
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

## First node (two H100s): P060-EXT on card 0 since 15:34 UTC 10-05; DAMP-off on card 1 since 17:35 UTC (LIVE NOW, top)

**P060-LVL5 `merge_orbit_flip_d12_p060_L128_lvl5from40_chi1e4_t060_lbf_csm_r04000` DONE (t = 60, no NaN, Ham
2.0e-4) — NO converged MOTS at lvl5 either: THE p060 STALL IS PHYSICAL, not resolution (rms θ_out ~1.8e-2
mid-window, 3.8e-2 at the end, R 4.514, deform 0.142 — the lvl4 arms' numbers). Late trapping (the lvl4
extrapolation, t ≈ 110–115) stays open: Chk06000 NFS-secured for a lvl5 extension (queue, PROPOSED). Filed
`06_binary_flyby/`. Was LIVE on card 0 since ~07:10 UTC 10-04 (the user: "kill it and run p060 lvl5 minchi"):** THE HORIZON-BIRTH DISCRIMINATOR — the
extension's params with ONLY max_level 4 → 5, min_chi 1e-4 (from the start) and stop 60; restarted from the
t040 leg's Chk04000 (t = 40, pre-contact, re-staged to scratch from NFS). If a common MOTS converges in
t ≈ 42–60 where lvl4 never trapped, the chi-leg stall is a resolution artefact and the horizon is real; if it
stays marginally untrapped at lvl5 too, the stall is physical (the p012 csm spiral precedent). ~2.5 u/h →
t = 60 ~15:00–17:00 UTC. Checkpoints every 5 keep 3 (inherited).

**EGW-p045 SUPERSEDED by P045-T100 (below: the p = 0.45 point, run to t = 100); its ~07:45 UTC relaunch on card 1
was stopped near step 0 as well (stubs archived). STOPPED at t = 0.91 (~07:00 UTC 10-04, the user: the lvl5 check takes the card). Nothing physical
lost (solve + 91 steps); scratch wiped, stub archived 00_archive/aborted (manifest 10-04). THE GO STANDS —
relaunches on the next free card (card 1 frees ~14:00 UTC). The chi leg's Chk10000 wiped on the user's word
(23G; the lvl5 arm answers the horizon question). Was LIVE on card 0 (the user 10-04: "start
something else from queue" — the queue's next midpoint):** the EGW recipe (p06's t040 template) with ONLY
p 0.6 → 0.45 and the names; stop 40, lvl4, checkpoints every 5 keep 3 (the template's block), orbit-modes +
the full MOTS-tuned consumer set, binary main3d_boostpair. Preflight PASS, paths one spelling. Fills the
E_GW(p) turnover between scatter (0.25) and plunge (0.60) for Figs. 9/12. ~4.1 u/h → t = 40 ~15:30 UTC 10-04.

**P045-T100 `merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm` DONE (reached t = 100, no NaN) — NO WALL AT
p = 0.45: a close fly-by (nearest approach 2.45 at t ≈ 47, no MOTS ever, receding to 5.85); THE PLUNGE/WALL
BOUNDARY SITS IN (0.45, 0.60). Trust t ≤ 67.6; E_GW/M 9.0e-2 at R = 20 (Sec. VIII). Filed `06_binary_flyby/`.
Was LIVE on card 1 since ~08:00 UTC 10-04 (the
user: "till 100 ... the actual dead time without extra settings ... no checkpoints"): THE DEATH CLOCK — the
EGW p = 0.45 point run at stock settings (min_chi 1e-8, no fixes), stop 100, NO checkpoints, to measure where
(whether) the natural wall kills the p = 0.45 arm between the clean scatter (p025, never died) and the
plunges (p060 wall 55.5, p09 K-wall 45.3). Same template otherwise; full MOTS-tuned consumer set.
~4.1 u/h → t = 100 ~08:00 UTC 10-05 if it survives; the two earlier t040 starts were stopped at/near step 0
(stubs archived).**

**P09-CHI DIED t = 45.27 (~07:3x UTC 10-04) — THE CHI FLOOR DOES NOT CURE THE p = 0.90 MERGER: χ_min 5.4e-3,
never near the 1e-4 floor; max|K| ran away at the merging core (93 → 172 in one step), Ham 1.9e-2 at death —
the K-WALL class, which the d6 chain cleared by resolution (lvl6), not the χ-steepness wall. No MOTS before
death (mid-merger, rms 0.21–0.53). The burst reached R = 14 only: E_GW(p = 0.90) needs a finer continuation —
Chk04500 (t = 45) NFS-SECURED for it — but it sits mid-runaway (max|K| 1.77 and climbing), so the continuation
ran from Chk04000: P09-LVL5 (12:48 UTC 10-05), which died at the same instant, t = 45.28 (top). Trust t ≤ 45.2. Filed `06_binary_flyby/`. Was LIVE on card 1 (the user
10-04: "start it with wall fix"):** p09's params with ONLY min_chi 1e-8 → 1e-4 (preemptive — the d6/p060 cure),
stop 40 → 100 and the names, restarted from p09's Chk04000 (NFS-secured first). Catches the p = 0.90 merger,
the FULL burst (p09's was cut mid-flight at its stop) and the wall era without dying. Preflight PASS; restart
verified at t = 40.09. ~7 u/h → t = 100 ~14:00 UTC 10-04.

**P060-CHI `merge_orbit_flip_d12_p060_L128_lvl4from50_chi1e4_t100_lbf_csm_r05000` DONE 10-04 (reached t = 100,
no NaN) — NO HORIZON CONVERGES AT lvl4: the surface stays marginally untrapped to the end (rms θ_out
5.7e-2 → 1.64e-2, monotone; R 4.49–4.52; waist 1.64 → 2.09, deform 0.17 → 0.136 — the pinched peanut rounds on
a ~75-u timescale, extrapolated convergence t ≈ 110–115, past the stop). THE FRAMES LOOK STATIC t = 51–100
BECAUSE THE SHAPE CHANGE IS ~0.1 %/u — real but slow (the user's eye was right). Trust t ≤ 80 (tightened from 84 on the user's eye: Weyl4 junk/pixelation visible from ~78; Ham e-folds
every ~11 u from ~80 to 8.8e-3; late ψ4 maxima out of order). Movies and the 0–80 stitch cut there. Chk10000 NFS-SECURED for a horizon-birth
extension (the open question: late horizon vs lvl4 artefact — a lvl5-from-90 spot check would also answer).
Filed `06_binary_flyby/`, closeout + the 0–100 stitch running. Was LIVE since ~08:4x UTC 10-03 (the user's go:
"through the wall ... lowering min chi"):** the extension's params from its own
Chk05000 (t = 50) with ONE knob — min_chi 1e-8 -> 1e-4, the d6 chain's proven wall cure — to t = 100.
Checkpoints every 5 keep 3 inherited; the full MOTS-tuned consumer set. **IT CROSSED THE WALL ~09:05 UTC:
past 55.52 with no NaN (min chi riding the 1e-4 floor, constraints clean) — the chi-floor cure generalizes
from the d6 merger to the d12 plunge, two systems now.** Through t = 88.75 at 13:45 UTC (~7 u/h): still NO
converged common MOTS, but rms theta_out falls monotonically post-wall (5.7e-2 at 55 -> 2.6e-2 at 88, R ~ 4.50,
deform 0.15 — a slowly settling remnant); max|K| 0.311 -> 0.287 over t = 83–88, a slow ringdown, not a freeze.
t = 100 ~15:20 UTC delivers the horizon verdict.

**EGW-p06-EXT DIED t = 55.52 (~08:00 UTC 10-03) — the merged-core single-cell h11 NaN, THE d6 CHAIN'S WALL ON
THE d12 PLUNGE** (level 4; chi pinned on its 1e-8 floor; global constraints clean, L2 Ham 3.5e-4 — the 1/chi
steepness runaway, ~15 units after contact; the t ~ 52 plunging-merger wall holds across separations). NO
converged common MOTS to the death: nearest approach to marginal t = 41 (rms theta_out 5.8e-3, R 5.06),
receding after. Filed `06_binary_flyby/`, trust t <= 55.5, closeout running; Chk05500 (t = 55) NFS-secured.
PROPOSED (no go yet): the chi-floor continuation from Chk05500 — min_chi 1e-4, the d6 chain's proven cure,
~8 min to the death point, then to t = 100 — settles whether a horizon forms on this plunge.

Queue (10-05 ~15:36 UTC): P060-EXT LIVE on card 0 since 15:34 UTC (LIVE NOW, top); P09-LVL5 DIED t = 45.28 (the
lvl4 instant), BBH-d6 DONE t = 100. SIGN-dyn will NOT run (the user, 10-05): the packed d12 like/flip csm pairs already hold both
signs from t = 0, so its initial-acceleration read is an analysis step on them. Left, all PROPOSED with NO go:
the P09 nan_autopsy restart from P09-LVL5's Chk04500 (~10 GPU-min) and the a = 1.5 / 3 flip arms (~1 GPU-h each:
they separate the coordinate under-read from finite size; GPU_PLAN 10-05 ~12:20). Restart pins: the P09 autopsy
reads P09-LVL5's Chk04500 (NFS-secured 04:53 UTC 10-06 in its `06_binary_flyby/` run dir; restage to scratch); the
p060 extension needs
Chk06000 (NFS). EGW-p012 DROPPED (the user,
10-05): the d = 12, p = 0.12 boosted spiral (SPIRAL-lbf) already is the p = 0.12 point on the same box and
spheres, so E_GW(p = 0.12) is an analysis step on its packed Weyl4 streams (no GPU). At 05:45 UTC 10-05 nothing was
running — all three overnight runs had finished clean and are packed.
The verdicts: the p060 stall is PHYSICAL (no MOTS at lvl5 either); p = 0.45 has NO WALL (the plunge boundary
sits in (0.45, 0.60)); the wave zone is RESOLVED (CONV-csm-w agrees with base-grid extraction to 0.15 % of
peak). Then queued, all PROPOSED with NO go: SIGN-dyn (GPU minutes), EGW-p012 (~4–6 h), the p09
finer continuation (lvl5 from its Chk04500 — the K-wall's knob is resolution), and BBH-d6 (the user,
10-05: the d = 6 merger needs its vacuum twin — a BBH control at d = 6, p = 0.10, bare punctures, the
d12 controls' template, t = 100; without it the gallery's merger row has no same-settings overlay;
~BBH-control cost class, a few h) — the last two LIVE since 12:48 UTC 10-05. Pending analysis: the E_GW(p)
curve (DONE 10-05: 3.85e-2 / 9.0e-2 / 4.9e-2 at R = 20, Sec. VIII + Fig. egw_momentum), the level-4-vs-5 comparison, Fig. 5/§VI on the complete MOTS history. DONE overnight: the p060
chi leg (t = 100, no horizon at lvl4), EGW-p09 (t = 40, third plunge, burst cut at the stop), MOTS-ho3
(t = 100, history complete), and CONV-csm-w on the second node (R = 28 ball; R = 44/36 both OOM one card). Both
nodes' scratch is clean: the first node empty, the second holds only the HFL cell (60G, the deliberate keep;
CONV-csm-w's 129G cell wiped ~05:35 UTC 10-05, manifest, 584G free). NEW from the full films (the user's eye,
10-05, on the p = 0.90 stitched t = 0–45 K movie): the mouths VISIBLY INFLATE on the approach and the merging
core starts to inflate — no wall is visible on screen; the run's NaN at t = 45.27 is where the code stops. Noted in the
registry (the chi-leg row) and the movies README; a quantitative mouth-radius read is a pending analysis step.

**EGW-p06 `merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm` DONE t = 40 (10-03 ~05:15 UTC; below). Was LIVE on
card 0 since ~19:25 UTC 10-02 (the user's go ~18:20 UTC):** E_GW(p) above the fly-by — the turnover hunt. The fly-by's packed params with only
p 0.25 -> 0.60, stop 40, max_level 4 (the user: exploratory; extraction reads the base grid either way) and
the name; checkpoints every 5 keep 3; binary main3d_boostpair_91ed17cd; the fly-by's consumer args +
--mots-spectral. Preflight PASS (14/14 frames); boosted solve passes 1-3 residual -> 3.5e-12; start
verification watcher armed. ~4-6 h -> t = 40 ~23:30-01:30 UTC. EGW-p09 follows on this card.

**EGW-p06-EXT `merge_orbit_flip_d12_p060_L128_lvl4_t100_lbf_csm_r04000` DIED t = 55.52 (10-03; above). Was LIVE on
card 0 since ~06:00 UTC 10-03 (the clean relaunch; the user: "run it till t 100 or nan"):** restarted from Chk04000 with the FULL consumer
set — the fly-by fields + the d6 chain's finder tuning (level 2, half 6, lmax 8, seeds 5.0/3.5, centre 64^3)
and the corrected horizon-track. First verdict t = 41: both seeds stall on ONE surface, R 5.057, deform 0.109,
rms theta_out 5.8e-3 AND FALLING (9.1e-3 at t = 40) — near-marginal, tightening; the converged row is the
merger verdict. ~7 u/h -> t = 100 ~14:30 UTC if no NaN. The FIRST attempt (suffix doubled, consumer up without
the finder flags, 3 points scanned untuned) was stopped at t ~ 43.5 and archived 00_archive/aborted on the
user's word (scratch wiped, manifest 10-03); p09's false start wiped/archived the same pass, relaunches on
card 1 after CONV with this full consumer set. Was:** the p = 0.60 PLUNGE continued from Chk04000 (t = 40; secured on
NFS first). The t040 leg ended mid-plunge: separation 3.47 -> 2.19 over t = 36-39, trackers onto the centre at
40, the 3D finder stalling NEAR a surface (R ~ 5.13, deform 0.104 — the d6 common-MOTS class) without
converging — the extension is the MOTS verdict. Same params, only stop_time 100; the launcher doubled the
_r04000 suffix (cosmetic); the consumer was restarted by hand with the corrected horizon-track path before the
first plotfile. EGW-p09 was stopped seconds into evolution for this card (the user's call; no data lost) and
relaunches after CONV. ~7 u/h -> t = 100 ~13:45 UTC 10-03 if no NaN.

**EGW-p06 t040 leg DONE 10-03 ~05:15 UTC — A PLUNGE, the turnover hunt finds a second merger candidate** (t = 40
clean, no NaN; L2 Ham blips over 2.5e-2 from t = 7.65 — 20 transits of <= 0.4 u, the p²-junk at lvl4 — sustained
level 1e-3 class). Filed `06_binary_flyby/` (file_run.sh moved the raw dir into the group folder; frames 196M +
Chk04000 22G intact there). Closeout + the E_GW burst read are pending the extension's verdict for the trust
window.

**WIDTH TWINS `ctrl_rest_a15_csm` + `ctrl_rest_a3_csm` DONE 19:21 UTC 10-02 — both reached t = 15 clean on
one card** (no NaN; Ham 7.2e-3 / 2.4e-3, Mom ~3e-5, the rest-probe class; no MOTS anywhere, correct). The
a-ladder of matching constants: c = 2.3154 (a1) / 2.0592 (a15) / 2.1155 (a2, the d12 rung) / 2.4506 (a3). Filed
`03_two_throats/csm/`; REDUCED 10-05 into `matched_rest_displacement.dat` and drawn as Fig. 4(d), the width
ladder (TO DO section above). Was LIVE since
~15:40 UTC: the §V.B width-ladder arms on matched data — A1-csm's recipe (the
archived superposed params + the d12_csm solve block + the 20-var plot_vars line), t = 15, L = 64 level 3,
checkpoints every 2.0 keep 3. TWO PREFLIGHT REFUSALS FIRST (nothing started): the archived a15/a3 params carry
a SECOND `amr.checkpoint_files_output = 0` line later in the file that overrode the block's `= 1` (A1's params
had no duplicate) — the later line flipped to 1 in both templates, relaunched. Start verified 15:45 UTC by
effect: solves pass (a15: pass 1, c = 2.0592, far sides matched 1.4e-8; a3: pass 2, c = 2.4506, 5.8e-9 — the
a-ladder around a1's 1.9735), both stepping, consumers rendering (frame 0 eyeballed: a3's throats visibly
wider), MOTS scan runs (no MOTS at t = 0, as a resting pair should), Chk00000 each. Measured pace sharing the
card: ~4.6 u/h each -> t = 15 ~19:00 UTC 10-02. Then the matched_rest_displacement re-measure + Fig. 4(a) redraw on all three arms.

**PLACE-csm (the user's go ~14:35 UTC) DONE 14:52 UTC:** the 18 one-step placement probes `place_d{6..48}_step1_csm` on
mode-3 data, sequential on card 0 via a driver (each: the superposed probe's params + the solve block + the
name; no checkpoints, max_steps 1, the t = 0 plotfile is the measurement). All 18 solved OK and packed
(`04_binary_headon/placement_csm/`, commit 8443c828); d6 R_min 1.073 vs the superposed 1.291 (17 %). The
placement-curve re-measure for Fig. 4(d,e) is the pending analysis step (placement_curve.py reads only the
superposed group).

**EGW-p09 `merge_orbit_flip_d12_p090_L128_lvl4_t040_lbf_csm` DONE 10-04 (reached its stop t = 40 clean, no
NaN, ~4.1 u/h; Ham sustained > 1e-3 from 11.5, the p²-junk lvl4 class) — A THIRD PLUNGE: separation 11.8
(t = 20) → 2.62 (t = 40), contact just past the stop, no MOTS yet (rms 0.19). THE BURST WAS CUT MID-FLIGHT
(R = 14 still rising at 40; the outer spheres never saw it): E_GW(p = 0.90) comes from the chi1e4 extension on
card 1. Filed `06_binary_flyby/`, Chk04000 NFS-secured. Was LIVE since ~07:12 UTC 10-03:** the
E_GW(p) far-side point, p = 0.90, lvl4, stop 40, checkpoints every 5 keep 3; the extension's full MOTS-tuned
consumer set; preflight paths check PASS. ~4-6 h -> t = 40 ~11:30-13:15 UTC.

**CONV-csm DONE 07:10 UTC 10-03 — t = 100, no NaN; trust t <= 57.2 (the lvl5 arm's own cut was 56.5: the two
levels AGREE on where trust ends — the first convergence statement). Filed `08_convergence/`, closeout without
movies; the level-4-vs-5 comparison is the pending analysis step. Was:** the solved spiral at
max_level 4 from t = 0 — the convergence/referee run against the paper's lvl5 csm spiral. Only the level and
names changed; checkpoints every 5 keep 3 (the base's block); NO frames/movies (the 08_convergence exception,
reason in the manifest); extractions kept (radii 14/20/30/44, scalar modes). Measured ~4.4 u/h (slower than
the 8-10 h estimate) -> t = 100 ~13:00 UTC 10-03.

**SEED-csm `single_eps_p1e1_t100_csm` (the user's go ~09:30 UTC 10-02, "ok agreed"; started 10:06 UTC):** the
kicked single on SOLVED data, to prove the declared kick is not the junk source. THE KICK CHANGED FORM at
launch: the binary ABORTS on a conformal seed + solve (uniqueness — the solve would erase the seed) and
prescribes the puncture coefficient, so the +10 % push is carried by solve mode 2 with
c_A = 1.1 x c_iso = 2.4126081 (the code's mode-1 note equates a c-offset with a spherical seed of that size).
Two preflight catches before that: a stale `checkpoint_keep = 2` in the inherited params (contradicts
checkpoints-off; line dropped), then the conformal-seed abort. Otherwise the old run's params byte-for-byte;
NO checkpoints (the user's word); `main3d_csmatch_5f988dbc`; the probe's consumer args + `--mots-spectral`.
L = 64 level 3, t = 100, ~5 GPU-h -> done ~15:00-20:00 UTC depending on pace. Start verified 10:06 UTC: solve
printed c_A 2.4126 (superposed 2.1933), far side 1.268 x isolated mass / 1.21 x charge (the kick is in the
solved data), M_ADM 1.2539 (volume identity), STEP 0 regrid, card 0 at 19.9 GB. The mirror m1e1 (c = 0.9 x
c_iso) stays the optional twin. STOPPED AT t = 31.5 (12:35 UTC 10-02, dump_and_stop on the user's word): the
question is settled — THE KICKED SOLVED DATA IS BORN TRAPPED (3D-finder MOTS on the t = 0 slice, R 4.306,
M 2.15; min lapse 0.008 by t = 30), the same prompt collapse as the superposed twin (round-scan horizon by
t = 1): the constraint solve does not erase or soften the declared kick. NO further single-wormhole runs (the
user's word; the m1e1 mirror cancelled). Consumer drained 12:05 UTC (MOTS to t = 31.5: R 4.306 -> 3.039, frames complete); PACKED `01_single_throat/seed/` 12:3x UTC (closeout 0 problems; its movies finished before the user's no-movies word and stay on disk); only the scratch prune and the idle watch-mode consumer remain for a first-node session. CONSUMER INCIDENT: `--profile none` sets WHM_CONSUME=0 and silently drops
`--consume-args`, so the run went 1.5 h with no consumer (no frames, no MOTS, plotfiles piling to 29); the
sidecar was started by hand 11:50 UTC with the intended args (venv `test_post` symlink; backlog from Plt00000
reprocessing, keep-last 3 pruning as it goes). CLAUDE.md launch step 4 now says the consumer is part of the
start. ~18 u/h -> t = 100 ~15:45 UTC.

**MOTS-ho1 `merge_headon_flip_d8_v1_L128_lvl5from0_mots_t035_csm` DONE 09:43 UTC 10-02: reached t = 35 clean**
(no NaN, L2 Ham 4.3e-4 / Mom 6.9e-4 at the end). THE HEAD-ON'S TRUE HORIZON HISTORY t = 0–35: birth at t = 18
(R 5.634, M_MS 2.817, deform 0.104) — 4 units earlier and 12 % larger than the round scan's caption values
(t ≈ 22, R 5.02) — settling to R 4.789, M_MS 2.394, deform 0.026 at t = 35. Packed `04_binary_headon/mots/`;
Fig. 5 / §VI re-measure proceeds when MOTS-ho2/ho3 land (both pinned to the SECOND node's checkpoints).

Both consumers find the common MOTS with the 3D finder from t = 50 (spiral) and t = 43 (fly-by) on (restarted 08:24 / 08:25 UTC 10-01, and again 08:42 / 08:43 so that a plotfile with no MOTS gets a row of nan; CRITICAL above).

**A1-csm `ctrl_rest_a1_csm` DONE 14:05 UTC 10-02: reached t = 15 clean** (no NaN, Ham 8.7e-3 probe class, no
MOTS as a resting pair should have). Fig. 4(a)'s width arm restored on matched data; the
matched_rest_displacement re-measure + the panel redraw are the NEXT ANALYSIS STEP. Packed
`03_two_throats/csm/`. Was: the a = 1 (half-width)
resting pair at d = 12 on matched data, t = 15 — restores Fig. 4(a)'s width arm. The archived a1 params +
only the d12_csm solve block + the family checkpoint rule (every 2.0 keep 3) + the full-frame plot_vars line
(the preflight refused the old 5-var set: shift/local_speed frames need them — output only). Solve converged
pass 1: c = 2.3154 both, far sides matched to 1.8e-8. ~10 u/h -> t = 15 ~13:30 UTC. PLACE-csm is next on this
card, on the user's go.

**BBH-HEADON `bbh_headon_d8_L128_lvl5_t100` DONE ~13:55 UTC 10-02: reached t = 100 clean** (no NaN). The
vacuum head-on control at per-hole ADM 1.00; the energy/waveform comparison against the wormhole head-on is
the NEXT ANALYSIS STEP. Packed `07_bbh_control/`. SEED-csm's leftovers cleared 14:10 UTC (idle consumer
killed, 7.1G scratch wiped, manifest). Was: the
vacuum control for the head-on — bare punctures, d = 8 from rest, t = 100, per-hole ADM 1.00 (bare mass
rescaled 0.9615 -> 0.9443 by the old file's own Brill-Lindquist rule), checkpoints every 5 units keeping 3
(the user's word; Chk00000 seen at start). Binary = the built BinaryBH example (the d12 controls'); profile
`bbh`. LAUNCH NOTE: the full preflight's start-up probe does not know the BinaryBH grammar's stop keys and ran
the actual evolution into `_preflight/` (54G by t = 11.5, would have filled the disk) — killed, wiped,
relaunched with `WHM_PREFLIGHT=static` (recorded in the manifest). The probe clocked ~32.6 u/h at lvl5, so
t = 100 is roughly 3 h: ~14:45 UTC. K-MOVIE FIX 15:25 UTC (the user caught the moving colourbar): closeout's
rerender skips K by default, leaving per-frame autoscale — `rerender_frames.py <frames> --only K --movies`
rebuilt movie_K_z.mp4 on a fixed scale from the cached slices. Other runs' K movies share the default
(fly-by, SEED, A1); fix not ordered.

**FLYBY-lbf `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` DONE 11:17 UTC 10-02: reached t = 100, no NaN —
A SCATTER, NOT A PLUNGE** (closest 2.33 at t ~ 47, no common MOTS on any plotfile). Trust t <= 63.3 (the L2 Ham
2.5e-2 crossing; 2.69 by t = 100 — late data past trust as expected). Packed `06_binary_flyby/`, movies cut at
63.3, closeout 0 problems; scratch (128G: 3 Plt + rolling Chk) wiped 11:35 UTC on the user's word (manifest).

**SPIRAL-lbf DIED at t = 71.78 (13:58 UTC 10-01, NaN in h11, level 2) — NO MERGER, the third d = 12 arm to
inflate instead.** Closed out 10-01 evening (`05_binary_spiral/lbf/`, movies to the trust window t <= 56.5 — the
L2 H criterion 2.5e-2 crossed at t = 56.3, the csm spiral's own cut): the trackers collapse onto the central pit
at t = 38.06, the 3D finder sees no common MOTS anywhere (±6 window valid to t ~ 61, nan rows to the end), and
the boost did not change the Bowen–York arm's verdict. Consumer drained to the end. Its scratch was wiped 20:15 UTC 10-01 (`MANIFEST_CLEANUP_2026-10-01`); card 0 went to MOTS-ho1, then SEED-csm (10-02).

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

## Second node (one H100): card idle, scratch clean — only the HFL cell (60G, the deliberate keep) remains, 584G free (05:35 UTC 10-05)

**CONV-csm-w `v2_spiral_d12_p012_L128_lvl4w_t040_csm` DONE ~18:00 UTC 10-04 (reached t = 40, no NaN; packed
`08_convergence/`, verdict in the queue paragraph above). Its scratch cell (129G) wiped ~05:35 UTC 10-05 on
the user's word ("wipe out leftovers"; manifest 10-05). Was LIVE on card 0 since ~06:50 UTC 10-04 (the user:
"whatever fits the gpu"): the wave-zone referee run at the R = 28 BALL — extraction_levels 0 1 0 0, the
ExtractionTagger refines r < 33.6 to level 1, so the R = 20 AND R = 28 waves travel and are extracted at
dx 0.25 the whole way (R = 36/44 stay base-grid). The sizing is now measured, not estimated: the R = 44 ball
(106M cells) OOM'd at the step-0 plotfile, the R = 36 ball (77M) OOM'd one step into the probe's evolution —
the evolution workspace is the hidden cost (~1 GB per M cells live) — and the R = 28 ball (~58M) runs at
77.6 of 80 GB: it fits, barely; a mid-run OOM would be loud in the log. Stop 40, checkpoints every 5 keep 3
(the user's standing answer), no frames/movies (the 08_convergence exception), consumer radii 14/20/30/44 +
scalar modes. ~3.5 u/h → t = 40 ~18:00 UTC 10-04. The two OOM probes' stub archived 00_archive/aborted.

**MOTS-ho3 `merge_headon_flip_d8_v1_L128_lvl4from50_mots_t100_csm_r05000` DONE ~21:20 UTC 10-03 (reached
t = 100, no NaN; Ham 1.2e-3 / Mom 5.9e-4 at the end) — THE TRUE HORIZON HISTORY IS COMPLETE t = 0–100
(ho1+ho2+ho3): 50 converged rows t = 51–100, seam with ho2 fine (R 4.7776 at 51 vs 4.7794 at 50), endpoint
R 4.7787, M_MS 2.3894, deform 0.0039 — the oriented scan's t = 100 endpoint (4.69 / 2.373) read 1.9 % / 0.7 %
low. Fig. 5 / §VI re-measure unblocked. Filed `04_binary_headon/mots/`, closeout running from the first node.
Its scratch cell (84G) and the released leg-1/leg-2 checkpoint cells (26G/28G) were pruned ~06:40 UTC 10-04
(manifest; the HFL cell 60G stays). Was LIVE since ~14:15 UTC 10-03 (the
standing go; checkpoints every 5 keep 3):** the head-on chain leg 3 (t = 50–100, max_level 4) with the 3D
finder on every plotfile — the last window of the true horizon history for Fig. 5 / §VI. Leg 3's packed params
with only the names + the checkpoint block changed, `amr.restart` stripped (the ho2 lesson, now launcher-
enforced), `--restart` from leg 2's Chk05000 (the scratch copy, 28G cell kept). Preflight PASS, paths "one
spelling". Start verified by effect: restart at t = 50.01, 7.03 u/h, card 46 GB; consumer pid live with the
full leading args + the suffixed horizon-track. ~7 h -> t = 100 ~21:30 UTC 10-03.

**CONV-csm-w (the user's go ~14:05 UTC, "the referee run") REFUSED by the preflight probe — nothing started:**
`extraction_levels = 0 0 0 1` (the R = 44 sphere) tags the ball r < 52.8 to level 1: 65.8M level-1 cells (49 %
of the domain), ~106M in all; the probe died "Arena out of memory" at 77.4 GB of this card's 80 (report kept in
`logs/preflight_refused/`). Template `templates_scan/params_v2_spiral_d12_p012_L128_lvl4w_t040_csm.txt` is
diffed and ready; as designed it needs the first node's TWO cards. One-card variants: the R = 36 ball
(0 0 1 0, ~77M cells, est. 60–65 GB) or the R = 28 ball (0 1 0 0, ~58M, ~45 GB). Awaiting the user's pick.

**MOTS-ho2 `merge_headon_flip_d8_v1_L128_lvl6from35_mots_t050_csm_r03500` DONE ~13:55 UTC 10-03 — reached
t = 50 clean (no NaN; L2 Ham 1.4e-4 / Mom 4.2e-4 at the end; 2.04 u/h). THE TRUE HORIZON HISTORY t = 35–50:
the common MOTS continues ho1's without a seam (R 4.7929 at t = 36 against ho1's 4.789 at 35) and settles to
R 4.7794, M_MS 2.3897, deform 0.026 at t = 50 (warm Newton 3 iters, residual 5.1e-7). Filed
`04_binary_headon/mots/`, closeout 0 problems (movies to t = 50, 14 fields); scratch cell (104G) pruned,
manifest 10-03. Was LIVE since ~06:40 UTC (the user's go; checkpoints every 5 keep 3) — THREE refusals first,
no GPU touched:** (1) leg 2's packed params
carry their own `amr.restart` and the launcher refuses doubling it with `--restart`; (2) without the flag the
final name loses its `_r03500` AND the full preflight refuses a restart template (the 0-step probe writes no
t = 0 frame); (3) the working form: strip `amr.restart` from the template ("no shipped template carries it")
and pass `--restart` — a restart-leg template must NEVER keep its parent's amr.restart line. Evolving at
~1.96 u/h from t = 35.016.** leg 2 again from leg 1's Chk03500 (t = 35, max_level 6) to t = 50 with the 3D finder on
every plotfile — the head-on's true MOTS through the wall, for Fig. 5. ho1's exact consumer recipe, only the
stop and names changed. ~2.0 u/h -> t = 50 ~13:45 UTC 10-03. ho3 follows from leg 2's Chk05000 (28G NFS copy
secured ~06:14 UTC). CHAIN SCRATCH PRUNED ~06:15 UTC: all four spiral cells (152G) wiped — every restart
point was verified NFS-secured first (Chk02500/03000/03500); the head-on cells and HFL kept (manifest 10-03).
STITCH DONE ~06:25 UTC: the chain's full t = 0-100 movies (leg 1 to 25, sigma to 30, chi to 35, settle to
100 — every handoff inside its leg's trust window), 14 fields x 101 frames in the settle leg's
stitched_from_t0/movies/. K is the exception to the symlog set (the user): one fixed LINEAR scale
(+-0.069 measured over the whole series) — static bar, lobes visible; frames eyeballed at t = 13 (merger)
and t = 60 (settled core). PRUNES 10-03 (the user's word, manifest): the t040 leg's first-node scratch
(94G, Chk04000 NFS-verified first) and the killed runs' cells; first-node scratch clean, 922G free.

**D6-lvl4from35 `spiral_d6_p010_L128_lvl4from35_t100_lbf_csm_r03500` DONE ~00:45 UTC 10-03 — reached t = 100
clean: THE d6 CHAIN COMPLETES, t = 0-100 through the wall** (no NaN; L2 Ham 1.0e-4 at the end, never near
2.5e-2; MOTS settling R 4.883, M_MS 2.441, deform ~0.01 at t = 100; min 1/chi ran ~6.7e-5 naturally — the
pre-wall numerics hold post-wall). Filed `05_binary_spiral/merger_d6/` (the raw dir moved into the group
folder); closeout running; the joined chain MOTS history + per-leg trust rows + the chain narrative are the
next analysis step. Its scratch prune needs a second-node session. Was LIVE since ~15:20 UTC 10-02:** the chain's settle leg from the chi leg's Chk03500
(t = 35, past the wall) with PRE-WALL NUMERICS — the wall knobs reverted per the user (min_chi back to 1e-8,
sigma back to 0.1: they were crossing devices), max_level 4, stop_time 100. Start verified by effect: t = 37.15
-> 38.05, maxK 0.45 and falling (min 1/chi runs ~6.7e-5 naturally, no cap needed post-wall), Ham 1.4e-4, MOTS
R 4.9175 deform 0.012, 15 frame series, consumer warm-starting the 3D finder each plotfile. ~7.1 u/h ->
t = 100 ~00:30 UTC 10-03. At the stop: the chain completes — full systematics, the joined chain MOTS history,
per-leg trust windows, the chain narrative. MOTS-ho2/ho3 queued behind it on this card (their Chk03500/Chk05000
pins live on this node's scratch).

**D6-chi `spiral_d6_p010_L128_lvl5from30_sig10_chi1e4_t060_lbf_csm_r03000` STOPPED BY HAND at t = 36.62
(~15:05 UTC 10-02) — THE CHI FLOOR CURES THE CELL.** min_chi 1e-8 -> 1e-4 from sig10's Chk03000 (sigma 1.0
kept): sailed through the t = 30.53 death point and ran clean to 36.62 — maxK 0.45-0.76, no bright pixels in
the K frames (user-verified visually), constraints ~2e-4, MOTS steady ~4.92. The missing Fig. 11 rung: the
single-cell h11 blow-up is a 1/chi steepness runaway, capped by the floor; it sits inside the MOTS, censored.
Stopped for the lvl4 downgrade once Chk03500 (t = 35) was written and COPIED TO ITS NFS RUN DIR. Close-out
(pack `05_binary_spiral/merger_d6/`, default movies — the chain's crossing leg; the chi-floor caveat in its
registry row) + its scratch prune PENDING a second-node session; sig10's scratch Chk03000 stays until the
chain's knob tests are declared done.

**D6-lvl7 `spiral_d6_p010_L128_lvl7from25_t060_lbf_csm_r02500` DIED t = 27.53 (11:16 UTC 10-02) — TWO UNITS
BEFORE lvl6's death, same single-cell h11 NaN at the core centre, max|K| still climbing (7.8 at death; lvl6's
5.6-peak-then-ringdown was therefore not converged).** Finer dx tracks the core blow-up further and dies
sooner: the core instability is continuum physics, NOT under-resolution — more levels are ruled out. It is all
inside the MOTS (steady at R 4.92), censored. Constraints clean to the last step (2.2e-4). Wrote no
checkpoints; `Chk02500` (t = 25, scratch + NFS) stays the chain's only restart point. Filed
`05_binary_spiral/merger_d6/` as a diagnostic arm (no movies; frames kept). Its scratch (plotfiles only)
awaits a prune from a second-node session. THE KNOB UNDER TEST NOW (the user's go 12:00 UTC: "higher
sigma wall test ... level 5 from chk 25"): D6-sig10 `spiral_d6_p010_L128_lvl5from25_sig10_t060_lbf_csm_r02500`
— KO `sigma` 0.1 -> 1.0 at LEVEL 5 from the same Chk02500, live since ~12:03 UTC. One run tests both walls: if
sigma holds the K runaway at lvl5 (which killed leg 1 there at 26.26) AND the core cell (which killed lvl6/7),
the whole chain finishes at lvl5 speed (~2.9 u/h, t = 60 ~12 h). VERDICT: cleared both earlier walls (max|K| 1.1-1.8 flat through 26-29) then DIED t = 30.53, the same single-cell h11 NaN (2.45 -> 57 in one step) -- sigma delays the cell, does not cure it. Chk03000 (t = 30, past both walls) written and COPIED TO NFS: every next knob restarts from it, ~8 min to the death point. The min_chi 1e-4 knob was taken (the user's go ~13:30 UTC) and CURED it — see D6-chi above. Trust 30.5; filed; scratch plotfiles to prune after closeout. Template = the lvl7 leg's with only the names,
max_level 5 and sigma; checkpoints keep the chain's rule (every 5, ONLY the newest). If it dies at the K wall:
sigma at lvl6 is the fallback; `min_chi` 1e-4 after; interior fill last. MOTS-ho2 queued behind it. lvl7's
scratch (15G plotfiles) wiped 12:00 UTC (manifest); Chk02500 + the ho2/ho3 checkpoints + HFL kept.

**D6-lvl6 `spiral_d6_p010_L128_lvl6from25_t060_lbf_csm_r02500` (RETIRED: died t = 29.407, 08:1x UTC 10-02):
through the K wall, killed by a grid-scale core instability.** It cleared leg 1's wall — max|K| peaked 5.6 at
t ≈ 26.5 and rang down to 1.95, constraints at the arm's best (Ham 1.9e-4) — then a single cell at the merged
core's centre went NaN in h11 on level 6 (`post_timestep` check; the single red spike in the K frame). Not the
K wall: everything global was clean to the last step. MOTS tracked to t = 29 (R 4.907, M_MS 2.454, deform
0.024). Trust t <= 29.4; packed `05_binary_spiral/merger_d6/` 10-02 (the user: needed for the ladder figure);
it wrote NO checkpoints (died 60 steps before Chk03000), so the lvl7 rerun restarts from the same Chk02500.

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
(p = 0, clean of the momentum issue) done to t = 100 as legs 1–3 (`main3d_csmatch_5f988dbc`); **spiral** done as the
boosted rerun (SPIRAL-lbf: died t = 71.78, no merger; the Bowen–York one stopped at t = 60.40, closed out); **fly-by** done
as the p = 0.25 lbf rerun (FLYBY-lbf: t = 100, a scatter; the Bowen–York one stopped at t = 64.98, overturned). Templates in `runs/wormhole_merger/templates_scan/`.

**Wave settings, the same in every run of the set (the user, 2026-09-30; checked 12:25 UTC against each run's
`params.txt`, manifest and output headers):**
- in-code Ψ4 (`Weyl4_mode_*.dat`, every coarse step): spheres 20/28/36/44, 24 × 37 points, 21 modes (l = 2–4,
  every m);
- consumer (every plotfile, 1.0): scalar modes l = 0–2 and the python Ψ4 l = 2 modes on spheres 14/20/30/44.
- Head-on, all three legs: these plus its old spheres (in-code Ψ4 also at 10/14/18, consumer also at 10/18), the
  same in each leg, t = 0–100 covered (legs 2–3's restart files carry no header; columns as leg 1's).
- The spheres against the grid (head-on, merged): R ≤ 20 lies inside the level-1 cube, R = 28 (and the consumer's
  R = 30) cuts its corners, R = 36 / 44 are on level 0 — the last two are the clean ones late (Traps).
- Spiral (done): exactly the shared set.
- Fly-by (done; launched with the fix): radii the shared set. **Fixed 12:27 UTC:** its template had no angular-grid or mode lines, so
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
| D6-lvl7 | `spiral_d6_p010_L128_lvl7from25_t060_lbf_csm_r02500` | **DIED t = 27.53 (10-02): the same core h11 NaN TWO UNITS EARLIER than lvl6, max\|K\| still climbing — resolution ruled out as the cure; diagnostic arm, filed, no movies. The chain went on (sig10, the chi leg, the lvl4 settle leg) and COMPLETED t = 0–100 (SPIRAL-d6-prod)** | leg 2's template with only the name and max_level 6→7; same `Chk02500` restart (leg 2 wrote no checkpoint); checkpoints every 5 keeping ONLY the newest (the user's word 10-02) — copy any Chk a later leg needs to NFS at once | ~1.3 u/h at lvl7: ~27 h for t = 25–60 (~12:00 UTC 10-03); the lvl4 drop once max\|K\| settles cuts it to ~this evening |
| D6-lvl6 | `spiral_d6_p010_L128_lvl6from25_t060_lbf_csm_r02500` | **RETIRED 10-02: died t = 29.407, single-cell h11 NaN at the merged core's centre (level 6), globals clean to the end** — not the K wall (max\|K\| 5.6 -> 1.95 falling, Ham 1.9e-4). MOTS to t = 29 (R 4.907). Trust t <= 29.4; packed `05_binary_spiral/merger_d6/` (the ladder figure will use it) | was: the head-on leg-2 pattern, restart from `Chk02500`, max_level 6 | ran ~2.0 u/h for t = 25–29.4 |
| MOTS-ho3 | `merge_headon_flip_d8_v1_L128_lvl4from50_mots_t100_csm_r05000` | **DONE ~21:20 UTC 10-03: t = 100 clean — the true horizon history complete t = 0–100 (endpoint R 4.7787, M_MS 2.3894); packed `04_binary_headon/mots/`.** PAPER, REQUIRED (CRITICAL above): the head-on's true MOTS over t = 50–100 for Fig. 5(a,b) and its end values (t = 100) | leg 3 again from leg 2's `Chk05000` (max_level 4) to t = 100, leg 3's packed params with only the name changed; `headon-modes-prod` (`--mots-spectral`), keep-last 3; checkpoints asked at launch; its input checkpoint lives on the SECOND node's scratch — run it there (after SPIRAL-d6-prod) | ~7 (7.2 u/h) |
| MOTS-ho2 | `merge_headon_flip_d8_v1_L128_lvl6from35_mots_t050_csm_r03500` | **DONE ~13:55 UTC 10-03: t = 50 clean, seamless with ho1 (R 4.7794 at t = 50); packed `04_binary_headon/mots/`.** PAPER, REQUIRED: the true MOTS over t = 35–50 (through the wall) | leg 2 again from leg 1's `Chk03500` (max_level 6) to t = 50, leg 2's packed params with only the stop (50) and the name changed; as MOTS-ho3 | ~7.5 (2.0 u/h) |
| MOTS-ho1 | `merge_headon_flip_d8_v1_L128_lvl5from0_mots_t035_csm` | **DONE 09:43 UTC 10-02, t = 35 clean; packed `04_binary_headon/mots/`.** The true birth: t = 18, R 5.634, M_MS 2.817 (the round scan was 4 units late and 12 % small: t ≈ 22, R 5.02); end t = 35: R 4.789, M_MS 2.394, deform 0.026; the round scan LOSES the surface over t = 26–35 | leg 1 again from t = 0 (max_level 5) to t = 35, leg 1's packed params with only the stop (35) and the name changed; as MOTS-ho3 | ~13 (2.7 u/h) |
| SPIRAL-lbf | `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` | THE PAPER RUN, FIRST (the user, 2026-09-30): the spiral on the boosted setup — the clean test of "inflates, no merger" | the csm spiral's template + momentum model 1, **no freeze** (the user's word; the pits move at v = 0.12, the runaway was a v = 0.41 problem), max_level 5, checkpoints every 5 keeping the newest 3 (the user's word; LAD-csm needs the t ≈ 50 one); its own verification A **PASSED**; **DONE — died t = 71.78, 10-01, no merger; closed out, trust t <= 56.5** (Live, above) | ~22 to t = 60, ~37 to t = 100 |
| SPIRAL-d6-prod | `spiral_d6_p010_L128_lvl5from0_t060_lbf_csm` | **The chain: leg 1 retired 26.26 -> lvl6 (died 29.4) -> lvl7 (died 27.5) -> sig10 (died 30.5) -> chi leg (cured, stopped 36.62) -> lvl4from35 settle leg DONE t = 100 (~00:45 UTC 10-03): THE CHAIN COMPLETES t = 0–100** (Second node, above). THE MERGER RUN (the merger scout, 10-01: common MOTS t = 12.5–20.5): the d = 6, p = 0.10 design point at production resolution, for the paper's orbital-merger section | the production box (L = 128, N = 256, max_level 5, the shared wave set) with the scout's initial-data block (d = 6: centers +-3, tangential p = 0.10, boosted-pair mode-3 solve); expect the head-on's leg structure through the wall (lvl6 restart) — plan the legs at launch; checkpoints every 5 keeping 3 | ~25–35 |
| SCOUT-d8p | `spiral_d8_p005/p010_lvl3_t040` | **DONE 10-01: the d = 6 scout (misnamed d8) MERGED — common MOTS t = 12.5–20.5; packed `05_binary_spiral/scout_merger/`.** Was: the collapsing-spiral design point (contact must beat the mouths' runaway; the head-on's d = 8 contact at t = 22 wins, d = 12's t ≈ 40 loses) | new setup, so level-3 scouts first (~2–3 h each, L = 64), then level 5 for the winner | ~5 + ~21 |
| FLYBY-lbf | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` | the fly-by rerun | **DONE 10-02: t = 100, no NaN, a scatter (closest 2.33 at t ~ 47, no common MOTS); trust 63.3; packed `06_binary_flyby/`** | ran ~46 h |
| LAD-csm | `ladder_csm_L{4,6,7}_r0XXXX` | **CANCELLED (the user, 10-02).** Was: the wall under refinement, mode-3 (Fig. 12a's rerun) | its restart point (the lb spiral's t ≈ 50 checkpoint) did not survive: `checkpoint_keep 3` pruned it during the run (only t ≈ 60–70 were left at death, past trust 56.5) and the 10-01 wipe removed those; a fresh checkpointed leg (~17 h) is not worth it — Fig. 12a stays on the superposed ladder. Lesson: copy any checkpoint a queued run needs off the keep-N rotation to NFS while the producer is live | — |
| SEED-csm | `single_eps_p1e1_t100_csm` | **DONE 10-02, stopped t = 31.5 on the user's word — BORN TRAPPED on solved data (MOTS at t = 0, R 4.306), the superposed twin's fate: the solve keeps the kick; no more single-wormhole runs, the m1e1 mirror cancelled** (Live, above; the kick carried by solve mode 2, c = 1.1 x c_iso — a conformal seed cannot survive the solve, the binary aborts). PAPER (the user, 10-02): the kicked single on SOLVED data — prove the ε kick is not the junk source (the seeded-throat verdicts §II.D/§IV.C are superposed-only) | `single_eps_p1e1_t100`'s packed params + the mode-3 constraint-solve block with the seed kept (`wormhole_seed_amplitude_A = 0.1`; preflight verifies the seed changes t = 0), only the name + `_csm` changed; L = 64, level 3, t = 100; checkpoints asked at launch; the mirror `m1e1` twin optional after | ~5 |
| BBH-HEADON | `bbh_headon_d8_L128_lvl5_t100` | **DONE 10-02, t = 100 clean; packed `07_bbh_control/`; the energy/waveform comparison is the next analysis step.** Was (WHM_PREFLIGHT=static — the full probe runs the BinaryBH evolution for real): The vacuum control for the head-on: bare punctures at d = 8 from rest, t = 100, for Fig. 5 and the gallery/energy comparison | the csm head-on's setup (same box, grid, spheres, plot cadence) with the drainhole/scalar blocks swapped for bare punctures, as the d = 12 BBH controls; template from `bbh_control_d12_p012_t150`'s params with d and p changed; checkpoints asked at launch | ~30–50 (the head-on chain's class; vacuum punctures ride through a merger, so likely one leg) |
| A1-csm | `ctrl_rest_a1_csm` (then `ctrl_rest_a15_csm` / `ctrl_rest_a3_csm`) | **DONE 10-02, t = 15 clean; packed `03_two_throats/csm/`; the a15/a3 twins done 19:21 UTC 10-02; all three REDUCED 10-05 into `matched_rest_displacement.dat`: Fig. 4(d) + Sec. V B's width sentence (TO DO section above).** Was: Restore Fig. 4(a)'s width arm on matched data (the a = 1 arm left the panel 09-30: no matched twin) and put clmNarrowPairRatio — and with the optional twins the §V.B width ladder clmALadder* — on mode 3 | the old run's packed `evolution_params.txt` with ONLY the constraint-solve block and the name changed (the rest-pair rule), t = 15, L = 64 level 3; checkpoints asked at launch; re-measure into `matched_rest_displacement.dat` and redraw Fig. 4(a) | ~1 each (the csm rest pairs' class: 18 u/h alone) |
| PLACE-csm | `place_d{6..48}_step1_csm` (the 18 one-step probes) | **DONE 14:52 UTC 10-02, all 18 solved and filed `04_binary_headon/placement_csm/`; the curve regeneration + Fig. 4(d,e) redraw are the next analysis step.** The matched placement curve for Fig. 4(d,e), now captioned as superposed-only: expected flat at R⋆ = 3.8895 (the matched pairs read 3.876–3.878 at t = 0), which would draw the clean-data contrast under the superposed excess; re-measures or retires clmMouthTauFlybyPlaced/SeedFlybyPlaced (CSM_SWITCHOVER) | the superposed probes' params (`04_binary_headon/placement/place_d*_step1`) with only mode 3 + names; initial data plus one step, scanned at t = 0; no frames beyond the default t = 0 set | < 1 total (minutes per probe) |
| CONV-csm | `v2_spiral_d12_p012_L128_lvl4from0_t100_csm` | **DONE 07:10 UTC 10-03: t = 100, no NaN; trust t <= 57.2 against the lvl5 arm's 56.5 — the two levels agree on where trust ends; packed `08_convergence/`.** Spiral burst/energy, level 4 vs 5 | the spiral template, max_level 4, from t = 0 | ~8–10 |
| EGW-p06 | `merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm` | **DONE: A PLUNGE — the t040 leg (10-03), the extension (died t = 55.52, the d6 wall), the chi-floor leg (t = 100, no horizon at lvl4) and the lvl5 check (none either: the stall is physical); E/M 4.9e-2 at R = 20 (the glued 0–80 record); packed `06_binary_flyby/`.** Was: E_GW(p) above the fly-by (turnover). max_level 4 on the user's word (exploratory; the extraction spheres read the base grid whatever max_level is — lvl4 only coarsens the throats, the "if it's not NaN" test); checkpoints every 5 keep 3 (the user's answer); template ready in templates_scan, diffed: only p 0.25 -> 0.6, stop 100 -> 40, the name | ~4–6 |
| EGW-p09 | `merge_orbit_flip_d12_p090_L128_lvl4_t040_lbf_csm` | **DONE t = 40 (10-03): a third plunge, its burst cut at the stop; the chi leg died t = 45.27 (the K wall); P09-LVL5 (lvl5 from Chk04000, 10-05) died at the same instant, t = 45.28.** Was: E_GW(p) far side of the peak | same, p = 0.90; template ready, diffed | ~4–6 |
| EGW-p045 | `merge_orbit_flip_d12_p045_L128_lvl4_t040_lbf_csm` | **SUPERSEDED by P045-T100 (t = 100, no wall; E/M 9.0e-2 at R = 20, in Sec. VIII); both t040 starts were stopped near step 0 (10-04).** Was (the user: "start something else from queue"): redraws Fig. 12 top, densifies the E_GW(p) turnover for Fig. 9. p = 0.12 stays the optional second midpoint, no go | the EGW recipe (fly-by template, lvl4, stop 40) at p = 0.45; template diffed (p + names only) | ~4–6 |
| CONV-csm-w | `v2_spiral_d12_p012_L128_lvl4w_t040_csm` | **DONE ~18:00 UTC 10-04: t = 40, no NaN — THE WAVE ZONE IS RESOLVED (the base-grid waveforms reproduced to 0.01–0.15 % of peak); packed `08_convergence/`.** Was (the user: whatever fits one card): the R = 28 ball (0 1 0 0) — R = 44 (106M cells) and R = 36 (77M) both OOM'd the probe; ~58M cells runs at 77.6/80 GB. R = 20 + 28 fully wave-zone-refined | the diffed template at extraction_levels 0 1 0 0 | ~11 |
| SIGN-dyn | `ctrl_sign_dyn_{pp,pm}_csm` | **NOT RUN (the user, 10-05): the packed `ctrl_rest_d12_csm` (like) and `ctrl_flip_d12_csm` (opposite) already ran both signs from t = 0 to 15; READ 10-05: opposite senses from the start (fixed charge excluded at t → 0), ratio 1.42–1.44 by quadratic fits over t = 2–8 and 1.44–1.49 by displacement over t = 4–11.5, against fixed potential 1.500.** Was PROPOSED, REFEREE: the energy-check claim (conductor vs fixed charge) tested dynamically — mode-3 rest pair at both scalar signs, read the initial acceleration from throat_track over a few units | the A1-csm recipe at both signs, stop ~2–5 | GPU minutes |
| P09-LVL5 | `merge_orbit_flip_d12_p090_L128_lvl5from40_chi1e4_t100_lbf_csm_r04000` | **DIED t = 45.28 (14:07 UTC 10-05): h11 NaN on level 4 at the lvl4 instant, max\|K\| calm (1.44) — resolution does not move the death; filed `06_binary_flyby/`, no movies; trust t <= 45.1.** Was: E_GW(p = 0.90) at the outer spheres — does lvl5 carry the merger past the lvl4 K wall (t = 45.27)? | the chi leg's params with only max_level 4 → 5, from p09's `Chk04000` (t = 40; Chk04500 sits mid-runaway); checkpoints every 5 keep 3 (the user) | ~20–24 (2.5–3 u/h) |
| BBH-d6 | `bbh_control_d6_p010_t100` | **DONE 14:44 UTC 10-05: t = 100, no NaN; filed `07_bbh_control/`, closed out with movies.** Was: the d = 6 merger's vacuum twin for the gallery's merger row | BBH-HEADON's params with d 8 → 6, p 0 → 0.10 tangential, bare mass 0.9443 → 0.9282; NO checkpoints (the user) | ~3 (34.5 u/h) |
| EGW-p012 | (not run) | **DROPPED (the user, 10-05):** the d = 12, p = 0.12 boosted spiral `v2_spiral_d12_p012_L128_lvl5from0_t100_lb_csm` (SPIRAL-lbf, `05_binary_spiral/lbf/`) already is the p = 0.12 point on the same box and spheres (no freeze, lvl5); E_GW(p = 0.12) is an analysis step on its packed Weyl4 streams. THE `_lb_csm` RUN ONLY (checked 10-05: constraint_solve 1, puncture mode 3, momentum model 1, binary 91ed17cd, far-side mass matched to 4e-6) — not the archived superposed `v2_spiral_d12_p012_L128_lvl5from0_t100` nor the Bowen–York `_csm` twin (logged L2 Ham cannot tell them apart: the base-grid floor reads 8.4e-4 superposed vs 1.1e-3 solved). Was: the optional second midpoint of the E_GW(p) curve | was: the fly-by template, lvl4, stop 40, p 0.25 → 0.12 | — |
| P060-ext | `merge_orbit_flip_d12_p060_L128_lvl5from60_chi1e4_t115_lbf_csm_r06000` | **LIVE on the first node's card 0 since 15:34 UTC 10-05** (LIVE NOW, top), stop 115, checkpoints every 5 keep 3 (the user). Was PROPOSED: late trapping — the lvl4 extrapolation puts a converged MOTS at t ≈ 110–115 | the lvl5 check's params with only the stop (past 115) and the name; restart from Chk06000 (NFS-secured) | ~22 to t = 115 (2.5 u/h) |
| FLIP-a | the flip arms at a = 1.5 and 3 (names at launch) | PROPOSED (no go): separate the coordinate under-read from finite size (predictions 1.889 / 1.222; GPU_PLAN 10-05 ~12:20) | the A1-csm recipe, flipped | ~1 each |

Also waiting (10-05): nothing beyond the table. p = 0.45 ran (P045-T100: no wall, so the boundary sits in
(0.45, 0.60)); p = 0.35 and the clean-data single throats are not queued (no further single-wormhole runs, the user
10-02); the spiral freeze continuation lost its restart points (the lb spiral's checkpoints, the 10-01 wipe). The old-data convergence
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
  (abstract and caption quote the ledger's 1.462 ± 0.022); **(d), since 10-05, the matched width ladder: the
  push grows as a^1.2–1.4, not the point-charge a²** (the placement panels left with the superposed campaign). (§V)
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
  **Mode-3 caveat: the csm rerun (Bowen–York momentum) does not end in a merger, and the boosted rerun
  (SPIRAL-lbf, 10-01) does not either — d = 12 never merges; the d = 6, p = 0.10 design point does (the d6 chain,
  common MOTS from t = 13, t = 0–100).** (§VII)
- **Fly-by / capture**: p = 0.45 scatters; p ≤ 0.25 merges, p ≥ 0.35 does not — **withdrawn. The boosted reruns
  (10-02–10-05): p = 0.25 and 0.45 scatter (no wall, no MOTS), p = 0.60 and 0.90 plunge; the boundary sits in
  (0.45, 0.60), and E_GW(p) turns over there (Sec. VIII).** (§VII.A)
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
