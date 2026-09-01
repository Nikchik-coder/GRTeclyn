# Merging two regular exotic-matter drainhole throats in 3D Cartesian CCZ4

Working document: the current plan and the concise log of what broke and what fixed it.
Started 2026-08-28; rewritten 2026-09-01 after the horizon-timing bug; **compacted
2026-09-01** — closed history condensed, every measured number kept.
Literature: [background.md](background.md). Design and prior art: [Reference.md](Reference.md).
Runs live under `runs/wormhole_merger/` (not in git, own README); the packed extract is
[`results/merger/`](../../results/merger/README.md).

**The campaign in one line:** two drainhole throats merge only if one field is flipped;
the merged object collapses, briefly holds a horizon, and the phantom scalar then
destroys first the run (NaN at t ≈ 52–55) and then the horizon itself. Every knob
inside the formulation is measured dead **except grid refinement, whose yield is
super-linear** (+1.01 for the first doubling, +2.50 for the second) — so refinement
is a candidate cure, not merely a delay. **User decision 2026-09-01: the merger
signal at any price** — the plan is the refinement ladder (live to level 7) with
late smooth-fill excision (M9b, coded and default-off) as insurance.

---

## Where we stand (2026-09-01)

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
| **grid refinement on restart (M4e)** | **the only real axis, and its yield GROWS: +1.01 then +2.50 per halving of dx; stacks with damping** |
| matter deletion (full window × rate plane) | +0.33 at the measured optimum τ = 0.05; window shape/size irrelevant |
| timestep | 0 — **dt-converged** (halving: +0.17 inside scatter; quartering: −0.39) |
| Kreiss–Oliger dissipation | flat plateau, harm at the high end (σ 1.0 died earlier) |
| slicing-source cancellation | 0 (taper-only arm = undamped baseline to 0.03) |
| shift freezing | fatal — −1.8, dead 0.24 units after engagement |
| earlier damping engagement | vetoed — alters the stress-energy sourcing the burst (wave 3b) |

**The two convergence pillars** (load-bearing for M8): the blowup is *dt-converged*
(refining time reproduces it) and *sharpens into refinement* (the NaN moves onto each
newly created finest level). Both are signatures of a feature of the continuum
solution, not of the integrator or the grid.

**The arithmetic, revised twice in one day.** On the level-4 rung alone the ladder
read +1 per doubling, needing level 17 to reach t = 66 — priced out, and M9 was
forced. The level-5 rung then came in at **+2.50, two and a half times the
previous rung**, and the two-point ratio (2.48) projects level 6 ≈ 61.8 and
level 7 ≈ 77.2. If that holds, **refinement alone clears t = 66 at level 7**, which
is inside the memory ceiling (≈ 7 GB per level; level 6 measured at 52 GB of 81).
Two increments do not make a law: levels 6 and 7 are running and measure it
directly. Plan for both outcomes — the ladder as the primary route, M9b as
insurance that also buys the *fill-radius* validation the paper wants either way.

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
  - [ ] Live: **level 7 undamped** (dx 0.00390625, user go-ahead 2026-09-01 —
    launched on the card the level-5 death freed, rather than waiting for the
    level-6 verdict, because if the trend holds it is the arm that reaches the
    signal), plus lvl5_fast and lvl6 ×2. `regrid_interval` needs **seven**
    entries at max_level 7. All ladder rungs run the *same* binary
    (`…ex.pre_fill`) so the ladder stays a single-variable experiment while the
    production binary rebuilds with M9b.
- [ ] **M9 — the formulation ladder** *(NEW 2026-09-01; user decision: the merger
  signal at any price)*. What the field actually does about singular/violent
  interiors, in ascending order of surgery:
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
  - [ ] **M9b — smooth-fill excision: the main move** *(new default-off module,
    ~1 day of code)*. At engagement time, snapshot every evolved field inside
    r < r_start; after every full RK step (and after each regrid), overwrite
    u ← (1 − W)·u + W·u_frozen with the C² quintic W (1 inside r_full, 0 at
    r_start). The interior becomes static junk; the shock site r ≈ 1–2 sits
    *inside* the fill and cannot steepen. Design answers to the three measured
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
    - Arms are proposed after the M4e read-out (they run on the best refined +
      τ = 0.05 restart, engagement at wall − 0.3). Cost per arm ≈ the lvl4/5
      arms' 3–4 cu/h → a full pass to 66 is an afternoon, not days.
  - [ ] **M9c — true excision** *(weeks; last resort)*. A real hole in the grid
    (lego boundary inside r ≈ 1, one-sided stencils, boundary tracked to stay
    inside the fill region), only if M9b's blend zone proves unfixable. Everything
    M9b learns about radii and engagement transfers.
- [ ] **M6 — overlap test** *(validates any surviving arm)*. Ψ₄ at R = 14 must match
  the undamped arms (r03000 to 52.06, n160 to 53.61, m4e_lvl4_plain to 53.10) over
  the shared window to the few-% level — no claim tighter than the ±0.35
  reproducibility scatter (issue 12). For M9b arms, extended by the fill-radius
  insensitivity ladder above.
- [ ] **M7 — the record.** One run clean through **t ≈ 66**: the collapse signature
  (source 44–51.5) on disk at R = 14. Optional stretch: 82 for R = 30.
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
| 58–65.5 | collapse signature crosses R = 14 — **never yet recorded** (44–47 collapse arrives 58–61; 51.5 horizon formation arrives 65.5 ⇒ stop_time ≈ 66) | propagation at v ≈ c (measured on the first burst) |

The black hole lives ~5 units, not the ~26 once claimed: **born at t ≈ 51 already
dissolving**. Every "merged at t ≈ 30" sentence in older READMEs/drafts is wrong;
the headon arm's "horizon at 29" is the same artefact; n160's "horizon convergence"
was the artefact converging with the geometry it is a function of (its inspiral and
waveform convergence stand).

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
| `merger_fix/m4e_lvl5_plain_r05000` | +2 levels (dx 0.015625), no damping | **55.60** (h11, lvl 5) | **all-time record, and the first clean one**: +2.50 over its lvl4 twin — the ladder is super-linear |
| `merger_fix/m4e_lvl5_fast_r05000` | +2 levels + matter ring | *(live)* | |
| `merger_fix/m4e_lvl6_plain_r05000` | +3 levels (dx 0.0078125), no damping | *(live)* | first test of the super-linear projection (~61.8) |
| `merger_fix/m4e_lvl6_fast_r05000` | +3 levels + matter ring | *(live)* | |
| `merger_fix/m4e_lvl7_plain_r05000` | +4 levels (dx 0.00390625), no damping | *(live)* | projected ~77 ⇒ the arm that could reach t = 66 outright; ~59 GB of 81 on the card |

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

## Traps that must not regress

| trap | guard |
| --- | --- |
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
