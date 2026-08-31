# Merging two regular exotic-matter wormhole throats in 3D Cartesian CCZ4

Working document: the plan, and the log of what was broken and what fixed it. Started
2026-08-28. Literature review: [background.md](background.md). Prior art, initial-data
gates and the file-by-file design: [Reference.md](Reference.md).

---

## The plan

### Stage 0 — put a real throat on the grid — **done 2026-08-28**

- [x] **0.1** Derive the massive Ellis–Bronnikov drainhole in the isotropic chart the code
  already uses; check it solves the constraints exactly
- [x] **0.2** Standalone check, no GPU: interior minimum of R exists, χ at the throat,
  proper cell width, the m/a ceiling, free-fall time
- [x] **0.3** Implement as a **default-off** initial-data mode
  ([BinaryWormholeInitialData.hpp](../../Examples/BinaryWormholeMerger/BinaryWormholeInitialData.hpp));
  no archived run may change
- [x] **0.4** Parameters + sanity net in
  [SimulationParameters.hpp](../../Examples/BinaryWormholeMerger/SimulationParameters.hpp)
- [x] **0.5** Build clean (CPU, then CUDA)
- [x] **0.6** Verify at t = 0 that χ_throat is O(1) and R_min holds at `max_level` 0, 1
  **and** 2 — the refinement test the puncture failed

### Stage 1 — one throat holds still — **exit condition met 2026-08-30**

- [x] **1.1** Params file: one throat, α = e^u exactly, 1+log, Gamma-driver from β = 0,
  `covariantZ4 = 0`, Sommerfeld out —
  [params_stage1_hold.txt](../../Examples/BinaryWormholeMerger/params_stage1_hold.txt)
- [x] **1.2** Run to t ≳ 20–30 M; measure R_min drift and constraint norms — five arms
- [x] **1.3** Decide the collar's fate — **keep it**, and know what it costs
- [x] **1.4** Mesh or wormhole? Two unigrid arms at dx = 0.50 and 0.25
- [x] **1.5** Stop the mesh chasing the error: add `FixedGridsTagger` as a default-off
  tagger choice
- [x] **1.6** Settle the wall at t ≈ 24 — bug or result. One extra refinement level

### Stage 2 — two throats

- [x] **2.0** Throat locator + moving boxes + wave-zone shells — implemented 2026-08-31;
  shakedown (boosted single throat) **in flight**
- [ ] **2.1** Superposed two-throat data with the Helfer/Ning companion correction, d = 16
- [ ] **2.2** CTTK solve in GRTresna; watch for K² < 0
- [ ] **2.3** Re-measure the growth rate on two-throat data — do not assume Stage 1 carries

### Stage 3 — the merger

- [ ] **3.1** Head-on from rest at d = 16, gravity-driven, no aimed momenta
- [ ] **3.2** Ψ₄ at several radii + the v ≈ c propagation test, to separate real radiation
  from superluminal constraint modes
- [ ] **3.3** Convergence and error budget

### Stage 4 — write

- [ ] **4.1** If 1–3 hold: two-throat head-on with Ψ₄
- [ ] **4.2** If 2 or 3 stalls: methods Letter on the regular two-throat data, or the
  exotic-lump head-on

### Open, not blocking

- [ ] Domain control (L = 96 or 128 at the same dx) — rules out the outer boundary and the
  sponge, which mesh-independence alone does not
- [ ] Does the surviving growing mode saturate? No run has gone past 40 M
- [ ] Print the NaN's position before the next arm that dies — the abort gives
  `level=… name=h11` and no coordinates
- [ ] Fix the phantom potential-sign inconsistency **before** any `phantom_mass ≠ 0` work

---

## Status at a glance

| | |
| --- | --- |
| the throat is regular | χ = 0.17 at the minimal surface, against the puncture's ~0.006 |
| the ADM mass goes in the lapse | `wormhole_id_type = 1`; the puncture route destroys the throat it is meant to weigh |
| one throat survives 40 M | −0.36 % on the throat radius, no NaN |
| the mesh is not the killer | fixed boxes hold 13.32 GB flat; moving the refinement boundary moves the death by 0.03 |
| the compactified origin is not the killer | refining it made every error smaller and pushed the wall past 40 M |
| **something real is still growing** | the momentum constraint rises exponentially and is still rising at t = 40 |
| two moving throats are now trackable | locator + moving boxes shipped 2026-08-31 |

**What 40 M is:** a fuse length, not stability. The run ends while the growth is
accelerating. Stage 3 can be budgeted against 40 M; it cannot be budgeted against an
unbounded window.

---

## What was broken, and what fixed it

### 1. The throat was not on the grid at all

**Broken.** The ADM mass was earned with a Brill–Lindquist puncture, `ψ += m/(2r̄)`, which
drives χ → 0 **at the throat itself**. Refining then *erased* the throat rather than
sharpening it. One cell at the minimal surface was 6.2 units of proper width — wider than
the throat it was meant to resolve.

**Fixed.** The massive Ellis–Bronnikov drainhole earns the same ADM mass from the **lapse**
and leaves the spatial conformal factor bounded. ~15 lines of initial data, no new chart.
With `X = (r̄ − a²/4r̄)/a` and `Ω = 1 + a²/(4r̄²)`:

| | |
| --- | --- |
| lapse exponent | `u = (m/a)(arctan X − π/2)` → 0 at infinity |
| lapse | `α = e^u` — part of the solution, not a gauge choice |
| conformal factor | `χ = e^{2u} / Ω²` |
| scalar | `φ = √(a²+m²)/(a√(4π)) · arctan X` |
| | `K = 0`, `A_ij = 0`, `Π = 0`, `M_ADM = m` |

The amplitude is fixed by the field equations (`4π C² = a² + m²`), not chosen, which is
what makes both constraints hold identically at t = 0. Verified to roundoff by
[drainhole_throat_check.py](../../grteclyn-wrapper/scripts/validation/drainhole_throat_check.py).

**Measured, 0.6** — a = 2, m = 1, L = 64, N = 128. Analytic: r̄ = 1.6180, R_min = 3.8895,
χ_throat = 0.1731.

| `max_level` | dx at the throat | puncture | drainhole | error |
| --- | --- | --- | --- | --- |
| 0 | 0.5 | present | R = 3.908 | 0.48 % |
| 1 | 0.25 | **gone** | R = 3.890 | **0.01 %** |
| 2 | 0.125 | **gone** | R = 3.892 | 0.06 % |

| at `max_level` 2 | throat areal radius | proper width of one cell there |
| --- | --- | --- |
| Brill–Lindquist puncture | 4.5 | **6.2 — wider than the throat** |
| massive drainhole | 3.89 | **0.31** |

A factor ~20 in proper resolution at the throat, bought with no extra grid.

**Three derived properties, two of them against the obvious guess:**

- the minimal surface is at `l = m`, i.e. `r̄ = (m + √(m²+a²))/2` — *not* at `l = 0`;
- `R_min = e^{−u(m)}√(m²+a²)`;
- **χ at the throat barely moves with mass** (0.25 at m/a = 0, 0.15 at 1.0): the throat
  migrates outward as m grows and the larger Ω⁻² almost cancels the smaller e^{2u}. Proper
  cell width there is 2.0–2.6 dx whatever the mass. **Mass no longer costs resolution.**

**New design constraint, not in the report:** `m/a` is capped near 1 — past that χ_throat
falls back toward puncture values. A heavier binary wants a *bigger* throat, not a heavier
one, and a bigger throat means a longer free-fall time (t_ff ∝ a at fixed m/a).

**Why the report's own fix was not taken.** It said to swap in the proper-radial (Ellis)
chart, whose slice has topology `R × S²` and cannot be embedded in one Cartesian box — as
the report itself says. The two are related by `l = r̄ − a²/(4r̄)` and the isotropic form is
equally regular at the throat; it only *also* compactifies the far universe to r̄ → 0, which
is unavoidable in a single box. **The chart was never the bug.**

### 2. Dissipation was destroying the throat while every monitor read clean

**Broken.** The inherited default `sigma = 2.0` shrinks the throat by **34 % over 40 M
while every constraint norm sits flat at 1.3e-3.** Smoothing *lowers* the violation it
causes, so the error monitors are structurally unable to see this failure. The overshoot on
the way (R = 4.40 at t = 20, above the initial 3.89) settles the direction — no collapsing
object grows first.

**Fixed.** `sigma = 0.1` in the three drainhole templates, 2026-08-30 — not 0, because a
little dissipation still buys stability at the refinement boundaries for ~0.1 % on R_min.
Puncture-era templates stay at 2.0: silently retuning runs the measurement does not cover
would be worse.

**The five arms** (a = 2, m = 1, `max_level = 2`; exact answer R_min = 3.8895):

| σ | collar | R_min reached | Hamiltonian L2 | ends |
| --- | --- | --- | --- | --- |
| 2.0 | no | **2.578** at t = 40 | 1.3e-3, flat throughout | ran to completion |
| 2.0 | yes | — | — | NaN at 21.7 |
| 0.1 | no | 3.894 — 0.1 % | 2.5e-3 flat, then spikes | NaN at 24.2 |
| 0.1 | yes | 3.127 — 20 % low | 3.7e+12 | NaN at 31.4 |
| 0.0 | no | 3.87–3.95, oscillating | 2e-3 → 1.2e-1, doubling ~5 M | **out of memory** at 35.2 |

The σ = 0 arm is the only one whose norm grows visibly — that growth is the run telling the
truth about an instability σ = 2.0 suppressed into silence.

### 3. The collar: predicted useless, measured load-bearing

**Broken prediction.** The plan said the origin-isolating collar (lapse type 6) was a
needless perturbation once χ was O(1) at the throat. Wrong.

**What the origin monitor shows.** `chiA_min` is the *origin* health monitor, not a throat
tracker, and it is the controlling variable in every arm:

| arm | dx at the origin | χ there at t = 0 | reaches the 1e-8 floor |
| --- | --- | --- | --- |
| unigrid, no collar | 0.5 | 2.44e-3 | **t = 6.6** |
| unigrid, no collar | 0.25 | 1.33e-4 | **t = 1.2** |
| `max_level` 2, no collar, σ = 0.1 | 0.125 | 7.19e-6 | t = 9.0 |
| `max_level` 2, **collar**, σ = 0.1 | 0.125 | 7.19e-6 | **t = 31.4** |
| `max_level` 2, no collar, σ = 0 | 0.125 | 7.19e-6 | **never** |

Collar buys a factor 3.5 in origin survival and costs 20 % of the throat radius. Collar and
dissipation are **two independent trade-offs, not one bad inherited setting**.

**Confirmed at t = 26, after an interim reading doubted it.** At t = 13 the collar arm
looked worst of three; it then outlived both (26.2 against 23.5 and 24.2) and failed the way
1.3 predicted — through the *throat* (−7.3 %, monotone), not the origin. Also corrected:
the collar arm's lapse sitting at the 1e-10 floor at the origin is **not** a failure — it
starts at 2.6e-7 by construction, because freezing the far universe is what the collar is
*for*. The pathological one is the collar-free arm, whose lapse began at 0.23 and collapsed
to the floor over t = 18–22.

### 4. The mesh chased its own noise until the card ran out

**Broken.** `ChiTagger` refines on χ gradients. With no dissipation the junk grows and
spreads, and the mesh follows it everywhere: level 2 ended at 1000 grids, 32.8M cells, 24 %
of the domain, 3.9 → 30.6 GB. That is what ended the σ = 0 arm at t = 35.2 — **memory, not
instability**, with the throat still at 3.87–3.95.

**Fixed.** `FixedGridsTagger` (already in `Source/Tagging/`, used unmodified) offered as a
default-off tagger choice. The footprint becomes a property of the *parameters* rather than
of the *error*, so the run can no longer die of its own mesh.

| key | default | meaning |
| --- | --- | --- |
| `tagging_type` | `0` | 0 = `ChiTagger`; 1 = fixed boxes; 2 = moving boxes (Stage 2.0) |
| `tagging_L` | `L` | level 0 tags \|x − centre\|_∞ < `tagging_L`/4, each finer level halves it |
| `tagging_center` | `center` | where the boxes sit |

`pre_tag_cells()` skips the χ ghost-fill entirely under the geometric taggers — it only
existed to feed `ChiTagger`'s second derivatives. `regrid_threshold` then does nothing, and
the parameter reader warns about exactly that, because a knob that silently does nothing is
how someone concludes the tagger did not help.

**Result, 2026-08-30: the memory failure mode is gone permanently, and the physics is
unchanged.** Levels 1 and 2 froze at 4 096 000 cells each for the whole run, against level 2
climbing to 32.8M under χ tagging; all three arms held 13.32 GB from first step to last. All
three still died, between t = 23.5 and 26.2, every one in `h11` on level 2.

| arm | σ | collar | NaN at | throat at death | how it got there |
| --- | --- | --- | --- | --- | --- |
| `s15_lapse5_sg00_fg` | 0 | no | **23.54** | +0.06 % until the last unit | Mom doubling every ~0.5 from t = 13; origin lapse 0.20 → floor over 18–22 |
| `s15_lapse6_sg00_fg` | 0 | yes | **26.23** | **−7.3 %, monotone** | constraints jump at 17–20, sit at 2–3e-1; throat shrinks throughout |
| `s15_lapse5_sg01_fg` | 0.1 | no | **24.17** | +0.04 % | **constraints flat at 3e-3 to the last step**; sudden and local |

**The tagger is necessary and not sufficient.** Two clean A/Bs against χ tagging:

| σ | collar | χ tagging | fixed boxes | verdict |
| --- | --- | --- | --- | --- |
| 0.1 | no | NaN at **24.2** | NaN at **24.17** | tagger irrelevant — 0.03 apart |
| 0 | no | t = **35.2**, OOM, no NaN | NaN at **23.54** | tagger costs **12 units** |

The σ = 0.1 pair is the sharp one: two runs with the level-2 boundary in completely
different places died at the same instant, in the same variable, with the throat 0.04 % from
its start. **Whatever kills them is mesh-independent.** The σ = 0 pair explains the rest —
with no dissipation the only thing suppressing the junk *was* the runaway refinement, so
removing it lets Mom run away from t = 13, far too fast for the physical mode. **The junk
must be either damped or resolved; χ tagging was silently supplying the second at a price it
could not afford.**

### 5. The refinement boundary was innocent — and so was the origin

**Suspected.** Both σ = 0.1 arms died on level 2, which reads like a refinement-boundary
failure.

**Measured (1.4).** Two `max_level = 0` arms, no refinement boundary anywhere:

| grid | NaN in | dies |
| --- | --- | --- |
| uniform dx = 0.50 | `K`, level 0 | t = 6.6 |
| uniform dx = 0.25 | `h11`, level 0 | t = 1.2 |

Removing refinement makes it **four times worse**; refining uniformly makes it **twenty
times worse**. Refinement is the protector. The mechanism is in the χ column above: χ
vanishes like r̄⁴ at the compactified far infinity, so halving dx puts the innermost cell
twice as close and drops χ there by 2⁴ (measured ratios 18.4 and 18.5) — and CCZ4 divides by
χ. A uniform grid cannot be refined at the origin without refining it everywhere. Reaching
the floor is a precursor, not the death: the no-collar σ = 0.1 arm floored at t = 9.0 and
ran to 24.2.

**Then the wall at t ≈ 24: bug or result.** Two explanations survived, and they predict
**opposite signs** under one extra refinement level:

| | adding a level predicts | the case for | the case against |
| --- | --- | --- | --- |
| **A — the under-resolved compactified origin** | the wall moves **earlier** | three unrelated levers all buy time and all target that region — dissipation damps it, the collar freezes it, runaway refinement resolves it | the collar arm froze the origin completely and **still died**, at 26.2, through the throat |
| **B — the real Ellis–Bronnikov growing mode** | the wall moves **later**, by ~4·ln(seed ratio) | one growing mode with timescale ~ throat/c ~ 4, so reaching O(1) from the 2e-3 floor takes ≈ 4·ln(500) ≈ 25 — it lands on the wall; and the two σ = 0.1 arms died 0.03 apart with the mesh rearranged | an order-of-magnitude argument: a factor 10 in the seed moves the prediction by 9 units |

**The answer, 2026-08-30** — `s16ml3_lapse5_sg01_fg`, the σ = 0.1 no-collar fixed-box arm
with `max_level = 3` and *nothing else changed*. Level 3 has dx = 0.0625 and covers
|x − c|_∞ < 4, holding both the throat and the compactified origin. 16.5 GB flat, 18.2 code
units/h, 2.2 h wall.

| | `max_level = 2` | `max_level = 3` |
| --- | --- | --- |
| outcome | NaN at 24.17 | **t = 40, clean** |
| R_min at t = 0 | 3.891721 (0.057 % high) | 3.889973 (**0.012 %**) |
| R_min drift at t = 12 | +0.035 % | +0.0005 % |
| L2 Ham at t = 12 | 2.48e-3 | 2.51e-3 |
| L2 Mom at t = 12 | 6.80e-5 | **7.51e-7** |
| χ at the origin | 7.19e-6, floors from t = 9 | 4.11e-7 → 9.95e-6, **rising all run** |
| α at the origin | 0.2315 → 0.2404 | 0.2194 → 0.1322 |

**The wall moved later, which excludes A.** Refining the origin was supposed to poison it —
and χ there did drop exactly as predicted (7.19e-6 → 4.11e-7) while every column got
*better*. The origin is not what was killing these runs.

**What is left is a real growing mode, still growing at the finish.** L2 Mom: 7.5e-7
(t = 12) → 5.1e-6 (17.6) → 1.4e-5 (26) → 3.3e-6 (34) → 3.9e-5 (40). The early e-folding time
is 4.4 against a predicted throat/c ≈ 4 — the one number Explanation B put on the table in
advance. It then dips near t = 34 and returns steeper, doubling every ~1.6, which no single
exponential explains and which no run has been taken far enough to resolve.

The frames say it in another currency: on a log scale with the throat drawn on
(`grteclyn-wrapper/scripts/plot/frames_logscale.py --ring 1.618`), K at t = 1 is a **square**
blob with corners on the grid axes and four diagonal lobes — the cubic mesh's own signature,
on a solution that should have K = 0 everywhere. By t = 39.5 it is smooth, round,
single-signed and monotone toward the centre, thirty times larger. Grid junk does not become
spherically symmetric; a physical mode does.

**So Stage 1's benchmark is met in the terms it was written in** — "R_min drift attributable
to the known EB unstable mode rather than to the grid": −0.36 % over 40 M, mode identified,
rate measured.

**Retracted along the way, because both would mislead a reader of the raw tables:**

- *"B predicts the wall does not move."* Wrong: a growing mode starts from the
  discretisation error, and refinement lowers it, so B predicts a **later** wall. Measured
  seed ratio 90 at t = 12 → ~18 units of delay → predicted wall near 42, off the end of a
  `stop_time = 40` run. Reaching 40 cleanly is a **B outcome**, not evidence against B.
- *"Do not run a deep fixed box on the origin as a fix."* Written from 1.4 and read across
  to a nested level, which it does not survive: the deep box was the cure, not the poison.
  1.4 stands for what it measured — halving dx *everywhere*, which also halves dt and
  rebuilds the whole solution.

**What refinement can still buy.** Each level halves dx, so χ at the innermost cell falls
16×: 4.11e-7 at level 3, ~2.6e-8 at 4, ~1.6e-9 at 5. With `min_chi = 1e-8`, **level 5 starts
below the floor** and level 4 sits 2.6× above it; each level also roughly doubles the wall
clock. Level 4 is reachable, level 5 is not. The thing to change is the *criterion*: centred
boxes refine throat and origin together, and a **shell-shaped tagger** removes the floor
problem entirely — the same work Stage 2.0 needed anyway.

### 6. The fixed box cannot survive two throats

**Broken by construction.** The throats *move*, one box cannot straddle both, and a merger
has to resolve a wave zone a single central box does not cover.

**The tempting wrong answer:** build a smarter criterion that tells junk from real structure.
Of the four taggers in `Source/Tagging/`, exactly one reads the solution — and that is the
field's answer, not an oversight:

| tagger | criterion | reads state? |
| --- | --- | --- |
| `ChiTagger` | \|∂²χ\| above a threshold | **yes** |
| `PunctureTagger` | distance to each tracked centre | no |
| `ExtractionTagger` | distance to each extraction radius, enforces a required level | no |
| `FixedGridsTagger` | distance to a fixed centre | no |

Production black-hole codes refine on **geometry decided before the run starts**. Junk never
gets a vote because the solution never gets a vote. The point underneath: **refining junk
feeds junk** — a finer grid resolves more of the noise spectrum, which pulls in more grid.
That loop ended the σ = 0 arm at 35.2, and no threshold makes a runaway loop safe; it only
sets the fuse length. Damp the junk; send refinement where it was told to go. (Textbook
Berger–Oliger truncation-error tagging fails for the same reason, harder: junk has enormous
truncation error by construction.)

**Fixed, 2026-08-31.** Three pieces, all in the example, none touching shared code:

| piece | where | what it does |
| --- | --- | --- |
| throat locator | [ThroatTracker.hpp](../../Examples/BinaryWormholeMerger/ThroatTracker.hpp) | finds each throat every coarse step, writes `throat_track.dat`; default off (`throat_tracking`) |
| moving boxes | `tagging_type = 2` | the fixed tagger's box arithmetic, centred on the tracked positions |
| wave-zone shells | same branch | the stock `ExtractionTagger`, composed in; a no-op while extraction is off |

**The locator is simpler than planned, and the reason is a wormhole-specific gift.** The plan
said "interior minimum of the areal radius, or the peak of the phantom field" — a
minimal-surface search in 3D. Neither is needed for the *boxes*: what the tagger wants is the
throat's **centre**, and in this chart every throat carries its own compactified far universe
exactly there, where χ falls like r̄⁴ to values orders of magnitude below anything else in the
field. The centre is the χ pit inside a small search sphere around the last known position —
a min-reduce plus a centroid over the near-minimum cells, which also handles a floor-clipped
plateau. **The very feature that makes the origin numerically fragile makes it an unmissable
beacon.** The minimal surface stays what it always was: a diagnostic, extracted post-hoc.

`PunctureTracker` stays off — it advects a particle backwards along the shift, locating a
coordinate singularity these data do not have. The pit is measured from the state, so the
tracker cannot drift away from the object it follows.

### 7. In flight: does a *moving* throat survive?

Every piece of Stage 1's evidence was collected with the throat pinned to the grid centre by
construction. A merger needs it to survive **crossing the grid**.

`s20_boost_p02`, launched 2026-08-31: the Stage 1 baseline (a = 2, m = 1, σ = 0.1, lapse 5,
`max_level = 3`, `tagging_L = 64`) plus one addition — a Bowen–York momentum P = 0.2 along z
([params_stage2_boosted.txt](../../Examples/BinaryWormholeMerger/params_stage2_boosted.txt)).
0.2 is the per-throat Newtonian speed of an equal-mass pair at d = 16, i.e. a genuine
late-inspiral speed. Two questions, in order:

1. **Infrastructure** — do the moving boxes keep the throat resolved as it crosses cells,
   refinement boundaries and box edges? Read `throat_track.dat`: `nA > 0` throughout. A zero
   means the boxes lost it — the failure this run exists to catch, visible not silent.
2. **Physics** — the boost makes the data inexact, so the mode starts from a larger seed.
   At t = 0, L2 Mom = 4.5e-6 (the discretisation residual of the analytically
   divergence-free Bowen–York term) against the resting arm's **exact zero**, with L2 Ham
   unchanged at 2.10e-3. The existing discretisation error is ~100× what the boost adds, so
   the wall may land near 40 rather than well before it.

**Readings to t ≈ 17** (continuing): zero lost rows; throat radius and origin lapse within
~1 %; Ham oscillating in 2.5–3.2e-3 with no trend; Mom doubling every ~12 units, *slower*
than the resting arm's 4.4. Coordinate speed ramps 0.02 → 0.115 as the shift builds from
zero — that is a **coordinate** speed, not the physical one, which is fixed at 0.2 by
construction. Settling near 0.2 means the grid has locked onto the object; plateauing low
means the boxes trail a throat still moving at 0.2.

Momentum stays a validation tool. **The merger itself remains gravity-driven** — two throats
released from rest, ADM mass in the lapse, never aimed momenta.

---

## Traps that must not regress

| trap | what happens | guard |
| --- | --- | --- |
| `sigma = 2.0` | eats 34 % of the throat while every norm reads flat | 0.1 in all drainhole templates |
| `wormhole_momentumB` default | it is **minus** `momentumA`; for a single centred throat that plants an equal-and-opposite term at the *same* point and cancels the boost exactly, silently | pin it to `0 0 0` |
| puncture route to ADM mass | destroys the throat it is meant to weigh | `wormhole_id_type = 1` + `drainhole_mass` |
| `regrid_threshold` under a geometric tagger | does nothing at all | the parameter reader warns |
| `tagging_type = 2` without `throat_tracking` | boxes centred on stale positions | rejected in `check_params` |
| frame slice plane | the default cuts the plane the motion is perpendicular to — a moving throat simply fades | pick the plane from the arm's physics at launch |
| areal radius under drift | it rays from the *static* grid centre, so it under-reads once the throat moves | re-extract post-hoc with the per-time centres in `throat_track.dat` |

**Not a candidate: σ = 2.0 as a stability fix.** It is the only setting that reaches t = 40
at `max_level = 2`, and it gets there by destroying the throat.

## Route B traps — what the 2026-08-28 matter investigation left behind

Folded in when `MatterDebug.md` was retired, 2026-08-31. Its main finding — a puncture
throat cannot be resolved in proper distance — is problem 1 above, and is fixed. These four
are not fixed but *dormant*, and each bites at **Stage 2.2**, the moment initial data starts
coming from a file instead of a formula.

**1. Refining below a file-based solve's own dx destroys the throat.** The `.gridinit`
bridge flattens the solve to level-0 dx; prolongation cannot recover sub-cell structure, so
it fills the interior with a nearly constant χ and the areal radius rises monotonically —
**the throat is gone before the first step**. Measured on identical data: `max_level = 0`
keeps it (interior minimum at r = 1.299, R = 4.507); levels 1 and 2 both lose it, while
level-0 ingestion is byte-exact, so the file is not the problem. "Do not evolve finer than
the ID's native dx" is too soft — refining does not fail to add detail, it **invents smooth
wrong detail**, here the absence of a wormhole. Route A is immune (analytic data evaluated
at each level's own dx; R_min recovered to 0.01 % at level 1). Either run throat diagnostics
at `max_level = 0`, or land the split-ID loader first.

**2. The solver can stall and report "Converged" anyway.** At `bh1_bare_mass = 4` the
GRTresna nonlinear solve went from 100 % Hamiltonian residual to **99.08 % in one
iteration** with max|δψ| = 0.005, exited early declaring convergence, and wrote an
`InitialDataFinal` that does not solve the constraints. A clean solve at m = 2 goes
100 % → 0.48 %. **Read the residual, never the word.** The stalled solve was deleted.

**3. Treat matter conservation as a resolution diagnostic, not a physics result.** On the
puncture geometry the Noether charge fell −10.52 → −2.09 (**−80 %**) by t = 14 while the
field amplitude barely moved (max φ 0.0997 → 0.075) and boundary flux was ~1e-11 — destroyed
*in the interior*, fastest over exactly the interval in which the throat closed. Until it
holds to a few per cent, no survival or collapse time from that family means anything.

**4. The areal-radius readout lands on the innermost cell if you let it.** R = r/√χ
*diverges* at the compactified origin, but unresolved inner cells report it small, so a bare
argmin tracks a "collapse" that is not happening — 0.152 against a true 0.498 on a b = 0.5
throat. `--areal-min-radius` excludes an inner ball; **archived `areal_radius.dat` columns
predating that flag are unreliable**, several reporting exactly dx/2.

**And the standing correction:** the Q-ball route (`ComplexExoticScalarField` + complex
sextic, whose conserved charge would give the support a preferred size) was **not refuted —
it was never testable.** Its own numbers were clean: painted amplitude 0.0997 against an
independently solved flat-space eigenstate of 0.0991, Π₂ = −ωφ to every printed digit, Ham
residual → 0.48 %, momentum residual identically zero. The geometry failed, not the matter.
On the drainhole it is testable again, and untested.

## Known inconsistencies in the matter sector

Flagged 2026-08-31 in review; none affects any run so far, all use `phantom_mass = 0`.

1. `ExoticScalarField` multiplies the *entire* T_μν — kinetic **and** potential — by
   −`support_strength`, while `add_matter_rhs` keeps the standard-sign `dVdphi`. Not
   derivable from one action once `phantom_mass ≠ 0`. **Fix before any massive-phantom or
   Q-ball work.**
2. Two-throat data is plain excess-sum superposition — no Helfer/Ning correction, no solve.
   That is exactly Stage 2.1/2.2.
3. `support_strength ≠ 1` scales gravity but not the field equation, so ∇·T ≠ 0. Diagnostic
   knob only.

## Decision gates (from the report, unchanged)

- single throat still loses charge > few % → the instability is *physical*; reframe as
  collapse/expansion of a two-throat system;
- CTTK returns K² < 0 with two exotic lumps → past the existence boundary; reduce ADM mass,
  increase separation, and **report the boundary as a finding**;
- timelike inner boundary (excision) unstable → abandon true topology for this paper.

## What Stage 3 costs, against the 40 M window

| separation d | free-fall time ≈ (π/2)·√(d³/8M) | fits in 40 M? |
| --- | --- | --- |
| 10 | ~12 M | easily — but the throats start close enough that the superposition correction works hard |
| 16 | ~25 M | **yes**, with 15 M of margin for ringdown and extraction |
| 20 | ~35 M | marginal; no room after merger |

The wide separation the superposition error wants (d/b ≥ 8, i.e. d = 16 at b = 2) is
affordable. That is what 1.6 bought.

**The caveat that survives.** The mode is still growing at t = 40 and doubling every ~1.6
there. Two throats seed it harder than one sitting at an exact fixed point, since superposed
data starts well above this run's 2.5e-3 floor. **Budget the merger to finish inside 40 M
rather than to run up to it, and re-measure the growth rate on two-throat data** rather than
assuming this one carries over.
