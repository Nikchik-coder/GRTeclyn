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
- [ ] **Phase 3 — V1, head-on from rest, d = 8** (user's go-ahead 2026-09-09: launch the scout now) → archive "Phase 3"
  - [ ] scout at level 3, seed declared (the superposition defect, measured), several frame fields, θ± scan on
  - [ ] gate: the throats touch (t ≈ 17) as wormholes, both within 0.1 % of exact at contact
  - [ ] the merged core: collapse with the surface count 2 → 1 (unassisted merger), or inflation/dissolution, or a naked pinch — whichever, believed and measured
  - [ ] no NaN through +30 units past horizon formation; constraints bounded outside the horizon
  - [ ] refined member (one level finer) and the ±ε family around it: outcome unchanged
- [ ] **Phase 2b — ±ε arms at level 3** (six runs; after or beside the scout)
  - [ ] +ε: collapse, MOTS, mass loss as at level 3
  - [ ] −ε: inflation, anti-trapped shell, no MOTS; with or without the inner-sheet deformation
  - [ ] onset(ε) linear in ln ε with slope ≈ −5.9
- [ ] **Phase 4 — V2, production with extraction** → archive "Phase 4"
  - [ ] waveform in both channels (Weyl and scalar)
  - [ ] balance: mass lost = energy radiated
  - [ ] ringdown against Kerr

Cards: all four free. Nothing in flight. Scratch: 758 GB free (everything pruned
2026-09-09 on the user's word). Frames: every launch now renders χ, K, lapse, φ, Π
by default (launcher, 2026-09-09) — the ladder runs rendered χ only, and no other
movie of the collapse or the inflation can be made.

## 3. Next — the queue

| ✓ | # | what | cards × wall | decides | success reads |
|---|---|---|---|---|---|
| ☐ | 1 | **V1 scout: head-on from rest, d = 8, level 3** — φ-sign flipped, K = 0, Π = 0, no boost; production settings of `single_hold_t100` (L 64, N 128, max_level 3, σ 0.1, dt 0.02) with `chi_rhs_floor` on; frames χ K lapse φ Π in the plane of the motion; θ± scan on; no checkpoints; NaN autopsy armed | 1 × ~10 h | Do the throats meet as wormholes before their own decay, and does the merged core collapse (2 → 1 surfaces) — from NaN to a black hole — or something else? | contact by t ≈ 17 with both throats within 0.1 % of exact; surface count 2 → 1 by the θ± scan; no NaN through +30 past the horizon |
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
- **The companion holds the throat open** at t = 30 (origin χ 0.2–0.7 dex above the isolated throat's, strongest on the fly-bys) — a hypothesis with a gauge caveat, for the V1 scout's areal radius to test. CLOCK_COMPARISON.md.
- Earlier, unchanged since 2026-09-04: like-oriented throats repel and one must be flipped; the p = 0.12 pair merges; the merged object is a black hole that dissolves; the wall is gauge + resolution, not physics; the Helfer correction is better data and a worse evolution; damping shapes nothing; the vacuum BBH control recovers the known answer. README, one section each.

## 5. Open questions

1. The late constraint growth on both branches (t ≳ 75): where does it live — inside the trapped region or outside? The plotfiles carry no Hamiltonian; the next launch adds it to the plot variables or the θ± scan gains a constraint column.
2. The inflation branch's inner-sheet deformation (R(r) non-monotonic inside the throat by t = 100): physics of the branch or the origin? The −ε arm at level 3 answers it.
3. Does the collapse-branch MOTS settle, and at what fraction of m? Needs a longer run or the stability eigenvalue.
4. GRTresna: the ψ_reg boundary condition; the bridge into the merger example.
5. Can the merger be modelled with the throats meeting before branching? Yes in principle — at level 3 the lone throat is exact to 0.1 % until t = 35 and to 1 % until t = 44, so a d = 8 pair (contact ≈ 17) collides as wormholes; and the collision is itself a large compressive perturbation, so the merged core's branch should be set by the collision, not by noise. That is Phase 3's premise and it is not yet demonstrated: item 1 measures how small a seed already decides the branch, item 3 tests it on the pair.

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
