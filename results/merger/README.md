# Drainhole merger — packed campaign results

Two exotic-matter (phantom scalar) drainhole throats, given a gentle orbital push,
spiralling together in full 3+1 numerical relativity. This directory is the light
extract of that campaign: every number the analysis rests on, the movies, a thinned set
of stills, and enough provenance to rebuild any run. It is what survives if the machine
that produced it does not.

- The reasoning and the full argument: [`research/merger/Plan.md`](../../research/merger/Plan.md)
- The article in preparation: [`research/merger/article/research.tex`](../../research/merger/article/research.tex)
- The working run tree, **not in git** (~14 GB, on the machine that produced it):
  `runs/wormhole_merger/`, filed by physics since 2026-09-10 into the same
  `NN_group/` folders as `campaign/` here; its README is the run inventory
- Rebuild this directory: `bash research/merger/pack_results.sh`

## The result, in seven lines

1. Two identical throats **repel**. Reversing one throat's scalar field is the only
   gravity-driven way to make them fall together — no aimed momenta, no support cuts.
2. Flipped and pushed, they **merge**: collapse of the whirling double core at t ≈ 45,
   a genuine common trapped surface at t ≈ 51, and a gravitational-wave burst that
   survives every check made on it. (The "merged at t ≈ 30" this file used to claim
   was a false verdict of the old in-code horizon scan, which assumed a conformally
   flat metric — fixed in code 2026-09-01; see `research/merger/Plan.md`.)
3. Then the merged object **dies** — a NaN wherever un-damped phantom matter sits on
   collapsed geometry. Four arms, four different treatments, four deaths between
   t = 51.7 and t = 55.0; a fifth (the floor-ladder reference rung, refined to
   level 5) pushed the record to t = 55.53.
4. The arm that lived longest measured the horizon **shrinking** — but how fast depends
   on how deep the scan looks. The level-3 curve read 1.07 at t = 51.5 down to 0.59 at
   t = 55.0 and accelerating; the level-5 scan of the record arm holds a trapped shell
   at 0.94 → 0.90 over t = 54.5–55.5, shrinking slowly, and the same files scanned at
   level 3 show nothing (the Theta ≈ −0.03 margin washes out) — so shrinkage is
   established, its *rate* is a scan-depth systematic to be re-measured (GPU_PLAN #12).
   The mechanism's ingredients are now measured (#13, 2026-09-04): negative-energy
   matter is concentrated exactly at the horizon ring (three orders above ambient),
   the net energy flux out of the enclosed ball has the sign that shrinks the mass,
   and the interior's areal radius is collapsing. The full energy/mass balance (#12)
   and the floor gate are still open; until both close, the mechanism is stated as
   strongly supported inference, the shrinkage as measurement.
4b. **And a single throat, alone, does the same thing.** `single_hold_t100` (2026-09-05):
   one throat, exact static data, empty box, t = 100 with zero NaN. It holds its exact
   radius for 26 units and then contracts exponentially, tau = 5.86, reaching -35 % by
   t = 65 — while the constraint norms *fall*. That is the Ellis-Bronnikov growing mode
   at the rate Gonzalez, Guzman & Sarbach predict for this parametrisation, to ~15 %.
   The binary wall is 44-56; a throat with nothing done to it dies on the same clock.
   **Everything above about the merged core has to be read against this.** See
   [`campaign/01_single_throat/INSTABILITY.md`](campaign/01_single_throat/INSTABILITY.md) for the level-3 analysis and
   [`campaign/01_single_throat/BRANCHES.md`](campaign/01_single_throat/BRANCHES.md) for the ladder (2026-09-08): one level
   finer (`single_hold_ml4_t100`) the same mode grows at the same rate to 9 % — with the
   opposite sign. Level 3 collapses to a black hole (a marginally trapped surface at
   R = 3.23 by t = 61, shrinking to 2.37 by t = 100 with the Misner-Sharp mass inside it
   falling 1.62 → 1.23, the lapse at the origin down to 0.016 and no bounce of the areal
   radius by t = 100 — a black hole slowly eating the phantom field; the constraint norms
   grow 60× from t ≈ 75, unexplained and not the floor's); level 4 inflates (throat radius
   3.89 → 10 by t = 100, an expanding anti-trapped shell around it, no horizon at any time).
   Both fates of Shinkai & Hayward (2002) are in the code, and which one a run takes is set
   by the truncation seed, not by the physics. **No fate may be quoted for any arm until the
   sign of its seed is controlled.**
   **The declared-seed scan that controls it (2026-09-10, `campaign/01_single_throat/seed/`).**
   The hidden seed is replaced by a stated one: at t = 0 the conformal factor is multiplied by
   a Gaussian shell on the throat (centre r = 1.618, half-width 0.5) of amplitude ε, with the
   velocity fields left at zero so the momentum constraint stays exact — measured 0.000e+00 at
   t = 0 in every arm — and only the Hamiltonian constraint violated, at order ε.
   **ε = ±0.1 is too large to be a perturbation:** both signs collapse and both NaN
   (`single_eps_m1e1_t100` t = 15.17, `single_eps_p1e1_t100` t = 14.07), starting from a
   Hamiltonian violation 3–5× the 1 % arms' and growing it to 0.40 and 55.6. The 1 % arms hold
   theirs flat (2.21e-3 → 2.38e-3 over twenty units), so **1 % or below is the usable range**.
   **The branch point belongs to the throat, not to the kick.** Each arm first moves the way it
   was pushed, comes back, crosses its twin, and only then runs apart — with the fate OPPOSITE to
   the push, so the first separation is the transient and the second is the branch. Two amplitudes
   a factor ten apart cross at the same time: **t = 13.01 for ε = ±0.01 and t = 13.04 for ε = ±0.001**,
   a shift of 0.03 for a tenfold change in the seed. At t = 63 the ±0.01 pair stands at R = 7.8
   (pushed in, inflating) against 1.9 (pushed out, collapsing); the ±0.001 pair is at 4.7 against
   2.85 by t = 39. Figure: `figures/01_single_throat/single_throat_seed_branches.png`.
   **Two caveats, both hard.** (i) The collapse arms outrun the diagnostic: the ray scan's areal
   minimum reaches its inner cutoff at r = 0.533 (ε = +0.01, from t = 29), and past that R_min is
   the areal radius AT the cutoff, not the throat — nothing after that point may be quoted as a
   throat radius. (ii) `single_eps_p1e3_t100` **died**: NaN at t = 40.07, mid-collapse at R = 2.85,
   so the 0.1 % collapse branch has no fate. It is not a faster collapse than ε = +0.01, which
   passed that same radius at t ≈ 27 and lived — the difference is the gauge. The big kick drives
   |K| to 0.5 and the lapse collapses to 0.0097, freezing the region; the small kick never gets
   |K| above 0.06, the lapse sits at 0.19, and χ drains to its 1e-8 floor at t ≈ 38 with no gauge
   response, after which |K| reaches 5.9 and the constraint norm goes 1.3e-3 → 28 in one step.
   **A collapse can be too gentle to trigger the singularity avoidance that protects a violent one.**
   No growth rate is quoted for any arm: the sliding-window rate is still falling everywhere
   (0.04 and 0.20 for ±0.01, 0.26 for −0.001) against 0.1702 for level 3's own truncation seed.
   The same split was seen in 3D before, for the massless
   Ellis-Bronnikov throat (Shirokov 2026, arXiv:2604.00071): noise alone drove that run to
   the inflation branch at five levels of refinement, and halving the phantom support with a
   quadrupolar seed forced the collapse branch — horizon, then a "phantom bounce" of the
   swallowed field at t ≈ 4 M. Here the massive drainhole shows no bounce in 40 units after
   its horizon forms; whether one comes later is open. Movies: χ in the x–y plane only
   (`campaign/01_single_throat/<run>/movies/movie_chi_z.mp4`), one frame per time unit — these launches
   rendered no other field, and the plotfiles are gone, so no lapse, K or scalar movie of
   either branch exists (launch policy fixed 2026-09-09: several fields by default).
5. Give the pair enough angular momentum that it never merges and the evolution is
   **healthy with no NaN at all**. The fly-by runs say so: `merge_orbit_flip_d12_p045`
   (clean to t = 60), its long rerun `..._p045_t200` (held to t ≈ 91), and
   `..._p035_t200` (closest approach 2.75, run to t = 73.9). ~~The instability belongs
   to the merged core, not to the code.~~ **Withdrawn 2026-09-05 by 4b:** the instability
   belongs to a *single throat*, so it is neither the merged core's nor the code's. It is
   the solution's. The fly-by arms are not counter-evidence — they were stopped or died
   at t = 60-91, and an isolated throat is already 35 % gone by t = 65. ("Healthy with no
   NaN at all" also overstates them; see B2 in `research/merger/archive/GPU_PLAN_2026-09-03.md`.)
   **Re-read 2026-09-09 (p = 0.45 t200, packed streams + slice cache):** a bound pair, not a
   fly-by — closest approach 3.95 at t = 40, a common trapped surface about the midpoint from
   t = 43.3 (R = 4.0, both throats inside it 4 apart; live level-1 scan), the collapsed-lapse
   region doubling every ~7 units to an equivalent radius 6.8 by t = 90, and from t ≈ 50 the
   phantom field blown outward at 0.37 per unit (χ > 1 front, lapse arc, K shell, the ±0.8
   scalar lobes, wound into a spiral by the orbit — the "phantom bounce" after horizon
   formation). The Hamiltonian norm e-folds every 7–9 units from t = 45 on that outflow;
   nothing after t ≈ 65 is trustworthy. The geometry collapses and the field expands; the
   throat radius itself was never measured in this run.
6. And it is not a resolution artefact. A 25 % finer grid reproduces the inspiral to
   within 1.8 % and the waveform to within 4 % — and then dies of the same NaN
   1.55 units later. Refining postpones the failure by 3 %; reaching t = 60 that way
   would cost roughly 90× the compute. (Confirmed again on p = 0.15: a max_level 5
   restart bought +0.88 over the level-3 wall and still died mid-fusion.)
7. The result survived its credibility batch (2026-09-03/04): turn the core damping
   off and nothing claimed changes; change the slicing and the *physics* holds while
   the crash time moves 8.4 units (the wall is gauge, not an event); rerun a scout
   and it dies on the identical step (deterministic); and the same pipeline, fed
   vacuum black holes, recovers the textbook Kerr ringdown to a few percent.

## The paper's claims, and the runs behind each

Written claim-first so a paper subsection can be lifted straight from here:
what the text asserts, the runs that establish it, and where the numbers sit.
Runs overlap between claims — that is the point of the map. *(pack)* = has a
directory under `campaign/<group>/` (the groups are the paper's sections:
`01_single_throat`, `03_two_throats`, `04_binary_headon`, `05_binary_spiral`,
`06_binary_flyby`, `07_bbh_control`; the pack mirrors the run tree); *(run tree)* = lives only in the gitignored
`runs/wormhole_merger/` tree on the production machine. As of 2026-09-09
every pack entry is a finished run (the from-t = 0 low-floor twin
`merge_twin_p012_nodamp_cf10_t060` died at t = 44.94 and is packed whole).
The Phase-3 head-on scout `merge_headon_flip_d8_v1_t100` (2026-09-09
01:09–03:04) died at t = 26.91 and is packed whole, with its fine-grid horizon
history in `horizon_offline_scan.dat`. The eighteen one-step placement probes
`place_d*_step1` (2026-09-09 02:06–02:48) are finished and packed; their result
is `campaign/04_binary_headon/PLACEMENT_CURVE.md`, regenerated at every pack.

### The initial data is exact, and the throat is unstable anyway
*(rewritten 2026-09-05; this section used to be titled "the initial data is
validated: a single throat holds 40 time units". The 40-unit number was right
and the framing was wrong — see below.)*
- **Claim.** The grid represents each wormhole by folding its entire far
  universe into the ball inside the throat sphere (the other side's infinity
  lands on the throat's centre point) — the route the background survey said
  to avoid, because the published single-throat attempt (arXiv:2604.00071)
  died of it at t ~ 1.5. We used it anyway and measured it instead of
  assuming: refining the origin made every error *smaller*, a small lapse
  collar over the centre bought ~3.5x on origin survival, the mass was put in
  the lapse (drainhole) rather than the spatial metric (which crushes the
  throat), and the resulting data is an exact fixed point of the evolved
  system — R_areal_min holds its closed-form value to **8 significant figures
  at t = 1 and 5 at t = 12**, with the constraints exact at t = 0.
- **And then it goes.** Run long enough and the same throat, alone in an empty
  box, closes itself: turnover at t = 26, then exponential contraction at
  **tau = 5.86 coordinate units** (0.1706 +/- 0.0031 per unit, flat over 2
  e-foldings), reaching -35 % by t = 65. In proper time at the throat that is
  T = 0.867 against the 0.68-0.76 predicted for this parametrisation by
  Gonzalez, Guzman & Sarbach (arXiv:0806.0608) — the predicted mode at the
  predicted rate to about 15 %. **The initial data is not the problem; the
  solution it represents is unstable.**
- **The constraints never see it.** L2_Ham *falls* from 2.509e-03 to 1.166e-03
  while the throat loses a third of its radius. A growing mode of the
  constrained system satisfies the constraints. Nothing in this campaign may
  be certified healthy on a constraint norm alone.
- **Runs.** `campaign/01_single_throat/hold/single_hold_t100/` *(pack)* — one throat, exact static
  data, production settings, t = 0 to 100 with zero NaN. Its one-knob twins
  (2026-09-08) *(pack)*: `single_hold_ml2_t100` — level 2, h11 NaN at
  t = 24.17 with the throat radius still exact to 0.12 %, so the origin death
  is resolution and the throat is innocent (confirmed 2026-09-08 by
  `single_hold_ml2_chireg_t100`, the same arm with the two 1/χ terms of the
  evolution floored at 1e-8 and the state clamp lowered to 1e-20: K NaN at
  t = 24.13, origin χ through 1e-8 at t = 8.95 in both, throat radius within
  2e-4 of the reference to the end — neither the clamp nor the 1/χ terms are
  the killer); `single_hold_chireg_t100` — the level-3 reference with the same
  χ regularisation: identical to 10 digits until the origin reaches the floor at
  t = 61.3, to 4 digits at t = 100 (constraints, origin, throat radius), so the
  floor is not load-bearing at level 3 either; `single_hold_ml4_t100` and
  `single_hold_ml4_lowfloor_t100` — the level-4 pair (floors 1e-8 and 5e-10),
  byte-identical on every stream because the origin χ never fell (2.4e-8 at t = 0,
  rising to 3.9e-4), clean to t = 100 and on the **inflation branch**
  (`campaign/01_single_throat/BRANCHES.md`); `single_hold_dt01_t070` — Courant
  0.1, origin blow-up, NaN at t = 16.07; `single_hold_dt005_t070` — Courant
  0.05, no NaN to t = 70 but off the 0.02 solution from t ≈ 33 (constraints
  35× by t = 40, lapse floored at 61.1), not usable. Three levels and the
  0.02 step are both necessary. The Stage-1 ladder is
  packed beside it under `campaign/01_single_throat/` *(pack)*: the lapse/collar/
  dissipation grid, the uniform-grid origin pair, and the long holds. The
  derived systematics, regenerated from those streams by
  `analysis/single_throat_instability.py`, are in
  [`campaign/01_single_throat/INSTABILITY.md`](campaign/01_single_throat/INSTABILITY.md).
- **Caveat — read INSTABILITY.md and BRANCHES.md before quoting a rate.** (a) The
  growth rate is measured at **two resolutions** (2026-09-08): τ = 5.86 at level 3
  and τ ≈ 5.3 at level 4, 9 % apart and moving toward the Gonzalez–Guzman–Sarbach
  band; the level-2 arms die at t = 24 before their turnover and give no rate.
  The onset moves later by +5.6 to +8.7 units per halving of dx (0.1 %, 1 % and
  10 % thresholds), against +16 for a fourth-order truncation seed — the seed is
  low-order, and it changes sign between the two levels.
  (b) Nothing past **t = 65** may be quoted from `areal_radius.dat` at level 3: the
  areal-minimum scan's minimum reaches the inner edge of its own search window
  there, and the apparent R ~ 1.92 plateau over t = 66-99 is that boundary
  reading. The shell scans in BRANCHES.md read the collapsed state directly instead.
  (c) χ at the compactified origin reaches its floor at **t = 61.3** and sits there
  for 1.4 units. The χ-regularised twin with the floor at 1e-20 reproduces the
  reference to 4 digits at t = 100 (≤ 0.25 % apart in the constraint norms during
  the event, 7 % in max|K| at its spike), so the clamp is not load-bearing and the
  late data may be read. The late constraint growth is real though — L2_Ham 60× by
  t = 100 at level 3, 6× at level 4 where nothing was ever clamped — and is not
  explained by the floor. (d) The older
  "e-fold ~ 4.4, about one throat-light-crossing" estimate in this file was a
  literature figure, not a measurement, and is superseded by the 5.86 above.

### Like-oriented throats repel; flipping one is what makes a binary
- **Claim (measured).** Two identical throats push apart, and the push scales
  with throat *width*, not mass. Reversing one throat's scalar field turns the
  push into a pull — the only gravity-driven route to a merger. At a = 2 the
  magnitude is pinned by the orientation flip, where the coordinate under-read
  cancels between two arms of the same width: pull/push 1.511 ± 0.033 measured
  against 1.500 predicted.
- **The magnitude law is NOT yet confirmed across widths** (#8, 2026-09-04).
  Four rest-release arms at a = 1 / 1.5 / 2 / 3, byte-identical but for the
  radius, give displacements by t = 11 of 0.147 / 0.283 / 0.416 / 0.615 —
  ratios 1.00 / 1.92 / 2.82 / 4.18 against the predicted a² = 1 / 2.25 / 4 / 9.
  The push is real and grows with width at every rung, but the measured
  exponent is ≈ 1.36 and *falling*, and at a = 3 the prediction overshoots by
  2.2×. Under-resolution is excluded — both new throats sit on the finest
  level, 48 and 96 cells across, so the widest arm is the *best* resolved.
  What remains is the coordinate under-read (which does not cancel between
  different widths) or genuine finite-size corrections to a point-charge
  formula at a/d = 0.25; like-charge arms alone cannot separate them. The
  decisive test is two flip arms at a = 1.5 and a = 3, where the under-read
  cancels within each width and the predictions are far apart (1.889 and
  1.222 against a = 2's confirmed 1.500). **The separation ladder below now
  favours the finite-size branch**: it finds an effective separation exceeding
  the coordinate one by about a throat radius, which is exactly the correction
  a point-charge formula is missing, and it does so in a geometry where the
  width is held fixed.
- **The DISTANCE law is confirmed, and it is inverse-square in an effective
  separation** (#8b, 2026-09-04). The width ladder above could never settle
  this, because `a` is a coordinate label whose physical meaning moves as you
  turn it (tripling `a` grows the measured throat radius only 1.6×). Holding
  the throat fixed and varying only the gap does settle it. Four rest-release
  pairs at d = 12 / 14 / 16 / 18, byte-identical but for the centres, give
  displacements at a common t = 11.5 of 0.4696 / 0.3699 / 0.2980 / 0.2438.
  - Pure 1/d² is **excluded**: F·d² rises monotonically 67.6 → 79.0, a 15.4%
    spread, far outside the scatter. The push falls off *more slowly* than
    inverse-square.
  - F ∝ 1/(d + δ)² with **δ ≈ 3.5** fits; all six rung pairs give δ =
    3.77 / 3.67 / 3.47 / 3.54 / 3.27 / 2.95.
  - This was a **blind prediction**. δ = 3.4 was fitted on d = 12/14/16 alone,
    before d = 18 reached t = 11.5. It predicts 0.243 there; pure 1/d² predicts
    0.209; the measurement is **0.2438** — 0.3% from the offset model, 17% from
    inverse-square.
  - δ ≈ 3.5 is comparable to the independently measured physical throat radius
    at a = 2, which is **4.29**. The reading is that the coordinate centre
    separation is not the physical separation.
- **Say it as.** The push exists, is outward at every width and every
  separation, and grows with throat width — quote the four displacements, not
  a² (unverified). For the distance dependence, say the force is inverse-square
  in an *effective* separation that exceeds the coordinate separation by about
  one throat radius. Do **not** write "the repulsion violates the inverse-square
  law": the deviation is in the distance label, not in the law.
- **Runs.** The Stage-2.5/2.6 control pairs `orbit_d12_p012`, `ctrl_rest_d12`,
  `ctrl_rest_a1`, `ctrl_flip_d12` under `campaign/03_two_throats/` *(pack since
  2026-09-10, their NOTES.md beside them)*;
  the two a-points `ctrl_rest_a15` and `ctrl_rest_a3` *(pack)* and the width
  measurement in `campaign/03_two_throats/scalar_charge_apoints_2026-09-04.txt`; the three separation
  rungs `ctrl_rest_d14` / `d16` / `d18` *(pack)* and the distance measurement
  in `campaign/03_two_throats/separation_ladder_2026-09-04.txt`;
  every `merge_*flip*` run below is the attracting configuration in action.

### The p = 0.12 pair merges
- **Claim.** Inspiral to t ≈ 33, whirling double core, collapse at t ≈ 45, a
  genuine common trapped surface at t ≈ 51, and a gravitational-wave burst.
- **Runs.** `merge_orbit_flip_d12_r03000` *(pack)* — the discovery arm (its
  `__part1` streams are t = 0 → 30.5); `merge_headon_flip_d12` *(pack)* — the
  no-orbit version, merges sooner; `merge_twin_p012_plain_t100` *(pack)* — an
  independent from-scratch rerun 2026-09-02 that retraced the record (sep 2.06
  at t = 32.00 vs the original's 2.0) and closed to sep 0.81 by t = 44: the
  reproducibility twin.
- **Numbers.** `campaign/05_binary_spiral/<run>/binary_throat_diagnostics.dat` (separation),
  `collapse_diagnostics.dat` (collapse), `campaign/05_binary_spiral/horizon/` (the trapped surface).

### The merged object is a black hole that dissolves
- **Claim (measured).** The common trapped surface shrinks — 1.07 at t = 51.5
  down to 0.59 at t = 55, accelerating — on two independent damping schemes
  giving one dissolution curve. The run dies at t = 55 with the surface still
  shrinking: this is the **onset** of dissolution, not its endpoint, and the
  paper must not claim the completed disappearance.
- **Mechanism (ingredients measured, balance still open).** Phantom matter
  carrying negative energy across the horizon fits every exclusion test
  (deleting the matter by damping pushes the energy budget the other way),
  and the GPU_PLAN #13 scan (2026-09-04, `blob_nature_scan.py` on the
  longest-lived arm's death window) now measures the ingredients directly:
  ρ < 0 concentrated at the horizon ring r ≈ 0.9–1.2 (pointwise to −0.9,
  three orders above ambient), net Eulerian energy flux out of the enclosed
  ball (+2.6 → +3.3 — the sign that shrinks the enclosed mass), and the
  interior bag's areal radius collapsing 22 % in the last time unit — all on
  NaN-free slices whose constraints hold to 3–7 % at proper scan depth.
  What is NOT yet done is the quantitative energy/mass balance (#12): until
  the flux integral is shown to account for the horizon's mass loss, the
  paper states the shrinkage and calls the mechanism strongly supported
  inference; it does not assert cause.
- **Runs.** `merge_orbit_flip_d12_r04000` and `..._rw_r05000` *(pack)* — two
  independent damping schemes, one dissolution curve;
  `merge_twin_p012_cf08_t060_r05000` *(pack)* — the record arm behind the
  #13 numbers and the level-5 shell track 0.94 → 0.90; `..._sg10_r05000`
  *(pack)* corroborates the death; the measurements themselves are the
  offline scans in `campaign/05_binary_spiral/horizon/`.
- **Say it as.** The merger produces a short-lived black hole that dissolves
  by swallowing its own exotic matter — written as **contingent** (GPU_PLAN
  §8 decision 7). Two gates before the hedge comes off: (1) the 2026-09-04
  floor ladder showed the collapsed-core state is floor-regularized (a
  relaxed χ-floor on the t = 50 state is instantly fatal), so horizon and
  dissolution numbers stand only if the from-t = 0 low-floor twin reproduces
  them; (2) "extinguished by negative-energy accretion" and "evaporates
  classically" are allowed only after #13 measures the sign. Nothing here is
  Hawking radiation either way.

### The instability belongs to the merged core, not the code
- **Claim.** Deny the merger and the evolution is healthy.
- **Runs.** `merge_orbit_flip_d12_p045` *(pack)* — clean to t = 60;
  `..._p045_t200` *(pack)* — the same fly-by held to t = 200, source of the
  six survival figures; `..._p035_t200` *(pack)* — a second fly-by (min sep
  2.75), though its inter-throat midpoint shows the slow lapse collapse of
  the freeze wall (last claim below), so "healthy" there needs the
  qualification.

### Resolution postpones the wall, never removes it
- **Claim.** The death time climbs +1.43 per refinement level, linearly over
  four rungs, no saturation and no cure; the NaN lands on each newly created
  finest level, so the blowup is a property of the continuum solution.
  Reaching t = 60 by refinement alone would cost ~10² × the compute.
- **Runs.** `merge_orbit_flip_d12_ml2` *(pack)* — level 2 dies at t = 9.4,
  before the throats meet; `..._r03000` (level 3, death 52.06) and `..._n160`
  *(pack)* — 25 % finer, same physics to 1.8 %, death 3 % later; the m4e
  refinement ladder, levels 4–7 with twins *(the level-6 rung
  `ladder_L6_r05000` and LAUNCHES.md are packed under
  `campaign/05_binary_spiral/p012_ladder/`, every rung packed since 2026-09-10; the tarballs live in that
  folder's ladder archives in the run tree)* —
  undamped-family deaths 52.07 / 53.10 / 55.60 / 56.13 / 56.20 for levels 3–7
  (`campaign/05_binary_spiral/refinement_ladder.dat`) — monotone and saturating,
  the last doubling buying 0.06; an earlier pair-mean quote that showed a
  turnover at level 7 mixed damped and undamped arms and is withdrawn;
  `..._p020_lvl5_t200` and `..._p025_lvl5_t200` *(pack)* — level 5 run
  from t = 0 dies at the level-3 wall (52.07 / 52.79): the +1.4/level gain
  belongs to the *restart* recipe (χ already clipped at the pits when a
  run starts deep), so depth must be added mid-run, not from birth.
- **The isolated throat on the same ladder (2026-09-08).** `single_hold_ml2_t100`
  *(pack)* dies at t = 24.17 (its χ-regularised twin at 24.13); `single_hold_t100`, one level finer, reaches
  t = 100. For the lone throat one halving of dx buys more than 75 units,
  against the binary's 1.4 per level. The level-4 pair (floors 1e-8 and
  5e-10) also reaches t = 100, byte-identical across its two floors — and on
  the other branch of the instability: the throat inflates instead of
  collapsing (`campaign/01_single_throat/BRANCHES.md`).
- **The head-on is the exception — preliminary (2026-09-09).**
  `merge_headon_flip_d8_v1_lvl5_t100_r02200` *(pack, in flight)*: the head-on
  at max_level 5, restarted from the freeze arm's t = 22 checkpoint with the
  fill off, passes the level-3 wall (26.91) at 27.05 and is at t = 42.9 with the
  constraint norms *falling* — Hamiltonian 1.5e-3 (t = 27–29) → 6.7e-4 (41–43),
  momentum 3.0e-3 → 1.1e-3, five times below the initial data's 3.2e-3 — while
  the level-3 freeze arm climbs from 2.5e-3 to 3.8e-3 over the same window. The
  orbital law above (two levels on restart = +2.9 units) predicted a delayed death
  at t ≈ 29.8; it did not come. The midpoint lapse sat on its 1e-10 floor from
  t = 38.5 to 41 and lifted again; chi touched its floor in single samples and
  is rising; max|K| peaked at 0.78 (t = 33) and reads 0.36. Not a fate yet:
  t = 100 is ~13.6 h away at 4.2 units/h. The horizon is there and clean:
  the fine oriented scan on the level-5 plotfiles (level 3, dx 0.0625) finds the
  outermost MOTS at r = 3.31 / areal radius 4.92 / Misner-Sharp mass 2.53 at
  t = 42.5 and r = 3.25 / 4.87 / 2.52 at t = 43.0, every shell inside fully
  trapped from r = 0.25, none anti-trapped, no throat left; against the scout's
  last reading (t = 26: r 1.98, R 4.72, M 3.16) the horizon has regrown to
  R ≈ 4.9 and shrinks slowly (−0.08 per unit). Scan text in the run's
  `small_data/horizon_offline_scan_lvl5_t42.5_43.dat` *(pack)*.

### The interior freeze rescues the ringdown window
- **Claim.** Freezing the collapsed interior after the burst closes carries
  the evolution to t = 100 with flat constraints for 27+ units; the exterior
  is bit-identical to the unfrozen twin beyond r = 6, the two seam-radius
  twins agree to five digits at every shared waveform sample, and the
  late-engagement control moves the R = 14 waveform ≤ 0.003 % (m = 2) /
  0.022 % (m = 0).
- **Runs.** The freeze program *(pack since 2026-09-10 — `campaign/05_binary_spiral/p012_freeze/`)*:
  `freeze_narrow_t080_r05000` / `freeze_wide_t080_r05000` (the t = 80 twins),
  `freeze_narrow_t100_r08000` / `freeze_wide_t100_r08000` (the t = 100 drains), plus
  the seam and late-engagement controls in `p012_freeze/`.
  Figures in `figures/`.
- **The head-on freeze arms (2026-09-09).** `merge_headon_flip_d8_v1c_latefreeze_t100`
  *(pack)* — the scout with the fill (r_full 1.2 / r_start 1.8) armed at t = 26.5,
  0.41 units before the scout's NaN — and its seam twin
  `merge_headon_flip_d8_v1c_fillnarrow_t100_r02200` *(pack)* (fill 1.0/1.5, from the
  t = 22 checkpoint) both reach t = 100 with no NaN. The (2,0) wave at R = 10/14/18
  swings three times (period ≈ 33, ×0.6 per half-swing) and is outgoing in every
  window — no wall echo. The head-on's seam is *not* the orbital's five digits:
  the twins agree to 3e-4 of peak until each fill's imprint arrives, then differ by
  1–5 % of peak at R = 10 and 3–12 % at R = 14 (t = 50–100); at R = 18 both grow a
  grid-scale wobble from t ≈ 80. **That drift is not the fill (2026-09-09):** the
  narrow-fill twin, the no-fill level-5 arm and the no-fill level-3 down-step agree
  with one another to 0.01–0.02 % of peak, and each differs from V1c by the same
  amount — the drift belongs to V1c, the only arm never restarted, and the likely
  cause is the regrid phase (a restart regrids 8 steps out of step with a continuous
  run). The control that settles it — a restart from the t = 22 checkpoint carrying
  V1c's own fill 1.2/1.8 — has not been run. What holds regardless: a run with a
  fill and a run with none agree to 0.01 % of peak, so the interior treatment does
  not reach the wave. The down-step itself reached t = 100 (2026-09-10): it tracks
  the level-5 arm to 0.05 / 0.22 / 0.33 % of peak at R = 10 / 14 / 18 over t = 45–100
  and matches its constraints to 0.05 % (Hamiltonian) and 1.4 % (momentum) at t = 100,
  so after the merger the coarse grid loses nothing the wave can see
  (`figures/04_binary_headon/headon_downstep_psi4_20_R10_14_18_t100.png`; both no-fill arms reached
  t = 100 on 2026-09-10). **The fill is not free after all:** V1c ends with
  Hamiltonian 6.06e-3 and momentum 5.78e-3 against 1.40e-3 and 1.30e-3 for either
  no-fill arm — 4.3x worse. It does not reach the wave, but it does cost constraint
  accuracy, so once resolution alone carries the run past the wall the fill is not
  worth taking.
  And the constraints are not flat here: Hamiltonian
  3.3e-3 (t = 30–40) → 5.8e-3 (90–100), doubling every ~80 units, in both twins.
  `figures/04_binary_headon/headon_freeze_psi4_20_R10_14_18_t100.png`.

### The recorded signal is a genuine gravitational wave
- **Claim.** Propagation at 0.889 of coordinate light matches the metric's
  own local light speed along the extraction path (14→30 crossing predicted
  ~19.5, measured 18.0); 1/R falloff holds; the (2,0) breathing and (2,2)
  whirl channels separate cleanly; the in-code mode integrals match an
  independent Simpson quadrature to 1e-8.
- **Runs.** The same M9b freeze arms *(run tree)*; the evidence is
  `figures/05_binary_spiral/psi4_analysis_freeze_wide_t080*` and `figures/05_binary_spiral/wave_speed_check.png`.

### Where the capture boundary sits in orbital momentum
- **Claim.** p = 0.20 and 0.25 are captured, p = 0.35 and 0.45 fly by — the
  boundary sits between 0.25 and 0.35 (50–70 % of circular). Whether a
  captured scout *completes* its merger is open: every one hits the t ≈ 53
  wall first, so "no completed merger at p ≠ 0.12" is untested, not
  established.
- **Runs.** `..._p020_t200`, `..._p025_t200`, `..._p035_t200`,
  `..._p045_t200` *(pack)*; `..._p020_nofill_t060` *(pack)* — p = 0.20 with
  damping off and in-code Weyl4: **hovered at sep 1.08 from t = 46 until the
  wall (52.08)** — captured but not fusing; the two lvl5 arms *(pack)* —
  the same answer at depth.  And the boundary is finer than "0.12 fuses,
  0.20 hovers": `..._p015_nofill_t060` and its insured rerun
  `..._p015_rr_t060` *(pack)* put **p = 0.15 on the fusing branch** —
  plateau at pit sep 0.816 (p012's was 0.815), dive to 0.70 with the core
  lapse *rising* (p012's endgame signature) — but the wall (53.35, the
  same step in both runs) cut it before the pits coincided.  So the fusing/
  hovering divide sits between 0.15 and 0.20.  The restart-refinement
  recipe was then tried and is **not enough**:
  `..._p015_lvl5_t060_r05000` *(pack)* — max_level 5 from the insured
  t = 50 seed — pushed the wall only +0.88 (h11 NaN at t = 54.23), the
  offline scan of its last plotfiles finds **no trapped surface** (1 % of
  rays at t = 54.0), and the (2,2) waveform was *still climbing* at death:
  3.14e-2, already 6 % above p012's complete peak.  p = 0.15 was wall-cut
  mid-fusion a third time; refinement alone cannot outrun the wall, and
  finishing p = 0.15 — and its full, larger signal — means the core-freeze
  continuation validated on p012.

### The Helfer correction: better initial data, worse evolution
- **Claim.** The correction removes the superposition's constraint defect at
  the throats but parks a fade-zone defect between them; at the default
  window (d/3 = 4) the orbit stalls at sep ≈ 4.7 and the run freezes —
  reproduced at levels 3, 4 and 5, so converged, not under-resolution.
  The halved window (2.0) did NOT clear it: the w2 twin tracked plain
  superposition exactly to t ≈ 14, then fell progressively behind and read
  sep 5.10 at the pre-registered t = 32 gate — above the 4.5 kill line and
  above even the wide-window run's 4.73 (plain: 2.06). Window placement was
  not the problem; the correction itself spoils the phantom binary's infall.
  Production therefore runs plain superposition (its +9.5 % initial-size
  artefact accepted).
- **Runs.** `merge_twin_p012_helfer_t100` vs `..._plain_t100` *(pack)* — the
  one-flag twins; `..._helfer_lvl4_t100` *(pack)* — stall reproduced to < 2 %
  in the lapse trace; `..._helfer_lvl5_t100` *(pack)* — stalled the same at
  production depth, stopped at t = 31.5; `..._helfer_w2_t060` *(pack)* —
  window halved to 2.0, killed by its pre-registered verdict (sep 5.10 > 4.5
  at t = 32), stopped by hand at t = 33.1.
- **The fly-by test, and why the initial size artefact is the point**
  *(2026-09-04)*. `merge_orbit_flip_d12_p045_helfer_t090` *(pack)* ran the
  correction on an arm that never merges, against the existing plain
  `..._p045_t200` as an exact one-flag control, to ask whether the late
  accuracy loss is an initial-data artefact. Answer, from t = 30 on: the plain
  arm's Hamiltonian norm sits flat at 2.15–2.21e-03 while the corrected arm
  grows 3.18e-03 → 1.59e-02, a factor 5 in seven units. Because the
  denominator is constant this is a real signal, not the ratio noise that
  earlier readings of this pair mistook for one (the pointwise ratio swings
  940× on regrid steps; quote rolling medians only).
  **Read it with the isolated-throat control, not alone.** `single_hold_t100`
  shows one throat, no companion and no superposition defect at all, holding
  its exact areal radius for 26 units and then contracting exponentially. The
  clocks match (26 vs 30). So the correction is not "worse initial data" — its
  +9.5 % change in each throat's initial size is a large perturbation of an
  *unstable equilibrium*, and it simply reaches the mode sooner. The honest
  claim is that the late degradation is neither an initial-data artefact nor a
  binary effect, but the constituent's own instability. Stopped by request at
  t = 37.29 of 90, short of the pre-registered t = 50–70 verdict point.

### The freeze wall itself: lapse collapse at the midpoint, not the throats
- **Claim.** In every binary the lapse collapses at the inter-throat midpoint
  (where the opposite scalar profiles cancel), never at the throat cores (the
  pits hold lapse 0.05–0.24 throughout). If the midpoint reaches the 1e-10
  floor the evolution goes static without a NaN — the "zombie"; if it hovers
  above, the run dies of the h11 NaN instead. Mergers interrupt the collapse;
  stalls and fly-bys let it finish.
- **Runs.** The Helfer twins *(pack)* — the clean zombie; `..._p025_t200`
  *(pack)* — the NaN side of the race; `..._p035_t200` *(pack)* — a slow
  zombie with no Helfer correction at all, proving the wall is not
  Helfer-specific; the unmasked runs (`_nofill`, damping off) confirmed it
  on p = 0.15 and 0.20. The validation and the slice-probe evidence are
  written up in `research/merger/archive/GPU_PLAN_2026-09-03.md` §9.

### The wall time is gauge + resolution, not physics
- **Claim.** The t ≈ 52–53 death time must never be read as a physical event.
  Three independent handles each move it while the physics underneath holds:
  refinement moves it +1.4 units per level (the ladder above); halving the
  slicing's `lapse_coeff` (2 → 1) moves it **8.4 units earlier** — to
  t = 43.64 — while the blob still nucleates on schedule, capture and plunge
  proceed, and the pits close to 0.442; and at fixed gauge + resolution it is
  *deterministic*: the p015 rerun died at the same step (5335, t = 53.35) as
  its original. The crash is the 1+log slicing losing its
  singularity-avoidance race, not the singularity arriving.
- **Runs.** `merge_twin_p012_lc1_t060` *(pack)* — the one-knob gauge arm;
  `merge_orbit_flip_d12_p015_nofill_t060` + `..._p015_rr_t060` *(pack)* — the
  determinism pair; the m4e ladder *(run tree)* — the resolution axis.
- **Autopsy (2026-09-08).** `autopsy_nodamp_r05000` *(pack)* — the
  no-damping twin restarted from t = 50 with the per-cell NaN report armed:
  same step as the original (t = 51.53), deterministic. The report
  (`run_tail.log`) puts the death ~0.8 units off the merged core, ≥ 16 cells
  from any patch edge or the domain wall, 11 steps after a regrid, with every
  field overflowed to finite 1e+88–1e+163 in one step and only A_ij true NaN;
  the core itself has sat on the χ floor since t ≈ 50.1 (`throat_track.dat`).
  Same mechanism as the isolated throat's origin death — a floored core with a
  vertical gradient beside it — so the fix belongs at the floor, not the
  throat. `..._HOOKFAIL_2026-09-08` *(pack)* is the identical death with the
  report silently disarmed, kept as the evidence behind the fix.
- **Say it as.** Every claimed event (blob, capture, fusion, burst) completes
  *before* the wall of the run that claims it; the wall itself is quoted only
  as the limit of the numerical window.

### The core damping shapes nothing that is claimed
- **Claim.** Every scan/twin verdict was originally taken with
  CoreMatterDamping engaged from t ≈ 30. The damping-off twin shows this
  never mattered: at t = 32 the damped and undamped runs agree to 3 decimals
  in separation, midpoint lapse, |φ| and scalar activity (the files are
  verifiably different — max |Δφ| = 0.0056, so this is agreement, not a
  copy), and the wall moves only 52.06 → 51.53 (~1 %, the arm-pair noise
  floor). Damping neither causes the blob, nor the merger, nor the wall —
  and production can run clean (damping off) with its behaviour measured
  rather than assumed.
- **Runs.** `merge_twin_p012_nodamp_t060` vs `merge_twin_p012_plain_t100`
  *(pack)* — the one-knob pair.

### The vacuum BBH control recovers the known answer
- **Claim.** The same grid, gauge, extraction chain and orbit (d = 12,
  p = ±0.12, ADM mass 1 each), with black holes instead of throats, does
  everything textbook: merger at t ≈ 70, then a ringdown whose fitted QNM
  (period 28.8–29.7, damping time 23–27) matches a Kerr remnant of
  M ≈ 1.9 with modest spin (Schwarzschild reference 16.8 M / 11.2 M —
  spin shortens the period exactly as seen); both extraction radii agree to
  3–7 %. The instruments cross-validate: the independent plotfile consumer
  and the in-code stream match to 0.31 % of peak (correlation 0.999999).
  Boundaries hold for 150 units with Sommerfeld alone — χ scatter *falls*
  outward, no reflected ripples (the sponge exists only in the wormhole
  code path; the vacuum run needs none, by construction). And at the same
  detector (R = 14) the wormhole merger is **~2.3× louder** than the BBH —
  with an extra (2,0) breathing channel 5.5× the BBH's.
- **Runs.** `bbh_control_d12_p012_t150` *(pack)* — the control;
  `bbh_control_d12_p012` *(pack)* — its t = 100 predecessor;
  `merge_twin_p012_plain_t100` *(pack)* — the wormhole side of the
  comparison. Figures: `figures/07_bbh_control/bbh_t150_ringdown.*`,
  `figures/05_binary_spiral/bbh_vs_wormhole_psi4.*`.

### The neighbour is on the ruler; the interaction squeezes the throats before contact
*(2026-09-09, during the V1 scout's approach)*

- **Claim.** Two exact drainhole throats simply *placed* at rest read wider at
  each mouth than an isolated throat, the more so the closer they sit: +1.8 %
  at d = 48 (the throat centres at the sponge's inner edge, the widest the
  box allows), +5.0 % at d = 20, +9.0 % at d = 12, +14.4 % at d = 8, +20.5 %
  at d = 6, falling as d^−1.16 over 6 ≤ d ≤ 48, close to the 1/d of a
  mass-like field. That is the neighbour's field on the ruler, not a wider
  throat.
  Against that placement curve, the scout's mouths during the approach are
  *narrower* than placed throats at the same separation: −0.6 % at t = 7,
  −1.7 % at t = 10, −4.0 % at t = 13 (separation 6.06), the deficit growing
  with the closing speed. The lone throat at level 3 is exact to 0.1 % until
  t = 35, so this is the interaction alone: it squeezes, in the direction of
  the collapse branch, and there is no expansion phase for the individual
  throats. The 14 % apparent widening of the d = 8 pair at t = 0, and the 9 %
  of every d = 12 pair of the earlier campaign, was placement.
- **Runs.** Eighteen probes `place_d{6,65,7,75,8,10,12,14,16,18,20,24,28,32,36,40,44,48}_step1`
  *(pack)* — initial data plus one step each, scanned at
  t = 0 with the scout's per-mouth horizon scan (mouth A and B agree to 1e-5;
  the d = 8 probe reproduces the scout's own t = 0 row to ten digits); the
  scout `merge_headon_flip_d8_v1_t100` *(pack)* for the pre-contact
  rows.
- **Where.** `campaign/04_binary_headon/PLACEMENT_CURVE.md` (tables, generated), `figures/04_binary_headon/placement_curve.png`,
  `analysis/placement_curve.py`.
- **Caveats.** The tracker snaps the mouth centres to the finest grid, so the
  reported separation at rest is 7.94 for a true 8.00 — that is the −0.13 %
  seen before the throats move, and the size of the systematic. Motion cannot
  fake the sign: a boost contracts the throat in coordinates but not in area,
  and a coordinate sphere cannot read below the least-area surface it encloses,
  so a pure boost pushes the scan *up*; the squeeze is if anything
  underestimated. Below d ≈ 4 the mouths overlap in coordinates and a per-mouth
  radius stops meaning much — the probes stop at 6, and the scout's rows below
  that separation are flagged in the table, not interpreted. What the merged
  core does after contact is a separate question, read from the sphere about
  the midpoint.
- **What it retires.** The Phase-3 gate "both throats within 0.1 % of exact at
  contact" (GPU_PLAN.md) cannot be met by construction and is replaced by "no
  trapped and no anti-trapped surface at either mouth before contact". The
  CLOCK_COMPARISON.md hypothesis that the companion *holds the throat open*
  (origin χ higher than the lone throat's) is not what the mouths measure: at
  the mouths, relative to placement, the companion squeezes.

### The head-on pair forms a black hole, and the code dies inside it five units later
*(Phase 3 scout, 2026-09-09; from NaN to a black hole — half way)*

- **Claim.** Two exact drainhole throats (a = 2, m = 1, one scalar sign flipped)
  released from rest at d = 8 at level 3 fall together on an inverse-square law
  and touch at t ≈ 20 as wormholes: no trapped and no anti-trapped surface at
  either mouth, each mouth squeezed 4 % relative to placement. Two units later a
  single marginally trapped surface encloses both mouths — no mouth ever had its
  own, so the surface count goes 0 → 1 about the midpoint. It grows until t = 24
  and then shrinks fast, the phantom dissolution seen before; the lapse at the
  midpoint collapses (0.09 at contact, 0.02 at death); chi at the midpoint
  reaches the 1e-20 floor from t ≈ 24.5; K there doubles every 0.3 units from
  t ≈ 25.3; and at t = 26.91 a cell 0.9 from the midpoint overflows in one step.
  Same anatomy as `autopsy_nodamp_r05000` (floored core, one-step overflow away
  from it, far from any grid edge). The point-of-use chi regularisation and the
  1e-20 floor changed the timing, not the outcome. New against every d = 12
  pair: the black hole is *seen forming before* the wall, on two instruments,
  and lasts at least four units.
- **Horizon history** (fine-grid oriented scan about the midpoint, level 3,
  `horizon_offline_scan.dat`; the live consumer's level-1 common scan lost the
  crossing at t = 23–25 and is not the record):

  | t | MOTS coordinate radius | areal radius | Misner-Sharp mass | fully trapped shells |
  |---|---|---|---|---|
  | 22 | 3.17 | 5.56 | 2.99 | 2.39–3.17 |
  | 23 | 3.44 | 5.64 | 2.94 | 1.91–3.43 |
  | 24 | 3.66 | 5.71 | 2.89 | 1.49–3.65 |
  | 25 | 2.85 | 5.16 | 3.03 | 1.15–2.85 |
  | 26 | 1.98 | 4.72 | 3.16 | 0.95–1.97 |

- **Runs.** `merge_headon_flip_d8_v1_t100` *(pack)*: `binary_throat_diagnostics.dat`
  (contact), `collapse_diagnostics.dat` (midpoint lapse, chi floor, K runaway),
  `constraint_norms.dat` (flat at 2.3e-3 until the last half unit, 13.6 at
  death), `horizon_scan.dat` (live, per mouth and common), `horizon_offline_scan.dat`,
  `run_tail.log` (the NaN autopsy: cells (516,511,498–499), chi 0.031 → 1e190 in
  one step, neighbours chi 0.030–0.033 and lapse 0.09–0.10), frames and movies of
  chi, lapse, K, phi, Pi to t = 26.
- **Caveats.** The horizon is read on coordinate spheres about the midpoint;
  the true surface is a peanut, so the Misner-Sharp numbers are ±20 % and the
  areal radii of the flagged spheres are upper bounds on the true minimal one.
  A shrinking horizon is allowed here (the phantom field violates the null
  energy condition) but the shrink from t = 24 coincides with chi reaching the
  floor at the midpoint, so interior numerics and interior physics are not yet
  separated. Infall in coordinates is 25 % slower than Newtonian free fall of
  two unit masses (contact 19.9 vs 16.4); the d = 12 head-on agreed to 5 %; the
  coordinate centre separation is not the physical one (see the like-oriented
  section, δ ≈ 3.5).
- **What it settles and what it opens.** Settled: the merger of two massive
  drainhole throats ends in a black hole, not in inflation or a stall, and the
  code reaches it. Open: the interior. The wall follows the horizon by five
  units and is the same one-step overflow as before, so the next arm is the
  interior freeze of the stage-3 chain applied once the common horizon exists
  (physically legitimate: nothing inside it reaches the outside), which ran the
  fill arms clean to t = 66 in 2026-09.
- **Update (2026-09-09, 11:35).** Both freeze arms ran to t = 100 (the freeze
  section above) and the level-5 restart with no fill is past the wall and past
  the orbital law's delayed death, at t = 42.9 with the constraints falling (the
  resolution section above) and a clean horizon on the fine scan (R ≈ 4.9,
  M_MS ≈ 2.5 at t = 43). The halved-mass control formed a horizon anyway and
  died earlier (the next section). Open: the level-5 arm to t = 100 and the
  ringdown against Kerr.

### Halving the mass does not avoid the horizon: the drainhole's size is not set by its mass

`merge_headon_flip_d6_m05_t100` (2026-09-09, level 3, fill off, frozen binary
`main3d_boost_2026-09-08.ex`). Two drainholes of mass 0.5 each — half the
scout's — released from rest at d = 6, the closest placement whose throats do
not overlap. The point was to put the merged mass below the hoop line and see
what two throats do when they touch *without* a horizon.

- **They still form one.** The offline level-3 scan about the midpoint finds a
  common marginally-outer-trapped surface at **t = 12** (coordinate radius
  2.28, areal radius **3.83**, Misner–Sharp mass **2.16**, 6 trapped rays) and
  a bigger one at **t = 13** (2.62, areal **3.91**, M_MS **2.05**, 18 trapped
  rays, outermost). The live level-1 scan, which is coarse, saw it from
  t = 12.32 to 13.37 and then lost it — the fine scan is the one to quote.
- **Why the mass knob failed.** The drainhole's mass parameter sets the pull,
  not the size. At m = 0.5 the throat's own areal radius is 3.18, against 3.89
  at m = 1: halving the mass shrinks the throat by 18 %. Two objects of areal
  radius 3.2 released 6 apart enclose a large area from the start, and the
  mass that ends up inside the surface is 2.05–2.16 — twice the sum of the two
  mass parameters, because the phantom field outside carries negative energy.
  Against R_mots 3.91 the hoop line 2·M_MS is 4.10: the configuration is on the
  line, exactly as the m = 1 pair was. The size of a drainhole is set by its
  phantom parameter, so lowering m cannot get a binary under the hoop.
- **The same wall, 12.9 units earlier.** The lapse falls from 0.44 (t = 7.5) to
  0.036 (t = 13); χ touches the 1e-20 floor from t = 6.80; the tracker merges
  the two mouths at t = 11.07. NaN at **t = 14.00** on level 3, in cells about
  1.0 from the box centre, 16 cells from every grid edge, with the lapse driven
  onto its 1e-10 floor in one step and χ, h_ij, K overflowing together. The
  Hamiltonian norm is flat at 3.4e-3 until the final step. Anatomy identical to
  the m = 1, d = 8 scout at t = 26.91 — so **the wall is not a mass effect**.
- **Read the mouths' radii with care.** The consumer was given the m = 1 exact
  throat radius (3.8895) as its reference, so the deviation column of this run
  is against the wrong number and only its trend means anything. The trend: the
  minimum areal radius rises 3.18 → 3.52 between t = 0 and t = 13, but from
  t ≈ 11 the two mouth centres are less than 0.7 apart, so after that the
  "per-mouth" scan is reading the merged region, not two throats.
- **What it opens.** A lone throat at m = 0.5 has never been run. Its own
  instability clock (onset 26, e-fold 5.9 are m = 1 numbers, and the rate
  depends on m/a) is what dates whether these mouths were already collapsing
  before they touched. Until that control exists, nothing here separates
  contact from self-decay.

Frames (χ, K, lapse, φ, Π, Weyl4), the slice cache and all Weyl4 modes at
R = 10/14/18 were written before the abort, so the run is fully analysable.

## `figures/` — the campaign figures, by group

One folder per group, the same names as `campaign/`.

**Since 2026-09-10 every merger figure is drawn by one package**,
`grteclyn_wrapper.visualisation.wormhole_merger`, in one house style: journal
typography, at most three dark hues told apart by their dash pattern first,
an ordinal ramp for ordered families (refinement levels, extraction radii),
`cividis`/`RdBu_r` for anything two-dimensional, and symbols — not sentences —
on the axes. Its README carries the palette and the rules. Every figure now
ships a PDF beside its PNG.

`pack_results.sh` runs the reductions (which write the generated notes and the
small tables beside them) and then the figure modules that need no arguments.
The rest are one command each, given below.

Removed on 2026-09-10 along with their scripts: `throat_clock_comparison.png`
(the origin-χ clock — a gauge-dependent monitor that could not be read as the
throat quantity it looked like) and `scalar_vs_psi4_R14*.png`. The two
live-snapshot figures of the head-on freeze arm (t = 38 and t = 54) went
earlier the same day; the t = 100 figure supersedes both.

| file | what it shows |
| --- | --- |
| `01_single_throat/single_throat_branches.{png,pdf}` | the level-3 / level-4 ladder of the lone throat: the same unstable mode at the same rate, opposite sign — collapse at level 3, inflation at level 4. Two panels: the throat radius, and its logarithmic deviation with each arm's fitted rate in the key. The third panel of shell profiles was dropped on 2026-09-10 (its own key covered the curves, and the shell scans are in the table in `BRANCHES.md`, which is where they can be read) (generated) |
| `04_binary_headon/placement_curve.png` | the placement curve from the eighteen one-step probes (d = 6 → 48) and the V1 scout's mouths against it before contact. The reduction (`analysis/placement_curve.py`) writes `placement_curve.dat` and `placement_scout_residual.dat` beside the note; `plot_placement_curve` draws them (generated) |
| `04_binary_headon/psi4_analysis_merge_headon_flip_d8_v1c_latefreeze_t100.{png,pdf}` | the six-panel wave analysis of the head-on programme, on V1c — the only head-on arm never restarted, so its spectrum carries no seam. The wave sits at f ≈ 0.03 and stays there: a bell, not a chirp. Panel (e)'s frequency band and wavelet width are chosen from the record itself — the band from the spectral peak, the width the widest that still leaves half the record outside the cone of influence — and the part the wavelet cannot reach is faded rather than hatched. Drawn to a fixed f = 1 with a fixed width, the panel was a decade and a half of empty page above the wave and almost entirely cone. `plot_psi4_analysis` |
| `04_binary_headon/headon_freeze_psi4_20_R10_14_18_t100.png` | the head-on freeze arm's (2,0) mode at R = 10/14/18 to t = 100 (final, 2026-09-09): **three swings of the merged object, outgoing all the way** — at R = 10 peak +0.23 (t = 28.2), trough −0.18 (43.6), peak +0.11 (62.7), trough −0.06 (79.0), period ≈ 33 and ×0.6 per half-swing; R = 14 and 18 the same, each ~4 units later per 4 units of radius. The cross-correlation lag from R = 10 to 18 is positive in every window, so nothing comes back from the wall. The fill twin (dashed, 1.0/1.5) lies on V1c to 3e-4 of peak until each fill's imprint arrives (red dotted), then differs by 1–5 % of peak at R = 10 and 3–12 % at R = 14 — a drift later shown to be V1c's own, not the fill's; at R = 18 both runs grow a grid-scale wobble (period ≈ 1.5) from t ≈ 80. Amplitude still grows with R: R = 18 is not the wave zone. |
| `04_binary_headon/headon_downstep_psi4_20_R10_14_18_t100.png` | the level-3 down-step (restarted from the level-5 t = 35 checkpoint with max_level 3) against the level-5 arm, the narrow-fill twin and V1c: Re r·ψ4 (2,0) at R = 10/14/18 to t = 100 (2026-09-10). The down-step and the level-5 arm lie on top of each other to 0.05 / 0.19 / 0.25 % of peak through t = 98.4, the fill twin inside 0.07 / 0.14 / 0.25 %; V1c, the only never-restarted arm, drifts by 6 / 14 / 41 %. Grey band: initial-data junk; black dotted: the restart at t = 35; red dotted: the earliest arrival of anything the restart changed. Made by `python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_modes --restart 35 …` from the every-step Weyl4 streams. |
| `05_binary_spiral/psi4_analysis_freeze_wide_t080.{png,pdf}` | six-panel analysis of the (2,0) breathing mode, full history t = 0–80 stitched across the restart chain: waveform at both radii, retarded-time overlay, PSD, propagation speed (0.889 of coordinate light — see the speed check below), spectrogram, strain vs Advanced LIGO |
| `05_binary_spiral/psi4_analysis_freeze_wide_t080_m2.{png,pdf}` | same six panels for the (2,2) whirl mode — the channel that carries the plunge burst |
| `05_binary_spiral/psi4_analysis_freeze_narrow_t100.{png,pdf}` | the six panels for the narrow-fill drain arm (fill 1.3/1.8) to t = 97 — the seam twin of the wide-fill analysis; the two agree to five digits outside the fill |
| `05_binary_spiral/gw_merger_full_history_0_97.png` | the stitched p = 0.12 waveform t = 0 → 97 (`campaign/05_binary_spiral/psi4_merger_stitched_0_97.dat`: r03000 to 50.5, fillwide80 to 79.5, fillwide100 to 97): no chirp and no ringdown anywhere in it (archive GPU_PLAN_2026-09-03 §B4) |
| `05_binary_spiral/merger_ladder_psi4_R14.{png,pdf}` | **one panel**: the refinement ladder (levels 4–7) and both freeze arms at R = 14, on the (2,2) channel. Every ladder arm dies at t = 53–56, short of the collapse band at 58–66; only the freeze arms cross it. All six trace the same wave to the width of the line where they overlap, which is the result — so the ladder is drawn on top of the freeze arms and its dashes let them show through. Redrawn 2026-09-10: it was two panels, (2,2) over (2,0), and the freeze arms were a fat quarter-opacity burgundy stroke that printed mauve. `plot_ladder_psi4 --radius 14 --mode 22 --run "level N=…" --under "…freeze arm=…"` |
| `05_binary_spiral/merger_constraints_t80.{png,pdf}` | Hamiltonian and momentum L2 for both completed t = 80 freeze arms, t = 0–80: the spikes before t = 34 are regrid transients; the smooth bump is the collapse; after the freeze engages at 53 both norms sit flat for 27 units |
| `05_binary_spiral/wave_speed_check.png` | why 0.889 c is not sub-luminal junk: the metric's own local light speed along the extraction path predicts a 14→30 crossing of ~19.5; the wave took 18.0. Constraint/gauge modes travel at √2 × light and are excluded |
| `05_binary_spiral/seam_ring_rescaling.png` | why the freeze-arm frames *look* like the signal vanishes: a growing Ψ₄ artefact confined to the freeze seam hijacks the per-frame colour scale; the radiation field is bit-identical to the unfrozen twin beyond r = 6 |
| `05_binary_spiral/bbh_vs_wormhole_psi4.{png,pdf}` | same masses, same orbit, different object: wormhole vs BBH waveforms, envelopes (2.3× / 5.5×), PSD |
| `06_binary_flyby/p045_flyby_separation.{png,pdf}` | the p = 0.45 arm's separation to t = 91: closest approach 3.95 at t = 40.05, then out again, with each throat's own monitor below. Redrawn 2026-09-10 as two stacked panels — the earlier version put separation and min χ on a shared frame with a second y-axis, where the crossing of the two curves read as an event it is not. `plot_separation --run merge_orbit_flip_d12_p045_t200` |
| `06_binary_flyby/p045_flyby_chi_linear.png`, `p045_flyby_logchi.png`, `p045_flyby_phi.png`, `p045_flyby_lapse_t84.png`, `p045_flyby_weyl4mag_t60.png` | slices of χ, φ, the lapse and \|Ψ₄\| through the fly-by (2026-09-02, drawn as "the throats survive it"). **Read with item 5 above:** from t ≈ 45 the midpoint lapse collapses and the Hamiltonian norm doubles every 5 units, so the frames after t ≈ 50 (the t = 60 and t = 84 ones here) show a run whose constraints are 3–100× the initial data's |
| `06_binary_flyby/gw_flyby_vs_merger_m0_chain.png`, `gw_flyby_vs_merger_m2.png`, `gw_merger_vs_flyby_full.png` | the p = 0.12 chain's (2,0) and (2,2) modes against the p = 0.45 fly-by's (2026-09-04): superposed over t = 0–25 (the initial-data junk, not the orbit); in the clean window the fly-by radiates ~1.7× harder than the merger; across the stitched 0–97 no chirp and no ringdown (archive GPU_PLAN_2026-09-03 §B4) |
| `07_bbh_control/bbh_t150_ringdown.{png,pdf}` | the BBH control's full (2,2) ringdown at R = 30 with the QNM fit (period 29.7, τ 27.1) and the Kerr known-answer comparison |
| `07_bbh_control/psi4_analysis_bbh_control.{png,pdf}`, `_m2.{png,pdf}` | the six-panel analysis of the vacuum control's (2,0) and (2,2) modes at R = 14/30 (2026-09-03, the t = 100 run); the ringdown figure above supersedes them for the late time |

## Layout

The pack mirrors the run tree: one folder per physics group, the groups being
the sections of the paper, and inside a group one directory per run. A run that
is still on a card sits at the top of `campaign/` until close-out files it.

```
campaign/
  01_single_throat/<run>/         one throat: the Stage-1 ladder (11 arms, old binary),
                                  the production hold single_hold_t100 and its seven
                                  one-knob twins (resolution, chi floor, time step)
    INSTABILITY.md                  the isolated-throat systematics, generated
    BRANCHES.md                     the level-3 / level-4 ladder read (two fates), generated
    CLOCK_COMPARISON.md             the throat clocks across arms, generated
    NOTES.md                        the Stage-1 working notes, copied from the run tree
  02_moving_throat/s20_boost_p02/ the boosted throat that crosses the grid (Stage 2.0)
  03_two_throats/<run>/           two throats released from rest: the four Stage-2.5/2.6
                                  controls (push, rest, width, flip) and the five a-point /
                                  separation rungs of 2026-09-04; the two ladder tables
                                  scalar_charge_apoints_*.txt, separation_ladder_*.txt
  04_binary_headon/<run>/         the head-on programme: the d = 12 old-binary run, the
                                  low-mass d = 6 pair, the V1 scout and its five arms
    placement/place_d*_step1/       the eighteen one-step placement probes
    PLACEMENT_CURVE.md              the placement curve and the scout against it, generated
  05_binary_spiral/<run>/         the p = 0.12 chain and its one-knob probes, the twins
                                  (plain, Helfer x4, damping, gauge, floors), the capture
                                  scan p = 0.15 / 0.20 / 0.25 with their level-5 and no-fill
                                  arms, the two NaN autopsies
    p012_ladder/<arm>/             every rung of the refinement ladder, levels 3-7
    p012_freeze/<arm>/             the interior-freeze programme, the headline waveform
                                    programme (fill80 / fillwide80 / fill100 / fillwide100,
                                    the Weyl-extraction tests) with its LAUNCHES.md
    horizon/                        the offline Theta = 0 scans behind the dissolution result
    psi4_merger_stitched_0_97.dat   the stitched p = 0.12 waveform, t = 0 -> 97
  06_binary_flyby/<run>/          p = 0.35 and 0.45: the fly-bys (and p045's Helfer twin)
  07_bbh_control/<run>/           the vacuum binary-black-hole control, t = 100 and t = 150
  <group>/NOTES.md                the group's working notes, copied from the run tree

campaign/<group>/<run>/           what every run directory holds
  collapse_diagnostics.dat        lapse, chi, K and scalar-field extrema
  constraint_norms.dat            Hamiltonian and momentum L2
  binary_throat_diagnostics.dat   separation, per-throat position and minima,
                                  the in-code Theta scan
  throat_track.dat                the tracker that aims the refinement boxes
  psi4_*.dat, Weyl4_*.dat         the extracted waveform (consumer; in-code where on)
  areal_radius.dat, horizon_*.dat the throat radius and the horizon scans, where on
  evolution_params.txt            the exact input the run was given
  launch_banner.txt               what the launcher resolved: template, binary,
                                  GPU, restart checkpoint, consumer arguments
  run_tail.log, backtrace.txt     the last 200 log lines and where it aborted
  movies/                         the stitched .mp4s, one per field (where made)
  frames/                         thinned stills, where the pictures carry a result
  part1/, *__part1*.dat           the pre-restart episode of the same run

figures/<group>/                  the figures, by the same groups (table above)
runs_registry.tsv                 ONE line per run: what is different, caveat, stopped
                                  note -- the only place a run is registered (the
                                  launcher appends it when WHM_WHAT is set)
analysis/pack_paths.py            how every script here finds a run by name, wherever filed
analysis/make_summary.py          builds the two summary tables, one block per group
analysis/single_throat_instability.py, throat_clock_comparison.py,
analysis/placement_curve.py       the REDUCTIONS: they write the generated notes above
                                  (INSTABILITY.md, CLOCK_COMPARISON.md,
                                  PLACEMENT_CURVE.md) plus the small .dat tables a
                                  figure needs.  They draw nothing and import nothing
                                  outside this folder, so a copy of the pack stays
                                  runnable with a stock Python.  The FIGURES all live in
                                  grteclyn_wrapper.visualisation.wormhole_merger
summary.md, summary.csv           one row per run (csv: plus a `group` column), generated
```

The four evolution streams are written every step (dt = 0.01) and thinned here to
dt = 0.05 — **except the last time unit of each run, kept at full cadence**, because that
is where a dying run does everything interesting. The `psi4` streams are one row per
plotfile and are packed whole.

Not packed, and not recoverable from here: plotfiles, checkpoints, the full frame series
(~250 per field) and the slice caches (7–620 MB per run). Those live in the run tree —
and, since 2026-09-10, only on the runs whose pictures matter (the run tree's README
says which).

## The stage-3 chain in detail

Nine runs (the 2026-09-02/03 scan, twin and wall runs are described in the
claim map above and carry rows in `summary.md`). The first five are one chain — each restarts from the previous one's
checkpoint, changing exactly one thing, hunting the same failure. The rest are
independent probes. `summary.md` has the measured columns for all of them.

Reading a name: `merge_orbit_flip_d12_rw_r05000` is a **merge** run, throats on an
**orbit** (given tangential momentum) rather than dropped head-on, one throat's scalar
field **flipped** in sign, started **d = 12** apart, using the **r**adius **w**indow
damping, **r**estarted from checkpoint **05000**. `_pNNN` is a different tangential
momentum, `_nNNN` a different cell count, `_mlN` a different `max_level`, `_sgNN` a
different Kreiss–Oliger dissipation.

| run | what is different | ran to | what happened |
| --- | --- | --- | --- |
| `..._r03000` | **the main arm** — no damping | 52.06 | Inspiral to t ≈ 33, whirling double core, collapse at t ≈ 45, horizon at t ≈ 51 — then the phantom core blew up. Everything after this is an attempt to save it. |
| `..._r05000` | damping on, built-in thresholds (≈3 cells) | 52.09 | Bought 0.02 units. Aimed too deep to touch the matter that kills it. **Its streams were deleted before extraction — only the log survives.** |
| `..._r04000` | window widened 1000× (lapse 3e-2 → 1e-3) | 52.86 | Core cleaned to φ ≈ 1e-10 and it still died: 1+log slicing lets the sickest cells re-inflate their own lapse and climb out of a lapse-defined window. |
| `..._sg10_r05000` | dissipation σ 0.1 → 1.0 | 51.68 | Backfired — died *earlier*. The dissipation attacks the puncture structure itself. |
| `..._rw_r05000` | damping anchored in **radius**, not lapse | **55.00** | Longest survivor, and the one that caught the horizon dissolving. |
| `merge_headon_...` | dropped head-on, no orbital momentum | 44.00 | Merges harder and sooner, dies the same death. (Its "horizon at t = 29" was the old-scan artefact; true timing unverifiable — no metric in its plots.) |
| `..._p045` | momentum 0.45 instead of 0.12 | **60.01, clean** | Never merges: closest approach 3.95 at t = 40, then back out to 4.6. The healthy control. |
| `..._n160` | 160 cells per side instead of 128 | 53.61 | The convergence check, and the only undamped arm that ran t = 0 → death in one piece. Everything before the collapse converged; the death moved by 3 % and stayed. |
| `..._ml2` | `max_level = 2` instead of 3 | 9.42 | Dies before the throats meet. Three levels is the floor, not a luxury. |

Everything not named above is identical across all nine: two drainhole throats, scale
`a = 2`, ADM mass 1 each carried by the lapse, separation 12, box `L = 64`, `N = 128`,
`max_level = 3`, Sommerfeld boundaries, σ = 0.1, `stop_time = 60`.

## How these runs were launched

Every run went through one launcher,
[`grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh`](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh),
from the repository root, on a single node with four H100s. **The binary is never
invoked directly** — AMReX writes `parameters_and_version.txt` into the working
directory with the absolute output paths it was given, and that file reached a commit
that way once. The launcher clones the params template, rewrites its path keys to point
at node-local scratch, `cd`s into the (gitignored) run directory, registers a
`launcher.pid`, and starts the plotfile consumer sidecar beside the evolution.

Two frame sets were used. The first five runs asked for the six evolved fields; the
damping arms added the metric and the derived views, which is also when `h_ij`/`A_ij`
entered the plot list:

```bash
F6="--frames-fields chi K lapse phi Pi Weyl4_Re \
    --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices --frames-auto-zlim"

F12="--frames-fields chi chi_minus_1 K lapse shift1 phi Pi \
     Weyl4_Re Weyl4_Im Weyl4_Mag scalar_activity local_speed \
     --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices --frames-auto-zlim"

L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh
R=runs/wormhole_merger
```

### The four independent runs, one per card

Launched together, detached, 2026-08-31:

```bash
WHM_PARAMS=params_merge_orbit_flip.txt      WHM_NAME=merge_orbit_flip_d12 \
  WHM_GPU=0 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu0.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_headon_flip.txt     WHM_NAME=merge_headon_flip_d12 \
  WHM_GPU=1 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu1.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_orbit_flip_n160.txt WHM_NAME=merge_orbit_flip_d12_n160 \
  WHM_GPU=2 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu2.log 2>&1 < /dev/null &

WHM_PARAMS=params_merge_orbit_flip_p045.txt WHM_NAME=merge_orbit_flip_d12_p045 \
  WHM_GPU=3 WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu3.log 2>&1 < /dev/null &
```

The `ml2` probe is the same orbit template with one knob, and it ran attached:

```bash
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12_ml2 \
  WHM_GPU=2 WHM_MAX_LEVEL=2 WHM_CONSUME_ARGS="$F6" bash $L
```

`WHM_MAX_LEVEL` rewrites `regrid_interval` to match — AMReX aborts if it does not
carry exactly `max_level` values.

### The restart chain

Only `params_merge_orbit_flip.txt` sets `checkpoint_interval` (1000 coarse steps, every
10 code units). The other three templates have it at `-1`, which is why `headon`, `n160`
and `p045` cannot be continued and why the whole damping investigation happens on the
orbit arm. Each restart names its **parent**; the launcher appends `_rNNNNN` itself, so
a continuation gets its own run directory and scratch and never clobbers the parent's
streams:

```bash
# r03000 -- the main arm resumed from the base run's newest checkpoint
CK=$(ls -d /tmp/grteclyn_scratch/merge_orbit_flip_d12/*Chk[0-9]* | sort -V | tail -1)
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 \
  WHM_GPU=0 WHM_RESTART="$CK" WHM_CONSUME_ARGS="$F6" \
  setsid nohup bash $L > $R/detached_gpu0.log 2>&1 < /dev/null &

# r05000 -- damping on, thresholds left at the built-in defaults
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r03000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_r05000.log 2>&1 < /dev/null &

# r04000 -- the wide lapse window, written into the template before launch
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r03000/BinaryWormholeChk04000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_r04000.log 2>&1 < /dev/null &

# sg10 -- same window, dissipation raised; WHM_SIGMA appends _sg10 to the name
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12 WHM_GPU=0 \
  WHM_SIGMA=1.0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r04000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_sg10_r05000.log 2>&1 < /dev/null &

# rw -- the radius window, also a template edit; renamed by hand to keep it apart
WHM_PARAMS=params_merge_orbit_flip.txt WHM_NAME=merge_orbit_flip_d12_rw WHM_GPU=0 \
  WHM_RESTART=/tmp/grteclyn_scratch/merge_orbit_flip_d12_r04000/BinaryWormholeChk05000 \
  WHM_CONSUME_ARGS="$F12" \
  setsid nohup bash $L > $R/detached_gpu0_rw_r05000.log 2>&1 < /dev/null &
```

**The three damping arms differ from each other by edits to the params template, not by
environment variables.** `core_damping_enabled`, the lapse thresholds and the radius
window were written into `params_merge_orbit_flip.txt` between launches, so the template
in git today is the *last* of them. The authoritative record of what each run actually
executed is its own `evolution_params.txt` in this pack — that is the cloned copy, taken
at launch.

### Four things that will cost you a day if you skip them

1. **No `env` prefix.** `setsid nohup env WHM_...=... bash $L` exits 0 in under a second
   and writes a zero-byte log. Variables go *before* the whole `setsid nohup` chain, as
   above.
2. **A printed PID proves nothing.** Four runs launched with a plain `&` from an editor
   session died when the editor restarted, losing 11, 11 and 3 code units on the arms
   that had no checkpoints. Detachment means the launcher is a session leader whose
   parent is init — check it, do not assume it:
   ```bash
   ps -eo pid,ppid,sess,args --no-headers | grep "[r]un_single.sh"
   # each launcher must show ppid = 1 and sess = its own pid
   ```
3. **Decide what to extract before launching.** The consumer deletes each plotfile once
   it has processed it (`--keep-last 3`), so anything not named in `WHM_CONSUME_ARGS`
   is gone with the plotfile. The five runs launched without `h_ij`/`A_ij` in
   `amr.plot_vars` can never be measured by the offline horizon finder — permanently.
   Frames also need `--frames-auto-zlim`: the preset colour ranges are black-hole
   values and wormhole frames come out blank without it.
4. **Dry-run first.** `WHM_DRYRUN=1` resolves the name, template, binary, scratch,
   restart checkpoint and consumer command, prints them, and touches nothing.

Stop a run with the campaign stopper, never by pattern-killing the binary — other
people's jobs share these cards:

```bash
bash grteclyn-wrapper/scripts/campaigns/stop_campaign.sh [--dry-run] runs/wormhole_merger/<run>
```

### After the run

```bash
# the whole close-out, mechanically: live check, scratch report, NaN check of the
# death window, registry check, movies on one fixed colour scale, repack,
# machine-identity grep, and the two edits left by hand (README claim, plan row)
bash research/merger/closeout.sh <run> [<run> ...]

# redraw every cached slice on one fixed colour scale, then stitch the movies
.venv/bin/python grteclyn-wrapper/scripts/plot/rerender_frames.py <run>/frames --movies

# the offline horizon scan (needs h_ij/A_ij in the plotfile)
.venv/bin/python grteclyn-wrapper/scripts/validation/ah_radial_scan.py <plotfile>

# rebuild this pack
bash research/merger/pack_results.sh                  # streams, movies, stills, tables
PACK_HORIZON=1 bash research/merger/pack_results.sh   # and re-run the horizon scan
```

Live frames are scaled per frame, so the colourbar moves; `rerender_frames.py` is what
makes a colour mean the same value in every frame of a movie.

## `campaign/05_binary_spiral/horizon/` — the dissolution measurement

`horizon_dissolution.dat` is the radius of the outermost **fully trapped** coordinate
sphere around the merged core, from an offline scan of the plotfiles:

| t | r_AH | from |
| --- | --- | --- |
| 51.50 | 1.070 | `r04000` |
| 52.00 | 1.050 | `r04000` |
| 52.50 | 1.030 | `r04000` |
| 54.00 | 0.890 | `rw` |
| 54.50 | 0.830 | `rw` |
| 55.00 | 0.590 | `rw` |

Two independent damping schemes, one curve, accelerating toward zero at t ≈ 56. It is a
measurement, not a fit, and it was checked three ways: no NaN or inf cell appears in any
scan box, doubling both the angular and the radial sampling moves every crossing by
≤ 0.01, and the t = 51.5 value matches the in-code diagnostic's ≈ 1.0 at the same step.
Damping cannot be blamed for it — deleting negative-energy matter pushes the energy
budget toward horizon *growth*, not shrinkage.

`ah_radial_scan_output.txt` is the raw scanner output, including the per-ray statistics.
Those show the trapped region is strongly deformed — reaching past r = 2 along the poles
while pinching to ~0.6 at the equator — which is also why a purely radial in-code proxy
loses sight of it.

Regenerate with `PACK_HORIZON=1 bash research/merger/pack_results.sh`, which needs
plotfiles that the consumer sidecar deletes as a run proceeds; only the last few of each
arm still exist. Without that flag the committed copy is left alone.

## Reading these files without being fooled

- **The last row of a dead run is the crash, not the spacetime.** `max|K|` of 3648 and an
  L2 Hamiltonian of 4.4 in the `rw` arm are the NaN arriving. `summary.md` quotes the row
  half a unit earlier for exactly this reason; do the same.
- **Separation can glitch to ~0 for a single row.** When the throats swap sides both
  finders can latch onto the same one; `p045` reads 0.06 at t = 38.46 between neighbours
  of 4.06. Its true closest approach is 3.95 at t = 40, and both trackers agree on it.
  `make_summary.py` drops rows that disagree with both neighbours by more than half.
- **The θ/AH columns (13–18) of every `binary_throat_diagnostics.dat` in this pack are
  tainted.** All were written by the pre-2026-09-01 scan, which assumed a conformally
  flat metric; wherever one scan sphere encloses two wells it produces false trapped
  verdicts — the t ≈ 30 "fusion" on the merger arms, and continuous trapping out to
  r = 6.2 over t ≈ 42–60 in `p045`, a run with no collapse anywhere. Trust only the
  offline scan (`campaign/05_binary_spiral/horizon/`), which needs `h_ij` and `A_ij` in the plotfiles: only
  `r04000`, `rw` and `sg10` were launched with them, so the undamped main arm can never
  be checked this way. That is permanent. The in-code scan computes the full-metric
  expansion since 2026-09-01; streams written after that date are trustworthy.
- **Waveforms across a restart.** The interior of a restart restores exactly; the outer
  boundary does not, and the error walks inward at roughly the speed of light. Do not
  read `psi4` at R = 30 across a restart boundary without allowing for it.
- **The first ~5 time units are gauge settling.** Nothing measured there means what it
  appears to mean.
