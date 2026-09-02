# Merging two regular exotic-matter drainhole throats in 3D Cartesian CCZ4

Working document: the current plan and the concise log of what broke and what fixed it.
Started 2026-08-28; rewritten 2026-09-01 after the horizon-timing bug; **compacted
2026-09-01** — closed history condensed, every measured number kept.
Literature: [background.md](background.md). Design and prior art: [Reference.md](Reference.md).
Runs live under `runs/wormhole_merger/` (not in git, own README); the packed extract is
[`results/merger/`](../../results/merger/README.md).

**The campaign in one line:** two drainhole throats merge only if one field is flipped;
the merged object collapses, briefly holds a horizon, and the phantom scalar then
destroys first the run (NaN at t ≈ 52–57) and then the horizon itself. Every knob
inside the formulation is measured dead, and the refinement ladder — linear +1.43/level
over four rungs — **turned over at level 7 (56.20 < level 6's 56.71): refinement is
finished as a route, by measurement**. The route that worked is **M9b smooth-fill
excision: on 2026-09-01 both freeze arms COMPLETED t = 66 — the first runs in
campaign history to reach their stop time — with the full R = 14 window on disk,
the waveform identical between the two fill radii and identical to every unfrozen
arm over shared times.** The window shows a smooth decaying tail, not a distinct
burst; wave 7 (both arms re-run to t = 80) gives the R = 30 sphere a causally clean
independent look at the collapse to settle whether that tail *is* the signature.

---

## Where we stand (2026-09-02)

**The record is in hand.** M7+M6 passed 2026-09-01: the freeze arms completed
(first completions in campaign history), re-ran clean to t = 80, and the R = 14
window is on disk and triple-validated (seam-radius twins identical, bit-identical
overlap with the unfrozen ladder arms, late-engagement control ≤ 0.003 %). What it
shows is not a burst: the waveform **oscillates** — it falls through a node at
t ≈ 66 and rises to a second peak ≈ 75, period ≈ 20. Measured propagation is
**1.125× slower than coordinate light** (R = 30 lags R = 14 by 18.0 over 16 units,
correlation 0.9998; 1/R falloff holds to 1.3 %), which moves the R = 30 collapse
window to **76.1–83.6** — so t = 80 stopped ~4 units short. Wave 8 is live: both
arms continued to t = 100 (from Chk08000, rolling checkpoints), plus the level-6
late-freeze control to t = 80. It closes the R = 30 window and tests whether the
second peak is real: it must reappear at R = 30 near t ≈ 93, and the late-freeze
arm's copy must not shift by 2.5. Everything below this paragraph is the history
of how the wall fell.

**The target.** The collapse (source time 44–51.5) emits the one waveform this
campaign exists to record. Signal at radius R lags the source by R, so it crosses the
R = 14 extraction sphere over **t ≈ 58–65.5**; the run must survive to **t ≈ 66**
(R = 30 would need 82 — optional). The recorded burst peaking at t = 37.5 is
plunge/whirl radiation, not the collapse.

**The wall.** The undamped Chk05000-cohort death is **52.0 ± 0.4** (±0.35 is the
measured run-to-run reproducibility floor; post-floor trajectories decohere by
construction, issue 12). Every interior knob has been turned and priced:

| knob | best effect on the wall |
| --- | --- |
| **grid refinement on restart (M4e)** | the only axis that ever moved the wall: **linear, +1.43 per level** over four rungs (arm-pair means). Delivers the window's leading edge by level 7–8; its *end* needs level ~13, past the memory ceiling |
| matter deletion (full window × rate plane) | +0.33, +0.65, −0.84, **+0.05 or better at level 6** — no consistent sign; inside the ±0.35 floor at three of four levels |
| timestep | 0 — **dt-converged at two depths**. Level 3: halving +0.17, quartering −0.39. Level 5: halving **+0.36** against a ±0.35 floor — the weakest possible "outside scatter", same death signature (h11, level 5), and priced out as a cure regardless (+0.36 per halving ⇒ ~2²³ × cost to reach t = 64) |
| Kreiss–Oliger dissipation | flat plateau, harm at the high end (σ 1.0 died earlier) |
| slicing-source cancellation | 0 (taper-only arm = undamped baseline to 0.03) |
| shift freezing | fatal — −1.8, dead 0.24 units after engagement |
| earlier damping engagement | vetoed — alters the stress-energy sourcing the burst (wave 3b) |

**The two convergence pillars** (load-bearing for M8): the blowup is *dt-converged*
(refining time reproduces it) and *sharpens into refinement* (the NaN moves onto each
newly created finest level). Both are signatures of a feature of the continuum
solution, not of the integrator or the grid.

**The arithmetic, revised three times in one day, and now closed.** On the level-4
rung the ladder read +1 per doubling — level 17 to reach t = 66, priced out, M9
forced. The level-5 rung then came in at **+2.50**, and the two-point ratio (2.48)
projected level 6 ≈ 61.8 and level 7 ≈ 77.2 — refinement as an outright cure. Level 6
measured it and the projection failed: **56.13, only +0.53**. The four clean rungs

| level | dx | death | gain |
| --- | --- | --- | --- |
| 3 (baseline) | 0.0625 | 52.09 | — |
| 4 | 0.03125 | 53.10 | +1.01 |
| 5 | 0.015625 | 55.60 | +2.50 |
| 6 | 0.0078125 | **56.13** | +0.53 |

look **saturating** — but that reading lasted twenty minutes. The damped level-6 arm
then died at **56.71**, its own largest gain (+1.95), and the two ladders are simply
noisy samples of one wall. Averaging each level's arm pair cancels the damping noise
(which is measured to be zero, below) and gives the robust estimator:

| level | clean | damped | pair mean | gain |
| --- | --- | --- | --- | --- |
| 3 | 52.09 | 52.42 | 52.26 | — |
| 4 | 53.10 | 53.75 | 53.43 | +1.17 |
| 5 | 55.60 | 54.76 | 55.18 | +1.76 |
| 6 | 56.13 | 56.71 | 56.42 | +1.24 |

**The ladder is LINEAR at +1.43 per level** (least-squares over four rungs; the three
increments 1.17/1.76/1.24 scatter by ±0.3, the size of the reproducibility floor).
Neither the super-linear reading nor the saturating one survives; both were
single-arm artefacts. Level 5 clean was high and level 5 damped was low, and each
in isolation told a different story.

**What linear means for the campaign.** Projected: level 7 ≈ **57.9**, level 8 ≈ 59.3,
level 9 ≈ 60.7. Reaching the *start* of the target window (58) takes level 7.1 —
essentially the arm now running. Reaching the *end* (66) takes **level 12.7**, far
beyond the memory ceiling (≈ 7 GB per level; level 7 measured at 57.5 GB of 81.5,
so level 9 is the last comfortable rung and level 10 is marginal). So refinement
alone can deliver the **leading edge** of the collapse burst and never the whole of
it. **M9b is promoted from insurance to the route to the complete signal**, with the
ladder continuing as the independent cross-check that M6 overlap needs.

What refinement has bought is real and kept: +4.6 units of wall, and the strongest
evidence in the campaign that the blowup is a continuum feature — the NaN moves onto
each newly created finest level, every time, in h11.

*(Superseded later the same day: level 7 measured **56.20**, below level 6 and below
both fits' projections — the ladder TURNED OVER, and the linear law fell like the two
before it. Refinement is closed as a route by measurement; the freeze delivered the
window instead. The paragraphs above stand as the record of how three laws were read
from four rungs in one day.)*

---

## The plan

Nothing launches without an explicit go-ahead; no step starts below a red gate.

- [x] **M1 — horizon instrument fixed** *(2026-09-01)*. The in-code θ₊ scan was
  conformally flat and invented a t ≈ 30 merger (see *The timing bug*). Now evaluates
  the full-metric expansion, same convention as the validated offline scanner; old
  binary preserved.
- [x] **M2+M3 — validation restart + horizon certification** *(2026-09-01, one
  undamped run from chk 04000)*. PASS both: fixed scan silent over t = 40 → 51.02
  (min θ = +0.158) where the old scan cried merger; first genuine trapped surface
  **t = 51.03, r = 1.0625**, offline scanner 0.7 % apart; evolution bit-identical to
  r03000 until the χ-floor at t ≈ 44.9. Died 51.71 (K), the expected undamped death.
- [x] **M4 — the certified causal seal FAILED, and the failure is the decisive
  measurement** *(2026-09-01)*. Radius window r < 0.80/0.95 gated to certification
  (t = 51.2) died at **51.69** — 0.015 before the undamped death. Damping worked
  where it reached (|φ|max 0.82 → 0.57 at engagement, then stalled); the killer sits
  at **r ≈ 0.95–1.3, at and outside the horizon**. The freeze hypothesis died with
  it: the horizon contracts from birth (1.110 → 1.070 over t = 50.5–51.5) and
  *accelerates* under the seal (1.0625 → 1.000 by 51.69) — the driver crosses from
  outside, exactly as the causal-seal argument requires. Lesson pair: a window
  strictly inside the horizon cannot reach the killer, and engagement at
  certification is too late by construction — publishability is recovered through
  the M6 overlap test, not the engagement clock.
- [x] **M4b waves 1–2 — the (window, rate) plane is exhausted** *(2026-09-01,
  seven arms; all deaths in the runs table)*. Rate is the only live axis and it
  peaks: τ = 0.25 → ~51.9 everywhere (window shape, size, lapse branch all
  irrelevant — even damping the whole object); **τ = 0.05 → 52.42–52.55**;
  τ = 0.02 → 51.88 with the NaN jumping to K. Optimum τ ≈ 0.05 buys ≈ +0.4 and no
  more. The mechanism, imaged in the fast arm's frames at t = 52.0: φ cleaned white
  inside the window with saturated crescents pinned at its edge, **wrong-sign K
  pockets (K ≈ −0.07) wrapped around the bar ends at r ≈ 1–2**, and Weyl4 showing
  the whirling bar radiating a clean quadrupole spiral — the collapse signature is
  in flight; the campaign needs only a run that survives its arrival.
- [x] **M4b wave 3a — gauge-source surgery falsified** *(2026-09-01)*. New
  default-off module `CoreLapseFreeze.hpp` (C² quintic taper of the Bona–Massó
  source only, advection intact). Taper-only arm **52.12 ≈ undamped 52.09**: the
  K → lapse re-inflation loop is *not* load-bearing — h_ij blows up regardless of
  the slicing source. Taper + matter (52.04/52.03) mildly *negated* the matter
  gain. The shift guard (shift/B RHS × (1−W)) killed in **0.24 units** — the
  fastest death on record; never freeze a sector partially.
- [x] **M4b wave 3b — damp through the collapse: VETOED** *(causality)*. The
  collapse at 44–51.5 sources the burst; damping in that window deletes the physics
  being recorded. rw's 55.00 stands as evidence about engagement timing only — its
  restart chain carries lapse damping through the collapse, so it is
  waveform-tainted.
- [x] **M4b wave 4 — timestep and dissipation closed** *(2026-09-01)*. dt halved
  in isolation: +0.17 (inside ±0.35). dt quartered: **−0.39** at 4× the cost — the
  blowup is dt-converged. σ lowered 5×: −0.15. Nothing to buy on either axis.
- [ ] **M4e — refine on restart: extra AMR levels from Chk05000** *(user-proposed
  2026-09-01; LIVE — the ladder runs to level 6)*. Restarting a max_level = 3
  checkpoint with a higher max_level works out of the box: `Amr::restart` fills the
  new levels' timestep/step-count state, geometry comes from the inputs file, and
  the geometric tagger (half-width L·2^−(l+2) about each throat) materialises each
  level at the first regrid. Level 4 = cube of half-width 2 at dx = 0.03125 —
  landing exactly on the r ≈ 1–2 bar ends; each further level halves both. This
  dodges the two costs that closed the old N-ladder: no t = 0 rerun (initial-data
  noise scales as 1/dx²) and ~3× cost per level instead of ~90×. `regrid_interval`
  needs max_level entries — templates carry six.
  - [x] **Level 4 results: resolution is a real axis — the first knob ever outside
    the scatter.** Undamped: 52.09 → **53.10** (+1.01). With τ = 0.05 ring:
    52.42 → **53.75** (+1.33) — refinement and matter deletion stack *better* than
    additively (0.33 + 1.01 < 1.66). Both NaNs in h11 **on the new level 4**.
  - [x] **Level 5 result: the ladder is SUPER-LINEAR, and the record is now
    clean.** Undamped 53.10 → **55.60** (h11, on the new level 5): **+2.50**,
    two and a half times the level-4 rung's +1.01. This is the campaign's
    all-time survival record *and* the first record with no matter damping
    anywhere in the run — the previous holder (rw, 55.00) damped through the
    collapse that sources the burst and is waveform-tainted. The NaN again
    moved onto the newest finest level: the shock is a real feature that
    sharpens into whatever grid resolves it, but refinement is now **outrunning**
    it rather than merely delaying it.
  - [x] **Level 6, both arms: the ladder is LINEAR, and single arms lie.**
    Undamped 55.60 → **56.13** (+0.53); damped 54.76 → **56.71** (+1.95).
    Both h11, both on the new level 6, 34 minutes apart. Read alone, the clean
    ladder said "saturating at 56" and the damped one said "accelerating" —
    and *both readings were wrong*, as the super-linear reading taken from
    clean level 5 had been. The arm-pair means (52.26, 53.43, 55.18, 56.42)
    are linear at **+1.43 per level**, increments 1.17/1.76/1.24 scattering by
    exactly the ±0.35 reproducibility floor. **Lesson for this campaign,
    recorded because it has now cost three reversals in one day: a ladder
    increment measured on ONE arm is at the noise floor and must not be
    extrapolated.** Quote pair means, or quote nothing.
  - [x] **Damping's effect is zero.** By level: +0.33, +0.65, −0.84, **+0.58**.
    Mean +0.18 against a ±0.35 floor; the signs alternate. The level-5
    "crossover from help to harm" was noise and is withdrawn. **Matter
    deletion buys nothing that survives refinement, in either direction** —
    so run the clean arms, which need no M6 overlap caveat, and use the
    damped arms only as the second sample that makes the pair mean possible.
    The NaN moved onto the newest finest level in every arm at every level:
    the *diagnostic* claim is untouched by any of these reversals.
  - [x] **Box coverage: mostly confirmed, and it explains the saturation.**
    The tagger's boxes are 160³ cells at every level, so their half-widths
    *halve* as levels are added: level 4 reaches r = 2.5, level 5 → 1.25,
    level 6 → 0.625, level 7 → 0.3125, level 8 → 0.156. The imaged blowup
    ring sits at r ≈ 1–2. The prediction on record was: die near 55.6 and the
    ladder is over; die near 62 and deeper levels keep paying. The pair mean
    came in at **56.42** — the near end, but the ladder did *not* stop. So
    coverage is a real drag (it is why the gain is +1.4 and not +2.5) without
    being a wall. **Level 8 is uncancelled but demoted** — under the linear
    fit it buys +1.4 to ≈ 59.3, real but not the signal, at ~64 GB of 81.
    The better refinement move is *wider* fine boxes at r ≈ 1–2 rather than
    deeper ones: **M4f**, a tagger change, which would restore the full +2.5
    if coverage is the whole story. Both sit behind M9b.
  - [ ] Live and now the **discriminating** arm: **level 7 undamped**
    (dx 0.00390625, launched on the card the level-5 death freed, before the
    level-6 verdict). The linear fit projects **57.9**; the saturating reading
    briefly entertained after clean level 6 projected 56.3. Those are 1.6 units
    apart and the run settles it. It was flagged as a stop candidate under the
    saturating reading — **that recommendation is withdrawn; let it run.** At
    57.9 it would also be the first arm to reach the *start* of the target
    window (58) to within the noise floor. **The halved-timestep control at the
    same depth is done: 55.96 vs its twin's 55.60, +0.36 against a ±0.35 floor,
    same h11 death on level 5 — no effect, and the ladder is confirmed a
    resolution ladder rather than a timestep artefact.** `regrid_interval` needs
    **seven** entries at
    max_level 7. All ladder rungs run the *same* binary (`…ex.pre_fill`) so
    the ladder stays a single-variable experiment while the production binary
    carries M9b.
- [ ] **M9 — the formulation ladder** *(NEW 2026-09-01; user decision: the merger
  signal at any price; **promoted from insurance to primary route** the same day,
  when the level-6 rungs fixed the refinement ladder at a linear +1.43/level —
  which reaches the window's start but needs level ~13 for its end)*. What the field
  actually does about singular/violent interiors, in ascending order of surgery:
  1. *Moving punctures* — let the slicing hide the interior behind a horizon.
     **Our current method; measured insufficient here**: the killer sits at and
     outside the horizon, and the phantom dissolves the horizon itself.
  2. *Slicing family change* — e.g. shock-avoiding Bona–Massó variants
     (f = 1 + κ/α² instead of 1+log's f = 2/α), which provably avoid the gauge
     shocks 1+log can form.
  3. *Smooth interior fill* ("turduckening") — overwrite the offending region with
     smooth junk data and let causality protect the exterior; proven for BSSN
     black-hole interiors (constraint violations stay inside the horizon).
  4. *True excision* — cut the region out of the domain, one-sided stencils, no
     boundary condition where all characteristics flow inward (the
     Pretorius/spectral-code route). Powerful, notoriously delicate in Cartesian
     finite differences; moving punctures were invented to avoid it.

  Phantom-dissolution spacetimes have **no standard recipe** — none of 1–4 was
  designed for a horizon that evaporates out from under the gauge. Either outcome
  (signal captured, or every formulation-level tool falsified on a convergent wall)
  is a publishable result; M8 frames it.

  - [ ] **M9a — shock-avoiding slicing probe** *(cheap: one line in the gauge RHS
    plus a parameter; hours)*. Swap the 1+log source −2α(K − 2Θ) for
    −(α² + κ)(K − 2Θ), κ ≈ 1. Prior: **low** — wave 3a showed the slicing source is
    not load-bearing, and h_ij is what blows — but falsifying it costs two GPU-hours
    and closes bullet 2 with data. Pass: death moves > +1 outside scatter.
  - [ ] **M9b — smooth-fill excision: the main move** *(module `CoreFreezeFill`,
    coded, built, default-off; two arms live since 2026-09-01)*. **What shipped
    differs from the design sketched here and is simpler**: instead of snapshotting
    the interior and overwriting the state after each RK step, the module multiplies
    the *entire assembled RHS* by (1 − W) with the C² quintic W (1 inside r_full, 0
    at r_start), applied **last** in `specificEvalRHS` so it freezes the sum. Same
    end state — du/dt = 0 inside r_full, so the interior holds whatever it had at
    engagement — with no snapshot buffer and nothing to re-apply after a regrid.
    The shock site r ≈ 1–2 sits *inside* the fill and cannot steepen. Design answers
    to the three measured
    failure modes: matter damping lost a *race* (rate-limited) — overwrite is
    instantaneous, so **late engagement is safe for a fill** (unlike damping);
    freezeshift died of a *partial* freeze — the fill freezes every field
    self-consistently; the M4 seal missed the killer — the fill radius is set by
    the measured killer site (r_start ≈ 1.5–1.9), not by the horizon.
    - **The causal budget — why refinement + late fill closes the campaign.** The
      fill is *not* inside the horizon, so its influence propagates. Contamination
      from radius r_s engaged at t_e reaches R = 14 no earlier than
      t_e + (14 − r_s). The refinement creep buys late engagement: on the level-4
      wall (53.75), engage 53.4 with r_s = 1.5 → contamination ≥ 65.9, and the
      **entire required window 58–65.5 is causally clean**. On a level-5/6 wall
      (~54–56 if the creep holds) the margin grows to 1.5–2.5 units. The collapse
      core (arrival 58–61) is clean under every option on the table.
    - **Validation = the fill-radius ladder**, replacing the horizon argument:
      arms at r_full/r_start ∈ {1.2/1.5, 1.5/1.9} must overlap at R = 14 to few %
      (the standard excision-radius insensitivity test), plus the M6 overlap
      against the undamped arms over the shared window, plus the causal-arrival
      plot printed next to the waveform.
    - **Failure mode to watch:** the blend zone itself shocking. First answers:
      widen the ramp; engage slightly earlier; fill with a static smooth profile
      instead of the snapshot. If the blend zone is unfixable → M9c.
    - **The two arms actually launched (2026-09-01, wave 6).** Both restart from
      Chk05000, undamped, `max_level = 5`, `stop_time = 66`, engagement
      `from_time = 53.0`; they differ in **nothing but the skin radii**, so the
      radius-insensitivity test is a genuine single-variable experiment (verified by
      diff against the shared parent template and against each other).

      | arm | r_full / r_start | contamination reaches R = 14 at | target window 58–65.5 |
      | --- | --- | --- | --- |
      | `m9b_fill` | 1.3 / 1.8 | 53 + (14 − 1.8) = **65.2** | clean |
      | `m9b_fillwide` | 1.5 / 2.0 | 53 + (14 − 2.0) = **65.0** | clean |

    - **Why max_level 5 and not a cheap coarse grid, given the freeze does the
      work.** The arm must *reach* the engagement time under its own power. Level 3
      dies at 52.09/52.42 — ~0.8 **before** t = 53, so it would never live to be
      frozen; level 4 (53.10/53.75) is within the ±0.35 floor of engagement, a coin
      flip. Level 5 (55.60/54.76) clears it by ~2 units. Engaging *earlier* to let a
      coarse grid reach it fails twice over: the collapse is still sourcing the burst
      until 51.5 (freezing before that deletes the signal), and engaging at 51.5 puts
      contamination at R = 14 at 63.7 — *inside* the window. 53.0 is the only
      comfortable slot, and level 5 is the cheapest grid that gets there.
    - **Watch t = 53.0–53.5.** `CoreLapseFreeze`'s partial freeze died 0.24 code units
      after switch-on, so a blend zone that fails, fails fast. Past 55.6 is new ground.
    - **Follow-up once the fill holds** (not before): the frozen core no longer needs
      fine cells, yet the geometric tagger keeps refining it. Moving the fine boxes
      off the dead zone is worth roughly 3× speed and costs nothing physically.
    - Cost per arm ≈ 4.3 cu/h → a full pass to 66 is an afternoon, not days.
  - [ ] **M9c — true excision** *(weeks; last resort)*. A real hole in the grid
    (lego boundary inside r ≈ 1, one-sided stencils, boundary tracked to stay
    inside the fill region), only if M9b's blend zone proves unfixable. Everything
    M9b learns about radii and engagement transfers.
- [x] **M6 — overlap test** *(PASSED 2026-09-01, stronger than asked)*. The freeze
  arms match the unfrozen level-5/6/7 arms at R = 14 not to the few-% level but
  **bit-identically (5 digits) at every shared sample, before and after the
  freeze engages** — and the two fill radii match each other the same way over
  the entire causally clean window 58–65.0. The fill is invisible at the
  detector and the radius is not in the physics. The last freedom — engagement
  time — closed 2026-09-02: freezing at 55.5 instead of 53, on a finer grid,
  changes the R = 14 window by ≤ 0.003 % (m = 2) / 0.022 % (m = 0).
- [x] **M7 — the record** *(ACHIEVED at R = 14, 2026-09-01)*. Both freeze arms ran
  clean through t = 66.0 — zero NaN, first completions in campaign history — with
  the full window 58–65.5 on disk at R = 14. **Caveat that motivates wave 7:** the
  window contains a smooth decaying tail (m=2 peak 0.0296 at 55.5 falling to
  0.0174; m=0 falling to ~0.0015), not a distinct burst. Either the phantom
  dissolution radiates no sharp feature, or the arrival estimate is off. The
  stretch goal is now the main question: both arms re-launched to **t = 80**
  (`m9b_fill80`, `m9b_fillwide80`, rolling checkpoints keep-1), because R = 30
  sees the collapse over 73–80.5 while freeze contamination arrives there only
  at ≥ 81.0 — an independent, fully clean second measurement.
  **Resolved (2026-09-02, wave-7 data):** the "smooth decaying tail" was the
  descent of an oscillation — with data to t = 80 the waveform passes through a
  node at t ≈ 66 and rises to a second peak ≈ 75 (period ≈ 20). The measured
  1.125× propagation slowdown revises the arrival arithmetic: R = 30 window
  76.1–83.6, contamination ceilings 66.5 (R = 14) and 84.5 (R = 30) — so t = 80
  stopped ~4 units short ⇒ wave 8 continues both arms to t = 100. The second
  peak at R = 14 sits past that detector's ceiling; its reality rests on three
  tests: the two seam radii already agree exactly, the late-engagement arm must
  not shift it by 2.5, and it must reappear at R = 30 near t ≈ 93.
- [ ] **M8 — endpoint honesty in the paper.** The post-fill core is a numerically
  sustained ("zombie") interior — state it, with the causal-arrival plot next to
  the waveform. Framing (review, 2026-09-01): the M4/M4b/M4d falsification table
  *is* a physical discovery — phantom accretion drives extrinsic-curvature shocks
  in the surrounding geometry faster than any interior treatment can absorb,
  dissolves the horizon (Babichev accretion, measured 1.07 → 0.59 over
  t = 51.5–55), and the wall is dt-converged and refinement-sharpening. The
  extremity of the matter is the story; the surgery is its measurement.

**Standing instrumentation for every launch:** full plot list including h_ij and
A_ij (their absence made four early runs permanently unmeasurable offline), NaN
coordinates printed at abort, frame plane chosen from the arm's motion, per-field
auto colour limits. Checkpoint retention: `checkpoint_keep` prunes after a
successful write, never the restart parent, default 0 = keep all; sweep arms run
with checkpoints off entirely and restart from the one kept parent (m4_sealed's
Chk05000, t = 50).

**Success = M7 + M6:** one run whose R = 14 Ψ₄ stream is clean through t ≈ 66, with
an overlap-validated waveform, fill-radius insensitivity, and an honestly-labelled
interior.

---

## The corrected merger timeline

| t | what happens | evidence (two sources) |
| --- | --- | --- |
| 0–23 | inspiral, separation 11.94 → ~4 | both trackers; both resolutions agree ≤ 1.8 % |
| ~24–33 | plunge; throats' fields overlap (sep 3.6 → 2.1) | separation streams; Ψ₄ burst at R = 14 peaks t = 37.5 ⇒ source ≈ 23.5 (R = 30 copy lags by exactly 16) |
| 29.95–32.71 | *(artefact — no horizon)* old scan's "fusion" | convicted, see *The timing bug* |
| 33–43 | horizonless whirling double core, sep 1.8 → 0.8 | slice caches; max\|K\| falling 0.13 → 0.08 |
| 44–47 | **collapse** — the merger proper | min χ → 1e-8 floor at 44.9, max\|K\| ×18; movies' crush at ≈ 45 |
| 51.03–51.5 | **first genuine common trapped surface**, r = 1.0625 → 1.070 (sustained from 51.47) | fixed in-code scan (M3); offline scanner on the same run's plotfiles, 0.7 % apart |
| 51.5–55 | horizon dissolves 1.07 → 0.59, accelerating; extrapolated gone ≈ 56 | two damped arms, one curve; sampling-doubling moves crossings ≤ 0.01 |
| 51.7–55.0 | NaN deaths (sealed 51.69, val 51.71, r03000 52.06, n160 53.61, rw 55.00; +1/refinement doubling) | abort logs + last stream rows agree |
| 58–65.5 | collapse signature crosses R = 14 — **RECORDED 2026-09-01** (freeze arms). Not a burst: a descent through a node at t ≈ 66, then a second peak ≈ 75 (period ≈ 20) | triple-validated (seam-radius twins, unfrozen-arm overlap, late-engagement control); measured propagation 1.125× slower than coordinate light (lag 18.0/16.0, corr 0.9998, 1/R falloff to 1.3 %) |

The black hole lives ~5 units, not the ~26 once claimed: **born at t ≈ 51 already
dissolving**. Every "merged at t ≈ 30" sentence in older READMEs/drafts is wrong;
the headon arm's "horizon at 29" is the same artefact; n160's "horizon convergence"
was the artefact converging with the geometry it is a function of (its inspiral and
waveform convergence stand).

## Is the recorded signal a genuine gravitational wave? (2026-09-02)

Challenged twice ("slower than light = junk?", "R = 14 starts high"), answered by
measurement. Figures: `results/merger/figures/wave_speed_check.png` and the two
six-panel analyses next to it.

**The speed.** The wave crossed 14 → 30 in 18.0 time units — 0.889 of coordinate
light speed. That is not sub-luminal: *coordinate* light is also slower than 1 out
there, because near a mass clocks run slow and space is stretched, so everything
covers fewer coordinate units per coordinate second. The run records its own local
light speed on every slice: 0.75 at r = 13, still only 0.82 at r = 21. Integrating
that profile, **light itself needs ~19.5 units to make the equatorial 14 → 30
crossing; the wave took 18.0** — slightly faster than the in-plane light average,
exactly right for a sphere-averaged mode whose off-plane paths cross shallower
gravity. An arrival at coordinate speed 1.0 would have been the actual alarm
(faster than local light). And the real junk of this formulation — constraint and
gauge modes — travels at **√2 × light**, which would have crossed in ~13.8 units:
excluded by the measured 18.0. (The perturbed-pack reference figure shows the same
physics from the other side: its sphere-pair speeds read 0.995 c, 1.028 c, 1.085 c
— coordinate speeds scatter around c.)

**The falloff and the shape.** r·Ψ₄ is equal at both spheres to 1.3 % (m = 2) —
the 1/distance dilution of genuine radiation — and the two detectors' waveforms
correlate at 0.9998 in retarded time. In the six-panel figures the two curves
collapse onto one.

**The t = 0 offset at R = 14.** Nothing has arrived at either sphere at t = 0;
that offset is the *static* near-zone curvature of the freshly laid-down two-throat
data. It dies as ~1/r⁴ (measured sphere ratio 16–20), while radiation keeps r·Ψ₄
equal between spheres — which is why R = 30 starts at essentially zero and why the
offset is not part of the signal.

**Not freeze junk either.** Two seam radii, one waveform (0.000 %); engagement
moved 53 → 55.5 on a finer grid changes the window by ≤ 0.003 %; constraint norms
sit flat for 27 units after engagement (`merger_constraints_t80.png` — the spike
forest before t = 34 is regrid transients, the smooth bump at 41 is the collapse
itself).

Open item, closes with wave 8: the t ≈ 75 second peak at R = 14 must reappear at
R = 30 near t ≈ 93 with the same 1/R dilution, and must not shift by 2.5 in the
late-engagement arm.

## The timing bug (found and fixed 2026-09-01)

The in-code common-horizon scan
([BinaryThroatDiagnostics.hpp](../../Examples/BinaryWormholeMerger/BinaryThroatDiagnostics.hpp))
evaluated θ₊ with a conformally-flat shortcut — O(1) wrong between two deep wells,
in the trapped direction. Convicted by the healthy control p045 (18 units of
continuous false trapping in a collapse-free run) and by the t ≈ 30 "fusion" having
no collapse indicator under it (min χ rising, max|K| falling; it vanishes when the
shrinking scan sphere stops enclosing both wells). The real collapse is 44–47; the
first genuine trapped surface 51.03–51.5, confirmed independently by
[ah_radial_scan.py](../../grteclyn-wrapper/scripts/validation/ah_radial_scan.py).
The fix computes the full expansion (γ_ij = h_ij/χ, SPD guard that reports
"no verdict" — never "trapped" — on broken cells); columns and file contract
unchanged. **Tainted data:** θ/r columns (13–18) of every
`binary_throat_diagnostics.dat` written pre-fix, wherever two wells share one scan
sphere; per-throat positions/separations/minima in the same files are fine; the
offline scanner was never affected. It survived because it was validated on single
collapsed objects, where conformal flatness is fair — the two-well regime is where
it fails.

---

## The campaign so far

**Stage 0** *(2026-08-28)*: massive Ellis–Bronnikov drainhole on the grid, ADM mass
in the lapse, constraints exact at t = 0. **Stage 1** *(08-30)*: one throat holds
40 M with −0.36 % drift; growing mode identified (e-fold ≈ 4.4 ≈ throat/c) — the
40 M window is a fuse; budget every arm inside it. **Stage 2** *(08-31)*: tracker +
moving boxes; a boosted throat survives; like throats **repel** (5× gravity);
flipping one field is the only gravity-driven merger route (C/A infall 1.511 ±
0.033 vs 1.500 predicted). **Stage 3** *(live)*: merger achieved and converged;
every merging arm dies of the phantom NaN; horizon dissolution measured; the
collapse waveform is the missing piece. **Stage 4**: write — blocked on M7.

### The runs

| run | what is different | ran to | what happened |
| --- | --- | --- | --- |
| `..._r03000` | **main arm**, no damping | 52.06 | inspiral, collapse ≈ 45, horizon ≈ 51, NaN 1 unit later |
| `..._r05000` | damping, built-in thresholds (~3 cells) | 52.09 | window too deep; bought 0.02 |
| `..._r04000` | lapse window ×1000 wider; full plot list | 52.86 | core cleaned to φ ~ 1e-10, died anyway — sick cells re-inflate their lapse and climb out |
| `..._sg10_r05000` | dissipation σ 0.1 → 1.0 | 51.68 | died *earlier*: dissipation attacks the puncture structure |
| `..._rw_r05000` | radius window (r < 0.5/0.7), from t = 50 | **55.00** | longest survivor ever; caught the horizon dissolving — but its chain damps through the collapse: timing evidence only, waveform-tainted |
| `merge_headon_...` | head-on, no orbit | 44.00 | dies at its own collapse |
| `..._p045` | momentum 0.45 | **60.01 clean** | never merges — the healthy control that convicts the old θ scan |
| `..._n160` | 160³ instead of 128³ | 53.61 | pre-collapse converged; death +1.55 for 1.25× refinement (paid the 1/dx² initial-data penalty) |
| `..._ml2` | max_level 2 | 9.42 | three levels is the floor |
| `merger_fix/val_ahfix_r04000` | fixed θ kernel, no damping, from t = 40 | 51.71 | M2+M3 gate: artefact gone, real horizon 51.03 / r = 1.0625, bit-identical to r03000 until the floor |
| `merger_fix/m4_sealed_r04000` | radius window r < 0.80/0.95, engage t = 51.2 | 51.69 | M4 FAIL: certified seal bought 0.015; killer measured at r ≈ 0.95–1.3 |
| `merger_fix/m4b_wide_r05000` | radius 1.00/1.30, τ 0.25, from t = 50 | 51.94 | window over the ring: +0.25 |
| `merger_fix/m4b_combo_r05000` | + lapse branch | 51.94 | identical to wide: lapse window adds nothing |
| `merger_fix/m4b_fast_r05000` | radius 1.00/1.30, **τ 0.05** | **52.42** | the rate is the control variable |
| `merger_fix/m4b_sledge_r05000` | radius 2.00/2.50, τ 0.25 | 51.91 | damping the whole object changed nothing |
| `merger_fix/m4b2_vfast_r05000` | τ 0.02 | 51.88 (K) | 2.5× past optimum: gain returned, gauge shocked |
| `merger_fix/m4b2_fastsledge_r05000` | radius 2.00/2.50, τ 0.05 | **52.55** | +0.13 over fast — inside scatter: coverage falsified at the winning rate |
| `merger_fix/m4b2_fastcombo_r05000` | lapse + radius, τ 0.05 | 52.42 | = fast exactly |
| `merger_fix/m4c_freeze_r05000` | matter ring + lapse-source taper 1.00/1.30 | 52.04 | taper negated the matter gain |
| `merger_fix/m4c_freezewide_r05000` | taper 2.00/2.50 | 52.03 (h12) | first off-diagonal death; covering the pockets changed nothing |
| `merger_fix/m4c_freezeonly_r05000` | taper only, **no matter damping** | 52.12 | ≈ undamped baseline: slicing source is not the killer |
| `merger_fix/m4c_freezeshift_r05000` | + shift/B RHS × (1−W) | 50.24 (K) | shift guard fatal — fastest death on record |
| `merger_fix/m4d_dt001_plain_r05000` | dt halved, no damping | 52.26 | dt axis in isolation: +0.17, inside scatter |
| `merger_fix/m4d_dt001_fast_r05000` | dt halved + matter ring | 52.07 | no gain at the best-known config |
| `merger_fix/m4d_dt0005_fast_r05000` | dt quartered + matter ring | 52.03 (K) | 4× cut moved it *backwards* — dt-converged |
| `merger_fix/m4d_sig002_fast_r05000` | σ 0.02 + matter ring | 52.27 (h22) | dissipation flat at the low end too |
| `merger_fix/m4e_lvl4_plain_r05000` | **+1 AMR level on restart** (dx 0.03125), no damping | **53.10** (h11, lvl 4) | resolution is a real axis: +1.01 vs 52.09 — first knob outside the scatter |
| `merger_fix/m4e_lvl4_fast_r05000` | +1 level + matter τ 0.05 ring | **53.75** (h11, lvl 4) | stacks with damping: +1.33 vs 52.42 — clean-cohort record (rw's 55.00 is collapse-tainted) |
| `merger_fix/m4e_lvl5_plain_r05000` | +2 levels (dx 0.015625), no damping | 55.60 (h11, lvl 5) | high arm of the level-5 pair; read alone it said "super-linear" and was wrong |
| `merger_fix/m4e_lvl5_fast_r05000` | +2 levels + matter ring | 54.76 (h11, lvl 5) | low arm of the same pair; read alone it said "damping now harms" and was wrong. Pair mean **55.18** |
| `merger_fix/m4e_lvl6_plain_r05000` | +3 levels (dx 0.0078125), no damping | 56.13 (h11, lvl 6) | clean record; +0.53 read alone ⇒ the (withdrawn) saturating story |
| `merger_fix/m4e_lvl6_fast_r05000` | +3 levels + matter ring | **56.71** (h11, lvl 6) | **all-time record**; +1.95 read alone ⇒ the opposite story, 34 min later. Pair mean **56.42**, and the ladder is linear at +1.43/level |
| `merger_fix/m4e_lvl7_plain_r05000` | +4 levels (dx 0.00390625), no damping | **56.20** (h11, lvl 7) | **the ladder TURNED OVER**: below level 6's 56.71 and both fits' projections (linear 57.9, saturating 56.3). Refinement is finished as a route — measured, not extrapolated |
| `merger_fix/m4e_lvl5_dt001_r05000` | +2 levels, dt halved (0.01) | **55.96** (h11, lvl 5) | dt-convergence control at depth: **+0.36 vs the 55.60 twin, against a ±0.35 floor** — sitting on the boundary, one arm, and read as *no effect*. Second convergence pillar for M8: the ladder is a resolution ladder, not a timestep artefact |
| `merger_fix/m9b_fill_r05000` | **first interior freeze**: +2 levels, RHS × (1−W) inside 1.3/1.8 from t = 53 | **COMPLETED t = 66.0** | **first run in campaign history to reach its stop time.** Zero NaN; the whole R = 14 window 58–65.5 on disk |
| `merger_fix/m9b_fillwide_r05000` | same, skin 1.5/2.0 | **COMPLETED t = 66.0** | the radius-insensitivity twin: waveform identical to arm A to 5 digits at every sample — the fill radius is not in the physics. Also identical to the unfrozen lvl-5/6/7 arms over all shared times: the freeze is invisible at the detector |
| `merger_fix/m9b_fill80_r05000` | arm A re-run, stop 80, rolling checkpoints (keep 1) | **COMPLETED t = 80.0** | wave 7: measured the propagation speed (R = 30 lags R = 14 by 18.0 over 16 units, corr 0.9998 — 1.125× slower than coordinate light) and the 1/R falloff (1.3 % at R = 14). Moves the R = 30 window to 76.1–83.6: t = 80 was ~4 units short ⇒ wave 8 |
| `merger_fix/m9b_fillwide80_r05000` | arm B re-run, stop 80 | **COMPLETED t = 80.0** | wave 7 twin: identical waveform at both radii — two seam radii, one signal |
| `merger_fix/m9b_late6_r05000` | freeze at **55.5** (not 53) on **max_level 6**, stop 80 | *(live)* | engagement-time control: 2.5 extra units of real core history on a finer grid change the R = 14 window by ≤ 0.003 % (m = 2) / 0.022 % (m = 0) — the freeze clips nothing. Also the discriminator for the t ≈ 75 second peak: seam junk would shift by 2.5 here |
| `merger_fix/m9b_fill100_r08000` | arm A continued from Chk08000, stop 100 | *(live)* | wave 8: covers the full revised R = 30 window 76.1–83.6 and the second peak's predicted R = 30 arrival ≈ 93 |
| `merger_fix/m9b_fillwide100_r08000` | arm B continued, stop 100 | *(live)* | wave 8 twin |

---

## Issues found and what was done — the log

1. **Throat not on the grid** (puncture mass drove χ → 0; one cell 6.2 proper units).
   Fix: massive drainhole, ADM mass in the lapse — ~20× resolution gain. Cap m/a ≲ 1.
2. **σ = 2.0 ate 34 % of the throat while every norm read flat** — its smoothing
   lowers the violation it causes. Fix: σ = 0.1 in drainhole templates.
3. **Origin collar is load-bearing**: ×3.5 origin survival for 20 % of throat radius.
4. **χ-gradient tagging chased its own noise** to OOM. Fix: geometric taggers only;
   memory flat at 13.32 GB.
5. **The t ≈ 24 wall was a real EB growing mode** (e-fold 4.4 ≈ throat/c);
   max_level = 3 reaches t = 40 clean; ml2 is not viable.
6. **A moving throat survives**, but coordinate speed under-reads physical speed up
   to ~4×, time-dependently — orbit questions go to the slice cache, never the tracker.
7. **Like throats repel — 5× gravity** (support field carries scalar charge; phantom
   scalars repel like charges). Flip one field → pull; C/A 1.511 ± 0.033 vs 1.500.
8. **Phantom on collapsed geometry kills every run**; the death sits at the edge of
   whatever was cleaned; lapse-defined windows self-defeat (wrong-sign-K pockets
   re-inflate the lapse); extra dissipation makes it worse.
9. **The horizon is dissolving** — 1.07 (t = 51.5) → 0.59 (t = 55), accelerating;
   phantom accretion (Babichev): negative energy across the horizon shrinks it.
   Damping cannot be blamed — deleting negative energy biases toward growth.
10. **Resolution postpones, never cures** — and the M4e restart-refinement ladder
    turned this from a priced-out guess into a measured exchange rate: ≈ +1 per
    halving of dx, NaN sharpening onto each new finest level.
11. **The in-code θ scan was conformally flat and invented the t ≈ 30 merger** —
    the headline error of the campaign; fixed and validated same day (see *The
    timing bug*). It had also *missed* the real horizon: wrong in both directions.
12. **Post-floor, runs are not reproducible from their own checkpoints** — streams
    decohere once χ touches min_chi (t ≈ 44.9; floor clipping + non-deterministic
    GPU reductions; deaths 0.35 apart). Physics repeats; trajectories are samples.
    No claim tighter than the scatter; quote per-run numbers per run.
13. **Checkpoints (~10 GB each) were never deleted.** Fix: `checkpoint_keep`
    (own module), prunes only after a successful write, never the restart parent,
    default keep-all.
14. **A causally sealed window engaged at certification buys nothing** (M4):
    the cure must precede the crisis for rate-limited damping — but *not* for the
    M9b fill, which is instantaneous; that asymmetry is what makes late fill viable.
15. **The R = 30 extraction sphere sits inside the sponge layer** (absorber ramps
    r = 24 → 32, quartic, strength 4; at r = 30 the extra dissipation is ~13× base;
    the Sommerfeld outer boundary is the backup behind it). R = 14 is clear. Use
    R = 30 for timing and shape, never absolute amplitude; future runs put the
    outer sphere below r = 24. Radii deliberately unchanged mid-campaign so the
    continuation's columns concatenate.
16. **Propagation is 1.125× slower than coordinate light** (measured: lag 18.0
    over 16 coordinate units between spheres, correlation 0.9998). Every arrival
    estimate computed at v = c was ~11 % early; all windows and contamination
    ceilings revised accordingly.
17. **The freeze seam ring hijacks the frame colour scale.** Ψ₄ across the
    frozen/evolving junction grows ~×370 (0.02 → 9.0 by t = 79.5) while the real
    radiation out at r > 6 is ~0.001; per-frame auto colour limits scale to the
    ring, so every frame after engagement *looks* like the signal was deleted.
    It wasn't: at t = 55 the frozen arm is identical to its unfrozen twin to the
    last bit everywhere beyond r = 6, and the outgoing field stays put for the
    next 25 units. The ring itself stays confined to the seam. **TODO: re-render
    the freeze arms' frames with colour limits taken from the field outside
    r = 3** so the movies show the radiation, not the artefact
    (`runs/.../plots/seam_ring_rescaling.png` is the demonstration).

## Traps that must not regress

| trap | guard |
| --- | --- |
| **extrapolating a ladder increment from ONE arm** | a single rung-to-rung difference is the size of the ±0.35 reproducibility floor. On 2026-09-01 this produced three contradictory laws in one day from the same four levels — "super-linear", "saturating", "accelerating" — each falsified within hours. **Quote arm-pair means and a fit over ≥ 3 increments, or quote nothing.** Never launch on a two-point ratio |
| flat-conformal θ₊ shortcut | full-metric scan only; never reduce the h_ij dependence "for speed" |
| σ = 2.0 | 0.1 in all drainhole templates |
| `wormhole_momentumB` default | it is **minus** momentumA — pin `0 0 0` for a single throat |
| puncture route to ADM mass | `wormhole_id_type = 1` + `drainhole_mass`; ψ += m/2r̄ destroys the throat |
| `tagging_type = 2` without `throat_tracking` | rejected in `check_params` |
| frame slice plane | pick from the arm's motion at launch; default x-y hides z-motion |
| fixed colour scale on a growing field | per-field auto-zlim at launch |
| tracker across a late restart | re-seeds from params positions; beyond search radius 2.0 reads nA = 0 — seed from the last recorded row |
| `checkpoint_interval` after grid changes | counts coarse steps, not code units — recompute |
| root-level `restart_file` | dead key; use `amr.restart` |
| restart outer boundary | boundary error walks inward at ~c — Ψ₄ at R = 14 clean ~20 units after a restart; R = 30 ~12 |
| plot list | h_ij + A_ij always |
| damping windows combine as `max(w_lapse, w_radius)` | radius-only window needs `core_damping_lapse_start = 0`, else the damped region has no constant edge |
| restarting from a checkpoint that carries damping | Chk05000-of-r04000 damps through the collapse; restart earlier and gate by time |
| relative paths handed to `run_single.sh` | it `cd`s into the run dir; relative WHM values die as exit 127 — and remove the stub run dir before retrying |
| comparing two restarts of one arm past the floor | decoherence at t ≈ 44.9 by construction — no claim tighter than the scatter |
| damping engagement late | rate-limited damping must precede the crisis (≤ t = 50); the M9b *fill* is exempt — overwrite has no rate |
| auto colour limits on freeze-arm frames | the seam ring grows without bound and blanks the real radiation — take frame colour limits from the field outside the freeze band (r > 3), else every post-engagement frame reads "signal lost" |
| re-opening closed cures | timestep, dissipation, matter windows, slicing-source taper, shift freeze: all measured dead; resolution buys runway only |
| partial-sector freezes | freezing shift/B while the metric evolves killed in 0.24 units; any freeze must take every field or none |
| higher max_level on restart | works, but `regrid_interval` needs max_level entries — templates carry six |

## Dormant traps for Stage 2.2 (file-based initial data)

- Refining below a `.gridinit` solve's own dx erases the throat before step one;
  diagnose at max_level 0 or land the split-ID loader first.
- GRTresna can stall and print "Converged" anyway — read the residual, never the word.
- Noether-charge conservation is a resolution diagnostic, not a physics one.
- The areal-radius argmin lands on the innermost unresolved cell without
  `--areal-min-radius`.
- The Q-ball route was never refuted — the puncture geometry failed, not the matter.

## Known matter-sector inconsistencies (none affects runs so far; all use `phantom_mass = 0`)

1. `ExoticScalarField` flips the sign of the whole T_μν but not `dVdphi` — fix
   before any massive-phantom or Q-ball work.
2. Two-throat data is plain superposition — no Helfer/Ning correction.
3. `support_strength ≠ 1` breaks ∇·T = 0 — diagnostic knob only.

## Decision gates

- single throat loses charge > few % → instability is physical; reframe;
- CTTK returns K² < 0 with two exotic lumps → past the existence boundary; report
  the boundary as a finding;
- M9b blend zone unfixable *and* M9c excision unstable → the record honestly ends
  at the wall: publish the discovery (M8) with the falsification table.

**The standing caveat:** the Stage 1 growing mode is still growing at t = 40; the
40 M window is a fuse, not stability. Budget every arm to finish inside it.
