# GPU plan for the paper runs

*Drafted 2026-09-02, while wave 8 (fill100 / fillwide100 / late6) was still on the
cards.  Companion to `Plan.md`, which holds the campaign record; this file holds
the design for the production data that goes into the article.*

Everything here is a **proposal** — no run in this file starts until it is
approved and launched by hand, one at a time, through `run_single.sh`.

*Revised 2026-09-02 after an external review of the plan.  Every claim in that
review was checked against Plan.md, Reference.md and the tree before anything
changed; the corrections are marked in place, and §8 records what survived,
what did not, and the comparison arms it added.*

---

## 0. The plan at a glance

**In hand**
- [x] The three headline results, measured and validated (§1)
- [x] Scout ladder relaunched at N = 128 after the N = 64 NaN (§2)
- [x] Scalar-mode extraction module `--scalar-modes`, validated three ways (§7 leg 1)
- [x] Freeze-artifact test on the ringdown period — fill vs fillwide, ~2 % (§3)
- [x] External review absorbed: §4 ladder corrected, causal budget stated (§7), comparison arms added (§8)

**In flight**
- [ ] Wave 8 drains to t = 100 (~93.6 as of this revision) → close-out: second peak at R = 30 near t ≈ 93; R = 30 tail past ceiling 84.5
- [ ] Scouts → capture boundary **+ the fuse audit** (§2).  Status 2026-09-03: **p020 CAPTURED** (crossed p012's sep-2.0 fusion mark at t ≈ 33.5, reached 1.08) but **froze** at sep 1.08 before fusing (stopped t = 47.8); **p025 captured-then-died** (reached sep 1.5, froze, h11 NaN at t = 52.98); **p035 fly-by** (min sep 2.746 at t = 42.4, receding to 4.0 when stopped at t = 73.9); p045 fly-by (§2).  Boundary sits between p = 0.25 and 0.35 (50–70 % of circular).  **No completed merger at any p ≠ 0.12 yet** — every capture above p012 hits the freeze first; the max_level = 5 reruns of p020/p025 (in flight) are the live test of whether depth clears it. **[Validation 2026-09-03, §9: p020 was NOT frozen — it was ~4 time units behind p012's own slow phase when stopped; p025 died of the known t ≈ 53 level-3 h11 wall with no fill armed; and the L5 arms' lapse diagnostics do not see the collapse site at all. "No completed merger at p ≠ 0.12" is untested, not established.]**  NOTE for mode extraction: those two L5 arms were launched from the scan template, which has **no in-code Weyl4 streams** — only the consumer psi4 at plot cadence (0.5 u).  Whatever p is chosen for the production waveform must be relaunched from a template with in-code extraction ON.
- [x] **Helfer twin pair — RESOLVED 2026-09-03, and the answer is the wrong way round: the correction is REJECTED for production.**  `merge_twin_p012_{helfer,plain}_t100`, identical but for the one flag.  **Plain merged** — retraced the p = 0.12 record (sep 2.06 at t = 32.00 vs the original's 2.0 at 32) and closed to **sep 0.81 by t = 44** before being stopped.  **Helfer stalled** — orbit died at sep ≈ 4.7 by t ≈ 30 (7° of orbit swept over t = 26–34 vs plain's 35°), cores collapsed to the 1e-10 lapse floor by t ≈ 55, then ran as a zombie (frozen, no NaN) to t = 60.3.  A **max_level = 4 rerun reproduces the stall to < 2 % in the lapse trace at every epoch** (1.45e-3/1.46e-3 at t = 34 … 3.84e-5/3.81e-5 at t = 47), so at production-class depth the freeze is *converged*, not under-resolution. **[Validation 2026-09-03, §9: the cores never collapsed — the throat pits keep lapse 0.07–0.20 and |φ| ≈ 0.9 to t = 60; what hit the floor is a growing blob at the inter-throat MIDPOINT (φ = 0 by symmetry, K > 0). The stall verdict stands; the stated mechanism does not.]**  Validated three ways: both twins' `binary_throat_diagnostics.dat` (independent streams), the L4 rerun's `.dat`, and the φ frames — helfer's matter swells into static ~8-unit lobes while plain's stays compact and orbits.  **Production arms therefore run plain superposition**; the known +9.5 % initial-size artefact is the price of an evolution that actually evolves.  One escape hatch is still in flight: `merge_twin_p012_helfer_lvl5_t100` (max_level 5 = the production finest dx) had cores 7× shallower than L3/L4 at t = 27 — if it demonstrably merges, the correction may be re-admitted at level 5 only; verdict due at its twin's stall epoch t ≈ 34.

**Decisions from the validation pass (§9), 2026-09-03 — run in order, one card at a time**
- [ ] **1. p020 at level 3, unmasked, to the wall** — first launched 2026-09-03 with the p012 production fill armed at t = 53; **stopped at t = 2.7 and withdrawn**: p020's merger time is unknown, so a fixed-time fill can freeze the throats mid-approach and hide the merger (the fill was tuned to p012, whose throats had already met at t = 48–51).  Relaunch as `merge_orbit_flip_d12_p020_nofill_t060` (`launch_p020_nofill.sh 0`): plain-twin template with p = 0.20, damping off, **no fill**, in-code Weyl4 streams, checkpoints every 10 units.  9.5 u/h → the wall (t ≈ 53) in ~5.5 h.  The question it answers: where are the throats when the wall hits — met (as p012 at 48–51) or still apart.  Only then, if they met, arm the fill from Chk05000 at a time *after* the meeting, the way p012 was done.  Doubles as the p020 damping-off control against `merge_orbit_flip_d12_p020_t200`.
- [ ] **2. Plain p012 twin with damping off to t = 50** — cannot start cleanly from a checkpoint: only Chk04000 (t = 40) survived the prune and the damping had been active since t = 30.35.  From scratch ~5 h.  Deferred: decision 1 answers the same question for p020 at no extra cost.
- [x] **3. Helfer at level 3 with the window halved** (`wormhole_helfer_width = 2.0`; the auto width is d/3 = 4.0) — an initial-data change, so it must start at t = 0; no checkpoint can seed it.  Launched 2026-09-03 on GPU 1 as `merge_twin_p012_helfer_w2_t060` (no checkpoints, ~6.5 h to t = 60): verdict at t ≈ 32 — sep < 3 means it tracks plain (window placement was the problem, correction re-admitted); sep > 4.5 means the correction itself is dead.
- [ ] **4. The level-5 arms** — corrected reading 2026-09-03: `p020_lvl5` and `p025_lvl5` carry no fill, so they are *unmasked* runs whose wall is pushed to t ≈ 55 by resolution (m4e ladder: L5 died 54.8, L6 56.1/56.7, L7 56.2).  They are the highest-resolution look at where the throats are when the wall hits, ~11 h from this revision; keep them.  Their in-code lapse diagnostics stay blind to the midpoint until sep < 2.5, but the half-space throat positions are valid (the finest blocks contain the pits) and the orbit agrees with L3 to 2 % through t = 29.  `helfer_lvl5` was stopped 2026-09-03 at t = 31.5 (stalled at sep 5.3 like L3/L4, nothing left to learn) and its scratch (43 GB: Chk03000 + plotfiles) was removed at user request — it cannot be resumed; GPU 1 now runs the w2 test.

**Cheap, next, no GPU conflict (each still needs one by-hand approval)**
- [x] Re-run initial-data check E on the production drainhole template — **done 2026-09-02, §3**: d/b = 6 is not a cliff (1.58× the d/b = 8 defect), but the defect never falls below the floor, so the Helfer/Ning correction is now indicated
- [ ] L = 128 / N = 256 smoke test, t = 5: memory + speed (§3)
- [ ] Switch on in-code Weyl extraction in the production templates — params-only (§3)
- [ ] BBH vacuum control, same masses and momenta (§8.1)

**Blocked on §6 decisions**
- [ ] Production arms at L = 128: headline + seam twin + third-fill-radius arm + level-6 twin (§4, §7)
- [ ] Head-on freeze arm (§8.2); N = 192 wave-zone twin (§8.4); +150 tail (§6.5)
- [ ] Repulsion a-scan with the scalar-charge prediction attached (§8.7)

**Analysis once the data lands (§5 phase 3)**
- [ ] 4-radius extrapolation in retarded time; energy/mass balance (§8.3); remnant-mass QNM discriminator (§8.5); dissolution re-measured on the undamped arm (§8.6); frames re-rendered (issue 17); pack + push

---

## 1. What the paper already has

Three results are in hand and validated; the production runs exist to make them
publication-grade, not to discover them.

| Result | Status | Where recorded |
|---|---|---|
| **Like-oriented throats repel** — 5× gravity at a=2, m=1, and the push scales with throat *width*, not mass; pull/push ratio 1.50 measured vs 6/4 predicted | Measured on three control arms, 2026-08-31 | params header of the merger IVP; Plan.md Stage 2.6 |
| **Opposite-oriented throats attract and merge** — gravity-driven (drainhole mass in the lapse), collapse at t ≈ 45, common horizon | Both freeze arms completed t = 80 | Plan.md M6/M7, results pack |
| **The interior freeze survives the merger** and the recorded signal is a genuine gravitational wave (speed, 1/R falloff, static-offset, not-freeze-junk checks) | Closed 2026-09-02 | Plan.md, "Is the recorded signal a genuine gravitational wave?" |

The freeze method's own validation is also paper material — it is the method
section.  Stated precisely (an earlier draft of this line conflated two
different comparisons): the two seam-radius twins agree to 5 digits at every
shared waveform sample (0.000 %); the frozen arm is bit-identical to its
*unfrozen* twin everywhere beyond r = 6 at t = 55 (that is where "outside
r = 6" belongs — issue 17); the late-engagement control (freeze at 55.5
instead of 53, finer grid) moves the R = 14 window ≤ 0.003 % (m = 2) /
0.022 % (m = 0); and constraints stay flat for 27 time units post-freeze.

---

## 2. The IVP question: how much orbit do we want?

**Where we are.**  The current IVP is d = 12, tangential momenta ±0.12,
opposite orientation.  A Newtonian estimate with the measured 6× coupling says
a *circular* orbit at d = 12 needs p ≈ 0.5 per body (and the period would be
~75 time units).  At p = 0.12 we are at 24% of circular — which is why the
trajectory is a bent plunge, not a spiral.

**The tension.**  More tangential momentum buys a visually and physically
richer inspiral (an l=2, m=2 chirp instead of a near-head-on burst), but past
some threshold the pair does not merge — the observed behaviour is expansion.
The Newtonian escape speed at d = 12 is ~0.7, so somewhere in p ≈ 0.45–0.7 the
capture boundary should sit; below it, eccentric capture with one or two
decaying orbits, then plunge.

**Is the low-p data bad for the paper?**  No — it is the clean baseline: the
first controlled wormhole–anti-wormhole merger does not need an inspiral to be
a result.  But an eccentric-capture arm alongside it is much stronger, and the
capture boundary itself (merge vs escape as a function of p) is a figure no
one has published.  The scan *is* paper content, not just tuning.

**Revised 2026-09-02 — the archive already held the key data point.**  A
p = 0.45 arm ran on 2026-08-31 (`merge_orbit_flip_d12_p045`): separation fell
12 → 3.95 by t = 40, swung back out to 4.61 by t = 60 — and the run *stopped
there*, mid-orbit, on the outbound leg.  Since 0.45 is 90% of circular
momentum for the 6× pull, that is a bound eccentric orbit cut off after one
periapsis, not an observed escape.  The run wrote no checkpoints
(checkpoint_interval = -1), so it cannot be continued — the decisive part,
t > 60, has to be re-simulated from t = 0.

**The ladder as launched** — max_level 3, the campaign's own proven
orbit-phase configuration (levels 4–5 were always added on restart near
collapse; scouts classify trajectories, so no extra refinement):

| Scout | p | Status / expectation |
|---|---|---|
| S1 | 0.12 | plunge, merges at 44.9 — in hand, re-used |
| S2 | 0.25 | **LIVE 2026-09-02**, sharing card 3 — bent plunge, maybe a half orbit |
| S3 | 0.35 | **LIVE 2026-09-02**, sharing card 3 — eccentric-capture candidate |
| S4 | 0.45 | **LIVE 2026-09-02**, solo on card 2 — **fly-by through t = 84**, see the verdict block below; still waiting on the return leg |
| S5 | 0.55 | optional, above circular (0.50) — only if the boundary needs bracketing from above |

All scouts: L = 64, **N = 128 (dx = 0.5)**, max_level 3, stop_time 200,
checkpoints every 10 time units with `checkpoint_keep = 3` — pruned to the
last three, and any arm extends by restart (the p045 lesson).  An N = 64
(dx = 1) economy attempt was tried first and is **dead**: all three arms
NaN'd in h11 on level 3 at t ≈ 7–8, independent of p — a throat resolved by
only 16 cells does not survive, so dx = 0.5 is the floor even for scouts.
At N = 128 expect ~10–12 u/h solo (~20 h worst case to t = 200) and roughly
half that for two arms sharing a card; a merger ends the run sooner.
Templates live in `runs/wormhole_merger/templates_scan/`; each launch
is one by-hand invocation of `launch_capture_scan.sh <p> <gpu>`.

**S4 = p 0.45, verdict through t = 84 (2026-09-02, frames + matter check; theta columns junk).**
A fly-by, not a merger: separation fell 12 → **3.95 at t = 40** (glitch-cleaned;
the tracker's momentary sub-1 spikes near the split plane are attribution
failures, not physics), and has climbed monotonically since (6.30 at t = 89).  What the encounter did to the throats:

- **They survive.**  φ still holds two clean lobes at ±0.88 against ±0.90 at
  t = 0 (−2.5 % over 84 u), and on a log colour scale both χ wells are present
  throughout — shallower (min χ per half-space **rose** 3.5e-7 → 7.6e-4) and
  broader, i.e. relaxed, not collapsed and not dissolved.  The huge black disc
  in the linear-scale frames is a colour artefact: the ejecta stretch the
  auto colour range to χ ≈ 9, so everything under ~0.5 renders black.
- **The encounter ejected phantom shells.**  Two χ > 1 crescents (peak ≈ 9 —
  *less* volume than flat space, the negative-energy signature) spiral
  outward; Pi went 0 → ±0.5.  The cores deflected a quarter-turn.
- **Why no collapse:** the perturbation was a transient *stretch* (mutual
  gravity + opposite-sign scalar attraction pull each throat toward the
  companion), passing in ~10 u — the Shinkai-Hayward collapse branch wants a
  sustained squeeze, which only a capture delivers.  Contrast the p = 0.12
  plunge: throats settle on top of each other → genuine trapped surface.
- **The lapse is not evidence:** α fell to ~2e-5 across the whole central
  band (slicing response, gauge).  And this run predates the 2026-09-01 theta
  fix, so its `theta_common`/`ah_r_common` columns carry the DOCUMENTED false
  positive of the conformally-flat scan (BinaryThroatDiagnostics.hpp history
  note names this exact run and window, t = 42.3–60) — a "common horizon at
  t = 43.3" read from that column is an artefact, twice fallen for now.
  Trajectory + matter + log-χ frames are the believable instruments here.
- Movies: 12 fields under `merge_orbit_flip_d12_p045_t200/movies/`.
- **Paper figures** (git-tracked, `results/merger/figures/`):
  [separation + χ-well](../../results/merger/figures/p045_flyby_separation.png) ·
  [log-χ trio, throats present throughout](../../results/merger/figures/p045_flyby_logchi.png) ·
  [linear-χ sequence t = 0/43/60/84](../../results/merger/figures/p045_flyby_chi_linear.png) ·
  [φ launch vs t = 84](../../results/merger/figures/p045_flyby_phi.png) ·
  [lapse t = 84](../../results/merger/figures/p045_flyby_lapse_t84.png) ·
  [|Ψ₄| t = 60](../../results/merger/figures/p045_flyby_weyl4mag_t60.png).
- Open: 0.45 is 90 % of circular momentum, so the orbit should be bound —
  whether the receding leg turns around before t = 200, and whether the
  post-encounter ringing tips a throat later, is what the rest of the run is
  for.  HOW validated: separation/φ/χ numbers from
  `binary_throat_diagnostics.dat` + `collapse_diagnostics.dat`, cross-checked
  visually against linear and log-scale renders of the cached slices — two
  independent sources per claim.

Caveat: higher p delays collapse by roughly the orbital time — expect
t_collapse ≈ 120–170 for the spiral arm, not 45.  Production stop_time must be
set per-IVP as **t_collapse (from the scout) + 100** (or + 150 if §6.5 is
taken).

**The fuse audit — a scout does not qualify its p by trajectory alone
(added 2026-09-02).**  Plan.md's standing caveat is that the single-throat
growing mode is still growing at t = 40: the 40 M window is a fuse, not
stability.  The Stage 1 record (in git history; the live docs compress it)
says the growing quantity is the L2 momentum-constraint norm, early e-fold
≈ 4.4 ≈ throat/c, and it *steepens* after t ≈ 34 — doubling every ~1.6 —
which no single exponential explains.  The spiral IVP plans 120–170 units
of orbit before collapse: three to four fuses deep.  So every scout gets a
throat-integrity audit through the orbit — min χ at each throat and the
throat's size, read from the **slice cache, never the tracker** (the tracker
under-reads speeds up to ~4×, issue 6) — plus the constraint norms, and a p
qualifies only if **both throats are still throats at periapsis**.  If they
are not, a production arm at that p would record two already-runaway objects
colliding, and the paper's headline IVP is the plunge.

**Periapsis overlap.**  The p = 0.45 swing-back bottomed at separation 3.95
with throat width a = 2 — the scalar profiles interpenetrate at closest
approach, and "bound eccentric orbit" is Newtonian point-particle intuition
applied exactly where it breaks.  The scout decides; the spiral is not
written into the schedule as the likely headline until it merges *and*
passes the fuse audit.

**Repulsion side-figure (cheap).**  One or two extra throat-width points
(a = 1.5, a = 3 at rest, level 3–4, t ≈ 20, measure the initial acceleration)
turn the three existing control arms into a power-law figure for the
width-scaling claim.  Hours, not days.

---

## 3. Grid design for correct GW extraction

**Current geometry, for the record.**  L = 64 (domain 64³, centre at 32),
**N = 128** base cells — so base dx = 0.5, and max_level 5 puts finest
dx = 1/64 on the throats.  (The plots that "only show 32" are zoomed: the
slice cache stores the central 32-wide window, r ≤ 16 from centre, to keep the
cache small.  The domain is genuinely 64.)

**What is wrong with it for a paper waveform:**
1. The outer detector R = 30 sits *inside* the sponge (24 → 32), soaking ~13×
   base dissipation (Plan.md issue 15).  Amplitude there is timing-grade only.
2. Two radii is not enough for an R → ∞ extrapolation; standard practice is
   4–6.
3. Waveform sampling is 0.5 time units (plot_interval 50) — coarse enough that
   a careless fit aliased (the QNM comb incident).

**Proposal: L = 128, N = 256 — same dx, twice the room.**

- Base dx stays 0.5; N = 256 is not "more resolution", it is the same
  resolution with the boundary pushed out.  (A "1/dx² initial-data noise"
  justification used to live here and is **withdrawn 2026-09-02** — the n160
  arm's own t = 0 row refutes it: refining the base 128³ → 160³ *lowered*
  L2_Ham by 15 % and halved L2_Mom, where 1/dx² predicts a 1.56× rise.  The
  claim was a fossil of the puncture era — the archive notes even say "more
  refinement helps here, opposite to puncture data".  Relatedly,
  Reference.md's "t = 0 violation identical to six digits at max_level 4 and
  5" is an artefact of the diagnostic: L2_Ham is computed over level 0 only,
  and level-0 data is analytic, so the number is max_level-independent by
  construction — bit-identical across ml2…ml5 in the archive.  The widening
  case stands on the sponge and the radii alone, and needs nothing else.)
- Sponge moves to 48 → 64 (radius from centre).  Extraction spheres at
  **R = 20, 28, 36, 44** — four radii, all in clean, un-sponged vacuum, wave
  zone resolved with ~30 base points per dominant wavelength (~15 units).
- **Waveform sampling: switch on the in-code extraction — params-only
  (revised 2026-09-02, replaces "halve plot_interval").**  GRTeclyn's
  `WeylExtraction` is already wired into the merger example
  (`BinaryWormholeLevel.cpp:765`) and has sat at `activate_extraction = 0` in
  every template to date.  Enabled, it integrates r·Ψ₄ modes on the
  extraction spheres **every coarse timestep** (dt = 0.01 — 50× finer than
  plotfile sampling; the QNM-comb class of aliasing error dies here) and
  writes its own `Weyl4_mode_lm.dat` stream.  Production templates set:
  `activate_extraction = 1`, `extraction_radii = 20 28 36 44`,
  `extraction_levels = 0 0 0 0`, `num_points_phi/theta` ≥ 24/37, and modes
  through **l = 4, all m** listed explicitly (the spiral would be
  (2,±2)/(3,±3)/(2,±1) dominated; the legacy parameter path validates
  nothing, so list every pair).  Working reference config:
  `Examples/RotatingWormholeCollapse/params_rotating_grtresna_exotic.txt:83-95`.
  Plotfiles stay at plot_interval 50 for frames and the consumer streams —
  which also makes the consumer-side Ψ₄ an *independent cross-check* of the
  in-code stream, the two-source validation rule for free.
- **In-code extraction: two bugs found and fixed before first use (2026-09-02).**
  The stream was junk on matter runs — NaN rows and O(0.4) plateaus on
  ~55 % of sphere points, clustered within 2 cells of internal grid-box
  faces.  (a) `ParticleInterpolator` allocated 2 ghost cells but the
  4th-order Lagrange stencil reaches 3 when the centre rounds into the
  first ghost layer — out-of-bounds GPU reads (`s_num_ghosts = order/2 + 1`).
  (b) The matter-sector derived functions (`Weyl4WithMatter`,
  `ConstraintsWithMatter`, `EMTensor`) called `amrex::ParallelFor(out_mf, …)`
  without the ghost argument, so when `derive(…, ngrow=3)` feeds the
  interpolator, the derived MultiFab's ghost cells were **never computed**
  and held stale arena memory.  The vacuum `Weyl4` passes
  `out_mf.nGrowVect()`; the matter variants didn't — which is why every
  upstream (vacuum BBH) test passes while every matter extraction is junk,
  and why plotfiles (derived with ngrow = 0) always looked clean.
  Validated two ways: a printf inside the interpolation kernel counted
  3 083–3 323 garbage stencil reads per 15-step window before the fix and
  the mechanism is gone after; and a point-by-point comparison of the fixed
  extraction stream against the same-step plotfile via the consumer pipeline
  (1 776 sphere points) — 0 plateaus, 0 NaN, the only residual disagreements
  are the poles and 4 zero-crossings where nearest-cell plotfile sampling
  itself is the cruder method (quadrant-average and neighbour-range checks
  confirm the in-code value).  Fix is 4 files; the code-only subset (3 files
  — EMTensor was independently fixed on upstream main) is submitted upstream
  from the `fix/derived-ghost-cells` fork branch.
  **Extraction-key templates are unblocked.**
- **Mode integration validated too (2026-09-02) — the in-code stream is now
  the primary waveform instrument.**  Second rung of the chain: an
  independent Simpson quadrature of the raw sphere points against the
  spin-weight −2 (2,2) harmonic reproduces `Weyl4_mode_22.dat` to **1e-8
  relative at both radii** — the print-precision floor of the .dat file,
  i.e. exact.  (Trapezoid lands at 1e-3–6e-3, so the in-code integrator is
  Simpson-consistent, not trapezoid.)  With point values verified against
  plotfiles and the harmonic integrals verified against independent
  quadrature, the in-code extraction is validated end-to-end and supersedes
  the consumer Ψ₄ for waveforms: 50× finer time sampling (every coarse step,
  dt = 0.01) and 4th-order interpolation vs the consumer's nearest-cell
  plotfile reads (demonstrably cruder at the sphere poles and at sign
  crossings).  The consumer Ψ₄ is **demoted to cross-check**, not deleted —
  plotfiles stay at interval 50, so every production arm still gets the
  two-source comparison for free, and the wrapper keeps its exclusive jobs
  (frames, scalar modes, kinematic flux).  Verification record:
  `runs/wormhole_merger/merger_fix/m9b_weyldiag10_r09000` (kept; the other
  diag runs and their scratch plotfiles are deleted).
- Consumer-side radii remain a free post-processing choice; every production
  launch adds `--scalar-modes` to `WHM_CONSUME_ARGS` so each arm records the
  scalar l ≤ 2 modes and the kinematic flux on the same spheres (§7 leg 1).
- **Ψ₄ in a non-vacuum exterior — name it, then defend it.**  |φ| ~ 6e-3 at
  R = 14 with a 1/r tail means no extraction sphere we can afford is in
  vacuum.  Defences to quote: the measured 1/R amplitude falloff, and — new
  with the scalar-modes stream — the ratio of scalar kinematic flux to GW
  flux at each radius.  If that ratio is small and falls with R, extraction
  stands on measurement, not assumption.
- stop_time per §2: baseline arm ~150, spiral arm t_collapse + 100 (~250).
  Long enough for the signal, the second peak, and the tail to clear R = 44.

**Re-run the initial-data gate on the production template (cheap, before
phase 2 — added 2026-09-02).**  The Phase 1 gate "run at d/b ≥ 8" was
measured on the massless Ellis–Bronnikov branch at b = 1 (Reference.md
check E, max_steps = 0 jobs).  The production IVP is b = 2 at d = 12 —
**d/b = 6, 25 % inside a gate the docs twice call "still binds"** — and the
gate has never been re-run on the drainhole branch.  Check E costs minutes:
re-run the defect ladder (d = 8, 12, 16, 24 at b = 2, plus the single-throat
zero control) on the production drainhole template before committing phase 2.
Two traps for the re-run: the check-F-style angular mean cancels on the
flipped binary (the dipole trap below) — read the defect from the constraint
norms and the l = 1 scalar mode instead; and the original ladder found the
defect below the discretisation floor for d/b ≥ 8, so the interesting number
is precisely where d/b = 6 sits relative to that floor.  Related, worth one
line in the method section either way: the two-throat data is plain
superposition with **no Helfer/Ning one-body conformal correction** (known
inconsistency 2) — the literature says exactly this correction suppresses
spurious squeeze/pulsation in horizonless objects, and our central
unexplained event is a collapse.  The check-E re-run bounds the defect the
correction would remove; implementing the correction itself is initial-data
level and cheap if the bound comes back non-negligible.

**Check E re-run — RESULT (2026-09-02, drainhole branch, b = 2).**  18 jobs,
L = 64, `max_level = 0`, initial data only, ladder N = 192 / 288 / 384 at
each separation; defect `A` from the `L2_Ham(N) = A + B·N^-p` fit.

> **First, the diagnostic had to be repaired.**  The whole-domain `L2_Ham`
> in `constraint_norms.dat` *rises* with resolution — even for the single
> throat, which is an **exact** solution and must converge.  Cause, measured
> from the t = 0 constraint field: **93.7 % (N = 192) → 99.98 % (N = 384) of
> the total Ham² lives in the outermost 2 cells**, the layer whose stencils
> read boundary ghosts; widening the excluded layer to 3, 4, 6 or 10 cells
> changes nothing, so it is exactly the ghost layer and not a corner-volume
> effect.  Drop those 2 cells and the exact throat converges at **4th order**
> (3.89) to `A = 8e-7`, i.e. zero — the method validates itself.  **The
> in-code whole-domain `L2_Ham` is unusable for convergence or defect work**;
> any past claim resting on it needs re-reading (this is a *second*,
> more serious artefact than the level-0-only one noted above).

| ladder | N=192 | N=288 | N=384 | **A (defect)** | vs error bar |
| --- | --- | --- | --- | --- | --- |
| single throat (exact — zero control) | 3.64e-4 | 7.57e-5 | 2.52e-5 | **8e-7** ≈ 0 | — |
| d = 8  (d/b = 4) | 6.37e-4 | 5.02e-4 | 4.93e-4 | **4.92e-4** | 603× |
| d = 12 (d/b = 6) **production** | 5.22e-4 | 3.03e-4 | 2.89e-4 | **2.87e-4** | 352× |
| d = 16 (d/b = 8) *old gate* | 4.89e-4 | 2.07e-4 | 1.86e-4 | **1.82e-4** | 223× |
| d = 24 (d/b = 12) | 4.81e-4 | 1.34e-4 | 9.70e-5 | **8.61e-5** | 106× |
| d = 12 + BY momenta p = 0.35 | 5.25e-4 | 3.08e-4 | 2.95e-4 | **2.92e-4** | 359× |

- **d/b = 6 is not a cliff.**  The production separation costs **1.58×** the
  old gate's d/b = 8 defect, and d/b = 4 only 2.70× — a smooth `A ~ d^-1.6`
  power law with no threshold anywhere in 4 ≤ d/b ≤ 12.  The Phase 1 gate
  "run at d/b ≥ 8" was inherited from the massless b = 1 EB branch, where
  d/b = 4 was an *order of magnitude* worse; **the drainhole branch is far
  more forgiving, and d = 12 needs no apology.**
- **But the defect never hides under the floor.**  Unlike the b = 1 branch
  (where d/b ≥ 8 sat below the discretisation floor and d = 8 / d = 16 were
  indistinguishable), here every separation is 100–600× the error bar and
  cleanly ordered.  The d/b = 6 defect exceeds the code's own discretisation
  error for any grid finer than **dx ≈ 0.31**; the production base grid is
  dx = 0.5, but its refined levels reach dx = 0.0625, so **over the region
  that actually resolves the throats the superposition defect — not
  truncation — is the dominant t = 0 error, and refining does not remove it.**
- **Bowen–York momenta add 1.9 %** at d = 12 — the tangential boost is not a
  meaningful extra defect source, so the orbit parameters are exonerated.
- **Decision, per this section's own rule: the bound came back
  non-negligible, so the Helfer/Ning one-body conformal correction is now
  indicated** (known inconsistency 2).  It is the one thing that would
  actually lower the number, and the literature attributes exactly the
  spurious squeeze/pulsation we see in a horizonless object to its absence.
- *Validated two ways.*  The primary metric (drop the 2-cell ghost layer) and
  a completely independent volume restriction (`r < 24`, inside the sponge)
  give **identical** ratios — 1.58, 2.70, +1.9 %, `d^-1.6` — on different
  cell sets.  Caveat kept honest: `A` is an unnormalised RMS, so the
  *relative* statements above are solid while "how big is 2.9e-4 physically"
  needs `Ham / Ham_abs_terms`, which this pass did not record.
- *Trap for the next person:* setting `amr.derive_plot_vars = constraints`
  aborts the run unless `G_Newton` is defined in the params — the derived
  path does a hard `pp.get` with no default, while the in-code norm hardcodes
  1.0.  Templates: `params_checkE*_<tag>_n<N>.txt`; runs under
  `runs/wormhole_merger/checkE/` (plotfiles deleted, `.dat` streams kept).

**Helfer/Ning one-body correction — IMPLEMENTED AND MEASURED (2026-09-02).**
Step (iii) of the background.md route is in the code as
`wormhole_helfer_correction` (default **0 = off**; also
`wormhole_helfer_width`, `wormhole_helfer_power`).  It removes the constants
the companion leaves at each throat's centre — Helfer Eq. 45,
`γ_ij = γ_ij^A + γ_ij^B − γ_ij^B(x_A)` — windowed onto each body with
`W = exp[−(r/w)^p]` so spatial infinity, and with it asymptotic flatness and
the Sommerfeld boundary condition, never sees the subtraction.

> **What the artefact actually is, measured.**  Expand the plain superposition
> about throat A: the companion hands it two constants, `dpsi = 3.47e-3` and
> `du = −0.0834`.  `du` is the dominant one by 24×.  Together they rescale
> throat A's spatial metric by `e^{−2du}(1+dpsi/psi_A)^4`, so the throat
> starts **+8.1 % (away) / +10.9 % (toward)** larger in areal radius than the
> static solution its own field equations support — it is not in equilibrium,
> and it rings.  That is exactly the failure Helfer et al. diagnose, and the
> reason they call it worse for horizonless objects.

**The correction works, and it is not free.**  Both halves were measured at
`a = 2, m = 1, d = 12, N = 192`, throat size from the analytic areal radius
(isolated = 3.88955), `L2_Ham` on the repaired 2-cell-excluded metric:

| window `w / p` | throat size error | `L2_Ham` | vs plain |
|---|---|---|---|
| plain superposition | +8.1 % / +10.9 % | 5.22e-4 | 1.00× |
| `0.4d / 6` (literal Eq. 45) | −1.1 % / +1.5 % | 4.71e-3 | 9.02× |
| `0.5d / 3` | −0.9 % / +1.6 % | 1.75e-3 | 3.36× |
| **`d/3 / 2` (the default)** | **+0.2 % / +2.8 %** | **9.60e-4** | **1.84×** |
| `d/4 / 2` | +1.1 % / +3.7 % | 8.68e-4 | 1.66× |
| `d/6 / 2` | +3.1 % / +5.6 % | 7.97e-4 | 1.53× |

- *The window is the whole engineering problem.*  A window that switches off
  over a length `w` has curvature `~1/w²`, and the Hamiltonian constraint sees
  that curvature times the constant being removed.  So the correction repairs
  the size by adding a defect of its own.  The default is the knee: **84 % of
  the spurious inflation removed for 1.8×**, where insisting on the last 16 %
  costs 9×.
- *Both columns are continuum properties.*  The corrected defect moves 1.5 %
  between N = 192 and N = 384 (d = 12: 4.71e-3 → 4.61e-3 at the old default),
  i.e. it does not converge away — same character as the superposition defect
  it trades against.  Full corrected ladder, all four separations × three
  resolutions, recorded alongside the plain ladder.
- *Regression, verified two ways.*  With the flag **off** the new binary
  reproduces the pre-change baseline **bit for bit** — d = 12, N = 192 gives
  `5.218469e-04 / 1.074869e-03 / 2.620791e-03`, all three columns identical to
  the 2026-09-02 plain run.  And the auto default reproduces the explicit
  `w = 4, p = 2` run to all seven digits (`9.602813e-04`), confirming
  `w_auto = d/3` is wired as documented.

**WHICH COLUMN MATTERS IS NOT SETTLED, AND THIS PASS CANNOT SETTLE IT.**
Helfer et al.'s claim is about **dynamics** — a body that starts the wrong size
rings, and the ringing is what destroys horizonless objects — not about the
initial constraint norm, which their fix also worsens.  Nothing above is
evidence either way about the collapse.  **The decisive test is an evolution:**
one arm with `wormhole_helfer_correction = 1` against the matched plain twin,
same everything else, watching the throat-radius oscillation and the collapse
time.  If the correction is what the literature claims, the corrected arm
should ring less and survive longer *despite* starting with 1.8× the
constraint violation.  Until that run exists, the honest statement is: this
flag trades a measured 9.5 % error in each throat's initial size for a
measured 1.8× increase in the initial Hamiltonian violation.

- *Whether it lets us drop the core freeze* is the same open question in
  different words, and the same run answers it.  Do not assume it does — the
  Ellis drainhole throat has its own linear instability, and if the collapse
  is physical no initial-data fix removes it.
- **ANSWERED 2026-09-03 (the twin ran — see the In-flight close-out above):
  the correction makes the dynamics WORSE at level 3/4, not better.**  The
  corrected arm did not ring less and survive longer; its cores collapsed
  *faster* (6× deeper in lapse at matched t ≈ 28), its orbit stalled at
  sep ≈ 4.7, and the whole system froze — while the plain twin, spurious
  +9.5 % size artefact and all, sailed through its merger.  The prediction
  quoted above is falsified at those depths, and the L3 = L4 lapse-trace
  agreement (< 2 %) says this is converged behaviour, not resolution error.
  The correction stays in the code, default off, and out of the production
  configuration; only a demonstrated level-5 merger of the still-running
  `helfer_lvl5` arm could re-admit it, and then only at level-5 cost
  (measured 5× wall-clock). **[Validation 2026-09-03, §9: "cores collapsed faster" should read "the inter-throat lapse collapse nucleates 5 units earlier (3e-2 at t = 25.4 vs 30.4)"; the `helfer_lvl5` arm cannot re-admit anything while its finest-level-only diagnostics exclude the midpoint (sep > 2.5).]**
- *Operational note:* N = 384 no longer fits one H100 with the constraints
  derive on (79 GB arena, OOM).  `run_single.sh` now takes `WHM_RANKS=2`
  with `WHM_GPU=0,1` and binds each rank to its own card inside the rank, per
  the wrapper README's binding rule — measured **55.5 GB per card**, run
  clean.  Probe templates now carry `amr.checkpoint_files_output = 0`: the
  first ladder left 87 GB of dead `Chk00001` dirs from `max_steps = 1` runs.

**Cost of the bigger box (estimated, then smoke-tested).**  The AMR hierarchy
currently carries ~4.1 M cells *per level*; fine levels dominate runtime
(level ℓ substeps 2^ℓ times).  Doubling L only grows level 0 (2.1 → 16.8 M
cells, weight 1 of ~62), so the slowdown should be modest — estimate
**3.5–4.0 u/h at level 5**, i.e. ~10–25% below today's 4.3.  Memory is the
real risk: current arms sit at 48–52 GB of 80; +14.7 M base cells adds an
estimated ~25 GB → ~75 GB, tight.  **A t = 5 smoke run measures both numbers
before anything is committed.**  (2026-09-02: if one card is tight, the
declared fallback is MPI multi-rank across cards — the known AMR crash is
specific to the radial regrid recipe, and the merger tags with type 2 — so
memory alone does not force L = 96.)  Fallback if it doesn't fit: L = 96 / N = 192
(sponge 40 → 48, radii 20/26/32/38) — still fixes issues 1–2.

**The oscillation is scalar-coupled, not a quiet-matter ringdown
(checked 2026-09-02).**  Question posed: is the post-merger waveform
oscillation driven by vacuum ringing of the remnant, or by the leftover
phantom scalar sloshing around it?  Answer from the m9b fill chain
(t = 60–91, R = 14, cached mid-plane slices every 0.5 units): **the scalar
rings in lockstep with the metric.**

| signal at R = 14 | period |
|---|---|
| Ψ4 (l = 2, m = 0) | ~17.3 |
| φ, m = 1 ring amplitude | ~17.0 |
| ∂t φ, m = 1 ring amplitude | ~17.7 |
| φ ring rms | ~17.0 |

The remnant keeps a live dipolar scalar halo at the extraction radius
(|φ| ~ 6e-3 — nothing like vacuum) whose amplitude oscillates by ±19 % at
the same period as Ψ4; the dipole pattern also precesses slowly (~41 units
per turn).  Framing for the paper: identical periods prove a **coupled
scalar–metric mode of the remnant** — not which channel drives which; in a
scalar-tensor system they ring together.  Either way it answers the reviewer
question "why does the waveform oscillate": the merged object retains
sloshing phantom matter, a signature no vacuum BBH can produce.

Method notes (validated two ways: φ and ∂t φ are independently evolved
fields and give the same period, cross-checked against the psi4 mode file;
window ends at t = 91 on a live, NaN-free run).  Trap for whoever repeats
this: the throats have opposite scalar signs, so φ at the ring is a *dipole*
— an angular mean cancels to 1e-10 and falsely reads "scalar quiet"; the
power sits in the m = 1 azimuthal harmonic.  Figure and script:
`runs/wormhole_merger/merger_fix/plots/scalar_vs_psi4_R14.{png,py}`.

**Is the ringing an artifact of the frozen core?  Tested — no.**  The
freeze only holds a tiny ball (fully frozen inside r = 1.3 for fill, 1.5 for
fillwide, blended out by 1.8 / 2.0); R = 14 is ten freeze-radii away, in fully
evolving field.  A frozen ball is still an artificial inner boundary, so the
check is whether the period follows the freeze geometry: fill vs fillwide
differ by ~15 % in freeze radius, and a cavity mode set by that boundary
would shift by roughly as much.  Measured: fill 17.3 / 17.0 / 17.7 vs
fillwide 17.7 / 17.7 / 18.0 (Ψ4 / φ m=1 / ∂t φ m=1) — a ~2 % shift, within
the 4-crossing precision — and the dipole precession rate matches to 0.2 %
(0.1537 vs 0.1540 rad/unit).  The mode belongs to the remnant and its halo,
not to the freeze ball.

Production implication: slice caches only reach r = 16, so this check cannot
be done at R = 30 or on the four production radii.  The production runs
should extract scalar modes on the same spheres as Ψ4 — per the diagnostics
rule, its own small module with its own output file, default off.

---

## 4. Max level: 5 for production, 6 as the convergence companion, 7 never by default

The question "start at max level 7, run till collapse, then freeze?" has a
measured answer — the m4e ladder.  *(Corrected 2026-09-02: the first draft of
this table quoted two readings Plan.md had already withdrawn the same day.)*

| max_level | speed (u/h, one card) | death, pair mean | gain per level |
|---|---|---|---|
| 3 | (scout ladder) | 52.26 | — |
| 4 | 9.0 | 53.43 | +1.17 |
| 5 | 4.3 | 55.18 | +1.76 |
| 6 | 2.2 | 56.42 | +1.24 |
| 7 | 1.1 | 56.20 — **one arm, no twin** | −0.22 vs the lvl-6 pair |

What the ladder actually established, in Plan.md's final wording:
- The pair-mean ladder is **linear at +1.43 per level over four rungs**; the
  increments scatter by ±0.3, the size of the ±0.35 reproducibility floor.
  No super-linear cure and no saturation — both were single-arm artefacts
  (the "three laws in one day" trap).
- **Damping's effect is zero** (by level +0.33 / +0.65 / −0.84 / +0.58, mean
  +0.18 against a ±0.35 floor, alternating sign).  The "crossover from cure
  to cost at level 5" is withdrawn; production runs the **clean** config.
- Level 7's 56.20 sits below the level-6 pair mean and both fits — but it is
  a single arm, exactly the read the trap table forbids, and it is *above*
  level 6's clean arm (56.13).  Honest wording: **consistent with saturation
  within the noise floor**, not "turned over".  Either way refinement is
  priced out as a route: even on the linear law, t ≈ 66 sits ~7 levels and
  ~10² × cost away, and the freeze delivered the window instead.
- The claim that survives every reversal: **the NaN lands on each newly
  created finest level, every time** (h11, every m4e arm) — the blowup is a
  feature of the continuum solution, not of the grid.

So: **production arms at max_level 5** (also the cheapest grid that reliably
reaches the engagement time — level 4 is a coin flip against its own death),
one **level-6 twin** of the headline arm as the convergence/error-bar
companion (that pair is also the paper's source-resolution study; the wave
zone gets its own twin, §8.4).  Level 7 only if a referee demands it, and
then as a **paired** short restart segment around collapse — never from
t = 0, and never as one arm.

**Engagement is a criterion, not a constant (revised 2026-09-02).**  The
first draft said "engage ~8 units after collapse"; that +8 was post-hoc
arithmetic.  What actually chose t_e = 53 was a three-way squeeze (Plan.md):
the collapse still sources the burst until ~51.5, so freezing earlier
deletes signal; the arm must *reach* t_e under its own power (level 5 clears
it by ~2 units); and t_e sets the contamination ceiling at every radius
(§7's causal budget).  For production — where the spiral's collapse time is
unmeasured — t_e is set per-IVP by the same squeeze: read t_collapse and the
burst-sourcing end from the level-3 scout, confirm at level 5, engage after
the burst closes, and print the resulting ceilings next to the windows
before launch.  Fill radius 1.5 / 2.0-wide twin, the seam twin, and one
late-engagement control re-run once at L = 128, all unchanged from M9b.

---

## 5. GPU schedule (4 × H100 80 GB, one run per card)

| Phase | Runs | Cards | Wall time |
|---|---|---|---|
| 0 (now) | wave 8 drains (fill100/fillwide100 → t = 100); then the wave-8 checks: second peak at R = 30 near t ≈ 93, R = 30 tail past ceiling 84.5 | 2 | ~1.5 h |
| 1 | p-scan scouts (lvl 3, N = 128, t = 200) **+ the §2 fuse audit per scout**: S4 solo on card 2, S2+S3 sharing card 3 | 2–3 | ≤20 h worst case, mergers end sooner |
| 1b — starts the moment a wave-8 card frees; waits for nothing | check E re-run on the drainhole template (max_steps = 0, minutes); L = 128 smoke test (t = 5: memory + speed); **BBH vacuum control** (§8.1); repulsion a-points with the charge prediction (§8.7) | 2 | check E minutes; smoke hours; BBH ~1 day |
| 2 | production at L = 128, lvl 5, in-code extraction ON, `--scalar-modes` ON: baseline p = 0.12 arm + seam twin + **third-fill-radius arm** (§7 causal budget); spiral arm only if its scout merged and passed the fuse audit; level-6 companion of the headline arm | 4 | lvl-5 arms ~2.5–3 days; lvl-6 companion ~5–6 days |
| 2b | late-engagement control at L = 128 (restart segment, ~40 units); **head-on freeze arm** (§8.2); N = 192 wave-zone twin (§8.4) if §6.7 taken | 1–2, as twins free | ~12 h + ~1 d + ~2 d |
| 3 | analysis: 4-radius extrapolation **in retarded time using the measured 1.125× speed** (turns issue 16 into a remark, not an apology); energy/mass balance and remnant-mass discriminator (§8.3, §8.5); dissolution re-measure on the undamped arm (§8.6); constraints; frames re-rendered with colour limits from outside r = 3 (issue 17); pack + push | — | — |

**The minimum publishable set**, if the clock runs short: baseline arm +
seam twin + level-6 twin + BBH control + head-on.  The spiral and the scan
boundary are upgrades, not prerequisites.

Calendar total: **~1.5 weeks of compute** if phases overlap sensibly.
Checkpoints prune by hand as always (they are never auto-deleted); heavy data
stays on scratch, run dirs keep params/logs/small_data only.

**Multi-GPU note.**  MPI itself works on this node; the known AMR crash is
specific to the radial regrid recipe, and the merger uses tagging_type 2.  A
cheap 2-rank smoke test on the L = 128 box is worth one slot in phase 1b — if
it holds, the level-6 companion halves to ~3 days.  If it crashes, we lose
nothing: the schedule above assumes single-card throughout.

---

## 6. Decisions needed before phase 2 — now eight

The external review recommended answers, noted in brackets; **nothing here
is approved until the author says so**, and every launch still goes through
the launcher, by hand, one approval each.

1. **Approve the scan values** p = 0.25 / 0.35 / 0.45 / 0.55 (S1 = 0.12 is
   re-used).  *(Scouts already live per the earlier approval; review: keep.)*
2. **Headline IVP intent**: spiral-led or plunge-led?  *(Review: lead with
   the plunge unless a scout merges cleanly AND passes the §2 fuse audit.)*
3. **L = 128 vs the L = 96 fallback** — decided by the smoke test, but say
   now if 2.5–3 days per arm is too slow regardless.  *(Review: take 128;
   let the memory number decide.)*
4. Whether the repulsion a-scan points are wanted for a power-law panel.
   *(Review: yes, with the §8.7 charge prediction attached — it upgrades the
   panel to an analytic check.)*
5. **Tail length for the headline arm** (from §7): stop_time collapse + 150
   instead of + 100, to buy a credible decay-time measurement for the
   scalar-coupled ringdown (~+12 h at level-5 speed).  *(Review: yes.)*
6. **The comparison arms** (§8.1–8.2): BBH vacuum control at matched
   masses/momenta, and a head-on freeze arm.  *(Review: run the control
   first; together they are the energy-budget table.)*
7. **The N = 192 wave-zone twin** (§8.4): one more ~2-day arm so the
   extracted waveform, not just the source, has a convergence factor.
8. **A twin-from-t = 0 of the headline arm** (§8.8): only if a per-waveform
   reproducibility bar is wanted beyond the quoted ±0.35 floor — no
   deterministic-reductions build flag exists to buy it cheaper.

Nothing launches until these are answered.

## 7. The exotic-matter ringdown as a detection signature (experimental thoughts, 2026-09-02)

The post-merger tail is the paper's potential physics headline, so this
section records what the data actually supports, what it refutes, and what
we do about it.  All numbers from the m9b fill chain at R = 14, window
t = 60–91 (~1.8 cycles), cross-validated between the independently evolved
φ and ∂t φ and the psi4 mode files.

**Established (each with its test):**
- The remnant is hairy: a dipolar phantom-scalar halo (|φ| ~ 6e-3 at R = 14)
  survives the merger and rings with the metric at the same ~17.3-unit
  period (§3 table).
- The channels are phase-locked: φ m=1 amplitude vs Ψ4 m=0 cross-correlate
  at |r| = 0.95 with lag +0.5 units — a quarter-period would be 4.3, so this
  is in-phase to measurement precision.  That is what one coupled eigenmode
  of the Einstein–Klein–Gordon system looks like, and what grid junk does
  not look like.
- The tail is long-lived but decaying: envelope fit over five extrema gives
  τ ≈ 150 units, i.e. quality factor Q ≈ 28 — an order of magnitude above a
  vacuum Schwarzschild l = 2 ringdown (Q ~ 3).  "Slow beat that outlives a
  vacuum ringdown by 10×" is the defensible headline; "continuous emission"
  is not (it decays), and τ from 1.8 cycles carries large error bars.
- Not a freeze artifact: 15 % change in freeze radius moves the period 2 %
  and the precession rate 0.2 % (§3).
- The story closes on the initial data: merging a +/− scalar pair (the sign
  flip that turned 5× repulsion into 6× attraction) is exactly what leaves a
  scalar dipole on the remnant.  The end of the run validates the beginning.

**Refuted by our own data — keep out of the paper:**
- The "lighthouse" mechanism (precessing dipole pumps the GW at twice its
  rotation rate).  Prediction: m = ±2 period π/0.1537 = 20.4.  Measured:
  m = ±2 rings at 17.3, same as m = 0, and its phase drifts at 0.187 rad/u,
  not 2 × 0.154.  All Ψ4 channels ring at the breathing period; the ~41-unit
  dipole precession is a separate, slower clock that does not detectably
  drive Ψ4.  The driver is the halo's amplitude breathing, not its rotation.

**Standing caveats for the writing:** the azimuthal ring harmonic is not a
proper spherical l = 1 mode (production fixes this); the true nature of the
core is masked by the freeze even though the exterior ignores the ball
size; phantom matter violates energy conditions, so "detection signature"
means "signature of this class of exotic matter", not an astrophysical
prediction; and there is **no ringdown convergence point yet** — the kept
lvl6 arm died at t = 56, before the window opens, so period convergence
rests entirely on the production level-6 twin.

**The causal budget — stated plainly (added 2026-09-02).**  The clean
window at any radius is set by the engagement delay, not by R: the burst
from the collapse arrives at ≈ t_c + 1.125·R, and freeze contamination
from r_s = 2 arrives at ≈ t_e + 1.125·(R − 2).  With t_c ≈ 45 and
t_e = 53 that is ~6–8 units of freeze-clean burst at R = 14 (ceiling
66.5) — and the *same* ~6–8 units at R = 44.  Pushing the spheres out
buys sponge-clean amplitude; it buys no freeze-clean time.  **The entire
17-unit-period ringdown, at every radius, sits inside the freeze's causal
cone.**  "Four radii, all causally clean" is true of the burst's leading
edge only.  The ringdown's credibility therefore rests on
freeze-insensitivity — the standard excision-radius argument, and the
right kind — which today has exactly two fill radii and ±2 % on a
4-crossing period.  Production upgrades, each cheap relative to the arm
it rides on:
1. **a third fill radius** (e.g. 1.0 / 1.4) so period-vs-fill-radius is a
   flat *trend*, not a two-point difference;
2. the engagement-time pair (t_e, t_e + 2.5) re-run at L = 128, as
   already planned;
3. **the causal-arrival plot printed under every published waveform**,
   clean window shaded per radius — the figure that turns this from a
   buried caveat into a method.

**Verdict on the proposed further investigation — proceed, on four legs:**
1. **Scalar-mode extraction module** — **IMPLEMENTED 2026-09-02**
   (consumer-side: `extraction/scalar_modes.py`, own stream
   `scalar_modes.dat`, off by default).  Projects φ and Π onto s = 0
   spherical harmonics (default l = 0..2, all m) on the same spheres as Ψ4,
   plus a kinematic scalar flux per radius for the energy budget.  Enable
   per launch by adding `--scalar-modes` to `WHM_CONSUME_ARGS`.  Validated
   three ways: analytic selftest (orthonormality + projection round-trip),
   physics of a live p045 plotfile at t = 13 (dipole |l1 m±1| = 0.76
   dominating by 4 orders, exact ± symmetry, zero z-dipole), and a 7 %
   match against the independent slice-cache ring harmonic at the same
   instant (residual = l = 3 leakage into the equatorial trace).
2. **A longer tail for the headline arm**: measuring τ ≈ 150 credibly needs
   ~1 e-fold of decay, i.e. ~150 units past merger.  Baseline stop_time 150
   gives only ~0.6 e-folds; extending the headline arm to collapse + 150
   buys the τ measurement for roughly +12 h at level-5 speed.  Added to §6
   as a decision.
3. **Ringdown convergence via the level-6 twin** (already planned §4): the
   17.3-unit period and the τ estimate must reproduce at level 6 with the
   freeze armed, or they are grid numbers.
4. **The remnant-mass discriminator (added 2026-09-02)**: a vacuum
   Schwarzschild l = 2 fundamental rings with period ≈ 16.8 M, so the
   measured 17.3 is what a plain BH of M ≈ 1.03 would do — while this
   system's ADM mass is ≈ 2, which would ring at ~34.  Measure M_ADM(t) of
   the remnant (§8.3's mass balance produces it); if M_remnant ≈ 1.9–2.0,
   the "it's just a BH ringdown" reading dies by a factor of two in one
   line.  The cheapest Letter-grade check on the list; no new runs.

Tier framing ("PRL vs PRD") is an author decision; the data case either way
is the four legs above, and the Letter version of the story — scalar-charge
dynamics, a horizon born dissolving, a hairy remnant ringing at 10× a
vacuum Q against a same-IVP BBH control — needs §8.1 and legs 2–4 to close,
with the freeze method and its validation as the companion-PRD material.
Figures: `runs/wormhole_merger/merger_fix/plots/`
(scalar_vs_psi4_R14 and the fillwide twin).

---

## 8. Comparison arms and budgets (added 2026-09-02, external review absorbed)

An external review of this plan was checked claim-by-claim against Plan.md,
Reference.md, the on-disk run data, and the code tree.  Its two structural
corrections — the withdrawn §4 readings and the causal budget — are folded
in above.  Two of its claims did **not** survive the check and are recorded
here so they are not re-imported later: "death time is bounded at 56–57
over levels 5–7" (three level-5 arms died below 56: 54.76 / 55.60 / 55.96),
and "the scalar charge is already measured per-throat to 0.3 %" (check F
was a *single* throat and an *angular-mean* estimator — the very estimator
the flipped binary cancels; the 0.3 % number is real but is the
single-throat tail, not a per-throat charge).  What follows is the review's
list of what a referee asks for first, sized against this tree.

**8.1 The vacuum BBH control — run it first.**  `Examples/BinaryBH` is
in-tree, same build system, in-code Weyl extraction already enabled in its
production params.  The same-IVP BBH waveform beside the wormhole waveform
is the standard figure of every boson-star and Proca-star merger paper — it
turns "a signature no vacuum BBH can produce" (§3) from a sentence into a
measurement.  Momenta are params-only (Bowen–York P *is* the ADM momentum:
`bh1.momentum` / `bh2.momentum`).  Masses carry one caveat: the default
`BoostedBHInitialData` takes a *bare* puncture mass, so matching the
target ADM mass means a short offline iteration on that number — or clone
TwoPunctures (external repo + GSL, `two_punctures.calculate_target_masses`)
for exact targets.  Vacuum steps are cheap; one card, roughly a day.

**8.2 A head-on arm with the freeze.**  The only configuration with a
literature number (BBH head-on from rest radiates ≈ 0.055 % of M, l = 2
m = 0 dominated); the campaign's old head-on died at its own collapse
before the freeze existed.  Shortest production run on the list, and with
8.1 it gives the paper an energy-budget table: wormhole vs BBH, head-on
and orbital.

**8.3 Energy/mass balance — the sum rule.**  M_ADM(t) at the outer
boundary versus E_GW from the in-code Ψ₄ stream (double-integrated, static
offset removed) plus the scalar kinematic flux from `--scalar-modes` —
which is *negative* for a phantom field.  Either the sum closes, or its
failure is itself a finding.  Angular-momentum balance for the spiral arm
if one qualifies.  Consumer-side work; no new runs.

**8.4 A resolution ladder that touches the wave zone.**  The level-6 twin
refines only the core; R = 20–44 sit on level 0 at dx = 0.5 in every arm,
so today the extracted waveform has no convergence factor of its own.  One
**N = 192 twin** of the headline arm (same L = 128, same max_level, base
dx = 2/3) is cheaper than the arm it shadows and gives the wave zone its
second point; with the level-6 twin that is three grids covering source
*and* wave zone.  Decision §6.7.

**8.5 The remnant-mass discriminator** — §7 leg 4.

**8.6 Horizon birth and dissolution, re-measured clean.**  The quoted
1.07 → 0.59 dissolution is a **two-arm splice whose late half comes from
the `rw` arm** — an arm the campaign itself disqualifies for wave physics
(lapse damping through collapse; admitted as timing evidence only).  The
trapped region is also strongly deformed (past r = 2 at the poles, ~0.6 at
the equator — results pack), which is why the radial in-code proxy loses
it.  Re-measure the full curve on the undamped level-5 headline arm with
the offline θ₊ scan over the ~4–5 units between collapse and freeze.  A
true MOTS finder does not exist in-tree (`docs/ah_finder.md` is a stub);
BHaHAHA goes on the infrastructure list — wanted for horizon mass/spin and
the angular-momentum budget, but not load-bearing for the dissolution
curve itself.

**8.7 Predict the scalar force, then measure it.**  The repulsion a-scan
becomes an analytic check if each throat's scalar charge q is read from
the l = 1 mode of the `--scalar-modes` stream (per-throat spheres; the old
check-F angular mean cancels on the flipped binary) and
F_scalar ∝ q_A·q_B is predicted alongside gravity.  The 6/4 pull/push
ratio and the 5× at a = 2 should both follow — the paper's cleanest
analytic check, for the price of a side figure.

**8.8 Reproducibility bar (issue 12) — closed, differently than the review
proposed.**  The review asked for a deterministic-GPU-reductions build
flag; **none exists in this tree** (AMReX's only determinism switch is a
C++ argument on `SumBoundary`, unreachable from GRTeclyn; the Ψ₄ surface
integral is already serial and deterministic on rank 0 — the
non-deterministic sums live in the diagnostics kernels).  The waveform's
reproducibility bar is therefore the *measured* ±0.35 twin floor: quote
it, and if a referee wants a per-waveform number, a twin-from-t = 0 of the
headline arm is one more arm (decision §6.8).

## 9. Validation pass 2026-09-03: C++ audit, build, and where the lapse actually collapses

Requested before the article: validate the merger implementation and build, and
explain the "zombie" (frozen, NaN-free) runs.  Method: a read-through of the
example's C++ (initial data, gauge, matter coupling, floors, damping/freeze
modules, tracker, diagnostics); a clean rebuild of a scratch copy of the
example; and a direct look at the cached z = 0 slices (χ, lapse, K, φ, Π,
shift) of nine runs at 2–6 epochs each, cross-checked against the `.dat`
streams.  Slices (yt covering grids from plotfiles) and `.dat` files (in-code
reductions) are independent instruments.

### 9.1 The lapse never collapses at the throats

In every binary run, at every epoch to the end, the two χ pits keep lapse
0.05–0.24 and |φ| 0.79–0.92.  The 3e-2 → 1e-3 → 1e-10 collapse that this plan
calls "core freeze" / "cores collapsed" sits at the **midpoint between the
throats**, where φ ≡ 0 by symmetry, K > 0 and the shift ≈ 0.  The isolated
throat never shows it (lapse 0.13 at t = 40).

| run | t | lapse at the pits | lapse at the midpoint | \|φ\| at the pits | K (sign, extent) |
|---|---|---|---|---|---|
| p020 L3 | 32.0 | 0.164 | 2.1e-2 | 0.87 | +0.14 |
| p020 L3 | 47.5 | 0.125 | 3.0e-3 | 0.87 | +0.20, no K < 0 core |
| plain p012 L3 | 43.5 | 0.134 | 1.9e-3 | 0.86 | — |
| helfer L3 | 30.0 | 0.175 | 5e-3 | 0.90 | — |
| helfer L3 | 60.0 | 0.073 | 1e-10 (floor) | 0.89 | +1.0, 5224 cells > 0.3 |
| helfer L4 | 48.0 | 0.177 | 3.1e-5 | 0.91 | +1.59, 1258 cells > 0.3 |
| helfer L5 | 28.0 | 0.209 | 1.08e-2 | 0.92 | +0.18 |
| p035 fly-by L3 | 73.5 | 0.046 | 1e-3 | — | +1.6, 7828 cells > 0.3 |
| p012 r03000 | 44.0 | 0.138 | blob to r ≈ 0.7 | 0.85 | +0.07 |
| p012 r03000 | 51.0 | 0.15–0.24 (rising) | shell: lapse < 3e-2 at r ≈ 0.5–0.85 | 0.79–0.83 | −1.5 at the core (K < 0) |

The midpoint value is the same at three resolutions (helfer L3/L4/L5 all
1.08e-2 at t = 28), so the collapse is converged: a property of these
equations, this gauge and this initial data, not of the grid.

### 9.2 Consequences for the readings above

- **"Zombie" explained.**  In helfer the floored region is a blob about the
  midpoint that grows outward (lapse < 1e-3 reaches 2.5 from a pit at t = 36,
  5.9 at t = 60; the K > 0.3 area grows 25× over t = 36–60; L2_Ham 5e-3 →
  1.1e-1).  At α = 1e-10 every α-proportional right-hand-side term vanishes,
  so the blob is static and NaN-free.  The runs that died of the level-3 h11
  NaN (r03000 52.06, n160 53.6, p025 52.98) had the midpoint lapse hovering
  near 3e-3, never floored — that is the t ≈ 52–53 wall, and reaching the
  floor is not what triggers it.
- **Helfer verdict.**  The stall is real (sep 4.7 → 5.3, 7° swept) and the
  REJECT stands, but the mechanism is the earlier nucleation of the midpoint
  blob (3e-2 at t = 25.4 vs 30.4 plain), which the throats then stall
  against.  Hypothesis worth one run: the window's constraint defect
  (1.8×) is concentrated near r ≈ width = 4 from each throat, i.e. at the
  midpoint; halving `wormhole_helfer_width` should move the nucleation.
- **p020 was not frozen.**  Half-space separation 1.44 (t = 40) → 1.19 (44)
  → 1.064 (45.5) → 1.079 (47.85, stopped by hand).  The merged p012 arm sat
  at 0.815 for 3.5 units (t = 40.5–44) before dropping to ~0.5 at t = 48.
  p020 at 47.5 (blob radius, pit lapse 0.125, K max +0.2, no K < 0 core yet)
  matches p012 at t ≈ 44: about 4 units behind the same sequence.  Its L3
  checkpoints were pruned; the L5 arm reaches this phase in ~10 h, a fresh
  L3 rerun to t = 60 in ~6 h.
- **p025 died of the wall, not of a freeze.**  Same level-3 h11 NaN at
  52.98 as the undamped p012 restart (52.06) and n160 (53.6).  The
  production p012 dodged it only because the freeze fill was armed at 53.4;
  p025 had no fill.  Its "freeze" is the same coordinate slow-down (shift → 0
  at the pits below sep ≈ 1) that p012 shows.
- **p012 endgame.**  At t = 48–51.5 the pits coincide within 0.2–0.6, the
  core lapse *rises* (0.14 → 0.24) with K < 0 (−0.8 → −1.6), and the
  collapsed-lapse region has become a shell at r ≈ 0.5–0.85 around the
  core.  The reported common trapped surface at r = 1.0 (t = 51.06) sits on
  that shell, where χ is at its floor and the constraints are rising.  It
  is consistent with black-hole formation in 1+log slicing, but it needs an
  independent apparent-horizon check on the t = 51 plotfile before the
  article says "common horizon".  The large-radius trapped verdicts in
  helfer (4.6 → 7.2), p035 (3.6–6.3) and p025 (2.06–2.12) coincide with the
  K ≈ 1 rim of the midpoint blob and are not credible.
- **The L5 arms cannot see the collapse.**  `collapse_diagnostics`,
  `binary_throat_diagnostics` and the tracker all reduce over the finest
  level only (`finest_lev` in `BinaryWormholeLevel.cpp`).  At t ≈ 29 the
  level-5 blocks sit within ±1.25 of each pit and none contains the midpoint
  (plotfile headers of all three L5 arms), so the "slower" L5 collapse
  (0.115 vs 0.0108 at t = 28, helfer) is the near-pit minimum, not the
  midpoint.  The L5 slices give the midpoint 1.08e-2 — identical to L3/L4.
  Depth is not being tested until sep < 2.5.  The level-5 grid also clips χ
  at the pits to the 1e-8 floor at t = 0 (level 3 does not), so L3 → L5 is
  not a clean refinement rung.
- **Tracker degeneracy.**  `throat_track.dat` places both throats at the
  origin with sep 0.000 from the moment sep < search radius 2.0 (p020 36.0,
  plain 32.0, headon 31.1, r04000 40.0): pass 2 of `ThroatTracker` averages
  every in-sphere cell within 1e-6 of χ_min, and both pits qualify by
  symmetry.  Moving boxes then centre on the origin (still covering both
  pits, so refinement is unaffected).  Every sub-2 separation quoted in this
  plan comes from the half-space method, which stays valid by symmetry but
  is cell-quantised (0.06 hops).  Fix: restrict pass 2 to the neighbourhood
  of the pass-1 argmin cell, or split the search by half-space while
  sep < 2 × radius.
- **CoreMatterDamping is aimed at the wrong place.**  It is on in every
  scan/twin template (lapse window 3e-2 → 1e-3) and engages at t ≈ 30 on
  the midpoint blob, when no trapped surface exists (ah_r = 0) — the
  template's "unambiguously inside the trapped surface" rationale is false.
  Since φ ≈ 0 on the blob's core its direct erasure is small; whether it
  feeds the K growth at the rim needs a damping-off control.

### 9.3 Code and build

- Clean scratch rebuild (copy of the example, same flags): 114 compile
  units, 0 errors, links.  Warnings only: `maybe_unused` attribute ignored
  (`SmallDataIO.hpp:83–85`) and an unused `num_ghosts` (`Weyl4.impl.hpp:345`).
  The binary the arms are running (Sep 2 08:40) is content-current; make
  wants a rebuild only because one header's mtime was touched with zero
  content change.
- No sign or coupling error found: the phantom sign enters only T_μν, the
  Klein–Gordon right-hand side is standard, the matter momentum feeds the
  B-driver, 1+log and Gamma-driver are standard, floors run at every RK
  stage, Bowen–York and the Helfer window match their documentation.
- Hygiene: `Make.package` omits `CoreFreezeFill.hpp` and `ThroatTracker.hpp`
  from the header list (fine with dependency files present, fragile on a
  fresh clone); `parameters_and_version.txt` records the version as
  "(unknown)"; `collapse_diagnostics` writes the floors into the finest
  state before reducing (harmless, but a diagnostic should not mutate
  state).

### 9.4 What this changes

- Rename "core freeze" → "inter-throat lapse collapse" throughout; the
  throats never collapse.
- Drop "no merger at p ≠ 0.12" and "every capture hits the freeze"; p020
  was mid-sequence, p025 hit the wall.
- The p012 common horizon needs an independent horizon check before the
  article.
- Runs that answer "does p020 / p025 merge" without masking: level-3 p020
  with damping off and **no fill** to the wall (~5.5 h; relaunch pending),
  and the running level-5 p020/p025 arms (no fill, wall ≈ 55).  A fill is
  armed only afterwards, from a checkpoint, at a time after the throats have
  met.  Helfer L3 with `wormhole_helfer_width` halved (~6 h) remains the one
  test of the correction; the plain-p012 damping-off twin is deferred (no
  clean checkpoint; the p020 run covers it).

### 9.5 Housekeeping and results refresh, 2026-09-03

The run tree was cleaned and the git pack brought up to date with everything
Stage 4 has produced so far (`runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-03.md`
has the ledger):

- **Removed:** only `ABORTED_p020_fill53_t060` (the withdrawn fill-at-53
  launch, decision 1). Every other run directory is evidence for a claim and
  stays — including the stopped helfer_lvl5 twin (the level-5 stall
  datapoint) and the old p045 (the packed healthy control).
- **Logs:** finished runs' launcher logs gzipped into their run directories;
  a top-level `detached_gpu*.log` now always means a run live on that card.
- **Results pack refreshed:** `results/merger/` went from 9 packed runs to
  **21** (67 MB) — the four t200 scouts, the five Helfer/plain twins, and
  mid-run snapshots of the four in-flight arms; `summary.md`/`.csv`
  regenerated with per-run fates. `results/merger/README.md` now opens with
  a **claim-by-claim map** (paper subsection → runs that back it → where the
  numbers sit), written to be lifted straight into the article.
- **Snapshot at pack time (~03:50):** p020_lvl5 at t = 33.1, sep 2.44;
  p025_lvl5 at t = 33.6, sep 2.76 — both level-5 arms are *closing*, well
  inside their level-3 twins' capture tracks. helfer_w2 at t = 7.6 and
  p020_nofill at t = 12.0, too early to read.
