# Merger campaign — the plan

One file, kept short, and the only plan that is updated. A finished run adds one
tick in §2 (and a row in §3's queue), and, if it settles something, one line in §4; the numbers themselves are
written once, in the pack (`results/merger/README.md` at the claim, the generated
`single_throat/*.md`), and pointed to from here. The long record is verbatim in
`archive/GPU_PLAN_UPDATED_2026-09-08.md` (the external audit, the forward plan
checked item by item against the code, the Stage-0 result, both ladder results,
the autopsy verdict, the time-step bracket). The model exactly as the code solves
it, with the decision ledger to 2026-09-04, is `archive/GPU_PLAN_2026-09-03.md`; the
campaign record to 2026-09-02 is `archive/Plan_2026-09-02.md`; the code map and traps
as of 2026-08-31 are `archive/Reference_2026-08-31.md`, the original research report
`archive/background.md`. All of that is frozen; this is the only plan.

**Nothing launches without the user's word, one run at a time, through
`grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh`.**

## 1. Goal

Two drainhole throats approach, touch while still wormholes, collapse together,
one black hole forms around the merged pair, and we record the gravitational
waves. No module modifies Einstein's equations mid-run; the untouched natural
run comes first and its verdict counts; every headline result must survive a
change of resolution, of gauge and of the small perturbation dial; "merger"
means the surface counter reads two, then one, by light-ray tracing. If the pair
refuses to merge, that is the result and we measure it.

## 2. Checklist (2026-09-09)

- [x] **Stage 0 — is a lone throat stable?** No. Exact static data holds 26 units, then the Gonzalez–Guzman–Sarbach radial mode grows at τ = 5.9 (T = τ_proper/r_throat 0.87 against the predicted 0.68–0.76). The binary "wall" at t = 44–56 was its clock, never a binary effect. → README "The initial data is exact, and the throat is unstable anyway"; `single_throat/INSTABILITY.md`
- [x] **Phase 2 — resolution ladder, χ twins, time-step bracket** → `single_throat/BRANCHES.md`, `figures/single_throat_branches.png`; archive "Ladder result" I/II, "Time-step bracket"
  - [x] level 2: dies at the origin at t = 24.2 with the throat exact — the grid, not the clamp (its χ twin dies the same)
  - [x] level 3: **collapses** — marginally trapped surface at t ≈ 61, R 3.23 → 2.37 by t = 100, Misner–Sharp mass inside 1.62 → 1.23, no bounce by t = 100
  - [x] level 4: **inflates** — R 3.89 → 10.0, no horizon, growing anti-trapped shell, compactified inner sheet deforming by t = 100
  - [x] same rate to 9 % (τ 5.88 vs 5.26); onset +5.6 to +8.7 units per halving (seed of order 1.5–2.3); the seed's sign flips with resolution
  - [x] χ floor not load-bearing at levels 2, 3, 4 (twins equal to 4 digits; the level-4 pair byte-identical)
  - [x] dt_multiplier 0.02 necessary (0.05 is a different solution from t ≈ 33; 0.1 dies at t = 16)
  - [ ] late constraint growth from t ≈ 75 on both branches explained (open question 1)
- [ ] **Phase 1 — code** → archive "Phase 1" table; `consume_plotfiles/README.md`; GRTresna `feature/grteclyn-wrapper` 5bfa159
  - [x] coded, built, smoke-tested: point-of-use χ regularisation (`chi_rhs_floor`; in a physics run: the twins), solution-following tagger, det h̃ rescale, shock-avoiding lapse, ε seed per throat with sign, boosted Π (the last five not yet in a physics run)
  - [x] in use: corrected θ± shell scan with Misner–Sharp mass, extremum guard and depth column (tested on Schwarzschild and the Ellis throat); NaN autopsy
  - [x] GRTresna: phantom sign and drainhole profile, one solve — throat present, ψ +2–5 % high
  - [ ] GRTresna outer boundary condition on ψ_reg (1 → 1 − b/2r), re-solve, bridge test
  - [ ] W = √χ
  - [ ] MOTS stability eigenvalue
- [ ] **Phase 3 — V1, head-on from rest, d = 8** → archive "Phase 3"
  - [x] scout at level 3: **RAN 2026-09-09 01:09–03:04 on card 0, NaN at t = 26.91** — `merge_headon_flip_d8_v1_t100` (template `templates_scan/params_v1_headon_d8_t100.txt`, launcher `launch_v1_scout.sh`, binary `bin/main3d_boost_2026-09-08.ex`), ~11.8 code units/h; contact t ≈ 20 (02:41), common horizon t = 22, NaN t = 26.91 (03:04); frames χ K lapse φ Π, horizon scan about the tracked mouths, ψ4 at R = 14/30. The seed is the superposition defect (the code warns at d = 8, m = 1 that it is not small — declared, not hidden)
  - [x] **placement curve** (2026-09-09 02:06–02:48, card 1, eighteen one-step probes `place_d{6…48}_step1`, d = 48 puts the centres at the sponge's inner edge): placed throats read +1.8 % (d = 48), +5.0 % (d = 20), +14.4 % (d = 8), +20.5 % (d = 6) above exact — the neighbour is on the ruler, ∝ d^−1.16; against it the scout's mouths are *squeezed* −0.6 % (t = 7), −1.7 % (t = 10), −4.0 % (t = 13, sep 6.06), growing with the closing speed, no expansion phase; the lone throat is exact to 0.1 % until t = 35 → the interaction alone. `PLACEMENT_CURVE.md`, README (placement section)
  - [x] gate: the throats touched at **t ≈ 20 (02:41, sep 2.44; the d = 12 pair needed t = 30)** as wormholes — no trapped and no anti-trapped surface at either mouth or about the midpoint through t = 19, mouths squeezed, midpoint lapse 0.09 and falling, no NaN, Hamiltonian norm 4.3e-3 (the old wording "within 0.1 % of exact" is retired: placement puts the mouths 14 % above exact at d = 8 by construction, and the interaction squeezes them 4 % by t = 13)
  - [x] the merged core: **collapse — a common marginally trapped surface from t = 22** (no mouth ever had its own, so the count goes 0 → 1 about the midpoint), fine scan r 3.17 → 3.66 / R 5.56 → 5.71 by t = 24, then shrinking to r 1.98 / R 4.72 by t = 26 (phantom dissolution again), M_MS ≈ 3, midpoint lapse 0.09 → 0.02; `horizon_offline_scan.dat`, README (Phase-3 section)
  - [ ] **FAILED** — no NaN through +30 units past horizon formation: NaN at +5 (t = 26.91). χ at the midpoint on the 1e-20 floor from t ≈ 24.5, K there doubling every 0.3 units from t ≈ 25.3, one-step overflow in cells 0.9 from the midpoint, 16 cells from any grid edge (autopsy) — the anatomy of `autopsy_nodamp_r05000`. Constraints flat at 2.3e-3 until the last half unit. The χ regularisation and the 1e-20 floor moved the timing, not the outcome
  - [ ] the interior freeze carries the merger past the wall (queue 1c, **in flight since 2026-09-09 04:47**, fill armed at t = 26.5) — and the two Weyl4 streams (in-code at R = 10/14/18 and the consumer's ψ4 at the same radii) agree
  - [ ] the fill-radius twin (queue 1f, from the t = 22 checkpoint) leaves r·ψ4 at R = 10/14/18 unchanged — the head-on's seam test
  - [ ] resolution alone: the level-5 restart from t = 22 (queue 1e) — passes the wall, or dies +1.4/level like the orbital pair
  - [ ] **low-mass head-on** (queue 1d, m = 0.5, d = 6, **in flight since 05:29 on card 1**): no horizon — and then what the throats do at contact
  - [ ] refined member (one level finer) and the ±ε family around it: outcome unchanged
- [ ] **Phase 2b — ±ε arms at level 3** (six runs; after or beside the scout)
  - [ ] +ε: collapse, MOTS, mass loss as at level 3
  - [ ] −ε: inflation, anti-trapped shell, no MOTS; with or without the inner-sheet deformation
  - [ ] onset(ε) linear in ln ε with slope ≈ −5.9
- [ ] **Phase 4 — V2, production with extraction** → archive "Phase 4"
  - [ ] waveform in both channels (Weyl and scalar)
  - [ ] balance: mass lost = energy radiated
  - [ ] ringdown against Kerr

Cards: 0 busy (the V1c late-freeze arm since 04:47), 1 busy (the low-mass head-on since 05:29), 2–3 reserved for the two t = 22 restarts (queue 1e, 1f) once the keeper has copied the checkpoint (~06:47). Scratch: ~750 GB free (everything pruned
2026-09-09 on the user's word; the probes deleted their own plotfiles). Frames: every launch now renders χ, K, lapse, φ, Π
by default (launcher, 2026-09-09) — the ladder runs rendered χ only, and no other
movie of the collapse or the inflation can be made.

## 3. Next — the queue

| ✓ | # | what | cards × wall | decides | success reads |
|---|---|---|---|---|---|
| ☒ ran 2026-09-09 01:09–03:04, NaN t = 26.91 | 1 | **V1 scout: head-on from rest, d = 8, level 3** — φ-sign flipped, K = 0, Π = 0, no boost; production settings of `single_hold_t100` (L 64, N 128, max_level 3, σ 0.1, dt 0.02) with `chi_rhs_floor` on; frames χ K lapse φ Π in the plane of the motion; θ± scan on; no checkpoints; NaN autopsy armed | 1 × ~10 h | Do the throats meet as wormholes before their own decay, and does the merged core collapse (2 → 1 surfaces) — from NaN to a black hole — or something else? | contact by t ≈ 17 with both throats within 0.1 % of exact; surface count 2 → 1 by the θ± scan; no NaN through +30 past the horizon |
| ☑ done 2026-09-09 02:48 | 1b | **placement curve**: the scout's two throats placed at rest at d = 6, 6.5, 7, 7.5, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 44, 48, one step each, per-mouth horizon scan at t = 0 (foreground on card 1; the launcher's consumer sees nothing in a 12-second run — its 30 s Header guard — so each probe was scanned by an explicit second pass over its t = 0 plotfile, `runs/wormhole_merger/launch_placement_probes.sh`) | 18 × 1 min | Is the scout's apparent mouth widening the neighbour's field or the throat? | placement curve ∝ d^−1.16, still +1.8 % at d = 48; the scout's mouths *below* it, −4.0 % by t = 13 → the interaction squeezes; no expansion phase. `PLACEMENT_CURVE.md` |
| 🚀 in flight 2026-09-09 04:47, card 0 | 1c | **V1c late-freeze arm** — `merge_headon_flip_d8_v1c_latefreeze_t100` (template `templates_scan/params_v1c_latefreeze_d8_t100.txt`, launcher `launch_v1_freeze.sh`, same frozen binary): the scout byte-for-byte plus (1) the interior fill armed **as late as the death clock allows, t = 26.5** — the last sample where the scout was still healthy (K = 0.47 finite; the blowup is entirely inside its final 0.15 units) and 0.41 units before its NaN at 26.91 — with r_full 1.2 / r_start 1.8, both inside the *shrunken* t = 26 trapped surface at r = 1.98 and outside the failure site at r = 0.89; (2) in-code Weyl4 extraction at **R = 10, 14, 18**, 21 modes, every coarse step, with the consumer's ψ4 at the same three radii; (3) Weyl4_Re frames over a 40-wide window with χ K lapse φ Π; (4) a rolling checkpoint every 1.0 unit, newest only, so a wall that shifts early is retried from ≤ 1 unit back; stop_time 100. ~11.1 units/h: fill arms ≈ 07:10, t = 100 ≈ 13:45. **Supersedes the pruned v1b arm** (fill at 22.5 — early freezing throws away the dynamics the run exists to capture) | 1 × ~9 h | Is the wall an interior artefact that the horizon makes irrelevant? If the freeze carries the run to t = 100 the *outside* (horizon area, M_MS, the two ψ4 streams) is the result | passes t = 26.91; no NaN to t = 100; the horizon survives the arming smoothly; the two Weyl4 streams agree; constraints bounded outside r ≈ 2 |
| 🚀 in flight 2026-09-09 05:29, card 1 | 1d | **low-mass head-on** — `merge_headon_flip_d6_m05_t100` (template `templates_scan/params_v1_m05_headon_d6_t100.txt`, launcher `launch_v1_arm.sh`, same frozen binary): the V1c file with the drainhole mass halved (0.5 per throat), the centres at ±3 (d = 6, the closest non-overlapping placement), the fill off, rolling checkpoint on, Weyl4 at R = 10/14/18. The "less energy" idea done through the mass: starting closer saves only ~15 % of the impact energy (nearly all of it is gained in the last few units of fall), halving the mass halves the pull and puts the merged mass (~1.5) below the hoop line against mouths of size ~4. ~12.3 units/h; contact ≈ t = 15 (06:45), t = 100 ≈ 13:40 | 1 × ~8 h | What do two throats do when they touch *without* forming a horizon — fuse, bounce, or expand? (The d = 8 pair was inside a horizon by t = 22, so the question could not be read there) | no common trapped surface; the per-mouth radii against the placement curve (+20.5 % at d = 6 by placement alone) through and after contact; no NaN to t = 100 |
| ☐ armed, waits for the t = 22 checkpoint (~06:47) | 1e | **head-on at max_level 5, restarted from t = 22** — `merge_headon_flip_d8_v1_lvl5_t100_r02200` (template `templates_scan/params_v1_lvl5_d8_t100.txt`): the V1c file with max_level 3 → 5 (regrid_interval to six levels), fill off, no checkpoints, plotfiles every 0.5 units, restarted from V1c's `BinaryWormholeChk02200` — kept by `keep_v1c_checkpoints.sh`, since the rolling checkpoint deletes it when t = 23 lands. Never tried for a head-on; on the orbital pair refinement moved the wall +1.4/level and only when the levels were *added mid-run*. ~2.2 units/h: the wall region in ~2.5 h | 1 × ~3 h (35 h if it passes) | Can resolution alone carry the head-on past t = 26.91? | passes the wall → the head-on wall is resolution, unlike the orbital one; dies at ~29–30 → the +1.4/level law holds and the freeze stays the only route |
| ☐ armed, waits for the t = 22 checkpoint (~06:47) | 1f | **fill-radius twin, restarted from t = 22** — `merge_headon_flip_d8_v1c_fillnarrow_t100_r02200` (template `templates_scan/params_v1c_fillnarrow_d8_t100.txt`): the V1c file with the fill radii 1.2/1.8 → 1.0/1.5 at the same t = 26.5, no checkpoints, otherwise byte-for-byte, from the same checkpoint. The head-on's own seam test, the check that certified the orbital freeze (M9b twins: 5-digit agreement, late-engagement 0.02 %) | 1 × ~7 h | Is the frozen ball hiding the crash only, or also changing the waves outside? | r·ψ4 at R = 10/14/18 agrees with V1c to within the resolution error → the head-on waveform is certified; the R = 10 waveform moves → the fill is in the physics and must go deeper |
| ✗ dropped 2026-09-09 (user's word) | — | gauge arms from the same checkpoint (`params_v1g_{eta4,lapse4,ko1}_d8_t100.txt`, never launched): σ 1.0 backfired on record (`sg10`, died earlier), lapse_coeff was tested (`lc1`, wall 8.4 units earlier, physics intact), η never tested; the record says gauge moves the wall by units and never removes it | — | — | — |
| ☐ | 2 | **±ε arms at level 3**: seed ±1e-3, ±1e-2, ±1e-1 on the areal-radius function (`wormhole_seed_amplitude_A`), six runs from `single_hold_t100`'s template, frozen `bin/main3d_boost_2026-09-08.ex`, frames χ K lapse φ Π, plotfiles kept-last for the θ± scan, no checkpoints | 6 × ~5 h | The branch by choice instead of by grid noise: τ and the horizon time per branch; the onset against ln ε; whether −ε reproduces level 4's inflation *with* the inner-sheet deformation (physics) or without it (the origin failing); the ε at which noise stops mattering | +ε collapse with MOTS and mass loss; −ε inflation with an anti-trapped shell; onset(ε) linear in ln ε, slope ≈ −5.9 |
| ☐ | 3 | GRTresna outer boundary condition on ψ_reg → 1 − b/2r; re-solve `params_drainhole_test.txt`; push the solution through `ExternalGridInitialData` | code, no GPU | Constraint-solved data for V1/V2 (the +8–11 % superposition error, or the seed, is otherwise in every claim) | solved ψ within 1 % of the exact drainhole at N = 64, throat at R = 2.0; the bridged run holds the throat to t = 20 |
| ☐ | 4 | V1 refined + ε family (both signs, d = 8) | 3–4 × ~1 day | The natural merger and its ensemble | outcome unchanged under one level, the gauge swap and the sign of ε |
| ☐ | 5 | V2 production with extraction (L5, plunge, both channels) | 1 × ~1 day | Waveform, E_rad/M, the ringdown against Kerr | mass lost = energy radiated |

Side tracks that block nothing: the foam-born-pair reading (`article/research.tex`
introduction), the handle version, the tidal and scattering estimates.

## 4. Results ledger — one line each, runs, where it is written

- **A lone throat is unstable** at the GGS rate; the binary wall is its clock. `single_hold_t100`. README (exact data section), INSTABILITY.md.
- **The origin death is resolution, the throat is innocent.** `single_hold_ml2_t100`, `single_hold_ml2_chireg_t100`. README 4b; archive "Ladder result".
- **Resolution picks the branch, not the rate.** `single_hold_chireg_t100` (collapse), `single_hold_ml4_t100` + `_lowfloor` (inflation). BRANCHES.md; README 4b. Rule: no fate is quoted for any arm without a declared seed.
- **The χ floor is not load-bearing** at levels 2, 3, 4. The three twins. BRANCHES.md §1.
- **The collapse branch ends in a black hole** that loses mass to the phantom field (MOTS R 3.23 → 2.37, M_MS 1.62 → 1.23 over 40 units), lapse at the origin 0.016, no bounce by t = 100; constraints grow 60× from t ≈ 75. BRANCHES.md §5–6.
- **Seen before in 3D** for the massless Ellis–Bronnikov throat (Shirokov 2026, arXiv:2604.00071, 5 levels): noise → inflation; support cut + quadrupole → collapse, horizon, "phantom bounce" at t ≈ 4 M, horizon destroyed by t ≈ 18.5 M. The massive drainhole shows no bounce in 40 units; whether one comes later is open.
- **dt_multiplier 0.02 is necessary.** `single_hold_dt01_t070`, `single_hold_dt005_t070`. archive "Time-step bracket".
- **The binary dies as the lone throat dies** (floored core, vertical gradient beside it, one-step overflow). `autopsy_nodamp_r05000`. archive "Autopsy verdict"; README.
- **The companion holds the throat open** at t = 30 (origin χ 0.2–0.7 dex above the isolated throat's, strongest on the fly-bys) — a hypothesis with a gauge caveat, for the V1 scout's areal radius to test. CLOCK_COMPARISON.md. **Tested 2026-09-09 at the mouths: the opposite.** Relative to two throats placed at the same separation, the scout's mouths are squeezed −4 % by t = 13; the origin-χ reading and the mouth-radius reading disagree in sign, and the mouth radius is the geometric one. PLACEMENT_CURVE.md.
- **The head-on pair forms a black hole, then the code dies inside it** (2026-09-09). Contact t ≈ 20, common MOTS from t = 22 (fine scan; grows to t = 24, shrinks to R 4.72 by t = 26, M_MS ≈ 3), NaN at t = 26.91 with the old anatomy (floored midpoint, K runaway, one-step overflow 0.9 away). First binary in which the black hole is seen forming *before* the wall. `merge_headon_flip_d8_v1_t100`. README (Phase-3 section), `horizon_offline_scan.dat`.
- **The neighbour is on the ruler; the interaction squeezes.** Placed throats read +1.8 % (d = 48) … +20.5 % (d = 6) above exact, ∝ d^−1.16 — every d = 12 pair of the earlier campaign started 9 % "wide" by placement alone. Against the curve the scout's mouths shrink −0.6 % (t = 7) → −4.0 % (t = 13), growing with the closing speed; no expansion phase; the lone throat is exact until t = 35, so this is the interaction. Eighteen `place_d*_step1` + the scout. PLACEMENT_CURVE.md; README (placement section).
- **The p = 0.45 "fly-by" is a bound pair that collapses without merging, then blows its phantom field out** (re-read 2026-09-09 from the packed streams and the slice cache of `merge_orbit_flip_d12_p045_t200`). Closest approach 3.95 at t = 40; a common trapped surface (θ < 0, live level-1 scan) about the midpoint from **t = 43.3 at R = 4.0** with both throats inside it 4 apart, deepest −0.21 at t = 62, weakening to −0.12 by t = 91; per-mouth trapped spheres R 5.2 → 6.4 over t = 59–77. The collapsed-lapse region (α < 0.01) grows from 0.6 to 147 area units (equivalent radius 6.8) by t = 90, doubling every ~7 units; min lapse 0.2 → 5e-6, max K 0.16 → 3.3. From t ≈ 50 an outgoing front — χ > 1 (up to 12.6 by t = 90, ψ ≈ 0.53), a lapse bright arc, a thin K ≈ 1 shell and the ±0.8 scalar lobes — moves out at **0.37 per unit** (r 7.5 → 21.3), the phantom field leaving the throats, wound into a spiral by the orbit: the "phantom bounce" of Shirokov 2026 after horizon formation, here in the bound pair. The Hamiltonian norm e-folds every 7–9 units from t = 45 (500× by t = 90, order 1) — it rides on the outflow, so nothing after t ≈ 65 (25× baseline) is trustworthy. Not "both throats expanding": the geometry collapses, the field expands; the throat radius itself was not measured in this run (no areal-radius stream then, plotfiles gone). Same sequence as the lone throat's collapse branch (MOTS, then unexplained constraint growth from t ≈ 75), faster. Streams: `binary_throat_diagnostics.dat`, `collapse_diagnostics.dat`, `constraint_norms.dat`; slices `frames/_slice_cache` (run tree).
- Earlier, unchanged since 2026-09-04: like-oriented throats repel and one must be flipped; the p = 0.12 pair merges; the merged object is a black hole that dissolves; the wall is gauge + resolution, not physics; the Helfer correction is better data and a worse evolution; damping shapes nothing; the vacuum BBH control recovers the known answer. README, one section each.

## 5. Open questions

1. The late constraint growth on both branches (t ≳ 75): where does it live — inside the trapped region or outside? The plotfiles carry no Hamiltonian; the next launch adds it to the plot variables or the θ± scan gains a constraint column.
2. The inflation branch's inner-sheet deformation (R(r) non-monotonic inside the throat by t = 100): physics of the branch or the origin? The −ε arm at level 3 answers it.
3. Does the collapse-branch MOTS settle, and at what fraction of m? Needs a longer run or the stability eigenvalue.
4. GRTresna: the ψ_reg boundary condition; the bridge into the merger example.
5. Can the merger be modelled with the throats meeting before branching? Yes in principle — at level 3 the lone throat is exact to 0.1 % until t = 35 and to 1 % until t = 44, so a d = 8 pair (contact ≈ 17) collides as wormholes; and the collision is itself a large compressive perturbation, so the merged core's branch should be set by the collision, not by noise. That is Phase 3's premise and it is not yet demonstrated: item 1 measures how small a seed already decides the branch, item 3 tests it on the pair. First data point (2026-09-09, before contact): the interaction squeezes each throat, −4 % by t = 13 relative to placement, in the collapse direction and with no expansion phase — the compressive-perturbation reading of the collision is so far borne out at the mouths. Answered 02:50: it collapses — a common trapped surface at t = 22. Whether the interior can be carried past its own collapse is question 6.

6. The wall inside the horizon (2026-09-09): five units after the common MOTS forms, χ at the midpoint is on the floor and K runs away there — a physical singularity reaching the slice (the phantom collapse is not vacuum; 1+log need not avoid it) or the χ → 0 gauge pathology of a puncture without puncture treatment? Either way the horizon makes the interior irrelevant to the outside, which is the case for the interior freeze (queue 1c). The distinguishing test: does the horizon's areal radius shrink *before* χ reaches the floor at the midpoint (physics) or only after (numerics)? At t = 24 → 25 both happen within the same unit; a plotfile every 0.25 units through t = 22–27 would separate them.

## 6. Rules

Physics: nothing modifies the evolution equations at run time (freeze, matter
damping, hard clamp all off; χ regularised at the point of use only); the
natural run first; every result on two independent streams; ladder increments
need arm pairs; growth rates by the plateau of d ln|δ|/dt, never a fit near the
zero crossing; constraint ratios by rolling medians; displacements, not fitted
accelerations; no fate quoted without a declared seed; no scan trusted across
an extremum of R(r).

Operations: launch only through the launcher; frames for several fields and the
slice cache every time, the slice plane chosen for the motion; checkpoints only
for production runs; plotfiles kept-last only for a named offline scan, then
pruned on the user's word and logged; never edit a running campaign script;
stop a campaign by its orchestrator first; other people's runs share the cards.

## 7. Close-out, every run

```bash
bash research/merger/closeout.sh <run> [<run> ...]   # live check, scratch report, NaN check,
                                                     # registry check, movies, repack, identity grep
```

Then by hand: the README Claim/Runs line of the section the run answers; the
§2 row and §3 queue here; the prune on the user's word, logged in
`runs/wormhole_merger/MANIFEST_CLEANUP_*.md`; commit without a Co-Authored-By
trailer; push to myfork. A run is registered by one tab-separated line in
`results/merger/runs_registry.tsv` — written by the launcher when `WHM_WHAT` is
set at launch — never by a code edit.
